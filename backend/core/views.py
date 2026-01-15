# core/views.py
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .filterset import (
    RAMBaseFilter, MotherboardFormFactorFilter, PSUFormFactorFilter,
    CPUFilter, MotherboardFilter, RAMFilter, StorageFilter, GPUFilter
)
from .models import (
    Manufacturer, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler, Build, GraphicsChip
)
from .models import (
    PSUFormFactor, MotherboardFormFactor, Connector, RAMBase, Socket
)
from .serializer import (
    ManufacturerSerializer, CPUSerializer, GPUSerializer, MotherboardSerializer,
    RAMSerializer, StorageSerializer, PSUSerializer, CaseSerializer,
    CoolerSerializer, BuildSerializer, BuildDetailSerializer,
    GPUDetailSerializer, PSUDetailSerializer, MotherboardDetailSerializer,
    CPUDetailSerializer, RAMDetailSerializer, StorageDetailSerializer,
    CaseDetailSerializer, CoolerDetailSerializer, PSUFormFactorSerializer,
    MotherboardFormFactorSerializer, ConnectorSerializer, RAMBaseSerializer,
    SocketSerializer, 
)
from core.services.motherboard_service import MotherboardService
from core.services.cpu_service import CPUService
from core.services.ram_service import RAMService
from core.services.gpu_service import GPUService
from core.services.psu_service import PSUService
from core.services.storage_service import StorageService
from core.services.case_service import CaseService
from core.services.builder_service import BuildBuilderService

from core import tools

OUTPUT_CATEGORIES = ("HDMI", "DisplayPort", "DVI", "VGA", "USB-C")


def build_options(values, label_fn=None):
    return [
        {"value": value, "label": label_fn(value) if label_fn else str(value)}
        for value in values
    ]


def values_to_options(rows, value_key, label_key):
    return [
        {"value": row[value_key], "label": row[label_key]}
        for row in rows
    ]


def rambase_options(qs):
    return [
        {"value": base.id, "label": f"{base.type}-{base.mts}"}
        for base in qs.order_by("type", "mts")
    ]


def connector_options(qs):
    return [
        {"value": connector.id, "label": str(connector)}
        for connector in qs.order_by("category", "version", "lanes")
    ]


def _resolve_field(model, field):
    current_model = model
    field_obj = None
    for part in field.split("__"):
        try:
            field_obj = current_model._meta.get_field(part)
        except Exception:
            return None
        if getattr(field_obj, "is_relation", False) and hasattr(field_obj, "related_model"):
            current_model = field_obj.related_model
    return field_obj


def distinct_values(qs, field, order=True):
    field_obj = _resolve_field(qs.model, field)
    if field_obj is not None and getattr(field_obj, "null", False):
        qs = qs.exclude(**{f"{field}__isnull": True})
    if field_obj is not None and field_obj.get_internal_type() in {
        "CharField",
        "TextField",
        "SlugField",
        "EmailField",
        "URLField",
    }:
        qs = qs.exclude(**{field: ""})
    values = qs.values_list(field, flat=True).distinct()
    if order:
        values = values.order_by(field)
    return list(values)


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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Ustal w podklasach: search_fields, ordering_fields


class ManufacturerViewSet(BaseViewSet):
    queryset = Manufacturer.objects.all().order_by("name")
    serializer_class = ManufacturerSerializer


class CPUViewSet(BaseViewSet):
    queryset = CPU.objects.all().order_by("id")
    filterset_class = CPUFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CPUDetailSerializer
        return CPUSerializer

    def get_queryset(self):
        return CPUService.get_compatible_cpus(
            data=tools.extract_params(self.request)                                    
        )


class GPUViewSet(BaseViewSet):
    queryset = GPU.objects.all().order_by("id")
    filterset_class = GPUFilter
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return GPUDetailSerializer
        return GPUSerializer

    def get_queryset(self):
        return GPUService.get_compatible_gpus(
            data=tools.extract_params(self.request)
        )


