import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from production.models import (
    MaterialConsumption,
    Operator,
    ProductionLine,
    ProductionReport,
    RawMaterial,
    Shift,
    WasteEntry,
    WasteType,
)


class Command(BaseCommand):
    help = "Generate one year of sample production reports from database master data."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365)

    def handle(self, *args, **options):
        days = options["days"]
        lines = list(ProductionLine.objects.filter(is_active=True, group__isnull=False).select_related("group"))
        shifts = list(Shift.objects.all())
        operators = list(Operator.objects.filter(is_active=True))
        if not lines or not shifts or not operators:
            raise CommandError("Master data is incomplete. Create product groups, lines, shifts and operators first.")

        end = timezone.localdate()
        start = end - timedelta(days=days - 1)
        random.seed(1405)
        created = 0

        for offset in range(days):
            current_date = start + timedelta(days=offset)
            for line in lines:
                products = list(line.group.product_set.filter(is_active=True))
                materials = list(RawMaterial.objects.filter(group=line.group, is_active=True))
                wastes = list(WasteType.objects.filter(group=line.group, is_active=True))
                if not products or not materials or not wastes:
                    continue
                for shift in shifts:
                    if random.random() < 0.12:
                        continue
                    product = random.choice(products)
                    operator = random.choice(operators)
                    total = Decimal(random.randint(2800, 6800))
                    useful_ratio = Decimal(random.randint(86, 96)) / Decimal("100")
                    useful = (total * useful_ratio).quantize(Decimal("0.01"))
                    max_waste = total - useful
                    waste_total = (max_waste * Decimal(random.randint(35, 90)) / Decimal("100")).quantize(Decimal("0.01"))
                    material_total = (total * Decimal(random.randint(78, 98)) / Decimal("100")).quantize(Decimal("0.01"))

                    exists = ProductionReport.objects.filter(
                        report_date=current_date,
                        shift=shift,
                        line=line,
                    ).exists()
                    if exists:
                        continue

                    report = ProductionReport.objects.create(
                        report_date=current_date,
                        shift=shift,
                        line=line,
                        product=product,
                        operator=operator,
                        crew_count=random.randint(6, 14),
                        total_production=total,
                        useful_production=useful,
                        notes="",
                    )

                    selected_materials = random.sample(materials, k=min(len(materials), random.randint(1, 3)))
                    weights = [Decimal(random.randint(1, 10)) for _ in selected_materials]
                    weight_total = sum(weights)
                    for index, material in enumerate(selected_materials):
                        qty = (
                            material_total
                            if index == len(selected_materials) - 1
                            else (material_total * weights[index] / weight_total).quantize(Decimal("0.01"))
                        )
                        if qty <= 0:
                            continue
                        material_total -= qty
                        MaterialConsumption.objects.create(report=report, material=material, quantity=qty)

                    selected_wastes = random.sample(wastes, k=min(len(wastes), random.randint(1, 3)))
                    weights = [Decimal(random.randint(1, 10)) for _ in selected_wastes]
                    weight_total = sum(weights)
                    for index, waste_type in enumerate(selected_wastes):
                        qty = (
                            waste_total
                            if index == len(selected_wastes) - 1
                            else (waste_total * weights[index] / weight_total).quantize(Decimal("0.01"))
                        )
                        if qty <= 0:
                            continue
                        waste_total -= qty
                        WasteEntry.objects.create(report=report, waste_type=waste_type, quantity=qty)

                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} sample production reports."))
