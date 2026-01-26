from core.models import CPU, Motherboard, RAM, PSU, GPU
from core.services.psu_service import PSUService


class CPUService:
    
    @staticmethod
    def get_compatible_motherboard(cpu: CPU):
        return Motherboard.objects.filter(socket=cpu.socket)
    
    @staticmethod
    def get_compatible_ram(cpu: CPU, mobo: Motherboard = None):
        if not hasattr(cpu, "supported_ram"):
            return RAM.objects.none()

        cpu_types = set(cpu.supported_ram.values_list("type", flat=True).distinct())
        if mobo:
            mobo_types = set(mobo.supported_ram.values_list("type", flat=True).distinct())
            cpu_types = cpu_types.intersection(mobo_types)
        if not cpu_types:
            return RAM.objects.none()
        qs = RAM.objects.filter(base__type__in=cpu_types)
        if mobo:
            qs = qs.filter(
                modules_count__lte=mobo.dimm_slots,
                total_capacity__lte=mobo.max_ram_capacity,
            )
        return qs
    
    @staticmethod
    def get_compatible_cpus(data: dict[str, int]):
        qs = CPU.objects.all()                              # qs = queryset -> zestaw wszystkich procesorów
        
        mobo_pk = data.get("mobo")                          # pobieranie klkucza płyty głównej
        ram_pk = data.get("ram")                            # pobieranie klucza pamięci RAM
        
        if mobo_pk:
            mobo_socket = (                                 # pobieranie socket'u płyty głównej
                Motherboard.objects.filter(pk=mobo_pk)      # filtrujemy po kluczu
                .values_list("socket", flat=True)           # spłycamy konkretne wartości (z jendoelementowych krotek do listy)
                .first()
            )
            qs = qs.filter(socket=mobo_socket)              # filtrujemy cpu po socket'cie płyty głównej
            
        if ram_pk:
            ram = RAM.objects.select_related("base").filter(pk=ram_pk).first()
            ram_type = ram.base.type if ram and ram.base else None
            if ram_type:
                qs = qs.filter(supported_ram__type=ram_type)    # cpu może wspierać różne częstotliwości pamięci ram
            
        return qs.distinct()
