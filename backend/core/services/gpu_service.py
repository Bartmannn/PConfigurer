from core.models import Motherboard, GPU, Case, GPUConnector

class GPUService:
        
    @staticmethod
    def get_compatible_cases(gpu: GPU):
        return Case.objects.filter(
            max_gpu_length_mm__gte=gpu.length_mm
        )
        
    @staticmethod
    def get_compatible_motherboard(gpu):
        gpu_conn = GPUConnector.objects.filter(gpu=gpu, connector__category="PCIe").first()
        
        if not gpu_conn:
            return Motherboard.objects.none()

        return Motherboard.objects.filter(
            motherboardconnector__connector__category="PCIe",
            motherboardconnector__connector__lanes__gte=gpu_conn.connector.lanes,
            motherboardconnector__connector__version__gte=gpu_conn.connector.version,
            motherboardconnector__ilosc__gte=1
        ).distinct()
