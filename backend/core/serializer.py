from rest_framework import serializers
from .models import CPU, GPU, Build

class CPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = "__all__"

class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = "__all__"

class BuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build
        fields = "__all__"
