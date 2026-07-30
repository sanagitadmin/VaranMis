from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.utils import timezone

from .models import (
    MaterialConsumption,
    ProductGroup,
    ProductionLine,
    ProductionReport,
    RawMaterial,
    WasteEntry,
    WasteType,
)


class DateInput(forms.DateInput):
    input_type = "date"


class TimeInput(forms.TimeInput):
    input_type = "time"


class GroupedSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            instance = getattr(value, "instance", None)
            group_id = getattr(instance, "group_id", None)
            if group_id:
                option["attrs"]["data-group"] = str(group_id)
        return option


class ProductionReportForm(forms.ModelForm):
    product_group = forms.ModelChoiceField(
        label="گروه محصول",
        queryset=ProductGroup.objects.all(),
        required=True,
    )

    class Meta:
        model = ProductionReport
        fields = [
            "product_group",
            "report_date",
            "shift",
            "operator",
            "crew_count",
            "line",
            "product",
            "total_production",
            "useful_production",
            "notes",
        ]
        widgets = {
            "report_date": DateInput(),
            "line": GroupedSelect(attrs={"data-cascade": "line"}),
            "product": GroupedSelect(attrs={"data-cascade": "product"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["product_group"].initial = self.instance.product.group_id

    def clean(self):
        cleaned = super().clean()
        group = cleaned.get("product_group")
        line = cleaned.get("line")
        product = cleaned.get("product")
        report_date = cleaned.get("report_date")
        shift = cleaned.get("shift")
        if group and line and line.group_id != group.id:
            self.add_error("line", "خط تولید باید متعلق به گروه محصول انتخاب‌شده باشد.")
        if group and product and product.group_id != group.id:
            self.add_error("product", "محصول باید متعلق به گروه محصول انتخاب‌شده باشد.")
        if report_date and report_date > timezone.localdate():
            self.add_error("report_date", "تاریخ گزارش نمی‌تواند آینده باشد.")
        if report_date and shift and line:
            exists = ProductionReport.objects.filter(
                report_date=report_date,
                shift=shift,
                line=line,
            )
            if self.instance and self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise ValidationError("برای این تاریخ، خط و شیفت قبلاً گزارش ثبت شده است؛ هر خط در هر شیفت روزانه فقط یک آمار دارد.")
        return cleaned


class GroupAwareInlineFormSet(BaseInlineFormSet):
    group = None

    def __init__(self, *args, group=None, **kwargs):
        self.group = group
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.group:
            return
        for form in self.forms:
            if not getattr(form, "cleaned_data", None) or form.cleaned_data.get("DELETE"):
                continue
            item = form.cleaned_data.get("material") or form.cleaned_data.get("waste_type")
            if item and item.group_id != self.group.id:
                raise ValidationError("مواد اولیه و ضایعات باید متعلق به گروه محصول انتخاب‌شده باشند.")


MaterialConsumptionFormSet = inlineformset_factory(
    ProductionReport,
    MaterialConsumption,
    fields=("material", "quantity"),
    formset=GroupAwareInlineFormSet,
    extra=1,
    can_delete=True,
    widgets={"material": GroupedSelect(attrs={"data-cascade": "material"})},
)

WasteEntryFormSet = inlineformset_factory(
    ProductionReport,
    WasteEntry,
    fields=("waste_type", "quantity"),
    formset=GroupAwareInlineFormSet,
    extra=1,
    can_delete=True,
    widgets={"waste_type": GroupedSelect(attrs={"data-cascade": "waste"})},
)
