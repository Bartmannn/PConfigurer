from django.test import TestCase
from core.models import Connector, GPU, GPUConnector, Motherboard, MotherboardConnector, FormFactor
from core.services.gpu_service import GPUService
from core.services.motherboard_service import MotherboardService


class CompatibilityServiceTest(TestCase):
    def setUp(self):
        # form factor
        ff = FormFactor.objects.create(name="ATX")

        # connectory
        self.pcie_5_x16 = Connector.objects.create(category="PCIe", version=5.0, lanes=16)
        self.pcie_3_x1 = Connector.objects.create(category="PCIe", version=3.0, lanes=1)

        # gpu
        self.gpu = GPU.objects.create(name="RTX 4070")
        GPUConnector.objects.create(gpu=self.gpu, connector=self.pcie_5_x16, ilosc=1)

        # motherboard z kompatybilnym slotem
        self.mobo_good = Motherboard.objects.create(name="ASUS Z790", form_factor=ff)
        MotherboardConnector.objects.create(motherboard=self.mobo_good, connector=self.pcie_5_x16, ilosc=1)

        # motherboard bez kompatybilnego slotu
        self.mobo_bad = Motherboard.objects.create(name="Old Board", form_factor=ff)
        MotherboardConnector.objects.create(motherboard=self.mobo_bad, connector=self.pcie_3_x1, ilosc=1)

    # def test_gpu_service_returns_compatible_mobo(self):
    #     mobos = GPUService.get_compatible_motherboards(self.gpu)
    #     self.assertIn(self.mobo_good, mobos)
    #     self.assertNotIn(self.mobo_bad, mobos)

    # def test_motherboard_service_returns_compatible_gpu(self):
    #     gpus = MotherboardService.get_compatible_gpus(self.mobo_good)
    #     self.assertIn(self.gpu, gpus)

    #     gpus_bad = MotherboardService.get_compatible_gpus(self.mobo_bad)
    #     self.assertNotIn(self.gpu, gpus_bad)
