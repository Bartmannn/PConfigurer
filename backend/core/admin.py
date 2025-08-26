from django.contrib import admin
from .models import Manufacturer, CPU, GPU, Build


admin.site.register(Manufacturer)
admin.site.register(CPU)
admin.site.register(GPU)
admin.site.register(Build)