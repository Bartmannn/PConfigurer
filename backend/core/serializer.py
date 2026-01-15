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
    class Meta:
        model = CPU
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'socket_name', 'cores_info', 'threads_info',
            'clock_speed_info', 'cache_info', 'integrated_gpu', 'ram_support_info',
            'tdp', 'price', 'tier_score'
        ]

class GraphicsChipSerializer(serializers.ModelSerializer):
    tier_score = serializers.FloatField(read_only=True)
    class Meta:
        model = GraphicsChip
        fields = "__all__"

class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = ['id', 'short_name']

class GPUDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'chip_name', 'chip_manufacturer_name',
            'vram_info', 'clock_speed_info', 'bus_width_info', 'dimensions_info',
            'ports_info', 'price', 'tier_score'
        ]

class MotherboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motherboard
        fields = ['id', 'short_name']
        
class MotherboardDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motherboard
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'socket_name', 'form_factor_name',
            'dimm_slots_count', 'supported_ram_types', 'max_ram_capacity_info',
            'pcie_slots_info', 'm2_slots_info', 'sata_ports_info', 'price'
        ]

class RAMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAM
        fields = ['id', 'short_name']

class RAMDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAM
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'kit_info', 'capacity_info',
            'type_info', 'latency_info', 'price', 'total_capacity'
        ]

class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ['id', 'short_name']

class StorageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'type_info', 'capacity_info',
            'interface_info', 'price', 'type', 'capacity_gb'
        ]

class PSUSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSU
        fields = ['id', 'short_name']
        
class PSUDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSU
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'wattage_info', 'form_factor_name',
            'connectors_info', 'price'
        ]

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ['id', 'short_name']

class CaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'id', 'full_name', 'short_name', 'manufacturer_name', 'mobo_support_info',
            'max_gpu_length_info', 'price'
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
