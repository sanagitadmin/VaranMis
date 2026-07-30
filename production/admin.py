from django.contrib import admin

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


class MaterialConsumptionInline(admin.TabularInline):
    model = MaterialConsumption
    extra = 1


class WasteEntryInline(admin.TabularInline):
    model = WasteEntry
    extra = 1


@admin.register(ProductionReport)
class ProductionReportAdmin(admin.ModelAdmin):
    list_display = (
        "report_date",
        "shift",
        "operator",
        "crew_count",
        "line",
        "product",
        "total_production",
        "useful_production",
        "yield_percent",
    )
    list_filter = ("report_date", "shift", "line", "product__group")
    search_fields = ("operator__full_name", "line__name", "product__name")
    inlines = [MaterialConsumptionInline, WasteEntryInline]


admin.site.register(ProductGroup)
admin.site.register(Product)
@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "code", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("name", "code")


admin.site.register(Shift)
admin.site.register(Operator)


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "unit", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("name",)


@admin.register(WasteType)
class WasteTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "category", "is_active")
    list_filter = ("group", "category", "is_active")
    search_fields = ("name",)
