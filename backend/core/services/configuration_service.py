from core.models import CPU, Motherboard, RAM


class ConfigurationService:
    
    @staticmethod
    def validate(cpu: CPU, mobo: Motherboard, ram: RAM) -> set[bool, str]:
        
        if cpu.socket != mobo.socket:
            return False, "CPU socket is not compatible with motherboard."
        
        if ram.base not in mobo.supported_ram.all():
            return False, "RAM mismatch."
        
        if ram.modules_count > mobo.dimm_slots:
            return False, "Not enough DIMM slots."
        
        if ram.total_capacity() > mobo.max_ram_capacity:
            return False, "RAM exceeds motherboard max capacity."
        
        return  True, ""
        