from django.db import migrations, models


def migrate_gpu_chip_fields(apps, schema_editor):
    GraphicsChip = apps.get_model("core", "GraphicsChip")
    GPU = apps.get_model("core", "GPU")

    vendor_choices = {"NVIDIA", "AMD", "Intel"}

    for chip in GraphicsChip.objects.select_related("manufacturer").all():
        if not chip.marketing_name and chip.name:
            chip.marketing_name = chip.name

        if not chip.vendor and chip.manufacturer_id:
            vendor_name = chip.manufacturer.name
            chip.vendor = vendor_name if vendor_name in vendor_choices else None

        if chip.supported_pcie_id:
            pcie = chip.supported_pcie
            if chip.pcie_max_gen is None and pcie.version is not None:
                chip.pcie_max_gen = int(pcie.version)
            if pcie.lanes:
                chip.pcie_max_width = pcie.lanes

        chip.save()

    for gpu in GPU.objects.select_related("graphics_chip").all():
        chip = gpu.graphics_chip
        if not chip:
            continue
        if gpu.vram_size_gb is None and chip.memory_size_gb is not None:
            gpu.vram_size_gb = chip.memory_size_gb
        if gpu.base_clock_mhz is None and chip.base_clock_mhz is not None:
            gpu.base_clock_mhz = chip.base_clock_mhz
        if gpu.boost_clock_mhz is None and chip.boost_clock_mhz is not None:
            gpu.boost_clock_mhz = chip.boost_clock_mhz
        if gpu.tdp is None and chip.total_graphics_power_w is not None:
            gpu.tdp = chip.total_graphics_power_w
        if gpu.recommended_system_power_w is None and chip.recommended_system_power_w is not None:
            gpu.recommended_system_power_w = chip.recommended_system_power_w
        gpu.save()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0028_move_gpu_supported_pcie_to_graphics_chip"),
    ]

    operations = [
        migrations.AddField(
            model_name="graphicschip",
            name="vendor",
            field=models.CharField(blank=True, choices=[("NVIDIA", "NVIDIA"), ("AMD", "AMD"), ("Intel", "Intel")], max_length=16, null=True),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="marketing_name",
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="architecture",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="release_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="pcie_max_gen",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="pcie_max_width",
            field=models.PositiveSmallIntegerField(default=16),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="ray_tracing_gen",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="upscaling_technology",
            field=models.CharField(blank=True, choices=[("DLSS", "DLSS"), ("FSR", "FSR"), ("None", "None")], default="None", max_length=8),
        ),
        migrations.AlterField(
            model_name="graphicschip",
            name="memory_bus_width",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name="gpu",
            old_name="name",
            new_name="model_name",
        ),
        migrations.AddField(
            model_name="gpu",
            name="vram_size_gb",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gpu",
            name="base_clock_mhz",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gpu",
            name="boost_clock_mhz",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gpu",
            name="tdp",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gpu",
            name="recommended_system_power_w",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gpu",
            name="slot_width",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name="gpu",
            name="outputs",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_gpu_chip_fields, reverse_code=noop_reverse),
        migrations.RemoveField(
            model_name="graphicschip",
            name="name",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="manufacturer",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="base_clock_mhz",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="boost_clock_mhz",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="memory_size_gb",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="total_graphics_power_w",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="recommended_system_power_w",
        ),
        migrations.RemoveField(
            model_name="graphicschip",
            name="supported_pcie",
        ),
        migrations.RemoveField(
            model_name="gpu",
            name="width_mm",
        ),
        migrations.RemoveField(
            model_name="gpu",
            name="height_mm",
        ),
    ]
