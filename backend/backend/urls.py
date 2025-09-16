"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import CPUViewSet, GPUViewSet, BuildViewSet
from core.views import (
    CPUViewSet, GPUViewSet, MotherboardViewSet, RAMViewSet, StorageViewSet,
    PSUViewSet, CaseViewSet, CoolerViewSet, BuildViewSet, ManufacturerViewSet
)

router = DefaultRouter()
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'cpus', CPUViewSet)
router.register(r'gpus', GPUViewSet)
router.register(r'motherboards', MotherboardViewSet)
router.register(r'rams', RAMViewSet)
router.register(r'storage', StorageViewSet)
router.register(r'psus', PSUViewSet)
router.register(r'cases', CaseViewSet)
router.register(r'coolers', CoolerViewSet)
router.register(r'builds', BuildViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]