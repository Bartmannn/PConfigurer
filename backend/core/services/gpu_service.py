from core.models import (
    Motherboard, GPU, Case, GPUConnector, MotherboardConnector,
    CPU, PSU, PSUConnector
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
            # TODO: This logic is a simplification. It checks if a GPU needs a connector type that the PSU
            # doesn't have at all, but it doesn't properly handle quantity (e.g., GPU needs 2x8-pin, PSU has 1x8-pin).
            
            # Get the IDs of PCIe power connectors the PSU provides.
            psu_power_connector_ids = PSUConnector.objects.filter(
                psu__pk=psu_pk,
                connector__category="PCIe Power"
            ).values_list("connector_id", flat=True)
            
            # Find all GPUs that require at least one PCIe power connector that the PSU *doesn't* have.
            incompatible_gpus = GPU.objects.filter(
                gpuconnector__connector__category="PCIe Power"
            ).exclude(
                gpuconnector__connector_id__in=psu_power_connector_ids
            )
            
            # Exclude these incompatible GPUs from the main queryset.
            qs = qs.exclude(pk__in=incompatible_gpus.values_list('pk', flat=True))

        if case_pk:
            case_max_gpu_length = (
                Case.objects.filter(pk=case_pk)
                .values_list("max_gpu_length_mm", flat=True)
                .first()
            )
            if case_max_gpu_length:
                qs = qs.filter(length_mm__lte=case_max_gpu_length)
            
        return qs.distinct()
