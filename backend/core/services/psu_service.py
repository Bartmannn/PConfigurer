
import re

from core.models import PSU, Case, Motherboard, GPU, MotherboardConnector, GPUConnector, CPU

class PSUService:
    
    SAFETY_FACTOR = 0.75

    @staticmethod
    def _coerce_number(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_requirement(requirement):
        if isinstance(requirement, dict):
            return (
                requirement.get("category"),
                requirement.get("lanes"),
                requirement.get("version"),
            )
        return requirement.category, requirement.lanes, requirement.version

    @staticmethod
    def _parse_connector_string(value: str):
        if not value:
            return None
        lowered = value.lower()
        category = None

        if "pcie" in lowered:
            category = "PCIe Power"
        elif "eps" in lowered or ("cpu" in lowered and "pin" in lowered):
            category = "CPU Power"
        elif "atx" in lowered:
            category = "ATX Power"
        elif "sata" in lowered:
            category = "SATA Power"
        elif "molex" in lowered:
            category = "Molex"

        if not category:
            return None

        lanes = None
        pin_match = re.search(r"(\d+)\s*-?\s*pin", lowered)
        if pin_match:
            lanes = int(pin_match.group(1))
        else:
            plus_match = re.search(r"(\d+)\s*\+\s*(\d+)", lowered)
            if plus_match:
                lanes = int(plus_match.group(1)) + int(plus_match.group(2))

        return category, lanes, None

    @staticmethod
    def _normalize_connector_item(item):
        if isinstance(item, dict):
            if item.get("category"):
                return item.get("category"), item.get("lanes"), item.get("version")
            text = item.get("name") or item.get("label") or item.get("connector")
            if text:
                return PSUService._parse_connector_string(text)
            return None
        if isinstance(item, str):
            return PSUService._parse_connector_string(item)
        return None

    @staticmethod
    def _extract_connector_quantity(item):
        if isinstance(item, dict):
            return item.get("quantity") or item.get("count") or item.get("value") or 1
        return 1

    @staticmethod
    def get_pcie_pins_list(connectors):
        if not connectors:
            return []
        if isinstance(connectors, dict):
            connectors = [
                {"name": name, "quantity": count} for name, count in connectors.items()
            ]
        pins = []
        has_data = False
        missing = False

        for item in connectors:
            category = None
            lanes = None
            if isinstance(item, dict):
                category = item.get("category")
                lanes = item.get("lanes")
                if not category or lanes is None:
                    text = item.get("name") or item.get("label") or item.get("connector")
                    parsed = PSUService._parse_connector_string(text)
                    if parsed:
                        category = category or parsed[0]
                        lanes = lanes if lanes is not None else parsed[1]
            elif isinstance(item, str):
                parsed = PSUService._parse_connector_string(item)
                if parsed:
                    category, lanes, _ = parsed

            if category != "PCIe Power":
                continue

            has_data = True
            quantity = PSUService._coerce_number(PSUService._extract_connector_quantity(item)) or 1
            lanes = PSUService._coerce_number(lanes)
            if lanes is None:
                missing = True
                continue

            for _ in range(int(quantity)):
                pins.append(int(lanes))

        if not has_data:
            return []
        if missing:
            return None
        return pins

    @staticmethod
    def get_gpu_pcie_pins_list(requirements):
        if not requirements:
            return []
        pins = []
        missing = False
        for req in requirements:
            connector = req.connector if hasattr(req, "connector") else req
            lanes = PSUService._coerce_number(getattr(connector, "lanes", None))
            quantity = PSUService._coerce_number(getattr(req, "quantity", None)) or 1
            if lanes is None:
                missing = True
                continue
            for _ in range(int(quantity)):
                pins.append(int(lanes))

        if missing:
            return None
        return pins

    @staticmethod
    def _find_best_subset(values, target):
        best_sum = None
        best = None

        def walk(start, total, chosen):
            nonlocal best_sum, best
            if total >= target:
                if best_sum is None or total < best_sum:
                    best_sum = total
                    best = list(chosen)
                return
            if start >= len(values):
                return
            if best_sum is not None and total >= best_sum:
                return

            for i in range(start, len(values)):
                chosen.append(i)
                walk(i + 1, total + values[i], chosen)
                chosen.pop()

        walk(0, 0, [])
        return best

    @staticmethod
    def can_satisfy_gpu_power(available_pins, required_pins):
        if available_pins is None or required_pins is None:
            return False
        if not required_pins:
            return True
        if not available_pins:
            return False

        available = sorted(available_pins, reverse=True)
        required = sorted(required_pins, reverse=True)

        for req in required:
            subset = PSUService._find_best_subset(available, req)
            if not subset:
                return False
            for index in sorted(subset, reverse=True):
                del available[index]

        return True

    @staticmethod
    def psu_supports_connector(psu_connectors, requirement) -> bool:
        req_category, req_lanes, req_version = PSUService._extract_requirement(requirement)
        if not req_category:
            return False

        req_lanes = PSUService._coerce_number(req_lanes)
        req_version = PSUService._coerce_number(req_version)
        for item in psu_connectors or []:
            normalized = PSUService._normalize_connector_item(item)
            if not normalized:
                continue
            item_category, item_lanes_raw, item_version_raw = normalized
            if item_category != req_category:
                continue

            item_lanes = PSUService._coerce_number(item_lanes_raw)
            if req_lanes is not None and (item_lanes is None or item_lanes < req_lanes):
                continue

            if req_version is not None:
                item_version = PSUService._coerce_number(item_version_raw)
                if item_version is not None and item_version < req_version:
                    continue

            return True

        return False
    
    @staticmethod
    def get_compatible_psus(data: dict[str, int]):
        
        qs = PSU.objects.all()
        
        gpu_pk = data.get("gpu")
        cpu_pk = data.get("cpu")
        mobo_pk = data.get("mobo")
        case_pk = data.get("case")

        min_wattage = 0
        
        if gpu_pk:
            # If a GPU is selected, its recommended system power is the primary criterion.
            gpu = GPU.objects.select_related('graphics_chip').filter(pk=gpu_pk).first()
            if gpu:
                if gpu.recommended_system_power_w:
                    min_wattage = gpu.recommended_system_power_w
        
        elif cpu_pk:
            # If no GPU, estimate based on CPU TDP + a baseline for the rest of the system.
            cpu_tdp = (
                CPU.objects.filter(pk=cpu_pk)
                .values_list("tdp", flat=True)
                .first()
            ) or 0
            min_wattage = cpu_tdp + 250 # Baseline for a system without a powerful GPU

        if mobo_pk:
            mobo = Motherboard.objects.get(pk=mobo_pk)
            qs = PSUService.filter_by_mobo(qs, mobo)
            
        if case_pk:
            case = Case.objects.filter(pk=case_pk).prefetch_related("psu_form_factor_support").first()
            supported_formats = case.psu_form_factor_support.all()
            qs = qs.filter(form_factor__in=supported_formats)
        
        qs = qs.filter(wattage__gte=min_wattage)

        return qs.distinct()
    
    
    @staticmethod
    def filter_by_mobo(qs, mobo: Motherboard): # TODO: też mi się to nie podoba
        
        mobo_conns = MotherboardConnector.objects.filter(
            motherboard=mobo,
            connector__is_power=True
        )

        requirements = [conn.connector for conn in mobo_conns.select_related("connector")]
        if not requirements:
            return qs.distinct()

        psu_ids = []
        for psu_id, connectors in qs.values_list("id", "connectors"):
            if all(PSUService.psu_supports_connector(connectors, req) for req in requirements):
                psu_ids.append(psu_id)

        return qs.filter(id__in=psu_ids).distinct()
    
    
    @staticmethod
    def filter_by_gpu(qs, gpu: GPU): # TODO: absolutnie mi się to nie podoba!
        
        gpu_conns = GPUConnector.objects.filter(
            gpu=gpu,
            connector__category="PCIe Power"
        ).select_related("connector")

        required_pins = PSUService.get_gpu_pcie_pins_list(gpu_conns)
        if required_pins is None:
            return qs.none()
        if not required_pins:
            return qs

        psu_ids = []
        for psu_id, connectors in qs.values_list("id", "connectors"):
            available_pins = PSUService.get_pcie_pins_list(connectors)
            if PSUService.can_satisfy_gpu_power(available_pins, required_pins):
                psu_ids.append(psu_id)

        return qs.filter(id__in=psu_ids)
        
        
