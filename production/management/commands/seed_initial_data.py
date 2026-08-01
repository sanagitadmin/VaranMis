from django.core.management.base import BaseCommand

from production.models import (
    Operator,
    Product,
    ProductGroup,
    ProductionLine,
    RawMaterial,
    Shift,
    WasteType,
)


class Command(BaseCommand):
    help = "Create starter master data for production tracking."

    def handle(self, *args, **options):
        pet, _ = ProductGroup.objects.get_or_create(name="پت")
        flake, _ = ProductGroup.objects.get_or_create(name="پرک")
        hotwash, _ = ProductGroup.objects.get_or_create(name="هاتواش")
        granule, _ = ProductGroup.objects.get_or_create(name="گرانول")

        for group, names in {
            pet: ["پت شفاف", "پت رنگی"],
            flake: ["پرک سفید", "پرک رنگی"],
            hotwash: ["هاتواش شفاف", "هاتواش رنگی"],
            granule: ["گرانول درجه ۱", "گرانول درجه ۲"],
        }.items():
            for name in names:
                Product.objects.get_or_create(group=group, name=name)

        for group, name in [
            (pet, "خط پت"),
            (flake, "خط پرک"),
            (hotwash, "خط هاتواش"),
            (granule, "خط گرانول"),
        ]:
            line, _ = ProductionLine.objects.get_or_create(name=name)
            if line.group_id != group.id:
                line.group = group
                line.save(update_fields=["group"])

        Shift.objects.get_or_create(name="صبح", defaults={"starts_at": "07:00", "ends_at": "15:00"})
        Shift.objects.get_or_create(name="عصر", defaults={"starts_at": "15:00", "ends_at": "23:00"})
        Shift.objects.get_or_create(name="شب", defaults={"starts_at": "23:00", "ends_at": "07:00"})

        Operator.objects.get_or_create(
            full_name="اپراتور نمونه",
            defaults={"group": hotwash, "personnel_code": "OP-001"},
        )

        material_names = ["هاتواش", "گرانول", "پرک", "پریفورم", "ON", "OFF"]
        for group in [pet, flake, hotwash, granule]:
            for name in material_names:
                RawMaterial.objects.get_or_create(group=group, name=name)

        waste_defaults = [
            ("ضایعات رول", WasteType.REUSABLE),
            ("لیبل خشک", WasteType.SALEABLE),
            ("لیبل خیس", WasteType.SALEABLE),
            ("PP-PVC", WasteType.SALEABLE),
            ("زباله", WasteType.DISPOSAL),
        ]
        for group in [pet, flake, hotwash, granule]:
            for name, category in waste_defaults:
                WasteType.objects.get_or_create(group=group, name=name, defaults={"category": category})

        self.stdout.write(self.style.SUCCESS("Starter master data is ready."))
