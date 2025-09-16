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
        
    @staticmethod
    def get_compatible_motherboards(data: dict[str, int]):
        qs = Motherboard.objects.all()
        
        cpu_pk = data.get("cpu")
        ram_pk = data.get("ram")
        
        print(f"\n\n\nCMP MOBO: {cpu_pk} | {ram_pk}")
        
        if cpu_pk:
            cpu = CPU.objects.get(pk=cpu_pk)
            qs = qs.filter(socket=cpu.socket)
            print(f"\nCMP MOBO cpu: {qs}")
            
        if ram_pk:
            ram = RAM.objects.get(pk=ram_pk)
            qs = qs.filter(
                supported_ram__in=[ram.base],
                dimm_slots__gte=ram.modules_count,
                max_ram_capacity__gte=ram.total_capacity
            )
            print(f"\nCMP MOBO ram: {qs}\n\n\n")

        return qs