# core/views.py
from rest_framework import viewsets, filters
from .filterset import RAMBaseFilter, MotherboardFormFactorFilter, PSUFormFactorFilter
from .models import (
    Manufacturer, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler, Build
)
from .models import (
    PSUFormFactor, MotherboardFormFactor, Connector, RAMBase, Socket
)
from .serializer import (
    ManufacturerSerializer, CPUSerializer, GPUSerializer, MotherboardSerializer,
    RAMSerializer, StorageSerializer, PSUSerializer, CaseSerializer,
    CoolerSerializer, BuildSerializer, BuildDetailSerializer,
    GPUDetailSerializer, PSUDetailSerializer, MotherboardDetailSerializer
)
from .serializer import (
    PSUFormFactorSerializer, MotherboardFormFactorSerializer,
    ConnectorSerializer, RAMBaseSerializer, SocketSerializer
)
from core.services.motherboard_service import MotherboardService
from core.services.cpu_service import CPUService
from core.services.ram_service import RAMService
from core.services.gpu_service import GPUService
from core.services.psu_service import PSUService
from core.services.storage_service import StorageService
from core.services.case_service import CaseService

from core import tools


class PSUFormFactorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PSUFormFactor.objects.all().order_by("name")
    serializer_class = PSUFormFactorSerializer
    filterset_class = PSUFormFactorFilter


class MotherboardFormFactorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MotherboardFormFactor.objects.all().order_by("name")
    serializer_class = MotherboardFormFactorSerializer
    filterset_class = MotherboardFormFactorFilter


class ConnectorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Connector.objects.all().order_by("category")
    serializer_class = ConnectorSerializer


class RAMBaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RAMBase.objects.all().order_by("type", "mts")
    serializer_class = RAMBaseSerializer
    filterset_class = RAMBaseFilter


class SocketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Socket.objects.all().order_by("name")
    serializer_class = SocketSerializer


class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # Ustal w podklasach: search_fields, ordering_fields


class ManufacturerViewSet(BaseViewSet):
    queryset = Manufacturer.objects.all().order_by("name")
    serializer_class = ManufacturerSerializer


class CPUViewSet(BaseViewSet):
    queryset = CPU.objects.all().order_by("id")
    serializer_class = CPUSerializer

    def get_queryset(self):
        return CPUService.get_compatible_cpus(
            data=tools.extract_params(self.request)                                    
        )


class GPUViewSet(BaseViewSet):
    queryset = GPU.objects.all().order_by("id")
    serializer_class = GPUDetailSerializer

    def get_queryset(self):
        return GPUService.get_compatible_gpus(
            data=tools.extract_params(self.request)
        )


class MotherboardViewSet(BaseViewSet):
    queryset = Motherboard.objects.all().order_by("id")
    serializer_class = MotherboardDetailSerializer

    def get_queryset(self):
        return MotherboardService.get_compatible_motherboards(
            data=tools.extract_params(self.request)
        )


class RAMViewSet(BaseViewSet):
    queryset = RAM.objects.all().order_by("id")
    serializer_class = RAMSerializer

    def get_queryset(self):
        return RAMService.get_compatible_rams(
            data=tools.extract_params(self.request)
        )


class StorageViewSet(BaseViewSet):
    queryset = Storage.objects.all().order_by("id")
    serializer_class = StorageSerializer

    def get_queryset(self):
        return StorageService.get_compatible_m2(
            data=tools.extract_params(self.request)
        )


class PSUViewSet(BaseViewSet):
    queryset = PSU.objects.all().order_by("id")
    serializer_class = PSUDetailSerializer

    def get_queryset(self):
        return PSUService.get_compatible_psus(
            data=tools.extract_params(self.request)
        )


class CaseViewSet(BaseViewSet):
    queryset = Case.objects.all().order_by("id")
    serializer_class = CaseSerializer

    def get_queryset(self):
        return CaseService.get_compatible_cases(
            data=tools.extract_params(self.request)
        )


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


class BuildViewSet(BaseViewSet):
    queryset = Build.objects.select_related(
        "cpu", "gpu", "motherboard", "ram", "storage", "psu", "case", "cooler", "user"
    ).all().order_by("-created_at")

    def get_serializer_class(self):
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
