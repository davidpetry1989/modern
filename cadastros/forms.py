from django import forms
from .models import Empresa, Parceiro
from contabill.models import GrupoEmpresarial
import re


def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r"\D", "", cnpj or "")
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def dv(nums, pesos):
        s = sum(int(n) * p for n, p in zip(nums, pesos))
        r = s % 11
        return "0" if r < 2 else str(11 - r)

    d1 = dv(cnpj[:12], [5,4,3,2,9,8,7,6,5,4,3,2])
    d2 = dv(cnpj[:12] + d1, [6,5,4,3,2,9,8,7,6,5,4,3,2])

    return cnpj.endswith(d1 + d2)



class EmpresaForm(forms.ModelForm):
    cnpj = forms.CharField(help_text="Apenas números", widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = Empresa
        fields = [
            "razao_social", "nome_fantasia", "cnpj", "ie", "im",
            "endereco", "numero", "complemento", "bairro", "cidade", "estado", "cep",
            "telefone", "email", "site", "grupo_empresarial", "ativo",
        ]
        widgets = {
            field: forms.TextInput(attrs={"class": "form-control"})
            for field in [
                "razao_social", "nome_fantasia", "cnpj", "ie", "im", "endereco",
                "numero", "complemento", "bairro", "cidade", "cep", "telefone", "email", "site"
            ]
        }
        widgets.update({
            "estado": forms.Select(attrs={"class": "form-select"}),
            "grupo_empresarial": forms.Select(attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        })

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj", "")
        if not validar_cnpj(cnpj):
            raise forms.ValidationError("CNPJ inválido")
        return re.sub(r"\D", "", cnpj)


class ParceiroForm(EmpresaForm):
    class Meta(EmpresaForm.Meta):
        model = Parceiro
        base_fields = [f for f in EmpresaForm.Meta.fields if f != "grupo_empresarial"]
        fields = base_fields + [
            "is_cliente", "is_fornecedor", "is_transportadora", "is_contador"
        ]
        widgets = EmpresaForm.Meta.widgets.copy()
        widgets.update({
            "is_cliente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_fornecedor": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_transportadora": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_contador": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        })
