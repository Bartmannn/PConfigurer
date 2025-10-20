
from core.models import PSU, PSUConnector, Motherboard, GPU, MotherboardConnector, GPUConnector, CPU

class PSUService:
    
    SAFETY_FACTOR = 0.75
    
    @staticmethod
    def get_compatible_psus(data: dict[str, int]):
        
        qs = PSU.objects.all()
        
        mobo_pk = data.get("mobo")
        gpu_pk = data.get("gpu")
        cpu_pk = data.get("cpu")

        total_tdp = 0
        
        if cpu_pk:
            cpu = CPU.objects.get(pk=cpu_pk)
            total_tdp += cpu.tdp or 0
            
        if gpu_pk:
            gpu = GPU.objects.get(pk=gpu_pk)
            total_tdp += gpu.tdp or 0
            qs = PSUService.filter_by_gpu(qs, gpu)

        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = PSUService.filter_by_mobo(qs, mobo)
            
        required_wattage = int(total_tdp * 1.3)
        qs = qs.filter(wattage__gte=required_wattage)

        return qs.distinct()
    
    
    @staticmethod
    def filter_by_mobo(qs, mobo: Motherboard):
        
        mobo_conns = MotherboardConnector.objects.filter(
            motherboard=mobo,
            connector__is_power=True
        )

        for conn in mobo_conns:
            qs = qs.filter(
                psuconnector__connector__category=conn.connector.category,
                psuconnector__connector__lanes__gte=conn.connector.lanes
            )
            
        return qs.distinct()
    
    
    @staticmethod
    def filter_by_gpu(qs, gpu: GPU):
        
        gpu_conns = GPUConnector.objects.filter(gpu=gpu, connector__category="PCIe Power")
        
        for conn in gpu_conns:
            qs = qs.filter(
                psuconnector__connector__category="PCIe Power",
                psuconnector__connector__lanes__gte=conn.connector.lanes,
            )
            
            if conn.connector.version:
                qs = qs.filter(
                    psuconnector__connector__version__gte=conn.connector.version
                )
                
        return qs
    
    
    @staticmethod
    def evaluate_psu_quality(psu: PSU, total_tdp: int) -> float:
        
        if not psu.wattage:
            return 0
        
        ratio = psu.wattage / total_tdp
        if ratio >= 1.5:
            return 5
        elif ratio >= 1.3:
            return 4
        elif ratio >= 1.1:
            return 3
        
        return 2
            
        
        