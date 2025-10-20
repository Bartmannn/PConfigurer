from core.models import CPU, Motherboard, RAM, PSU, GPU
from core.services.psu_service import PSUService


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
        gpu_pk = data.get("gpu")
        psu_pk = data.get("psu")
        
        gpu_wattage = 0
        
        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = qs.filter(socket=mobo.socket)
            
        if ram_pk:
            ram = RAM.objects.get(pk=ram_pk)
            qs = qs.filter(supported_ram__in=[ram.base])
            
        if gpu_pk:
            gpu_wattage = GPU.objects.filter(pk=gpu_pk).values_list("tdp", flat=True).first()
            
        if psu_pk:
            psu_wattage = PSU.objects.filter(pk=psu_pk).values_list("wattage", flat=True).first()
            qs = qs.filter(tdp__lte=psu_wattage * PSUService.SAFETY_FACTOR - gpu_wattage)
            
        return qs.distinct()
