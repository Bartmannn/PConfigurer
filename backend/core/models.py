from django.db import models
from django.contrib.auth.models import User


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Connector(models.Model):
     # TODO: pozostałe złączki
    category = models.CharField(max_length=10, choices=[
        ("PCIe", "PCIe"),
        ("M.2 PCIe", "M.2 PCIe"),
        ("M.2 SATA", "M.2 SATA"),
        ("SATA", "SATA"),
        ("USB", "USB"),
        ("Fan", "Fan"),
        ("ATX Power", "ATX Power"),
        ("CPU Power", "CPU Power"),
        ("PCIe Power", "PCIe Power"),
        ("SATA Power", "SATA Power"),
        ("Molex", "Moelx"),
        ("Audio", "Audio"),
        ("Audio", "Audio"),
        
    ])
    version = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    lanes = models.PositiveSmallIntegerField(null=True, blank=True)
    speed = models.CharField(max_length=8, null=True, blank=True)
    extra = models.CharField(max_length=16, null=True, blank=True)
    is_power = models.BooleanField(default=False)

    def __str__(self):
        match self.category:
            case "PCIe":
                return f"{self.category} {self.version} x{self.lanes}"
            case "M.2 PCIe":
                support_SATA = " / SATA" if self.extra else ""
                return f"{self.category} NVMe {self.version} x{self.lanes}{support_SATA}"
            case "M.2 SATA":
                return f"{self.category}"
            case "SATA":
                rome_digit = 'I'*int(self.version)
                return f"{self.category} {rome_digit} ({self.speed}Gb/s)"
            case "USB":
                return f"{self.category} {self.version}"
            case "Fan":
                raise NotImplemented("Sprawdź to")
            case "ATX Power" | "CPU Power" | "PCIe Power" | "SATA Power" | "Molex":
                return f"{self.category} {self.lanes} pin {self.version or ''}"
            case "Audio":
                raise NotImplemented("Sprawdź to")
            case _:
                return "?"


class RAMBase(models.Model):
    type = models.CharField(
        max_length=8,
        choices=[('DDR3', 'DDR3'), ('DDR4', 'DDR4'), ('DDR5', 'DDR5')]
    )
    mts = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return f"{self.type}-{self.mts}"


class RAM(models.Model):
    name = models.CharField(max_length=120)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    base = models.ForeignKey(RAMBase, on_delete=models.CASCADE, related_name="variants")
    modules_count = models.PositiveSmallIntegerField(choices=[(1,1), (2,2),(3,3),(4,4),(6,6),(8,8)])
    module_memory = models.PositiveSmallIntegerField(choices=[(4,4),(8,8),(16,16),(24,24),(32,32),(48,48),(64,64)])
    total_capacity = models.PositiveSmallIntegerField(editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cycle_latency = models.PositiveSmallIntegerField() # CL
    ram_latency_ns = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.total_capacity = self.modules_count * self.module_memory
        self.ram_latency_ns = self.cycle_latency * 2000 / self.base.mts
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.total_capacity}GB {self.base.type}"


class Socket(models.Model):
    name = models.CharField(max_length=16, unique=True)
    
    def __str__(self):
        return f"Socket {self.name}"


class CPU(models.Model):
    # TODO: chipset, typy pamięci

    name = models.CharField(max_length=120)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    socket = models.ForeignKey(Socket, on_delete=models.PROTECT)
    p_cores = models.PositiveIntegerField(default=0)
    e_cores = models.PositiveIntegerField(default=0)
    threads = models.PositiveIntegerField()
    base_clock_ghz = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False)
    boost_clock_ghz = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    supported_ram = models.ManyToManyField(RAMBase)
    tdp = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cache_mb = models.PositiveIntegerField(null=True, blank=True, help_text="Total cache size in MB")
    integrated_gpu = models.BooleanField(default=False)

    @property
    def tier_score(self):
        MAX_CPU_SCORE = 125

        # Raw score calculation now includes p-cores, e-cores, and cache
        raw_score = (self.p_cores * 4) + \
                    (self.e_cores * 1) + \
                    (self.threads * 1) + \
                    ((self.cache_mb or 0) * 0.5) + \
                    (float(self.boost_clock_ghz or self.base_clock_ghz) * 2)
        
        normalized_score = 0
        if raw_score > MAX_CPU_SCORE:
            normalized_score = 10
        else:
            normalized_score = (raw_score / MAX_CPU_SCORE) * 10
        
        return round(normalized_score)

    def __str__(self):
        return f"{self.name} {self.base_clock_ghz}GHz"


