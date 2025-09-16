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

