# core/views.py
from rest_framework import viewsets, filters
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
from core.services.gpu_service import GPUService
from core.services.psu_service import PSUService

from core import tools

# --- Bazowy ViewSet z wyszukiwaniem i sortowaniem ---
class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # Ustal w podklasach: search_fields, ordering_fields


# --- Manufacturer ---
class ManufacturerViewSet(BaseViewSet):
    queryset = Manufacturer.objects.all().order_by("name")
    serializer_class = ManufacturerSerializer


# --- CPU ---
class CPUViewSet(BaseViewSet):
    queryset = CPU.objects.all().order_by("id")
    serializer_class = CPUSerializer

    def get_queryset(self):
        return CPUService.get_compatible_cpus(
            data=tools.extract_params(self.request)                                    
        )


# --- GPU ---
class GPUViewSet(BaseViewSet):
    queryset = GPU.objects.all().order_by("id")
    serializer_class = GPUSerializer

    def get_queryset(self):
        return GPUService.get_compatible_gpus(
            data=tools.extract_params(self.request)
        )


# --- Motherboard ---
class MotherboardViewSet(BaseViewSet):
    queryset = Motherboard.objects.all().order_by("id")
    serializer_class = MotherboardSerializer

    def get_queryset(self):
        return MotherboardService.get_compatible_motherboards(
            data=tools.extract_params(self.request)
        )


# --- RAM ---
class RAMViewSet(BaseViewSet):
    queryset = RAM.objects.all().order_by("id")
    serializer_class = RAMSerializer

    def get_queryset(self):
        return RAMService.get_compatible_rams(
            data=tools.extract_params(self.request)
        )


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

    def get_queryset(self):
        return PSUService.get_compatible_psus(
            data=tools.extract_params(self.request)
        )


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