class Storage(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    connector = models.ForeignKey(Connector, on_delete=models.PROTECT)
    capacity_gb = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    @property
    def type(self):
        match self.connector.category:
            case "M.2 PCIe":
                return "NVMe"
            case "M.2 SATA" | "SATA":
                return "SATA"
            case _:
                return "Unknown"

    def __str__(self):
        return f"{self.manufacturer} {self.name} {self.capacity_gb}GB {self.connector}"


class PSUFormFactor(models.Model):
    name = models.CharField(max_length=5, unique=True)
    
    def __str__(self):
        return self.name


class PSU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    wattage = models.PositiveSmallIntegerField(help_text="Maximum output power (W)")
    connectors = models.ManyToManyField("Connector", through="PSUConnector")
    form_factor = models.ForeignKey(PSUFormFactor, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.wattage}W"


class PSUConnector(models.Model):
    psu = models.ForeignKey(PSU, on_delete=models.CASCADE)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()


class GraphicsChip(models.Model):
    name = models.CharField(max_length=120, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    
    # Core Specs
    cuda_cores = models.PositiveSmallIntegerField(default=0) # Or stream_processors for AMD
    base_clock_mhz = models.PositiveSmallIntegerField(null=True, blank=True)
    boost_clock_mhz = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Memory Specs
    memory_type = models.CharField(max_length=8, choices=[('GDDR5', 'GDDR5'), ('GDDR6', 'GDDR6'), ('GDDR6X', 'GDDR6X'), ('GDDR7', 'GDDR7')], null=True, blank=True)
    memory_size_gb = models.PositiveSmallIntegerField()
    memory_bus_width = models.PositiveSmallIntegerField()
    
    # Power Specs
    total_graphics_power_w = models.PositiveSmallIntegerField(null=True, blank=True)
    recommended_system_power_w = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def tier_score(self):
        MAX_GPU_SCORE = 314 + 241

        raw_score = (
            (self.cuda_cores or 0) * 0.01 +
            (self.boost_clock_mhz or self.base_clock_mhz or 0) * 0.1 +
            (self.memory_size_gb or 0) * 1
        )
        
        normalized_score = 0
        if raw_score >= MAX_GPU_SCORE:
            normalized_score = 10
        else:
            normalized_score = (raw_score / MAX_GPU_SCORE) * 10
        
        return round(normalized_score)

    def __str__(self):
        return self.name


class GPU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT) # e.g., ASUS, MSI
    name = models.CharField(max_length=120) # e.g., "TUF GAMING OC"
    graphics_chip = models.ForeignKey(GraphicsChip, on_delete=models.PROTECT, null=True)

    # Physical properties & Price
    length_mm = models.PositiveSmallIntegerField()
    width_mm = models.PositiveSmallIntegerField()
    height_mm = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Connectors
    connectors = models.ManyToManyField(Connector, through="GPUConnector")

    def __str__(self):
        return f"{self.manufacturer} {self.graphics_chip} {self.name} {self.graphics_chip.memory_size_gb}GB {self.graphics_chip.memory_type}"


class GPUConnector(models.Model):
    gpu = models.ForeignKey(GPU, on_delete=models.CASCADE)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)


class Cooler(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=16)
    socket_compat = models.CharField(max_length=120)  # np. "AM4,AM5,LGA1700"
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class MotherboardFormFactor(models.Model):
    name = models.CharField(max_length=5, unique=True)
    
    def __str__(self):
        return self.name


class Case(models.Model): # TODO: chłodzenie procka wysokość
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    mobo_form_factor_support = models.ManyToManyField(MotherboardFormFactor)
    psu_form_factor_support = models.ManyToManyField(PSUFormFactor)
    max_gpu_length_mm = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # max_cooler_height_mm = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.manufacturer} {self.name}"


class Motherboard(models.Model):
    #TODO: chipsety
    name = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    socket = models.ForeignKey(Socket, on_delete=models.PROTECT)
    form_factor = models.ForeignKey(MotherboardFormFactor, on_delete=models.CASCADE)
    
    # RAM
    supported_ram = models.ManyToManyField(RAMBase)
    max_ram_capacity = models.PositiveSmallIntegerField(choices=[
        (32, "32 GB"),(64, "64 GB"),(96, "96 GB"),(128, "128 GB"),
        (192, "192 GB"),(256, "256 GB"),(1024, "1024 GB"),(2048, "2048 GB")
    ])
    dimm_slots = models.PositiveSmallIntegerField(choices=[(2, "2 x DIMM"), (4, "4 x DIMM")])
    
    # GPU, Dyski, Chłodzenie, Zasilanie, itp.
    connectors = models.ManyToManyField(Connector, through="MotherboardConnector")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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

