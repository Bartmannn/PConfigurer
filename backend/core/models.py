from django.db import models
from django.contrib.auth.models import User


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Connector(models.Model):
     # TODO: pozostałe złączki
    category = models.CharField(max_length=20, choices=[
        ("PCIe", "PCIe"),
        ("M.2 PCIe", "M.2 PCIe"),
        ("M.2 SATA", "M.2 SATA"),
        ("SATA", "SATA"),
        ("USB", "USB"),
        ("HDMI", "HDMI"),
        ("DisplayPort", "DisplayPort"),
        ("DVI", "DVI"),
        ("VGA", "VGA"),
        ("USB-C", "USB-C"),
        ("Fan", "Fan"),
        ("ATX Power", "ATX Power"),
        ("CPU Power", "CPU Power"),
        ("PCIe Power", "PCIe Power"),
        ("SATA Power", "SATA Power"),
        ("Molex", "Moelx"),
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
                version = f" {self.version}" if self.version is not None else ""
                lanes = f" x{self.lanes}" if self.lanes else ""
                return f"{self.category}{version}{lanes}"
            case "M.2 PCIe":
                support_SATA = " / SATA" if self.extra else ""
                version = f" {self.version}" if self.version is not None else ""
                lanes = f" x{self.lanes}" if self.lanes else ""
                return f"{self.category} NVMe{version}{lanes}{support_SATA}"
            case "M.2 SATA":
                return f"{self.category}"
            case "SATA":
                rome_digit = 'I'*int(self.version)
                return f"{self.category} {rome_digit} ({self.speed}Gb/s)"
            case "USB":
                return f"{self.category} {self.version}"
            case "HDMI" | "DisplayPort":
                version = f" {self.version}" if self.version is not None else ""
                suffix = f"{self.extra}" if self.extra else ""
                return f"{self.category}{version}{suffix}"
            case "DVI" | "VGA" | "USB-C":
                suffix = f" {self.extra}" if self.extra else ""
                return f"{self.category}{suffix}"
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

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name} {self.total_capacity}GB ({self.modules_count}x{self.module_memory}GB) {self.base.type}-{self.base.mts} CL{self.cycle_latency}"

    @property
    def short_name(self):
        return f"{self.manufacturer.name} {self.total_capacity}GB {self.base.type} {self.base.mts}"

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def kit_info(self):
        return f"{self.modules_count}x {self.module_memory}GB"

    @property
    def capacity_info(self):
        return f"{self.total_capacity} GB"

    @property
    def type_info(self):
        return f"{self.base.type} {self.base.mts} MHz"

    @property
    def latency_info(self):
        return f"CL{self.cycle_latency}"

    def __str__(self):
        return self.short_name


class Socket(models.Model):
    name = models.CharField(max_length=16, unique=True)
    
    def __str__(self):
        return f"{self.name}"


class CPU(models.Model):
    name = models.CharField(max_length=120)
    family = models.CharField(max_length=64, null=True, blank=True)
    generation = models.CharField(max_length=32, null=True, blank=True)
    model_code = models.CharField(max_length=64, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    socket = models.ForeignKey(Socket, on_delete=models.PROTECT)
    p_cores = models.PositiveIntegerField(default=0)
    e_cores = models.PositiveIntegerField(default=0)
    threads = models.PositiveIntegerField()
    base_clock_ghz = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False)
    boost_clock_ghz = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    supported_ram = models.ManyToManyField(RAMBase)
    max_internal_memory_gb = models.PositiveSmallIntegerField(null=True, blank=True)
    supported_pcie = models.ManyToManyField(
        Connector,
        through="CPUSupportedPCIe",
        related_name="cpu_supported_pcie",
        blank=True,
        limit_choices_to={"category": "PCIe"},
    )
    tdp = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cache_mb = models.PositiveIntegerField(null=True, blank=True, help_text="Total cache size in MB")
    integrated_gpu = models.BooleanField(default=False)

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name}"

    @property
    def short_name(self):
        return self.name

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def socket_name(self):
        return self.socket.name

    @property
    def cores_info(self):
        return f"Performance: {self.p_cores}, Efficient: {self.e_cores}"

    @property
    def threads_info(self):
        return self.threads

    @property
    def clock_speed_info(self):
        boost_clock = f" ({self.boost_clock_ghz} GHz Boost)" if self.boost_clock_ghz else ""
        return f"{self.base_clock_ghz} GHz{boost_clock}"

    @property
    def cache_info(self):
        return f"{self.cache_mb} MB" if self.cache_mb else "N/A"

    @property
    def integrated_graphics(self):
        return self.integrated_gpu

    @property
    def ram_support_info(self):
        return [str(ram) for ram in self.supported_ram.all()]

    @property
    def tier_score(self):
        MAX_CPU_SCORE = 125
        raw_score = (self.p_cores * 4) + (self.e_cores * 1) + (self.threads * 1) + ((self.cache_mb or 0) * 0.5) + (float(self.boost_clock_ghz or self.base_clock_ghz) * 2)
        normalized_score = 10 if raw_score > MAX_CPU_SCORE else (raw_score / MAX_CPU_SCORE) * 10
        return round(normalized_score)

    def __str__(self):
        return self.full_name


