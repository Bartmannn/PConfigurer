from core.models import Motherboard, CPU, RAM, MotherboardConnector, Case, GPU, Storage
from core import tools

class MotherboardService:
    
    @staticmethod
    def get_compatible_cpus(mobo: Motherboard):
        return CPU.objects.filter(socket=mobo.socket)
    
    @staticmethod
    def get_compatible_ram(mobo: Motherboard):
        return RAM.objects.filter(
            base__in=mobo.supported_ram.all(),
            modules_count__lte=mobo.dimm_slots,
            total_capacity__lte=mobo.max_ram_capacity,
        )
        
    @staticmethod
    def get_compatible_motherboards(data: dict[str, int]):
        qs = Motherboard.objects.all()
        
        cpu_pk = data.get("cpu")
        ram_pk = data.get("ram")
        gpu_pk = data.get("gpu")
        mem_pk = data.get("mem")
        case_pk = data.get("case")
        
        if cpu_pk:
            cpu = CPU.objects.get(pk=cpu_pk)
            qs = qs.filter(socket=cpu.socket)
            
        if ram_pk:
            ram = RAM.objects.get(pk=ram_pk)
            qs = qs.filter(
                supported_ram__in=[ram.base],
                dimm_slots__gte=ram.modules_count,
                max_ram_capacity__gte=ram.total_capacity,
            )
            
        if gpu_pk:
            gpu = GPU.objects.get(pk=gpu_pk) # TODO: czy tutaj order_by jest konieczne?
            gpu_chip = gpu.graphics_chip
            if not gpu_chip:
                raise ValueError("GPU bez PCIe!")

            qs = qs.filter(
                motherboardconnector__connector__category="PCIe",
                motherboardconnector__connector__lanes__gte=gpu_chip.pcie_max_width,
                motherboardconnector__quantity__gte=1
            )
            
        if mem_pk:
            mem = Storage.objects.get(pk=mem_pk)
            mem_conn = mem.connector
            
            allowed_slots = [mem_conn.category]
            if mem_conn.extra:
                allowed_slots.append("M.2 SATA")
                
            if mem_conn.category == "M.2 SATA":
                qs = qs.filter(
                    motherboardconnector__connector__category__in=allowed_slots,
                )
            else:
                qs = qs.filter(
                    motherboardconnector__connector__category__in=allowed_slots,
                    motherboardconnector__connector__version__gte=mem_conn.version,
                    motherboardconnector__connector__lanes__gte=mem_conn.lanes,
                )
                
        if case_pk: # TODO: jak działa prefetch_related? nie mam intuicji
            case = (
                Case.objects.filter(pk=case_pk)
                    .prefetch_related("mobo_form_factor_support")
                    .first()
            )
            supported_formats = case.mobo_form_factor_support.all()
            qs = qs.filter(form_factor__in=supported_formats)
            
        return qs.distinct()
    
    @staticmethod
    def get_compatible_gpus(mobo: Motherboard):
        # pobierz maksymalne wartości PCIe z mobo
        mobo_slot = (
            MotherboardConnector.objects
                .filter(motherboard=mobo, connector__category="PCIe")
                .order_by("-connector__lanes", "-connector__version")
                .values("connector__lanes")
                .first()
        )

        if not mobo_slot: # TODO: płyta główna może nie mieć PCIe?
            return GPU.objects.none()

        lanes = mobo_slot["connector__lanes"]
        qs = GPU.objects.filter(
            graphics_chip__pcie_max_width__lte=lanes,
        )

        return qs.distinct()
