from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import (
    MaterialConsumption,
    Operator,
    Product,
    ProductGroup,
    ProductionLine,
    ProductionReport,
    RawMaterial,
    Shift,
    WasteEntry,
    WasteType,
)
from .permissions import ROLE_REGISTRAR, ROLE_VIEWER


class ProductionReportTests(TestCase):
    def setUp(self):
        self.group = ProductGroup.objects.create(name="هاتواش")
        self.product = Product.objects.create(group=self.group, name="هاتواش شفاف")
        self.line = ProductionLine.objects.create(group=self.group, name="خط هاتواش")
        self.shift = Shift.objects.create(name="صبح", starts_at="07:00", ends_at="15:00")
        self.operator = Operator.objects.create(full_name="اپراتور تست", personnel_code="T-001")
        self.material = RawMaterial.objects.create(group=self.group, name="پرک")
        self.waste_type = WasteType.objects.create(
            group=self.group,
            name="ضایعات رول",
            category=WasteType.REUSABLE,
        )
        User = get_user_model()
        self.registrar_group = Group.objects.create(name=ROLE_REGISTRAR)
        self.viewer_group = Group.objects.create(name=ROLE_VIEWER)
        self.registrar = User.objects.create_user(username="registrar", password="test-pass")
        self.registrar.groups.add(self.registrar_group)
        self.viewer = User.objects.create_user(username="viewer", password="test-pass")
        self.viewer.groups.add(self.viewer_group)

    def registrar_client(self):
        client = Client()
        client.force_login(self.registrar)
        return client

    def viewer_client(self):
        client = Client()
        client.force_login(self.viewer)
        return client

    def report_payload(self, **overrides):
        data = {
            "report_date": "2026-07-30",
            "product_group": self.group.id,
            "shift": self.shift.id,
            "operator": self.operator.id,
            "crew_count": "8",
            "line": self.line.id,
            "product": self.product.id,
            "total_production": "1000",
            "useful_production": "920",
            "notes": "",
            "materials-TOTAL_FORMS": "3",
            "materials-INITIAL_FORMS": "0",
            "materials-MIN_NUM_FORMS": "0",
            "materials-MAX_NUM_FORMS": "1000",
            "materials-0-material": self.material.id,
            "materials-0-quantity": "1000",
            "materials-1-material": "",
            "materials-1-quantity": "",
            "materials-2-material": "",
            "materials-2-quantity": "",
            "wastes-TOTAL_FORMS": "3",
            "wastes-INITIAL_FORMS": "0",
            "wastes-MIN_NUM_FORMS": "0",
            "wastes-MAX_NUM_FORMS": "1000",
            "wastes-0-waste_type": self.waste_type.id,
            "wastes-0-quantity": "80",
            "wastes-1-waste_type": "",
            "wastes-1-quantity": "",
            "wastes-2-waste_type": "",
            "wastes-2-quantity": "",
        }
        data.update(overrides)
        return data

    def test_report_metrics(self):
        report = ProductionReport.objects.create(
            report_date="2026-07-30",
            shift=self.shift,
            operator=self.operator,
            crew_count=8,
            line=self.line,
            product=self.product,
            total_production=1000,
            useful_production=920,
        )
        WasteEntry.objects.create(report=report, waste_type=self.waste_type, quantity=80)

        self.assertEqual(report.yield_percent, 92)
        self.assertEqual(report.waste_percent, 8)
        self.assertEqual(report.useful_per_person, 115)

    def test_create_report_with_material_and_waste(self):
        client = self.registrar_client()
        response = client.post(
            reverse("production:report_create"),
            self.report_payload(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProductionReport.objects.count(), 1)
        self.assertEqual(MaterialConsumption.objects.count(), 1)
        self.assertEqual(WasteEntry.objects.count(), 1)

    def test_rejects_materials_greater_than_total_production(self):
        client = self.registrar_client()
        response = client.post(
            reverse("production:report_create"),
            self.report_payload(**{"materials-0-quantity": "1100"}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مجموع مصرف مواد اولیه نمی‌تواند از تولید کل بیشتر باشد")
        self.assertEqual(ProductionReport.objects.count(), 0)

    def test_rejects_useful_plus_waste_greater_than_total(self):
        client = self.registrar_client()
        response = client.post(
            reverse("production:report_create"),
            self.report_payload(useful_production="950", **{"wastes-0-quantity": "80"}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "جمع تولید مفید و ضایعات نمی‌تواند از تولید کل بیشتر باشد")
        self.assertEqual(ProductionReport.objects.count(), 0)

    def test_allows_useful_plus_waste_less_than_total(self):
        client = self.registrar_client()
        response = client.post(
            reverse("production:report_create"),
            self.report_payload(useful_production="900", **{"wastes-0-quantity": "80"}),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProductionReport.objects.count(), 1)

    def test_create_form_starts_with_one_inline_row(self):
        client = self.registrar_client()
        response = client.get(reverse("production:report_create"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["material_formset"].total_form_count(), 1)
        self.assertEqual(response.context["waste_formset"].total_form_count(), 1)

    def test_rejects_zero_quantity_material(self):
        client = self.registrar_client()
        response = client.post(
            reverse("production:report_create"),
            self.report_payload(**{"materials-0-quantity": "0"}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductionReport.objects.count(), 0)

    def test_management_report_pages_and_pdfs_load(self):
        client = self.viewer_client()
        for url in [
            reverse("production:dashboard"),
            reverse("production:reports_hub"),
            reverse("production:executive_report"),
            reverse("production:operations_report"),
            reverse("production:planning_report"),
            reverse("production:sales_report"),
            reverse("production:daily_report"),
            reverse("production:comparison_report"),
            reverse("production:report_list_pdf"),
            reverse("production:report_list_excel"),
            reverse("production:dashboard_pdf"),
            reverse("production:dashboard_excel"),
            reverse("production:daily_report_pdf"),
            reverse("production:daily_report_excel"),
            reverse("production:comparison_report_pdf"),
            reverse("production:comparison_report_excel"),
            reverse("production:executive_report_pdf"),
            reverse("production:executive_report_excel"),
            reverse("production:operations_report_pdf"),
            reverse("production:operations_report_excel"),
            reverse("production:planning_report_pdf"),
            reverse("production:planning_report_excel"),
            reverse("production:sales_report_pdf"),
            reverse("production:sales_report_excel"),
        ]:
            response = client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_report_detail_has_pdf_and_excel(self):
        report = ProductionReport.objects.create(
            report_date="2026-07-29",
            shift=self.shift,
            operator=self.operator,
            crew_count=8,
            line=self.line,
            product=self.product,
            total_production=1000,
            useful_production=920,
        )
        MaterialConsumption.objects.create(report=report, material=self.material, quantity=1000)
        WasteEntry.objects.create(report=report, waste_type=self.waste_type, quantity=80)
        client = self.viewer_client()

        detail = client.get(reverse("production:report_detail", args=[report.pk]))
        pdf = client.get(reverse("production:report_detail_pdf", args=[report.pk]))
        excel = client.get(reverse("production:report_detail_excel", args=[report.pk]))

        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, self.group.name)
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertEqual(
            excel["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_rejects_second_report_for_same_date_line_and_shift(self):
        ProductionReport.objects.create(
            report_date="2026-07-30",
            shift=self.shift,
            operator=self.operator,
            crew_count=8,
            line=self.line,
            product=self.product,
            total_production=1000,
            useful_production=920,
        )
        other_product = Product.objects.create(group=self.group, name="محصول دوم")
        client = self.registrar_client()

        response = client.post(
            reverse("production:report_create"),
            self.report_payload(product=other_product.id),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "برای این تاریخ، خط و شیفت قبلاً گزارش ثبت شده است")
        self.assertEqual(ProductionReport.objects.count(), 1)

    def test_dashboard_does_not_show_report_count(self):
        response = self.viewer_client().get(reverse("production:dashboard"))

        self.assertNotContains(response, "تعداد گزارش")

    def test_viewer_cannot_create_report(self):
        client = self.viewer_client()
        response = client.get(reverse("production:report_create"))

        self.assertEqual(response.status_code, 302)
