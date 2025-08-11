from django import forms
from .models import Empresa, Parceiro
import re


def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r"\D", "", cnpj)
    if len(cnpj) != 14 or cnpj in {c * 14 for c in "0123456789"}:
        return False
    def calc_digit(digits):
        s = sum(int(d) * w for d, w in zip(digits, [5,4,3,2,9,8,7,6,5,4,3,2]))
        r = s % 11
        return '0' if r < 2 else str(11 - r)
    dv1 = calc_digit(cnpj[:12])
    dv2 = calc_digit(cnpj[:12] + dv1)
    return cnpj[-2:] == dv1 + dv2


class EmpresaForm(forms.ModelForm):
    cnpj = forms.CharField(help_text="Apenas números", widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = Empresa
        fields = [
            "razao_social", "nome_fantasia", "cnpj", "ie", "im",
            "endereco", "numero", "complemento", "bairro", "cidade", "estado", "cep",
            "telefone", "email", "site", "ativo",
        ]
        widgets = {
            field: forms.TextInput(attrs={"class": "form-control"})
            for field in [
                "razao_social", "nome_fantasia", "cnpj", "ie", "im", "endereco",
                "numero", "complemento", "bairro", "cidade", "cep", "telefone", "email", "site"
            ]
        }
        widgets.update({"estado": forms.Select(attrs={"class": "form-select"}), "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"})})

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj", "")
        if not validar_cnpj(cnpj):
            raise forms.ValidationError("CNPJ inválido")
        return re.sub(r"\D", "", cnpj)


class ParceiroForm(EmpresaForm):
    class Meta(EmpresaForm.Meta):
        model = Parceiro
        fields = EmpresaForm.Meta.fields + [
            "is_cliente", "is_fornecedor", "is_transportadora", "is_contador"
        ]
        widgets = EmpresaForm.Meta.widgets.copy()
        widgets.update({
            "is_cliente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_fornecedor": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_transportadora": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_contador": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        })
