from core.models import Motherboard, CPU, RAM


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
