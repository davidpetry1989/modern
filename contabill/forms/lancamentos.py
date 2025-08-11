from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from ..models import (
    LancamentoContabil,
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    RateioLancamentoItemProjeto,
)


class LancamentoContabilForm(forms.ModelForm):
    class Meta:
        model = LancamentoContabil
        fields = [
            "data_lancamento",
            "data_competencia",
            "tipo_lancamento",
            "origem",
            "numero_documento",
            "descricao",
            "codigo_externo",
            "filial",
            "usuario",
            "status",
        ]
        widgets = {
            "data_lancamento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "data_competencia": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "tipo_lancamento": forms.Select(attrs={"class": "form-select"}),
            "origem": forms.Select(attrs={"class": "form-select"}),
            "numero_documento": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_externo": forms.TextInput(attrs={"class": "form-control"}),
            "filial": forms.Select(attrs={"class": "form-select"}),
            "usuario": forms.Select(attrs={"class": "form-select"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class LancamentoItemForm(forms.ModelForm):
    class Meta:
        model = LancamentoItem
        fields = [
            "conta_contabil",
            "filial",
            "moeda",
            "codigo_externo",
            "valor",
            "tipo_dc",
            "historico",
            "status",
        ]
        widgets = {
            "conta_contabil": forms.Select(attrs={"class": "form-select"}),
            "filial": forms.Select(attrs={"class": "form-select"}),
            "moeda": forms.Select(attrs={"class": "form-select"}),
            "codigo_externo": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "tipo_dc": forms.Select(attrs={"class": "form-select"}),
            "historico": forms.Select(attrs={"class": "form-select"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class BaseLancamentoItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_d = Decimal("0.00")
        total_c = Decimal("0.00")
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or form.cleaned_data.get("DELETE"):
                continue
            valor = form.cleaned_data.get("valor") or Decimal("0.00")
            if form.cleaned_data.get("tipo_dc") == "D":
                total_d += valor
            else:
                total_c += valor
        if total_d.quantize(Decimal("0.01")) != total_c.quantize(Decimal("0.01")):
            raise forms.ValidationError("Débitos e créditos não estão balanceados")


LancamentoItemFormSet = inlineformset_factory(
    LancamentoContabil,
    LancamentoItem,
    form=LancamentoItemForm,
    formset=BaseLancamentoItemFormSet,
    extra=1,
    can_delete=True,
)


RateioCentroCustoFormSet = inlineformset_factory(
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    fields=["centro_custo", "valor"],
    extra=1,
    can_delete=True,
)


RateioProjetoFormSet = inlineformset_factory(
    LancamentoItem,
    RateioLancamentoItemProjeto,
    fields=["projeto", "valor"],
    extra=1,
    can_delete=True,
)