class MotherboardViewSet(BaseViewSet):
    queryset = Motherboard.objects.all().order_by("id")
    filterset_class = MotherboardFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return MotherboardDetailSerializer
        return MotherboardSerializer

    def get_queryset(self):
        return MotherboardService.get_compatible_motherboards(
            data=tools.extract_params(self.request)
        )


class RAMViewSet(BaseViewSet):
    queryset = RAM.objects.all().order_by("id")
    filterset_class = RAMFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RAMDetailSerializer
        return RAMSerializer

    def get_queryset(self):
        return RAMService.get_compatible_rams(
            data=tools.extract_params(self.request)
        )


class StorageViewSet(BaseViewSet):
    queryset = Storage.objects.all().order_by("id")
    filterset_class = StorageFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return StorageDetailSerializer
        return StorageSerializer

    def get_queryset(self):
        return StorageService.get_compatible_m2(
            data=tools.extract_params(self.request)
        )


class PSUViewSet(BaseViewSet):
    queryset = PSU.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return PSUDetailSerializer
        return PSUSerializer

    def get_queryset(self):
        return PSUService.get_compatible_psus(
            data=tools.extract_params(self.request)
        )


class CaseViewSet(BaseViewSet):
    queryset = Case.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CaseDetailSerializer
        return CaseSerializer

    def get_queryset(self):
        return CaseService.get_compatible_cases(
            data=tools.extract_params(self.request)
        )


