from core.models import RAM, CPU, Motherboard


class RAMService:
    
    @staticmethod
    def get_compatible_cpus(ram: RAM):
        return CPU.objects.filter(supported_ram__in=[ram.base])
    
    @staticmethod
    def get_compatible_motherboards(ram: RAM):
        return Motherboard.objects.filter(
            supported_ram__in=[ram.base],
            dimm_slots__gte=ram.modules_count,
            max_ram_capacity__gte=ram.total_capacity,
        )
        
    @staticmethod
    def get_compatible_rams(data: dict[str, int]):
        qs = RAM.objects.all()
        
        cpu_pk = data.get("cpu")
        mobo_pk = data.get("mobo")
        
        # print(f"\n\n\nCMP RAM: {cpu_pk} | {mobo_pk}")
        
        if cpu_pk:
            cpu = CPU.objects.get(pk=cpu_pk)
            qs = qs.filter(base__in=cpu.supported_ram.all())
            # print(f"\nCMP RAM cpu: {qs}")
        
        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = qs.filter(
                base__in=mobo.supported_ram.all(),
                modules_count__lte=mobo.dimm_slots,
                total_capacity__lte=mobo.max_ram_capacity
            )
            # print(f"\nCMP RAM mobo: {qs}\n\n\n")

        return qs
