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
            ram_base = (
                RAM.objects.filter(pk=ram_pk)
                .values_list("base", flat=True)
                .first()
            )
            qs = qs.filter(supported_ram__in=[ram_base])    # cpu może wspierać różne częstotliwości pamięci ram
            
        return qs.distinct()
