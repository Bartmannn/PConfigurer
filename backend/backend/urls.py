from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import CPUViewSet, GPUViewSet, BuildViewSet, FilterOptionsView, BuildBuilderView
from core.views import (
    CPUViewSet, GPUViewSet, MotherboardViewSet, RAMViewSet, StorageViewSet,
    PSUViewSet, CaseViewSet, CoolerViewSet, BuildViewSet, ManufacturerViewSet,
    PSUFormFactorViewSet, MotherboardFormFactorViewSet, ConnectorViewSet,
    RAMBaseViewSet, SocketViewSet
)

router = DefaultRouter()
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'cpus', CPUViewSet)
router.register(r'gpus', GPUViewSet)
router.register(r'motherboards', MotherboardViewSet)
router.register(r'rams', RAMViewSet)
router.register(r'mems', StorageViewSet)
router.register(r'psus', PSUViewSet)
router.register(r'cases', CaseViewSet)
router.register(r'coolers', CoolerViewSet)
router.register(r'builds', BuildViewSet)

router.register(r"psuformfactors", PSUFormFactorViewSet)
router.register(r"motherboardformfactors", MotherboardFormFactorViewSet)
router.register(r"connectors", ConnectorViewSet)
router.register(r"rambases", RAMBaseViewSet)
router.register(r"sockets", SocketViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/filters/options/', FilterOptionsView.as_view()),
    path('api/builder/', BuildBuilderView.as_view()),
]
