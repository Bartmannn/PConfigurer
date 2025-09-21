from django.db import models
from django.contrib.auth.models import User


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class RAMBase(models.Model):
    type = models.CharField(
        max_length=8,
        choices=[('DDR3', 'DDR3'), ('DDR4', 'DDR4'), ('DDR5', 'DDR5')]
    )
    mts = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return f"{self.type}-{self.mts}"


class RAM(models.Model):
    # TODO: Napięcie, timingi, przelicznik
    
    name = models.CharField(max_length=120)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    base = models.ForeignKey(RAMBase, on_delete=models.CASCADE, related_name="variants")
    modules_count = models.PositiveSmallIntegerField(choices=[(1,1), (2,2),(3,3),(4,4),(6,6),(8,8)])
    module_memory = models.PositiveSmallIntegerField(choices=[(4,4),(8,8),(16,16),(24,24),(32,32),(48,48),(64,64)])
    total_capacity = models.PositiveSmallIntegerField(editable=False)
    
    def save(self, *args, **kwargs):
        self.total_capacity = self.modules_count * self.module_memory
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.total_capacity}GB {self.base.type}"


class Socket(models.Model):
    name = models.CharField(max_length=16, unique=True)
    
    def __str__(self):
        return f"Socket {self.name}"


class CPU(models.Model):
    # TODO: chipset, TDP, typy pamięci

    name = models.CharField(max_length=120)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    socket = models.ForeignKey(Socket, on_delete=models.PROTECT)
    cores = models.PositiveIntegerField()
    threads = models.PositiveIntegerField()
    base_clock_ghz = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False)
    boost_clock_ghz = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    supported_ram = models.ManyToManyField(RAMBase)

    def __str__(self):
        return f"{self.name} {self.base_clock_ghz}GHz"


class Storage(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=16)         # NVMe / SATA
    capacity_gb = models.PositiveIntegerField()
    pcie_version = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.capacity_gb}GB {self.type}"


class PSU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    wattage_w = models.PositiveIntegerField()
    efficiency = models.CharField(max_length=16)   # 80+ Bronze/Gold/Platinum

    def __str__(self):
        return f"{self.name} {self.wattage_w}W"


class Connector(models.Model):
     # TODO: pozostałe złączki
    category = models.CharField(max_length=8, choices=[
        ("PCIe", "PCIe"),
        ("M.2 PCIe", "M.2 PCIe"),
        ("M.2 SATA", "M.2 SATA"),
        ("SATA", "SATA"),
        ("USB", "USB"),
        ("Fan", "Fan"),
        ("Power", "Power"),
        ("Audio", "Audio"),
    ])
    version = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    lanes = models.PositiveSmallIntegerField(null=True, blank=True)
    speed = models.CharField(max_length=8, null=True, blank=True)
    extra = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        match self.category:
            case "PCIe":
                return f"{self.category} {self.version} x{self.lanes}"
            case "M.2 PCIe":
                support_SATA = " / SATA" if self.extra else ""
                return f"{self.category} NVMe {self.version} {self.lanes}{support_SATA}"
            case "M.2 SATA":
                return f"{self.category}"
            case "SATA":
                rome_digit = 'I'*int(self.version)
                return f"{self.category} {rome_digit} ({self.speed}Gb/s)"
            case "USB":
                return f"{self.category} {self.version}"
            case "Fan":
                raise NotImplemented("Sprawdź to")
            case "Power":
                return f"{self.category} {self.lanes} pin"
            case "Audio":
                raise NotImplemented("Sprawdź to")


class GPU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    vram_type = models.CharField()
    vram_capacity = models.PositiveIntegerField()
    length_mm = models.PositiveSmallIntegerField()
    width_mm = models.PositiveSmallIntegerField()
    height_mm = models.PositiveSmallIntegerField()
    
    # PCIe, HDMI, DisplayPort, PSU
    connectors = models.ManyToManyField(Connector, through="GPUConnector")

    def __str__(self):
        return self.name


class GPUConnector(models.Model):
    gpu = models.ForeignKey(GPU, on_delete=models.CASCADE)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)


class Cooler(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=16)         # air / aio240 / aio360
    tdp_w_supported = models.PositiveIntegerField()
    socket_compat = models.CharField(max_length=120)  # np. "AM4,AM5,LGA1700"

    def __str__(self):
        return self.name
    
    
class FormFactor(models.Model):
    name = models.CharField(max_length=5, unique=True)
    
    def __str__(self):
        return self.name

    
class Case(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    form_factor_support = models.ManyToManyField(FormFactor)
    max_gpu_length_mm = models.PositiveIntegerField()
    max_cooler_height_mm = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Motherboard(models.Model):
    #TODO: zasilanie (piny), chipsety, osobny model dla form_factor'a?
    name = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    socket = models.ForeignKey(Socket, on_delete=models.PROTECT)
    form_factor = models.ForeignKey(FormFactor, on_delete=models.CASCADE)
    
    # RAM
    supported_ram = models.ManyToManyField(RAMBase)
    max_ram_capacity = models.PositiveSmallIntegerField(choices=[
        (32, "32 GB"),(64, "64 GB"),(96, "96 GB"),(128, "128 GB"),
        (192, "192 GB"),(256, "256 GB"),(1024, "1024 GB"),(2048, "2048 GB")
    ])
    dimm_slots = models.PositiveSmallIntegerField(choices=[(2, "2 x DIMM"), (4, "4 x DIMM")])
    
    # GPU, Dyski, Chłodzenie, Zasilanie, itp.
    connectors = models.ManyToManyField(Connector, through="MotherboardConnector")

    def __str__(self):
        return self.name


class MotherboardConnector(models.Model):
    motherboard = models.ForeignKey(Motherboard, on_delete=models.CASCADE)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)


class Build(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="builds")
    name = models.CharField(max_length=120, default="My build")
    cpu = models.ForeignKey(CPU, on_delete=models.PROTECT, null=True, blank=True)
    gpu = models.ForeignKey(GPU, on_delete=models.PROTECT, null=True, blank=True)
    motherboard = models.ForeignKey(Motherboard, on_delete=models.PROTECT, null=True, blank=True)
    ram = models.ForeignKey(RAM, on_delete=models.PROTECT, null=True, blank=True)
    storage = models.ForeignKey(Storage, on_delete=models.PROTECT, null=True, blank=True)
    psu = models.ForeignKey(PSU, on_delete=models.PROTECT, null=True, blank=True)
    case = models.ForeignKey(Case, on_delete=models.PROTECT, null=True, blank=True)
    cooler = models.ForeignKey(Cooler, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

