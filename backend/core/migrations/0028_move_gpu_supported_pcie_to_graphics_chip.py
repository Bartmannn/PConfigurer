from django.db import migrations, models
import django.db.models.deletion


def copy_gpu_supported_pcie(apps, schema_editor):
    GPU = apps.get_model("core", "GPU")

    for gpu in GPU.objects.select_related("graphics_chip").all():
        if not gpu.graphics_chip_id:
            continue
        if gpu.supported_pcie_id and not gpu.graphics_chip.supported_pcie_id:
            gpu.graphics_chip.supported_pcie_id = gpu.supported_pcie_id
            gpu.graphics_chip.save(update_fields=["supported_pcie"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_remove_cooler_socket_compat_gpu_supported_pcie_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connector",
            name="category",
            field=models.CharField(choices=[("PCIe", "PCIe"), ("M.2 PCIe", "M.2 PCIe"), ("M.2 SATA", "M.2 SATA"), ("SATA", "SATA"), ("USB", "USB"), ("HDMI", "HDMI"), ("DisplayPort", "DisplayPort"), ("DVI", "DVI"), ("VGA", "VGA"), ("USB-C", "USB-C"), ("Fan", "Fan"), ("ATX Power", "ATX Power"), ("CPU Power", "CPU Power"), ("PCIe Power", "PCIe Power"), ("SATA Power", "SATA Power"), ("Molex", "Moelx"), ("Audio", "Audio")], max_length=20),
        ),
        migrations.AddField(
            model_name="graphicschip",
            name="supported_pcie",
            field=models.ForeignKey(blank=True, limit_choices_to={"category": "PCIe"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="graphics_chips_supported_pcie", to="core.connector"),
        ),
        migrations.RunPython(copy_gpu_supported_pcie, reverse_code=noop_reverse),
        migrations.RemoveField(
            model_name="gpu",
            name="supported_pcie",
        ),
    ]
