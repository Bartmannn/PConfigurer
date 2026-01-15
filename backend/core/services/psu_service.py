
from core.models import PSU, Case, Motherboard, GPU, MotherboardConnector, GPUConnector, CPU

class PSUService:
    
    SAFETY_FACTOR = 0.75

    @staticmethod
    def _coerce_number(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_requirement(requirement):
        if isinstance(requirement, dict):
            return (
                requirement.get("category"),
                requirement.get("lanes"),
                requirement.get("version"),
            )
        return requirement.category, requirement.lanes, requirement.version

    @staticmethod
    def psu_supports_connector(psu_connectors, requirement) -> bool:
        req_category, req_lanes, req_version = PSUService._extract_requirement(requirement)
        if not req_category:
            return False

        req_lanes = PSUService._coerce_number(req_lanes)
        req_version = PSUService._coerce_number(req_version)
        for item in psu_connectors or []:
            if not isinstance(item, dict):
                continue
            if item.get("category") != req_category:
                continue

            item_lanes = PSUService._coerce_number(item.get("lanes"))
            if req_lanes is not None and (item_lanes is None or item_lanes < req_lanes):
                continue

            if req_version is not None:
                item_version = PSUService._coerce_number(item.get("version"))
                if item_version is None or item_version < req_version:
                    continue

            return True

        return False
    
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
            if gpu:
                if gpu.recommended_system_power_w:
                    min_wattage = gpu.recommended_system_power_w
                elif gpu.tdp:
                    min_wattage = int(gpu.tdp / PSUService.SAFETY_FACTOR)
        
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

        requirements = [conn.connector for conn in mobo_conns.select_related("connector")]
        if not requirements:
            return qs.distinct()

        psu_ids = []
        for psu_id, connectors in qs.values_list("id", "connectors"):
            if all(PSUService.psu_supports_connector(connectors, req) for req in requirements):
                psu_ids.append(psu_id)

        return qs.filter(id__in=psu_ids).distinct()
    
    
    @staticmethod
    def filter_by_gpu(qs, gpu: GPU): # TODO: absolutnie mi się to nie podoba!
        
        gpu_conns = GPUConnector.objects.filter(
            gpu=gpu,
            connector__category="PCIe Power"
        ).select_related("connector")

        requirements = [conn.connector for conn in gpu_conns]
        if not requirements:
            return qs

        psu_ids = []
        for psu_id, connectors in qs.values_list("id", "connectors"):
            if all(PSUService.psu_supports_connector(connectors, req) for req in requirements):
                psu_ids.append(psu_id)

        return qs.filter(id__in=psu_ids)
        
        
