# core/serializers.py
from rest_framework import serializers
from .models import (
    Manufacturer, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler, Build
)

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"

class CPUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = CPU
        fields = "__all__"

class GPUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
    class Meta:
        model = GPU
        fields = "__all__"

class MotherboardSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
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
    class Meta:
        model = Storage
        fields = "__all__"

class PSUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name")
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