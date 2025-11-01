# core/filtersets.py
import django_filters
from .models import RAMBase, MotherboardFormFactor, PSUFormFactor

class IDInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Pozwala filtrować po liście ID np. ?id__in=1,2,3"""
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