class CPUSupportedPCIe(models.Model):
    cpu = models.ForeignKey(CPU, on_delete=models.CASCADE)
    connector = models.ForeignKey(
        Connector,
        on_delete=models.PROTECT,
        limit_choices_to={"category": "PCIe"},
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cpu", "connector"], name="cpu_supported_pcie_unique")
        ]


class Storage(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    connector = models.ForeignKey(Connector, on_delete=models.PROTECT)
    capacity_gb = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name} {self.capacity_gb}GB"

    @property
    def short_name(self):
        return f"{self.name} {self.capacity_gb}GB"

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def capacity_info(self):
        return f"{self.capacity_gb} GB"

    @property
    def interface_info(self):
        return str(self.connector)

    @property
    def type_info(self):
        return self.type

    @property
    def type(self):
        match self.connector.category:
            case "M.2 PCIe": return "NVMe"
            case "M.2 SATA" | "SATA": return "SATA"
            case _: return "HDD"

    def __str__(self):
        return self.full_name


class PSUFormFactor(models.Model):
    name = models.CharField(max_length=5, unique=True)
    
    def __str__(self):
        return self.name


class PSU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    wattage = models.PositiveSmallIntegerField(help_text="Maximum output power (W)")
    connectors = models.JSONField(default=list, blank=True)
    form_factor = models.ForeignKey(PSUFormFactor, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name} {self.wattage}W"

    @property
    def short_name(self):
        return f"{self.name} {self.wattage}W"

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def wattage_info(self):
        return f"{self.wattage} W"

    @property
    def form_factor_name(self):
        return self.form_factor.name

    @property
    def connectors_info(self):
        connectors = self.connectors or []
        return [self._format_connector(item) for item in connectors if isinstance(item, dict)]

    @staticmethod
    def _format_connector(item: dict) -> str:
        category = item.get("category", "?")
        lanes = item.get("lanes")
        version = item.get("version")
        quantity = item.get("quantity", 1)
        pin_suffix = f" {lanes} pin" if lanes else ""
        version_suffix = f" {version}" if version else ""
        return f"{quantity}x {category}{pin_suffix}{version_suffix}".strip()

    def __str__(self):
        return self.full_name


class GraphicsChip(models.Model):
    vendor = models.CharField(
        max_length=16,
        choices=[("NVIDIA", "NVIDIA"), ("AMD", "AMD"), ("Intel", "Intel")],
        null=True,
        blank=True,
    )
    marketing_name = models.CharField(max_length=120, unique=True, null=True, blank=True)
    architecture = models.CharField(max_length=64, null=True, blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    pcie_max_gen = models.PositiveSmallIntegerField(null=True, blank=True)
    pcie_max_width = models.PositiveSmallIntegerField(default=16)
    memory_type = models.CharField(
        max_length=8,
        choices=[('GDDR5', 'GDDR5'), ('GDDR6', 'GDDR6'), ('GDDR6X', 'GDDR6X'), ('GDDR7', 'GDDR7')],
        null=True,
        blank=True,
    )
    memory_bus_width = models.PositiveSmallIntegerField(null=True, blank=True)
    ray_tracing_gen = models.PositiveSmallIntegerField(null=True, blank=True)
    upscaling_technology = models.CharField(
        max_length=8,
        choices=[("DLSS", "DLSS"), ("FSR", "FSR"), ("None", "None")],
        default="None",
        blank=True,
    )

    @property
    def chip_manufacturer_name(self):
        return self.vendor

    @property
    def chip_name(self):
        return self.marketing_name

    @property
    def bus_width_info(self):
        return f"{self.memory_bus_width}-bit" if self.memory_bus_width else "N/A"

    @property
    def tier_score(self):
        MAX_GPU_SCORE = 250
        raw_score = ((self.cuda_cores or 0) * 0.01) + ((self.memory_bus_width or 0) * 0.1)
        normalized_score = 10 if raw_score >= MAX_GPU_SCORE else (raw_score / MAX_GPU_SCORE) * 10
        return round(normalized_score)

    def __str__(self):
        return self.marketing_name or "Unknown GPU"


class GPU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    model_name = models.CharField(max_length=120)
    graphics_chip = models.ForeignKey(GraphicsChip, on_delete=models.PROTECT, null=True)
    vram_size_gb = models.PositiveSmallIntegerField(null=True, blank=True)
    base_clock_mhz = models.PositiveSmallIntegerField(null=True, blank=True)
    boost_clock_mhz = models.PositiveSmallIntegerField(null=True, blank=True)
    tdp = models.PositiveSmallIntegerField(null=True, blank=True)
    recommended_system_power_w = models.PositiveSmallIntegerField(null=True, blank=True)
    length_mm = models.PositiveSmallIntegerField()
    slot_width = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    outputs = models.JSONField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    connectors = models.ManyToManyField(Connector, through="GPUConnector")

    @property
    def full_name(self):
        chip_name = self.graphics_chip.chip_name if self.graphics_chip else ""
        return f"{self.manufacturer.name} {chip_name} {self.model_name}".strip()

    @property
    def short_name(self):
        chip_name = self.graphics_chip.chip_name if self.graphics_chip else ""
        chip_name = chip_name.replace("GeForce", "").strip()
        return f"{self.manufacturer.name} {chip_name} {self.model_name}".strip()

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def dimensions_info(self):
        slot_info = f", Slots: {self.slot_width}" if self.slot_width else ""
        return f"Length: {self.length_mm}mm{slot_info}"

    @property
    def ports_info(self):
        output_categories = ("HDMI", "DisplayPort", "DVI", "VGA", "USB-C")
        return [
            f"{item.quantity}x {item.connector}"
            for item in self.gpuconnector_set.filter(
                connector__category__in=output_categories
            )
        ]

    @property
    def chip_manufacturer_name(self):
        return self.graphics_chip.chip_manufacturer_name if self.graphics_chip else None

    @property
    def chip_name(self):
        return self.graphics_chip.chip_name if self.graphics_chip else None

    @property
    def vram_info(self):
        if not self.vram_size_gb:
            return "N/A"
        memory_type = self.graphics_chip.memory_type if self.graphics_chip else None
        if memory_type:
            return f"{self.vram_size_gb}GB {memory_type}"
        return f"{self.vram_size_gb}GB"

    @property
    def clock_speed_info(self):
        if not self.base_clock_mhz and not self.boost_clock_mhz:
            return "N/A"
        base_clock = f"{self.base_clock_mhz} MHz" if self.base_clock_mhz else "N/A"
        boost_clock = f" ({self.boost_clock_mhz} MHz Boost)" if self.boost_clock_mhz else ""
        return f"{base_clock}{boost_clock}"

    @property
    def bus_width_info(self):
        return self.graphics_chip.bus_width_info if self.graphics_chip else "N/A"

    @property
    def tier_score(self):
        cuda_cores = self.graphics_chip.cuda_cores if self.graphics_chip else 0
        clock = self.boost_clock_mhz or self.base_clock_mhz or 0
        raw_score = ((cuda_cores or 0) * 0.01) + ((clock or 0) * 0.1) + ((self.vram_size_gb or 0) * 1)
        max_score = 314 + 241
        normalized_score = 10 if raw_score >= max_score else (raw_score / max_score) * 10
        return round(normalized_score)

    def __str__(self):
        return self.full_name


class GPUConnector(models.Model):
    gpu = models.ForeignKey(GPU, on_delete=models.CASCADE)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)


