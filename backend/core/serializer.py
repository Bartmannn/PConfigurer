# core/serializers.py
from rest_framework import serializers

from .models import (
    Manufacturer, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler, Build,
    PSUFormFactor, MotherboardFormFactor, Connector, RAMBase, Socket, GPUConnector,
    MotherboardConnector, PSUConnector, GraphicsChip
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
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    tier_score = serializers.FloatField(read_only=True)

    class Meta:
        model = CPU
        fields = "__all__"

class GraphicsChipSerializer(serializers.ModelSerializer):
    tier_score = serializers.FloatField(read_only=True)

    class Meta:
        model = GraphicsChip
        fields = "__all__"


class GPUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    display_name = serializers.CharField(source='__str__', read_only=True)
    graphics_chip = GraphicsChipSerializer(read_only=True)

    class Meta:
        model = GPU
        fields = "__all__"


class GPUConnectorSerializer(serializers.ModelSerializer):
    connector = ConnectorSerializer(read_only=True)
    class Meta:
        model = GPUConnector
        fields = ["connector"]


class GPUDetailSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    display_name = serializers.CharField(source='__str__', read_only=True)
    graphics_chip = GraphicsChipSerializer(read_only=True)
    connectors = GPUConnectorSerializer(source="gpuconnector_set", many=True, read_only=True)

    class Meta:
        model = GPU
        fields = "__all__"

class MotherboardSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = Motherboard
        fields = "__all__"
        
class MotherboardConnectorSerializer(serializers.ModelSerializer):
    connector = ConnectorSerializer(read_only=True)
    class Meta:
        model = MotherboardConnector
        fields = ["connector"]
        
class MotherboardDetailSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    connectors = MotherboardConnectorSerializer(source="motherboardconnector_set", many=True, read_only=True)

    class Meta:
        model = Motherboard
        fields = "__all__"

class RAMSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = RAM
        fields = "__all__"

class StorageSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    type = serializers.ReadOnlyField()
    
    class Meta:
        model = Storage
        fields = "__all__"

class PSUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = PSU
        fields = "__all__"
        
class PSUConnectorSerializer(serializers.ModelSerializer):
    connector = ConnectorSerializer(read_only=True)
    class Meta:
        model = PSUConnector
        fields = ["connector"]
        
class PSUDetailSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    connectors = PSUConnectorSerializer(source="psuconnector_set", many=True, read_only=True)

    class Meta:
        model = PSU
        fields = "__all__"

class CaseSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = Case
        fields = "__all__"

class CoolerSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = Cooler
        fields = "__all__"

# Build – wersja prosta (ID-ki części + pola tylko do odczytu z nazwami)
class BuildSerializer(serializers.ModelSerializer):
    cpu_name = serializers.ReadOnlyField(source="cpu.name")
    gpu_name = serializers.ReadOnlyField(source="gpu.name")
    motherboard_name = serializers.ReadOnlyField(source="motherboard.name")
    ram_name = serializers.ReadOnlyField(source="ram.name")
    storage_name = serializers.ReadOnlyField(source="storage.name")
    psu_name = serializers.ReadOnlyField(source="psu.name")
    case_name = serializers.ReadOnlyField(source="case.name")
    cooler_name = serializers.ReadOnlyField(source="cooler.name")

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