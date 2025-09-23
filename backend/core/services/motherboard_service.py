from core.models import Motherboard, CPU, RAM, MotherboardConnector, GPU, GPUConnector


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
            gpu = GPU.objects.get(pk=gpu_pk)
            gpu_conn = (
                GPUConnector.objects
                .filter(gpu=gpu, connector__category="PCIe")
                .order_by("-connector__lanes", "-connector__version")
                .first()
            )
            
            if not gpu_conn:
                raise ValueError("GPU bez PCIe!")

            qs = qs.filter(
                motherboardconnector__connector__category="PCIe",
                motherboardconnector__connector__lanes__gte=gpu_conn.connector.lanes,
                motherboardconnector__connector__version__gte=gpu_conn.connector.version,
                motherboardconnector__quantity__gte=1
            )
            
        return qs
    
    @staticmethod
    def get_compatible_gpus(mobo: Motherboard):
        # pobierz maksymalne wartości PCIe z mobo
        mobo_slot = (
            MotherboardConnector.objects
            .filter(motherboard=mobo, connector__category="PCIe")
            .order_by("-connector__lanes", "-connector__version")
            .values("connector__lanes", "connector__version")
            .first()
        )

        if not mobo_slot: # TODO: płyta główna może nie mieć PCIe?
            return GPU.objects.none()

        lanes = mobo_slot["connector__lanes"]
        version = mobo_slot["connector__version"]

        qs = GPU.objects.filter(
            gpuconnector__connector__category="PCIe",
            gpuconnector__connector__lanes__lte=lanes,
            gpuconnector__connector__version__lte=version,
        )

        return qs.distinct()