class Cooler(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=16)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name}"

    @property
    def short_name(self):
        return self.name

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def type_info(self):
        return self.type

    @property
    def supported_sockets_info(self):
        return self.socket_compat

    def __str__(self):
        return self.full_name


class MotherboardFormFactor(models.Model):
    name = models.CharField(max_length=5, unique=True)
    
    def __str__(self):
        return self.name


class Case(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    mobo_form_factor_support = models.ManyToManyField(MotherboardFormFactor)
    psu_form_factor_support = models.ManyToManyField(PSUFormFactor)
    max_gpu_length_mm = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name}"

    @property
    def short_name(self):
        return self.name

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def mobo_support_info(self):
        return [str(ff) for ff in self.mobo_form_factor_support.all()]

    @property
    def max_gpu_length_info(self):
        return f"{self.max_gpu_length_mm} mm"

    def __str__(self):
        return self.full_name


class Motherboard(models.Model):
    name = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    socket = models.ForeignKey(Socket, on_delete=models.PROTECT)
    form_factor = models.ForeignKey(MotherboardFormFactor, on_delete=models.CASCADE)
    supported_ram = models.ManyToManyField(RAMBase)
    max_ram_capacity = models.PositiveSmallIntegerField(choices=[(32, "32 GB"),(64, "64 GB"),(96, "96 GB"),(128, "128 GB"),(192, "192 GB"),(256, "256 GB"),(1024, "1024 GB"),(2048, "2048 GB")])
    dimm_slots = models.PositiveSmallIntegerField(choices=[(2, "2 x DIMM"), (4, "4 x DIMM")])
    connectors = models.ManyToManyField(Connector, through="MotherboardConnector")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name}"

    @property
    def short_name(self):
        return self.name

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def socket_name(self):
        return self.socket.name

    @property
    def form_factor_name(self):
        return self.form_factor.name

    @property
    def dimm_slots_count(self):
        return self.dimm_slots

    @property
    def supported_ram_types(self):
        return list(self.supported_ram.values_list('type', flat=True).distinct())

    @property
    def max_ram_capacity_info(self):
        return f"{self.max_ram_capacity} GB"

    @property
    def pcie_slots_info(self):
        return [f"{item.quantity}x {item.connector}" for item in self.motherboardconnector_set.filter(connector__category="PCIe")]

    @property
    def m2_slots_info(self):
        return [f"{item.quantity}x {item.connector}" for item in self.motherboardconnector_set.filter(connector__category__startswith="M.2")]

    @property
    def sata_ports_info(self):
        return [f"{item.quantity}x {item.connector}" for item in self.motherboardconnector_set.filter(connector__category="SATA")]

    def __str__(self):
        return self.full_name


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
