
from core.models import PSU, PSUConnector, Case, Motherboard, GPU, MotherboardConnector, GPUConnector, CPU

class PSUService:
    
    SAFETY_FACTOR = 0.75
    
    @staticmethod
    def get_compatible_psus(data: dict[str, int]):
        
        qs = PSU.objects.all()
        
        gpu_pk = data.get("gpu")
        cpu_pk = data.get("cpu")
        mobo_pk = data.get("mobo")
        case_pk = data.get("case")

        total_tdp = 0
        
        if cpu_pk:
            cpu_tdp = (
                CPU.objects.filter(pk=cpu_pk)
                .values_list("tdp", flat=True)
                .first()
            ) or 0
            total_tdp += cpu_tdp
            
        if gpu_pk:
            gpu_tdp = (
                GPU.objects.filter(pk=gpu_pk)
                .values_list("tdp", flat=True)
                .first()
            ) or 0
            total_tdp += gpu_tdp
            # qs = PSUService.filter_by_gpu(qs, gpu) # TODO: do poprawy, coś nie działało!

        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = PSUService.filter_by_mobo(qs, mobo)
            
        if case_pk:
            case = Case.objects.filter(pk=case_pk).prefetch_related("psu_form_factor_support").first()
            supported_formats = case.psu_form_factor_support.all()
            qs = qs.filter(form_factor__in=supported_formats)
        
        required_wattage = int(total_tdp * 1.3)
        qs = qs.filter(wattage__gte=required_wattage)

        return qs.distinct()
    
    
    @staticmethod
    def filter_by_mobo(qs, mobo: Motherboard): # TODO: też mi się to nie podoba
        
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
    def filter_by_gpu(qs, gpu: GPU): # TODO: absolutnie mi się to nie podoba!
        
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
        
        