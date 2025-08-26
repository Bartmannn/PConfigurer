# from django.shortcuts import render
from rest_framework import viewsets
from .models import CPU, GPU, Build
from .serializer import CPUSerializer, GPUSerializer, BuildSerializer

class CPUViewSet(viewsets.ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer

class GPUViewSet(viewsets.ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer

class BuildViewSet(viewsets.ModelViewSet):
    queryset = Build.objects.all()
    serializer_class = BuildSerializer
