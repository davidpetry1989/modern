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
        """Permite inclusão incremental de itens.

        O balanceamento de débitos e créditos é validado no
        momento da gravação do lançamento completo, através do método
        ``LancamentoContabil.validar``. Aqui executamos apenas a limpeza
        padrão para não bloquear a adição de novas linhas enquanto o
        total de débitos e créditos ainda não estiver fechado."""

        super().clean()


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

