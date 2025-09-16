# from django.test import TestCase

from core.services.configuration_service import ConfigurationService
from core.services.motherboard_service import MotherboardService
from core.services.ram_service import RAMService
from core.services.cpu_service import CPUService
from core.models import *

gigabyte = Manufacturer.objects.get(name="Gigabyte")
intel = Manufacturer.objects.get(name="Intel")
amd = Manufacturer.objects.get(name="AMD")

mobo = Motherboard.objects.get(manufacturer=gigabyte)

cpu_intel = CPU.objects.get(manufacturer=intel)
cpu_amd = CPU.objects.get(manufacturer=amd)

ram = RAM.objects.all()[0]


def base_test(test_no: int = None):
    match test_no:
        case 1:
            print(f"CPUintel-RAM: {CPUService.get_compatible_ram(cpu_intel)}")
            print(f"CPUamd-RAM: {CPUService.get_compatible_ram(cpu_amd)}")
        case 2:
            print(f"CPUintel-MOBO: {CPUService.get_compatible_motherboard(cpu_intel)}")
            print(f"CPUamd-MOBO: {CPUService.get_compatible_motherboard(cpu_amd)}")
        case 3:
            print(f"RAM-MOBO: {RAMService.get_compatible_motherboards(ram)}")
            print(f"RAM-CPUS: {RAMService.get_compatible_cpus(ram)}")
        case 4:
            print(f"MOBO-CPUS: {MotherboardService.get_compatible_cpus(mobo)}")
            print(f"MOBO-RAMS: {MotherboardService.get_compatible_ram(mobo)}")
        case _:
            print("")
