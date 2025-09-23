from core.models import Motherboard, GPU, Case, GPUConnector, MotherboardConnector

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
    def get_compatible_gpus(data: dict[str, int]):
        qs = GPU.objects.all()
        
        mobo_pk = data.get("mobo")
        
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

            qs = GPU.objects.filter(
                gpuconnector__connector__category="PCIe",
                gpuconnector__connector__lanes__lte=lanes,
                gpuconnector__connector__version__lte=version,
            )

        return qs.distinct()

