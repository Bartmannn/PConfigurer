# core/views.py
from rest_framework import viewsets, filters
from django.db.models import Q
from .models import (
    Manufacturer, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler, Build
)
from .serializer import (
    ManufacturerSerializer, CPUSerializer, GPUSerializer, MotherboardSerializer,
    RAMSerializer, StorageSerializer, PSUSerializer, CaseSerializer,
    CoolerSerializer, BuildSerializer, BuildDetailSerializer
)
from core.services.motherboard_service import MotherboardService
from core.services.cpu_service import CPUService
from core.services.ram_service import RAMService

# --- Bazowy ViewSet z wyszukiwaniem i sortowaniem ---
class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # Ustal w podklasach: search_fields, ordering_fields


# --- Manufacturer ---
class ManufacturerViewSet(BaseViewSet):
    queryset = Manufacturer.objects.all().order_by("name")
    serializer_class = ManufacturerSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "id"]


# --- CPU ---
class CPUViewSet(BaseViewSet):
    queryset = CPU.objects.all().order_by("id")
    serializer_class = CPUSerializer

    def get_queryset(self):
        params = {
            k: int(v) \
                for k, v in self.request.query_params.items()
        }
        qs = CPUService.get_compatible_cpus(params)
        
        return qs


# --- GPU ---
class GPUViewSet(BaseViewSet):
    queryset = GPU.objects.all().order_by("id")
    serializer_class = GPUSerializer
    search_fields = ["name", "manufacturer__name"]
    ordering_fields = ["vram_gb", "tdp_w", "length_mm", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        min_vram = self.request.query_params.get("min_vram")
        max_length = self.request.query_params.get("max_length")
        if min_vram:
            qs = qs.filter(vram_gb__gte=min_vram)
        if max_length:
            qs = qs.filter(length_mm__lte=max_length)
        return qs


# --- Motherboard ---
class MotherboardViewSet(BaseViewSet):
    queryset = Motherboard.objects.all().order_by("id")
    serializer_class = MotherboardSerializer

    def get_queryset(self):
        params = {
            k: int(v) \
                for k, v in self.request.query_params.items()
        }
        qs = MotherboardService.get_compatible_motherboards(params)

        return qs


# --- RAM ---
class RAMViewSet(BaseViewSet):
    queryset = RAM.objects.all().order_by("id")
    serializer_class = RAMSerializer

    def get_queryset(self):
        params = {
            k: int(v) \
                for k, v in self.request.query_params.items()
        }
        qs = RAMService.get_compatible_rams(params)
        return qs


# --- Storage ---
class StorageViewSet(BaseViewSet):
    queryset = Storage.objects.all().order_by("id")
    serializer_class = StorageSerializer
    search_fields = ["name", "manufacturer__name", "type"]
    ordering_fields = ["capacity_gb", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        typ = self.request.query_params.get("type")      # NVMe / SATA
        min_capacity = self.request.query_params.get("min_capacity")
        if typ:
            qs = qs.filter(type__iexact=typ)
        if min_capacity:
            qs = qs.filter(capacity_gb__gte=min_capacity)
        return qs


# --- PSU ---
class PSUViewSet(BaseViewSet):
    queryset = PSU.objects.all().order_by("id")
    serializer_class = PSUSerializer
    search_fields = ["name", "manufacturer__name", "efficiency"]
    ordering_fields = ["wattage_w", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        min_wattage = self.request.query_params.get("min_wattage")
        efficiency = self.request.query_params.get("efficiency")  # np. "80+ Gold"
        if min_wattage:
            qs = qs.filter(wattage_w__gte=min_wattage)
        if efficiency:
            qs = qs.filter(efficiency__icontains=efficiency)
        return qs


# --- Case ---
class CaseViewSet(BaseViewSet):
    queryset = Case.objects.all().order_by("id")
    serializer_class = CaseSerializer
    search_fields = ["name", "manufacturer__name", "form_factor_support"]
    ordering_fields = ["max_gpu_length_mm", "max_cooler_height_mm", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        needs_form = self.request.query_params.get("form_factor")  # ATX / mATX / ITX
        min_gpu_len = self.request.query_params.get("min_gpu_length")
        min_cooler_h = self.request.query_params.get("min_cooler_height")
        if needs_form:
            qs = qs.filter(form_factor_support__icontains=needs_form)
        if min_gpu_len:
            qs = qs.filter(max_gpu_length_mm__gte=min_gpu_len)
        if min_cooler_h:
            qs = qs.filter(max_cooler_height_mm__gte=min_cooler_h)
        return qs


# --- Cooler ---
class CoolerViewSet(BaseViewSet):
    queryset = Cooler.objects.all().order_by("id")
    serializer_class = CoolerSerializer
    search_fields = ["name", "manufacturer__name", "type", "socket_compat"]
    ordering_fields = ["tdp_w_supported", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        min_tdp = self.request.query_params.get("min_tdp")
        socket = self.request.query_params.get("socket")
        typ = self.request.query_params.get("type")
        if min_tdp:
            qs = qs.filter(tdp_w_supported__gte=min_tdp)
        if socket:
            qs = qs.filter(socket_compat__icontains=socket)
        if typ:
            qs = qs.filter(type__iexact=typ)
        return qs


# --- Build ---
class BuildViewSet(BaseViewSet):
    queryset = Build.objects.select_related(
        "cpu", "gpu", "motherboard", "ram", "storage", "psu", "case", "cooler", "user"
    ).all().order_by("-created_at")

    def get_serializer_class(self):
        # Ładny, zagnieżdżony odczyt; prosty serializer przy tworzeniu/edycji
        if self.action in ["list", "retrieve"]:
            return BuildDetailSerializer
        return BuildSerializer

    search_fields = [
        "name", "user__username",
        "cpu__name", "gpu__name", "motherboard__name"
    ]
    ordering_fields = ["created_at", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

