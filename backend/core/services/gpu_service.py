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
        gpu_conn = GPUConnector.objects\
            .filter(gpu=gpu, connector__category="PCIe")\
            .first()
        
        if not gpu_conn:
            return Motherboard.objects.none()

        return Motherboard.objects.filter(
            motherboardconnector__connector__category="PCIe",
            motherboardconnector__connector__lanes__gte=gpu_conn.connector.lanes,
            motherboardconnector__connector__version__gte=gpu_conn.connector.version,
            motherboardconnector__ilosc__gte=1
        ).distinct()

    @staticmethod
    def get_compatible_gpus(data: dict[str, int]): # TODO: check ram and adjust CPU!
        qs = GPU.objects.all()
        
        cpu_pk = data.get("cpu")
        psu_pk = data.get("psu")
        case_pk = data.get("case")
        mobo_pk = data.get("mobo")
        
        cpu_wattage = 0
        
        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            mobo_slot = (
                MotherboardConnector.objects
                .filter(motherboard=mobo, connector__category="PCIe")
                .order_by("-connector__lanes", "-connector__version")
                .values("connector__lanes", "connector__version")
                .first()
            )

            if not mobo_slot:
                return GPU.objects.none()

            lanes = mobo_slot["connector__lanes"]
            version = mobo_slot["connector__version"]

            qs = qs.filter(
                gpuconnector__connector__category="PCIe",
                gpuconnector__connector__lanes__lte=lanes,
                gpuconnector__connector__version__lte=version,
            )
            
        if cpu_pk:
            cpu_wattage = CPU.objects.filter(pk=cpu_pk).values_list("tdp", flat=True).first()
            
        if psu_pk:
            psu_wattage = (
                PSU.objects.filter(pk=psu_pk)
                .values_list("wattage", flat=True)
                .first()
            )
            
            psu_gpu_power = (
                PSUConnector.objects.filter(
                    psu__pk=psu_pk,
                    connector__category="PCIe Power"
                )
                .values_list("connector", flat=True)
            )
            
            qs = qs.filter(
                gpuconnector__connector__category="PCIe Power",
                gpuconnector__connector__in=psu_gpu_power,
                tdp__lte=psu_wattage * PSUService.SAFETY_FACTOR - cpu_wattage
            )

        if case_pk:
            case_max_gpu_length = (
                Case.objects.filter(pk=case_pk)
                .values_list("max_gpu_length_mm", flat=True)
                .first()
            )
            qs.filter(height_mm__lte=case_max_gpu_length)
            
        return qs.distinct()

