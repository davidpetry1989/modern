from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone

from ..models import (
    LancamentoContabil,
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    RateioLancamentoItemProjeto,
)

TOL = Decimal("0.00")


class LancamentoContabilForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoje = timezone.localdate()
        self.initial.setdefault("data_lancamento", hoje)
        self.initial.setdefault("data_competencia", hoje)
        self.initial.setdefault("tipo_lancamento", "0")
        self.initial.setdefault("origem", "0")

    class Meta:
        model = LancamentoContabil
        fields = [
            "data_lancamento",
            "data_competencia",
            "tipo_lancamento",
            "origem",
            "numero_documento",
            "descricao",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.setdefault("moeda", 1)
        self.initial.setdefault("tipo_dc", "D")

    class Meta:
        model = LancamentoItem
        fields = ["conta_contabil", "moeda", "valor", "tipo_dc", "historico"]
        widgets = {
            "conta_contabil": forms.Select(attrs={"class": "form-select"}),
            "moeda": forms.Select(attrs={"class": "form-select"}),
            "tipo_dc": forms.Select(attrs={"class": "form-select"}),
            "historico": forms.Select(attrs={"class": "form-select"}),
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
    extra=0,
    can_delete=True,
)


class RateioCentroCustoBaseFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = Decimal("0.00")
        count = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            cd = form.cleaned_data
            if cd.get("DELETE"):
                continue
            valor = cd.get("valor") or Decimal("0.00")
            total += valor
            count += 1
        item = self.instance
        valor_item = getattr(item, "valor", Decimal("0.00"))
        if item.conta_contabil.classificacao in {"R", "D", "C"}:
            if count == 0:
                raise ValidationError("CC obrigatório para contas de Receita/Despesa/Custo")
            if total.quantize(Decimal("0.01")) != valor_item.quantize(Decimal("0.01")):
                raise ValidationError("Somatório de CC não fecha com o valor do item")
        elif count and total.quantize(Decimal("0.01")) != valor_item.quantize(Decimal("0.01")):
            raise ValidationError("Somatório de CC não fecha com o valor do item")


class RateioProjetoBaseFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = Decimal("0.00")
        count = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            cd = form.cleaned_data
            if cd.get("DELETE"):
                continue
            valor = cd.get("valor") or Decimal("0.00")
            total += valor
            count += 1
        valor_item = getattr(self.instance, "valor", Decimal("0.00"))
        if count and total.quantize(Decimal("0.01")) != valor_item.quantize(Decimal("0.01")):
            raise ValidationError("Projeto não fecha com o valor do item")


RateioCentroCustoFormSet = inlineformset_factory(
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    fields=["centro_custo", "valor"],
    formset=RateioCentroCustoBaseFormSet,
    extra=1,
    can_delete=True,
)


RateioProjetoFormSet = inlineformset_factory(
    LancamentoItem,
    RateioLancamentoItemProjeto,
    fields=["projeto", "valor"],
    formset=RateioProjetoBaseFormSet,
    extra=1,
    can_delete=True,
)

