from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class ProductGroup(models.Model):
    name = models.CharField("نام گروه محصول", max_length=120, unique=True)
    description = models.TextField("توضیحات", blank=True)

    class Meta:
        verbose_name = "گروه محصول"
        verbose_name_plural = "گروه‌های محصول"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    group = models.ForeignKey(ProductGroup, verbose_name="گروه محصول", on_delete=models.PROTECT)
    name = models.CharField("نام محصول", max_length=120)
    code = models.CharField("کد محصول", max_length=40, blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["group__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="unique_product_per_group")
        ]

    def __str__(self):
        return f"{self.group} - {self.name}"


class ProductionLine(models.Model):
    group = models.ForeignKey(
        ProductGroup,
        verbose_name="گروه محصول",
        related_name="lines",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.CharField("نام خط تولید", max_length=120, unique=True)
    code = models.CharField("کد خط", max_length=40, blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "خط تولید"
        verbose_name_plural = "خطوط تولید"
        ordering = ["group__name", "name"]

    def __str__(self):
        return self.name


class Shift(models.Model):
    name = models.CharField("نام شیفت", max_length=80, unique=True)
    starts_at = models.TimeField("شروع")
    ends_at = models.TimeField("پایان")

    class Meta:
        verbose_name = "شیفت"
        verbose_name_plural = "شیفت‌ها"
        ordering = ["starts_at"]

    def __str__(self):
        return self.name


class Operator(models.Model):
    group = models.ForeignKey(
        ProductGroup,
        verbose_name="گروه محصول",
        related_name="operators",
        on_delete=models.PROTECT,
        null=True,
    )
    full_name = models.CharField("نام و نام خانوادگی", max_length=160)
    personnel_code = models.CharField("کد پرسنلی", max_length=40, blank=True, unique=True, null=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "اپراتور"
        verbose_name_plural = "اپراتورها"
        ordering = ["group__name", "full_name"]

    def __str__(self):
        return self.full_name


class RawMaterial(models.Model):
    group = models.ForeignKey(
        ProductGroup,
        verbose_name="گروه محصول",
        related_name="raw_materials",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.CharField("نام ماده اولیه", max_length=120)
    unit = models.CharField("واحد", max_length=30, default="کیلوگرم")
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "ماده اولیه"
        verbose_name_plural = "مواد اولیه"
        ordering = ["group__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="unique_raw_material_per_group")
        ]

    def __str__(self):
        return self.name


class WasteType(models.Model):
    REUSABLE = "reusable"
    SALEABLE = "saleable"
    DISPOSAL = "disposal"
    CATEGORY_CHOICES = [
        (REUSABLE, "قابل مصرف مجدد"),
        (SALEABLE, "ضایعات فروشی"),
        (DISPOSAL, "دورریز"),
    ]

    group = models.ForeignKey(
        ProductGroup,
        verbose_name="گروه محصول",
        related_name="waste_types",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.CharField("نوع ضایعات", max_length=120)
    category = models.CharField("دسته‌بندی", max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "نوع ضایعات"
        verbose_name_plural = "انواع ضایعات"
        ordering = ["group__name", "category", "name"]
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="unique_waste_type_per_group")
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ProductionReport(models.Model):
    report_date = models.DateField("تاریخ")
    shift = models.ForeignKey(Shift, verbose_name="شیفت", on_delete=models.PROTECT)
    operator = models.ForeignKey(Operator, verbose_name="اپراتور مسئول", on_delete=models.PROTECT)
    crew_count = models.PositiveIntegerField("تعداد نفرات شیفت", validators=[MinValueValidator(1)])
    line = models.ForeignKey(ProductionLine, verbose_name="خط تولید", on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name="محصول تولیدی", on_delete=models.PROTECT)
    total_production = models.DecimalField(
        "تولید کل",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    useful_production = models.DecimalField(
        "تولید مفید",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField("توضیحات", blank=True)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "گزارش تولید"
        verbose_name_plural = "گزارش‌های تولید"
        ordering = ["-report_date", "line__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["report_date", "line", "shift"],
                name="unique_report_per_date_line_shift",
            )
        ]

    def __str__(self):
        return f"{self.report_date} - {self.line} - {self.product}"

    @property
    def total_waste(self):
        return self.wastes.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def reusable_waste(self):
        return self.wastes.filter(waste_type__category=WasteType.REUSABLE).aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def saleable_waste(self):
        return self.wastes.filter(waste_type__category=WasteType.SALEABLE).aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def yield_percent(self):
        if not self.total_production:
            return 0
        return round((self.useful_production / self.total_production) * 100, 2)

    @property
    def waste_percent(self):
        if not self.total_production:
            return 0
        return round((self.total_waste / self.total_production) * 100, 2)

    @property
    def useful_per_person(self):
        if not self.crew_count:
            return 0
        return round(self.useful_production / self.crew_count, 2)

    def clean(self):
        if self.crew_count < 1:
            raise ValidationError({"crew_count": "تعداد نفرات باید بزرگ‌تر از صفر باشد."})
        if self.useful_production > self.total_production:
            raise ValidationError({"useful_production": "تولید مفید نمی‌تواند از تولید کل بیشتر باشد."})
        if self.line_id and self.product_id and self.line.group_id and self.product.group_id != self.line.group_id:
            raise ValidationError({"line": "خط تولید و محصول باید از یک گروه محصول باشند."})
        if self.line_id and self.operator_id and self.line.group_id and self.operator.group_id != self.line.group_id:
            raise ValidationError({"operator": "اپراتور باید متعلق به گروه محصول خط تولید باشد."})


class MaterialConsumption(models.Model):
    report = models.ForeignKey(
        ProductionReport,
        verbose_name="گزارش تولید",
        related_name="materials",
        on_delete=models.CASCADE,
    )
    material = models.ForeignKey(RawMaterial, verbose_name="ماده اولیه", on_delete=models.PROTECT)
    quantity = models.DecimalField(
        "مقدار مصرف",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        verbose_name = "مصرف ماده"
        verbose_name_plural = "مصرف مواد"
        constraints = [
            models.UniqueConstraint(fields=["report", "material"], name="unique_material_per_report")
        ]

    def __str__(self):
        return f"{self.material}: {self.quantity}"


class WasteEntry(models.Model):
    report = models.ForeignKey(
        ProductionReport,
        verbose_name="گزارش تولید",
        related_name="wastes",
        on_delete=models.CASCADE,
    )
    waste_type = models.ForeignKey(WasteType, verbose_name="نوع ضایعات", on_delete=models.PROTECT)
    quantity = models.DecimalField(
        "مقدار",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        verbose_name = "ضایعات"
        verbose_name_plural = "ضایعات"
        constraints = [
            models.UniqueConstraint(fields=["report", "waste_type"], name="unique_waste_per_report")
        ]

    def __str__(self):
        return f"{self.waste_type}: {self.quantity}"
