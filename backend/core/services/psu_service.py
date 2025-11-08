
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

        min_wattage = 0
        
        if gpu_pk:
            # If a GPU is selected, its recommended system power is the primary criterion.
            gpu = GPU.objects.select_related('graphics_chip').filter(pk=gpu_pk).first()
            if gpu and gpu.graphics_chip.recommended_system_power_w:
                min_wattage = gpu.graphics_chip.recommended_system_power_w
        
        elif cpu_pk:
            # If no GPU, estimate based on CPU TDP + a baseline for the rest of the system.
            cpu_tdp = (
                CPU.objects.filter(pk=cpu_pk)
                .values_list("tdp", flat=True)
                .first()
            ) or 0
            min_wattage = cpu_tdp + 250 # Baseline for a system without a powerful GPU

        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = PSUService.filter_by_mobo(qs, mobo)
            
        if case_pk:
            case = Case.objects.filter(pk=case_pk).prefetch_related("psu_form_factor_support").first()
            supported_formats = case.psu_form_factor_support.all()
            qs = qs.filter(form_factor__in=supported_formats)
        
        qs = qs.filter(wattage__gte=min_wattage)

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
        
        