from django.contrib import admin
from .models import (
    MotherboardConnector, GPUConnector, PSUConnector,
    Manufacturer, Motherboard, Connector, Storage,
    RAMBase, Socket, Cooler, Build, Case, CPU, GPU,
    RAM, PSU, MotherboardFormFactor, PSUFormFactor,
    GraphicsChip, CPUSupportedPCIe
)

admin.site.register(MotherboardFormFactor)
admin.site.register(PSUFormFactor)
admin.site.register(Manufacturer)
admin.site.register(RAMBase)
admin.site.register(Socket)
admin.site.register(Cooler)
admin.site.register(Build)
admin.site.register(Case)
class CPUSupportedPCIeInline(admin.TabularInline):
    model = CPUSupportedPCIe
    extra = 1
    autocomplete_fields = ["connector"]


@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    inlines = [CPUSupportedPCIeInline]
    search_fields = ("name",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manufacturer":
            cpu_manufacturers = ['Intel', 'AMD']
            kwargs["queryset"] = Manufacturer.objects.filter(name__in=cpu_manufacturers)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "connector":
            kwargs["queryset"] = Connector.objects.filter(category__in=["M.2 PCIe", "M.2 SATA", "SATA"])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
admin.site.register(RAM)


@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = ("category", "version", "lanes", "speed", "extra", "is_power")
    search_fields = ("category", "specification")


class MotherboardConnectorInline(admin.TabularInline):
    model = MotherboardConnector
    extra = 1
    autocomplete_fields = ["connector"]


@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    inlines = [MotherboardConnectorInline]
    search_fields = ("name",)


class GPUConnectorInline(admin.TabularInline):
    model = GPUConnector
    extra = 1
    autocomplete_fields = ["connector"]


@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    inlines = [GPUConnectorInline]
    search_fields = ("name",)


class PSUConnectorInline(admin.TabularInline):
    model = PSUConnector
    extra = 1
    autocomplete_fields = ["connector"]


@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    inlines = [PSUConnectorInline]
    search_fields = ("name",)


@admin.register(GraphicsChip)
class GraphicsChipAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer')
    list_filter = ('manufacturer',)
    search_fields = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manufacturer":
            gpu_manufacturers = ['NVIDIA', 'AMD', 'Intel']
            kwargs["queryset"] = Manufacturer.objects.filter(name__in=gpu_manufacturers)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
