from django.contrib import admin
from .models import Manufacturer, Socket, CPU, GPU, Motherboard, RAMBase, RAM, Storage, PSU, Case, Cooler, Build


admin.site.register(Manufacturer)
admin.site.register(Socket)
admin.site.register(CPU)
admin.site.register(GPU)
admin.site.register(RAMBase)
admin.site.register(RAM)
admin.site.register(Storage)
admin.site.register(PSU)
admin.site.register(Case)
admin.site.register(Cooler)
admin.site.register(Motherboard)
admin.site.register(Build)
