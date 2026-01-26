from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from core.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case
from core.services.psu_service import PSUService
from core.services.case_service import CaseService


@dataclass
class BuildResult:
    cpu: CPU
    gpu: GPU
    motherboard: Motherboard
    ram: RAM
    storage: Storage
    psu: PSU
    case: Case
    total_price: Decimal
    score: float


class BuildBuilderService:
    GPU_LIMIT = 20
    CPU_LIMIT = 25
    MOBO_LIMIT = 25

    @staticmethod
    def get_targets(budget: Decimal) -> tuple[int, int]:
        if budget > 10000:
            return 64, 2000
        if budget >= 6000:
            return 32, 2000
        return 16, 1000

    @staticmethod
    def build(budget: int) -> Optional[BuildResult]:
        try:
            budget_value = Decimal(budget)
        except Exception:
            return None

        if budget_value <= 0:
            return None

        target_ram_gb, target_storage_gb = BuildBuilderService.get_targets(budget_value)

        gpus = list(
            GPU.objects.select_related("graphics_chip")
            .filter(
                price__isnull=False,
                graphics_chip__isnull=False,
                graphics_chip__pcie_max_gen__isnull=False,
                recommended_system_power_w__isnull=False,
            )
        )
        gpus.sort(key=lambda gpu: (-BuildBuilderService._safe_tier_score(gpu), gpu.price))

        best_result = None

        for gpu in gpus[: BuildBuilderService.GPU_LIMIT]:
            pcie_gen = gpu.graphics_chip.pcie_max_gen
            if not pcie_gen:
                continue

            cpu_candidates = (
                CPU.objects.filter(
                    price__isnull=False,
                    supported_pcie__version=pcie_gen,
                )
                .prefetch_related("supported_ram", "supported_pcie")
                .distinct()
            )
            cpu_list = list(cpu_candidates)
            cpu_list.sort(
                key=lambda cpu: (
                    0 if BuildBuilderService._cpu_supports_ram_type(cpu, "DDR5") else 1,
                    -BuildBuilderService._safe_tier_score(cpu),
                    cpu.price,
                )
            )

            for cpu in cpu_list[: BuildBuilderService.CPU_LIMIT]:
                result = BuildBuilderService._try_build_for_cpu_gpu(
                    cpu=cpu,
                    gpu=gpu,
                    pcie_gen=pcie_gen,
                    target_ram_gb=target_ram_gb,
                    target_storage_gb=target_storage_gb,
                    budget=budget_value,
                )
                if not result:
                    continue

                if best_result is None:
                    best_result = result
                    continue

                if result.score > best_result.score:
                    best_result = result
                    continue

                if result.score == best_result.score and result.total_price > best_result.total_price:
                    best_result = result

        return best_result

    @staticmethod
    def _ram_target_fallbacks(target_ram_gb: int) -> list[int]:
        if target_ram_gb >= 64:
            return [64, 32, 16]
        if target_ram_gb >= 32:
            return [32, 16]
        return [16]

    @staticmethod
    def _storage_target_fallbacks(target_storage_gb: int) -> list[int]:
        if target_storage_gb >= 2000:
            return [2000, 1000]
        return [1000]

    @staticmethod
    def _try_build_for_cpu_gpu(
        cpu: CPU,
        gpu: GPU,
        pcie_gen: int,
        target_ram_gb: int,
        target_storage_gb: int,
        budget: Decimal,
    ) -> Optional[BuildResult]:
        mobo_candidates = Motherboard.objects.filter(
            price__isnull=False,
            socket=cpu.socket,
        ).prefetch_related("supported_ram", "motherboardconnector_set__connector")

        mobo_list = [
            mobo
            for mobo in mobo_candidates
            if BuildBuilderService._mobo_supports_pcie(mobo, pcie_gen, gpu.graphics_chip.pcie_max_width)
        ]
        mobo_list.sort(key=lambda mobo: mobo.price)

        for mobo in mobo_list[: BuildBuilderService.MOBO_LIMIT]:
            ram = None
            for ram_target in BuildBuilderService._ram_target_fallbacks(target_ram_gb):
                ram = BuildBuilderService._pick_ram(cpu, mobo, ram_target)
                if ram:
                    break
            if not ram:
                continue

            storage = None
            for storage_target in BuildBuilderService._storage_target_fallbacks(target_storage_gb):
                storage = BuildBuilderService._pick_storage(mobo, pcie_gen, storage_target)
                if storage:
                    break
            if not storage:
                continue

            psu, case = BuildBuilderService._pick_psu_and_case(cpu, gpu, mobo)
            if not psu or not case:
                continue

            total_price = BuildBuilderService._sum_prices(
                cpu, gpu, mobo, ram, storage, psu, case
            )
            if total_price is None or total_price > budget:
                continue

            score = float(
                BuildBuilderService._safe_tier_score(cpu)
                + BuildBuilderService._safe_tier_score(gpu)
            )
            return BuildResult(
                cpu=cpu,
                gpu=gpu,
                motherboard=mobo,
                ram=ram,
                storage=storage,
                psu=psu,
                case=case,
                total_price=total_price,
                score=score,
            )

        return None

    @staticmethod
    def _sum_prices(*items) -> Optional[Decimal]:
        total = Decimal("0")
        for item in items:
            price = getattr(item, "price", None)
            if price is None:
                return None
            total += Decimal(price)
        return total

    @staticmethod
    def _safe_tier_score(item) -> int:
        try:
            return int(item.tier_score or 0)
        except Exception:
            return 0

    @staticmethod
    def _cpu_supports_ram_type(cpu: CPU, ram_type: str) -> bool:
        return any(base.type == ram_type for base in cpu.supported_ram.all())

    @staticmethod
    def _mobo_supports_pcie(mobo: Motherboard, pcie_gen: int, gpu_width: int) -> bool:
        connectors = list(mobo.motherboardconnector_set.all())
        has_gpu_slot = False
        has_storage_slot = False

        for conn in connectors:
            connector = conn.connector
            if connector.category == "PCIe" and connector.version == pcie_gen:
                if connector.lanes >= gpu_width and conn.quantity >= 1:
                    has_gpu_slot = True
            if connector.category == "M.2 PCIe" and connector.version == pcie_gen:
                if conn.quantity >= 1:
                    has_storage_slot = True

        return has_gpu_slot and has_storage_slot

    @staticmethod
    def _pick_ram(cpu: CPU, mobo: Motherboard, target_ram_gb: int) -> Optional[RAM]:
        cpu_types = set(cpu.supported_ram.values_list("type", flat=True).distinct())
        mobo_types = set(mobo.supported_ram.values_list("type", flat=True).distinct())
        allowed_types = cpu_types.intersection(mobo_types)
        if not allowed_types:
            return None
        qs = RAM.objects.select_related("base").filter(
            price__isnull=False,
            modules_count=2,
            total_capacity__gte=target_ram_gb,
            base__type__in=allowed_types,
            total_capacity__lte=mobo.max_ram_capacity,
        )
        if cpu.max_internal_memory_gb:
            qs = qs.filter(total_capacity__lte=cpu.max_internal_memory_gb)

        preferred = qs.filter(base__type="DDR5")
        if preferred.exists():
            qs = preferred

        return qs.order_by("price", "total_capacity").first()

    @staticmethod
    def _pick_storage(mobo: Motherboard, pcie_gen: int, target_storage_gb: int) -> Optional[Storage]:
        qs = Storage.objects.select_related("connector").filter(
            price__isnull=False,
            capacity_gb__gte=target_storage_gb,
            connector__category="M.2 PCIe",
            connector__version=pcie_gen,
        )

        return qs.order_by("price", "capacity_gb").first()

    @staticmethod
    def _pick_psu_and_case(
        cpu: CPU,
        gpu: GPU,
        mobo: Motherboard,
    ) -> Tuple[Optional[PSU], Optional[Case]]:
        psu_candidates = PSUService.get_compatible_psus(
            data={"gpu": gpu.id, "cpu": cpu.id, "mobo": mobo.id}
        ).filter(price__isnull=False)

        for psu in psu_candidates.order_by("price"):
            case_qs = CaseService.get_compatible_cases(
                data={"mobo": mobo.id, "psu": psu.id, "gpu": gpu.id}
            ).filter(price__isnull=False)

            case = case_qs.order_by("price").first()
            if case:
                return psu, case

        return None, None
