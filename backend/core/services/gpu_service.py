from collections import defaultdict

from core.models import (
    Motherboard, GPU, Case, GPUConnector, MotherboardConnector,
    CPU, PSU
)
from core.services.psu_service import PSUService
from core import tools

class GPUService:
        
    @staticmethod
    def get_compatible_cases(gpu: GPU):
        return Case.objects.filter(
            max_gpu_length_mm__gte=gpu.length_mm
        )
        
    @staticmethod
    def get_compatible_motherboard(gpu):
        gpu_chip = gpu.graphics_chip
        if not gpu_chip:
            return Motherboard.objects.none()

        return Motherboard.objects.filter(
            motherboardconnector__connector__category="PCIe",
            motherboardconnector__connector__lanes__gte=gpu_chip.pcie_max_width,
            motherboardconnector__quantity__gte=1
        ).distinct()

    @staticmethod
    def get_compatible_gpus(data: dict[str, int]): # TODO: check ram and adjust CPU!
        qs = GPU.objects.all()
        
        psu_pk = data.get("psu")
        case_pk = data.get("case")
        mobo_pk = data.get("mobo")
        
        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            mobo_slot = (
                MotherboardConnector.objects
                .filter(motherboard=mobo, connector__category="PCIe")
                .order_by("-connector__lanes", "-connector__version")
                .values("connector__lanes")
                .first()
            )

            if not mobo_slot:
                return GPU.objects.none()

            lanes = mobo_slot["connector__lanes"]
            qs = qs.filter(
                graphics_chip__pcie_max_width__lte=lanes,
            )

        if psu_pk:
            # TODO: This logic doesn't handle quantity (e.g., GPU needs 2x8-pin, PSU has 1x8-pin).
            psu_connectors = (
                PSU.objects.filter(pk=psu_pk)
                .values_list("connectors", flat=True)
                .first()
            ) or []

            gpu_connectors = GPUConnector.objects.filter(
                gpu__in=qs,
                connector__category="PCIe Power"
            ).select_related("connector")

            requirements_by_gpu = defaultdict(list)
            for item in gpu_connectors:
                requirements_by_gpu[item.gpu_id].append(item.connector)

            compatible_ids = []
            for gpu_id in qs.values_list("id", flat=True):
                requirements = requirements_by_gpu.get(gpu_id, [])
                if all(
                    PSUService.psu_supports_connector(psu_connectors, req)
                    for req in requirements
                ):
                    compatible_ids.append(gpu_id)

            qs = qs.filter(pk__in=compatible_ids)

        if case_pk:
            case_max_gpu_length = (
                Case.objects.filter(pk=case_pk)
                .values_list("max_gpu_length_mm", flat=True)
                .first()
            )
            if case_max_gpu_length:
                qs = qs.filter(length_mm__lte=case_max_gpu_length)
            
        return qs.distinct()
