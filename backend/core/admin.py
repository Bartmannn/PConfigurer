from django.contrib import admin
from .models import             \
        MotherboardConnector,   \
        GPUConnector,           \
        Manufacturer,           \
        Motherboard,            \
        FormFactor,             \
        Connector,              \
        Storage,                \
        RAMBase,                \
        Socket,                 \
        Cooler,                 \
        Build,                  \
        Case,                   \
        CPU,                    \
        GPU,                    \
        RAM,                    \
        PSU

admin.site.register(MotherboardConnector)
admin.site.register(GPUConnector)
admin.site.register(Manufacturer)
# admin.site.register(Motherboard)
admin.site.register(FormFactor)
# admin.site.register(Connector)
admin.site.register(Storage)
admin.site.register(RAMBase)
admin.site.register(Socket)
admin.site.register(Cooler)
admin.site.register(Build)
admin.site.register(Case)
admin.site.register(CPU)
# admin.site.register(GPU)
admin.site.register(RAM)
admin.site.register(PSU)


class MotherboardConnectorInline(admin.TabularInline):
    model = MotherboardConnector
    extra = 1
    autocomplete_fields = ["connector"]


@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    inlines = [MotherboardConnectorInline]
    # list_display = ("name", "form_factor")
    search_fields = ("name",)


@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = ("category", "version", "lanes", "speed", "extra")
    search_fields = ("category", "specification")


class GPUConnectorInline(admin.TabularInline):
    model = GPUConnector
    extra = 1
    autocomplete_fields = ["connector"]


@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    inlines = [GPUConnectorInline]
    # list_display = ("name", "form_factor")
    search_fields = ("name",)
