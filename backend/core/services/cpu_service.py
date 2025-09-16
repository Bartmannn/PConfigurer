from core.models import CPU, Motherboard, RAM


class CPUService:
    
    @staticmethod
    def get_compatible_motherboard(cpu: CPU):
        return Motherboard.objects.filter(socket=cpu.socket)
    
    @staticmethod
    def get_compatible_ram(cpu: CPU, mobo: Motherboard = None):
        if hasattr(cpu, "supported_ram"):
            return RAM.objects.filter(base__in=cpu.supported_ram.all())
        return RAM.objects.none()
    
