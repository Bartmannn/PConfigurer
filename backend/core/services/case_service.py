from core.models import Case, Motherboard, PSU, GPU


class CaseService:
    
    @staticmethod
    def get_compatible_cases(data: dict[str, int]):
        qs = Case.objects.all()
        
        mobo_pk = data.get("mobo")
        psu_pk = data.get("psu")
        gpu_pk = data.get("gpu")
        
        if mobo_pk:
            mobo_form_factor = (
                Motherboard.objects
                .filter(pk=mobo_pk)
                .values_list("form_factor", flat=True)
                .first()
            )
            qs = qs.filter(mobo_form_factor_support=mobo_form_factor)
            
        if psu_pk:
            psu_form_factor = (
                PSU.objects
                .filter(pk=psu_pk)
                .values_list("form_factor", flat=True)
                .first()
            )
            qs = qs.filter(psu_form_factor_support=psu_form_factor)
            
        if gpu_pk:
            gpu_length = (
                GPU.objects
                .filter(pk=gpu_pk)
                .values_list("length_mm", flat=True)
                .first()
            )
            qs = qs.filter(max_gpu_length_mm__gte=gpu_length)
        
        return qs