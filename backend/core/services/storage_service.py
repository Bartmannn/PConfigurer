from core.models import Storage, MotherboardConnector

class StorageService:
    
    @staticmethod
    def get_compatible_m2(data: dict[str, int]):
        qs = Storage.objects.all()
        
        mobo_pk = data.get("mobo")
        slot = StorageService.get_mobo_slot(mobo_pk)
            
        if slot:
            slot_category = slot["connector__category"]
            slot_version = slot["connector__version"]
            slot_lanes = slot["connector__lanes"]
            
            allowed_categories = [slot_category]
            if slot_category == "M.2 PCIe" and slot.get("connector__extra"):
                allowed_categories = ["M.2 PCIe", "M.2 SATA"]

            qs = qs.filter(
                connector__category__in=allowed_categories,
                connector__version__lte=slot_version,
                connector__lanes__lte=slot_lanes,
            )
        
        return qs.distinct()
    
    def get_mobo_slot(mobo_pk, categories=["M.2 PCIe", "M.2 SATA"]):
        if not mobo_pk:
            return None
        return (
            MotherboardConnector.objects
            .filter(motherboard_id=mobo_pk, connector__category__in=categories)
            .order_by("-connector__version", "-connector__lanes")
            .values(
                "connector__category",
                "connector__version",
                "connector__lanes",
                "connector__extra",
            )
            .first()
        )

