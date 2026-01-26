from core.models import RAM, CPU, Motherboard


class RAMService:

    @staticmethod
    def _get_supported_ram_types(component):
        if not component or not hasattr(component, "supported_ram"):
            return set()
        return set(component.supported_ram.values_list("type", flat=True).distinct())
    
    @staticmethod
    def get_compatible_cpus(ram: RAM):
        return CPU.objects.filter(supported_ram__type=ram.base.type).distinct()
    
    @staticmethod
    def get_compatible_motherboards(ram: RAM):
        return Motherboard.objects.filter(
            supported_ram__type=ram.base.type,
            dimm_slots__gte=ram.modules_count,
            max_ram_capacity__gte=ram.total_capacity,
        ).distinct()
        
    @staticmethod
    def get_compatible_rams(data: dict[str, int]):
        qs = RAM.objects.all()
        
        cpu_pk = data.get("cpu")
        mobo_pk = data.get("mobo")
        cpu = None
        mobo = None
        
        # print(f"\n\n\nCMP RAM: {cpu_pk} | {mobo_pk}")
        
        if cpu_pk:
            cpu = CPU.objects.get(pk=cpu_pk)
            # print(f"\nCMP RAM cpu: {qs}")
        
        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            # print(f"\nCMP RAM mobo: {qs}\n\n\n")
        
        if cpu or mobo:
            types = None
            if cpu:
                types = RAMService._get_supported_ram_types(cpu)
            if mobo:
                mobo_types = RAMService._get_supported_ram_types(mobo)
                types = mobo_types if types is None else types.intersection(mobo_types)
            if not types:
                return qs.none()
            qs = qs.filter(base__type__in=types)

        if mobo:
            qs = qs.filter(
                modules_count__lte=mobo.dimm_slots,
                total_capacity__lte=mobo.max_ram_capacity
            )

        return qs
