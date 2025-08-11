from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet

from ..models import (
    LancamentoContabil,
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    RateioLancamentoItemProjeto,
)

TOL = Decimal("0.00")


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


class ValorField(forms.DecimalField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, str):
            value = value.replace(".", "").replace(",", ".")
        try:
            return super().to_python(value)
        except InvalidOperation:
            raise ValidationError("Informe um número válido.")


class LancamentoItemForm(forms.ModelForm):
    valor = ValorField(max_digits=18, decimal_places=2, widget=forms.TextInput(attrs={"class": "form-control"}))

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
            "tipo_dc": forms.Select(attrs={"class": "form-select"}),
            "historico": forms.Select(attrs={"class": "form-select"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class LancamentoItemBaseFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_d = Decimal("0.00")
        total_c = Decimal("0.00")
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            cd = form.cleaned_data
            if cd.get("DELETE"):
                continue
            valor = cd.get("valor") or Decimal("0.00")
            tipo = cd.get("tipo_dc")
            if tipo == "D":
                total_d += valor
            elif tipo == "C":
                total_c += valor
        if (total_d - total_c).quantize(TOL) != Decimal("0.00"):
            raise ValidationError("Débitos e créditos não estão balanceados.")


LancamentoItemFormSet = inlineformset_factory(
    LancamentoContabil,
    LancamentoItem,
    form=LancamentoItemForm,
    formset=LancamentoItemBaseFormSet,
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

