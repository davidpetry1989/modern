from django import forms
from .models import LayoutImportacao


class LayoutForm(forms.ModelForm):
    class Meta:
        model = LayoutImportacao
        fields = [
            "nome",
            "origem_sistema",
            "descricao",
            "tipo_arquivo",
            "delimitador",
            "ativo",
        ]


TARGET_CHOICES = [
    ("contas", "Conta Contábil"),
    ("centros", "Centro de Custo"),
    ("empresas", "Empresa"),
    ("filiais", "Filial"),
    ("projetos", "Projeto"),
    ("moedas", "Moeda"),
    ("historicos", "Histórico Padrão"),
    ("parceiros", "Parceiro de Negócio"),
]


class LayoutSelectForm(forms.Form):
    layout = forms.ModelChoiceField(
        queryset=LayoutImportacao.objects.filter(ativo=True), label="Layout"
    )
    target = forms.ChoiceField(choices=TARGET_CHOICES, label="Tipo de De/Para")
    arquivo = forms.FileField(label="Arquivo")


class PreviewForm(forms.Form):
    linhas = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput)    