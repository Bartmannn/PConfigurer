from django.contrib import admin
from .models import (
    MotherboardConnector, GPUConnector, PSUConnector,
    Manufacturer, Motherboard, FormFactor, Connector,
    Storage, RAMBase, Socket, Cooler, Build, Case,
    CPU, GPU, RAM, PSU 
)

admin.site.register(Manufacturer)
admin.site.register(FormFactor)
admin.site.register(Storage)
admin.site.register(RAMBase)
admin.site.register(Socket)
admin.site.register(Cooler)
admin.site.register(Build)
admin.site.register(Case)
admin.site.register(CPU)
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