class CoolerViewSet(BaseViewSet):
    queryset = Cooler.objects.all().order_by("id")
    search_fields = ["name", "manufacturer__name", "type", "socket_compat"]
    ordering_fields = ["tdp_w_supported", "id"]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CoolerDetailSerializer
        return CoolerSerializer

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
    search_fields = [
        "name", "user__username",
        "cpu__name", "gpu__name", "motherboard__name"
    ]
    ordering_fields = ["created_at", "id"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BuildDetailSerializer
        return BuildSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class FilterOptionsView(APIView):
    def get(self, request):
        cpu_qs = CPU.objects.all()
        mobo_qs = Motherboard.objects.all()
        ram_qs = RAM.objects.all()
        storage_qs = Storage.objects.all()
        gpu_qs = GPU.objects.all()
        chip_qs = GraphicsChip.objects.filter(gpu__isnull=False).distinct()

        cpu_options = {
            "family": build_options(distinct_values(cpu_qs, "family")),
            "generation": build_options(distinct_values(cpu_qs, "generation")),
            "manufacturer": values_to_options(
                cpu_qs.values("manufacturer_id", "manufacturer__name").distinct().order_by("manufacturer__name"),
                "manufacturer_id",
                "manufacturer__name",
            ),
            "socket": values_to_options(
                cpu_qs.values("socket_id", "socket__name").distinct().order_by("socket__name"),
                "socket_id",
                "socket__name",
            ),
            "p_cores": build_options(distinct_values(cpu_qs, "p_cores")),
            "e_cores": build_options(distinct_values(cpu_qs, "e_cores")),
            "threads": build_options(distinct_values(cpu_qs, "threads")),
            "supported_ram": rambase_options(
                RAMBase.objects.filter(cpu__isnull=False).distinct()
            ),
            "max_internal_memory_gb": build_options(distinct_values(cpu_qs, "max_internal_memory_gb")),
            "supported_pcie": connector_options(
                Connector.objects.filter(cpu_supported_pcie__isnull=False, category="PCIe").distinct()
            ),
            "cache_mb": build_options(distinct_values(cpu_qs, "cache_mb")),
            "pcie_max_gen": build_options(
                distinct_values(
                    Connector.objects.filter(cpu_supported_pcie__isnull=False, category="PCIe"),
                    "version",
                )
            ),
        }

        motherboard_options = {
            "manufacturer": values_to_options(
                mobo_qs.values("manufacturer_id", "manufacturer__name").distinct().order_by("manufacturer__name"),
                "manufacturer_id",
                "manufacturer__name",
            ),
            "socket": values_to_options(
                mobo_qs.values("socket_id", "socket__name").distinct().order_by("socket__name"),
                "socket_id",
                "socket__name",
            ),
            "form_factor": values_to_options(
                mobo_qs.values("form_factor_id", "form_factor__name").distinct().order_by("form_factor__name"),
                "form_factor_id",
                "form_factor__name",
            ),
            "supported_ram": rambase_options(
                RAMBase.objects.filter(motherboard__isnull=False).distinct()
            ),
            "max_ram_capacity": build_options(distinct_values(mobo_qs, "max_ram_capacity")),
            "dimm_slots": build_options(distinct_values(mobo_qs, "dimm_slots")),
            "pcie_max_gen": build_options(
                distinct_values(
                    Connector.objects.filter(motherboardconnector__isnull=False, category="PCIe"),
                    "version",
                )
            ),
        }

        ram_options = {
            "manufacturer": values_to_options(
                ram_qs.values("manufacturer_id", "manufacturer__name").distinct().order_by("manufacturer__name"),
                "manufacturer_id",
                "manufacturer__name",
            ),
            "base": rambase_options(
                RAMBase.objects.filter(variants__isnull=False).distinct()
            ),
            "modules_count": build_options(distinct_values(ram_qs, "modules_count")),
            "total_capacity": build_options(distinct_values(ram_qs, "total_capacity")),
        }

        storage_options = {
            "manufacturer": values_to_options(
                storage_qs.values("manufacturer_id", "manufacturer__name").distinct().order_by("manufacturer__name"),
                "manufacturer_id",
                "manufacturer__name",
            ),
            "connector": connector_options(
                Connector.objects.filter(storage__isnull=False).distinct()
            ),
            "capacity_gb": build_options(distinct_values(storage_qs, "capacity_gb")),
            "pcie_max_gen": build_options(
                distinct_values(
                    Connector.objects.filter(storage__isnull=False, category="M.2 PCIe"),
                    "version",
                )
            ),
        }

        gpu_output_values = distinct_values(
            Connector.objects.filter(gpuconnector__isnull=False, category__in=OUTPUT_CATEGORIES),
            "category",
        )

        gpu_options = {
            "manufacturer": values_to_options(
                gpu_qs.values("manufacturer_id", "manufacturer__name").distinct().order_by("manufacturer__name"),
                "manufacturer_id",
                "manufacturer__name",
            ),
            "vram_size_gb": build_options(distinct_values(gpu_qs, "vram_size_gb")),
            "outputs": build_options(gpu_output_values),
            "graphics_chip_vendor": build_options(distinct_values(chip_qs, "vendor")),
            "graphics_chip_marketing_name": build_options(
                distinct_values(chip_qs, "marketing_name")
            ),
            "graphics_chip_pcie_max_gen": build_options(
                distinct_values(chip_qs, "pcie_max_gen")
            ),
            "graphics_chip_memory_type": build_options(
                distinct_values(chip_qs, "memory_type")
            ),
            "graphics_chip_ray_tracing_gen": build_options(
                distinct_values(chip_qs, "ray_tracing_gen")
            ),
            "graphics_chip_upscaling_technology": build_options(
                distinct_values(chip_qs, "upscaling_technology")
            ),
        }

        return Response({
            "cpu": cpu_options,
            "mobo": motherboard_options,
            "ram": ram_options,
            "mem": storage_options,
            "gpu": gpu_options,
        })


class BuildBuilderView(APIView):
    def get(self, request):
        budget_raw = request.query_params.get("budget")
        if not budget_raw:
            return Response({"error": "budget_required"}, status=400)

        try:
            budget = int(budget_raw)
        except ValueError:
            return Response({"error": "budget_invalid"}, status=400)

        result = BuildBuilderService.build(budget)
        if not result:
            return Response({"error": "build_not_found"}, status=404)

        return Response({
            "budget": budget,
            "total_price": str(result.total_price),
            "cpu": CPUDetailSerializer(result.cpu).data,
            "gpu": GPUDetailSerializer(result.gpu).data,
            "mobo": MotherboardDetailSerializer(result.motherboard).data,
            "ram": RAMDetailSerializer(result.ram).data,
            "mem": StorageDetailSerializer(result.storage).data,
            "psu": PSUDetailSerializer(result.psu).data,
            "chassis": CaseDetailSerializer(result.case).data,
        })
