# core/serializers.py
from rest_framework import serializers

from .models import (
    Manufacturer, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler, Build,
    PSUFormFactor, MotherboardFormFactor, Connector, RAMBase, Socket, GPUConnector,
    MotherboardConnector, GraphicsChip
)

class PSUFormFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSUFormFactor
        fields = "__all__"


class MotherboardFormFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotherboardFormFactor
        fields = "__all__"


class ConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = ["id", "category", "version", "lanes", "speed", "extra", "is_power"]


class RAMBaseSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = RAMBase
        fields = "__all__"

    def get_display_name(self, obj):
        return f"{obj.type}-{obj.mts}"


class SocketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socket
        fields = "__all__"


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class CPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = ['id', 'short_name']

class CPUDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    socket = serializers.CharField(source="socket.name", read_only=True)
    supported_ram = RAMBaseSerializer(many=True, read_only=True)
    supported_pcie = serializers.SerializerMethodField()

    def get_supported_pcie(self, obj):
        items = obj.cpusupportedpcie_set.select_related("connector")
        return [
            {
                "version": str(item.connector.version) if item.connector.version is not None else None,
                "lanes": item.connector.lanes,
                "quantity": item.quantity,
            }
            for item in items
        ]

    class Meta:
        model = CPU
        fields = [
            'id', 'full_name', 'short_name', 'name', 'manufacturer', 'manufacturer_name',
            'family', 'generation', 'socket', 'socket_name',
            'p_cores', 'e_cores', 'threads', 'base_clock_ghz', 'boost_clock_ghz',
            'cores_info', 'threads_info', 'clock_speed_info', 'cache_info', 'cache_mb',
            'integrated_gpu', 'ram_support_info', 'supported_ram', 'max_internal_memory_gb',
            'supported_pcie', 'tdp', 'price', 'tier_score'
        ]

class GraphicsChipSerializer(serializers.ModelSerializer):
    tier_score = serializers.FloatField(read_only=True)
    class Meta:
        model = GraphicsChip
        fields = "__all__"


class GraphicsChipInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphicsChip
        fields = ["marketing_name", "pcie_max_gen", "pcie_max_width", "memory_type"]


class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = ['id', 'short_name']

class GPUDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    graphics_chip = GraphicsChipInfoSerializer(read_only=True)
    power_connectors = serializers.SerializerMethodField()

    def get_power_connectors(self, obj):
        items = obj.gpuconnector_set.select_related("connector").filter(connector__is_power=True)
        return [
            {
                "pins": item.connector.lanes,
                "quantity": item.quantity,
            }
            for item in items
        ]

    class Meta:
        model = GPU
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer', 'manufacturer_name',
            'model_name', 'graphics_chip', 'chip_name', 'chip_manufacturer_name',
            'vram_size_gb', 'vram_info', 'base_clock_mhz', 'boost_clock_mhz', 'clock_speed_info',
            'bus_width_info', 'dimensions_info', 'outputs', 'ports_info',
            'length_mm', 'slot_width', 'tdp', 'recommended_system_power_w',
            'power_connectors', 'price', 'tier_score'
        ]

class MotherboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motherboard
        fields = ['id', 'short_name']
        
class MotherboardDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    socket = serializers.CharField(source="socket.name", read_only=True)
    form_factor = serializers.CharField(source="form_factor.name", read_only=True)
    supported_ram = RAMBaseSerializer(many=True, read_only=True)
    connectors = serializers.SerializerMethodField()

    def get_connectors(self, obj):
        items = obj.motherboardconnector_set.select_related("connector")
        return [
            {
                "category": item.connector.category,
                "version": str(item.connector.version) if item.connector.version is not None else None,
                "lanes": item.connector.lanes,
                "quantity": item.quantity,
            }
            for item in items
        ]

    class Meta:
        model = Motherboard
        fields = [
            'id', 'full_name', 'short_name', 'name', 'manufacturer', 'manufacturer_name',
            'socket', 'socket_name', 'form_factor', 'form_factor_name',
            'supported_ram', 'supported_ram_types', 'max_ram_capacity', 'max_ram_capacity_info',
            'dimm_slots', 'dimm_slots_count', 'connectors',
            'pcie_slots_info', 'm2_slots_info', 'sata_ports_info', 'price'
        ]

class RAMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAM
        fields = ['id', 'short_name']

class RAMDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    base = RAMBaseSerializer(read_only=True)

    class Meta:
        model = RAM
        fields = [
            'id', 'full_name', 'short_name', 'name', 'manufacturer', 'manufacturer_name',
            'base', 'modules_count', 'total_capacity', 'kit_info', 'capacity_info',
            'type_info', 'latency_info', 'price'
        ]

class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ['id', 'short_name']

class StorageDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    connector = ConnectorSerializer(read_only=True)

    class Meta:
        model = Storage
        fields = [
            'id', 'full_name', 'short_name', 'name', 'manufacturer', 'manufacturer_name',
            'connector', 'capacity_gb', 'capacity_info', 'type', 'type_info',
            'interface_info', 'price'
        ]

class PSUSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSU
        fields = ['id', 'short_name']
        
class PSUDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    form_factor = serializers.CharField(source="form_factor.name", read_only=True)

    class Meta:
        model = PSU
        fields = [
            'id', 'full_name', 'short_name', 'name', 'manufacturer', 'manufacturer_name',
            'wattage', 'wattage_info', 'form_factor', 'form_factor_name',
            'connectors', 'connectors_info', 'price'
        ]

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ['id', 'short_name']

class CaseDetailSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name", read_only=True)
    mobo_form_factor_support = serializers.SerializerMethodField()
    psu_form_factor_support = serializers.SerializerMethodField()

    def get_mobo_form_factor_support(self, obj):
        return list(obj.mobo_form_factor_support.values_list("name", flat=True))

    def get_psu_form_factor_support(self, obj):
        return list(obj.psu_form_factor_support.values_list("name", flat=True))

    class Meta:
        model = Case
        fields = [
            'id', 'full_name', 'short_name', 'name', 'manufacturer', 'manufacturer_name',
            'mobo_form_factor_support', 'mobo_support_info',
            'psu_form_factor_support', 'max_gpu_length_mm', 'max_gpu_length_info',
            'price'
        ]

class CoolerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooler
        fields = ['id', 'short_name']

class CoolerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooler
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'type_info', 'supported_sockets_info', 'price'
        ]

class BuildSerializer(serializers.ModelSerializer):
    cpu_name = serializers.ReadOnlyField(source="cpu.short_name")
    gpu_name = serializers.ReadOnlyField(source="gpu.short_name")
    motherboard_name = serializers.ReadOnlyField(source="motherboard.short_name")
    ram_name = serializers.ReadOnlyField(source="ram.short_name")
    storage_name = serializers.ReadOnlyField(source="storage.short_name")
    psu_name = serializers.ReadOnlyField(source="psu.short_name")
    case_name = serializers.ReadOnlyField(source="case.short_name")
    cooler_name = serializers.ReadOnlyField(source="cooler.short_name")

    class Meta:
        model = Build
        fields = "__all__"

class BuildDetailSerializer(serializers.ModelSerializer):
    cpu = CPUSerializer(read_only=True)
    gpu = GPUSerializer(read_only=True)
    motherboard = MotherboardSerializer(read_only=True)
    ram = RAMSerializer(read_only=True)
    storage = StorageSerializer(read_only=True)
    psu = PSUSerializer(read_only=True)
    case = CaseSerializer(read_only=True)
    cooler = CoolerSerializer(read_only=True)

    class Meta:
        model = Build
        fields = "__all__"
