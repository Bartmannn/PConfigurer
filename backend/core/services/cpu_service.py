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
    
    @staticmethod
    def get_compatible_cpus(data: dict[str, int]):
        qs = CPU.objects.all()
        
        mobo_pk = data.get("mobo")
        ram_pk = data.get("ram")
        
        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = qs.filter(socket=mobo.socket)
            
        if ram_pk:
            ram = RAM.objects.get(pk=ram_pk)
            qs = qs.filter(supported_ram__in=[ram.base])
            
        return qs
