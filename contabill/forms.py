from django import forms

from .models import (
    ContaContabil,
    CentroCusto,
    GrupoEmpresarial,
    Filial,
    Projeto,
    Moeda,
    HistoricoPadrao,
    Periodo,
)


class ContaContabilForm(forms.ModelForm):
    codigo = forms.CharField(
        help_text="Ex: 1, 1.01, 1.01.02, 1.01.02.003, 1.01.02.003.0001",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = ContaContabil
        fields = [
            "codigo",
            "descricao",
            "tipo",
            "natureza",
            "ordem",
            "conta_pai",
            "classificacao",
            "status",
        ]
        widgets = {
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "natureza": forms.Select(attrs={"class": "form-select"}),
            "ordem": forms.NumberInput(attrs={"class": "form-control"}),
            "conta_pai": forms.Select(attrs={"class": "form-select"}),
            "classificacao": forms.Select(attrs={"class": "form-select"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CentroCustoForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = ["codigo", "descricao", "tipo", "centro_custo_pai", "status"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "centro_custo_pai": forms.Select(attrs={"class": "form-select"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class GrupoEmpresarialForm(forms.ModelForm):
    class Meta:
        model = GrupoEmpresarial
        fields = ["nome", "descricao", "status"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class FilialForm(forms.ModelForm):
    class Meta:
        model = Filial
        fields = ["empresa", "codigo", "descricao", "status"]
        widgets = {
            "empresa": forms.Select(attrs={"class": "form-select"}),
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ["codigo", "descricao", "data_inicio", "data_fim", "status"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "data_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "data_fim": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MoedaForm(forms.ModelForm):
    class Meta:
        model = Moeda
        fields = ["codigo", "descricao", "simbolo", "status"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "simbolo": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class HistoricoPadraoForm(forms.ModelForm):
    class Meta:
        model = HistoricoPadrao
        fields = ["descricao", "tipo", "status"]
        widgets = {
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = [
            "codigo",
            "data_inicio",
            "data_fim",
            "empresa",
            "status",
            "bloqueio_lancamento",
            "observacao",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "data_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "data_fim": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "empresa": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "bloqueio_lancamento": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "observacao": forms.TextInput(attrs={"class": "form-control"}),
        }

