# core/filtersets.py
import django_filters
from .models import (
    RAMBase, MotherboardFormFactor, PSUFormFactor,
    CPU, Motherboard, RAM, Storage, GPU
)

class IDInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Pozwala filtrować po liście ID np. ?id__in=1,2,3"""
    pass

class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass

class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class RAMBaseFilter(django_filters.FilterSet):
    id__in = IDInFilter(field_name="id", lookup_expr="in")

    class Meta:
        model = RAMBase
        fields = ["id__in"]

class MotherboardFormFactorFilter(django_filters.FilterSet):
    id__in = IDInFilter(field_name="id", lookup_expr="in")

    class Meta:
        model = MotherboardFormFactor
        fields = ["id__in"]

class PSUFormFactorFilter(django_filters.FilterSet):
    id__in = IDInFilter(field_name="id", lookup_expr="in")

    class Meta:
        model = PSUFormFactor
        fields = ["id__in"]


class CPUFilter(django_filters.FilterSet):
    family = CharInFilter(field_name="family", lookup_expr="in")
    generation = CharInFilter(field_name="generation", lookup_expr="in")
    manufacturer = NumberInFilter(field_name="manufacturer_id", lookup_expr="in")
    socket = NumberInFilter(field_name="socket_id", lookup_expr="in")
    p_cores = NumberInFilter(field_name="p_cores", lookup_expr="in")
    e_cores = NumberInFilter(field_name="e_cores", lookup_expr="in")
    threads = NumberInFilter(field_name="threads", lookup_expr="in")
    boost_clock_ghz = django_filters.RangeFilter(field_name="boost_clock_ghz")
    supported_ram = NumberInFilter(field_name="supported_ram", lookup_expr="in")
    max_internal_memory_gb = NumberInFilter(field_name="max_internal_memory_gb", lookup_expr="in")
    supported_pcie = NumberInFilter(field_name="supported_pcie", lookup_expr="in")
    tdp = django_filters.RangeFilter(field_name="tdp")
    price = django_filters.RangeFilter(field_name="price")
    cache_mb = NumberInFilter(field_name="cache_mb", lookup_expr="in")
    integrated_gpu = django_filters.BooleanFilter(field_name="integrated_gpu")
    pcie_max_gen = NumberInFilter(method="filter_pcie_max_gen")

    class Meta:
        model = CPU
        fields = [
            "family", "generation", "manufacturer", "socket", "p_cores", "e_cores",
            "threads", "boost_clock_ghz", "supported_ram", "max_internal_memory_gb",
            "supported_pcie", "tdp", "price", "cache_mb", "integrated_gpu", "pcie_max_gen",
        ]

    def filter_pcie_max_gen(self, queryset, name, value):
        return queryset.filter(supported_pcie__version__in=value).distinct()


class MotherboardFilter(django_filters.FilterSet):
    manufacturer = NumberInFilter(field_name="manufacturer_id", lookup_expr="in")
    socket = NumberInFilter(field_name="socket_id", lookup_expr="in")
    form_factor = NumberInFilter(field_name="form_factor_id", lookup_expr="in")
    supported_ram = NumberInFilter(field_name="supported_ram", lookup_expr="in")
    max_ram_capacity = NumberInFilter(field_name="max_ram_capacity", lookup_expr="in")
    dimm_slots = NumberInFilter(field_name="dimm_slots", lookup_expr="in")
    price = django_filters.RangeFilter(field_name="price")
    pcie_max_gen = NumberInFilter(method="filter_pcie_max_gen")

    class Meta:
        model = Motherboard
        fields = [
            "manufacturer", "socket", "form_factor", "supported_ram",
            "max_ram_capacity", "dimm_slots", "price", "pcie_max_gen",
        ]

    def filter_pcie_max_gen(self, queryset, name, value):
        return queryset.filter(
            motherboardconnector__connector__category="PCIe",
            motherboardconnector__connector__version__in=value,
        ).distinct()


class RAMFilter(django_filters.FilterSet):
    manufacturer = NumberInFilter(field_name="manufacturer_id", lookup_expr="in")
    base = NumberInFilter(field_name="base_id", lookup_expr="in")
    modules_count = NumberInFilter(field_name="modules_count", lookup_expr="in")
    total_capacity = NumberInFilter(field_name="total_capacity", lookup_expr="in")
    price = django_filters.RangeFilter(field_name="price")

    class Meta:
        model = RAM
        fields = ["manufacturer", "base", "modules_count", "total_capacity", "price"]


class StorageFilter(django_filters.FilterSet):
    manufacturer = NumberInFilter(field_name="manufacturer_id", lookup_expr="in")
    connector = NumberInFilter(field_name="connector_id", lookup_expr="in")
    capacity_gb = NumberInFilter(field_name="capacity_gb", lookup_expr="in")
    price = django_filters.RangeFilter(field_name="price")
    pcie_max_gen = NumberInFilter(method="filter_pcie_max_gen")

    class Meta:
        model = Storage
        fields = ["manufacturer", "connector", "capacity_gb", "price", "pcie_max_gen"]

    def filter_pcie_max_gen(self, queryset, name, value):
        return queryset.filter(
            connector__category="M.2 PCIe",
            connector__version__in=value,
        ).distinct()


class GPUFilter(django_filters.FilterSet):
    manufacturer = NumberInFilter(field_name="manufacturer_id", lookup_expr="in")
    vram_size_gb = NumberInFilter(field_name="vram_size_gb", lookup_expr="in")
    base_clock_mhz = django_filters.RangeFilter(field_name="base_clock_mhz")
    boost_clock_mhz = django_filters.RangeFilter(field_name="boost_clock_mhz")
    tdp = django_filters.RangeFilter(field_name="tdp")
    recommended_system_power_w = django_filters.RangeFilter(field_name="recommended_system_power_w")
    length_mm = django_filters.RangeFilter(field_name="length_mm")
    slot_width = django_filters.RangeFilter(field_name="slot_width")
    outputs = CharInFilter(method="filter_outputs")
    price = django_filters.RangeFilter(field_name="price")
    graphics_chip_vendor = CharInFilter(field_name="graphics_chip__vendor", lookup_expr="in")
    graphics_chip_marketing_name = CharInFilter(field_name="graphics_chip__marketing_name", lookup_expr="in")
    graphics_chip_pcie_max_gen = NumberInFilter(field_name="graphics_chip__pcie_max_gen", lookup_expr="in")
    graphics_chip_memory_type = CharInFilter(field_name="graphics_chip__memory_type", lookup_expr="in")
    graphics_chip_ray_tracing_gen = NumberInFilter(field_name="graphics_chip__ray_tracing_gen", lookup_expr="in")
    graphics_chip_upscaling_technology = CharInFilter(field_name="graphics_chip__upscaling_technology", lookup_expr="in")

    class Meta:
        model = GPU
        fields = [
            "manufacturer", "vram_size_gb", "base_clock_mhz", "boost_clock_mhz",
            "tdp", "recommended_system_power_w", "length_mm", "slot_width", "outputs",
            "price", "graphics_chip_vendor", "graphics_chip_marketing_name",
            "graphics_chip_pcie_max_gen", "graphics_chip_memory_type",
            "graphics_chip_ray_tracing_gen", "graphics_chip_upscaling_technology",
        ]

    def filter_outputs(self, queryset, name, value):
        return queryset.filter(
            gpuconnector__connector__category__in=value
        ).distinct()
