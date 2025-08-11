from django import forms
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from .models import LayoutImportacao, DePara


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
        labels = {
            "nome": "Nome",
            "origem_sistema": "Origem do sistema",
            "descricao": "Descrição",
            "tipo_arquivo": "Tipo de arquivo",
            "delimitador": "Delimitador",
            "ativo": "Ativo",
        }
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "origem_sistema": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_arquivo": forms.Select(attrs={"class": "form-select"}),
            "delimitador": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 5, "placeholder": ";"}
            ),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get("delimitador"):
            self.initial["delimitador"] = ";"

    def clean_delimitador(self):
        val = (self.cleaned_data.get("delimitador") or ";").strip()
        return val[:5] or ";"


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
        queryset=LayoutImportacao.objects.filter(ativo=True).order_by("nome"),
        label="Layout",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    target = forms.ChoiceField(
        choices=TARGET_CHOICES,
        label="Tipo de De/Para",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    arquivo = forms.FileField(
        label="Arquivo",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".csv,.xlsx,.xml"}
        ),
    )


# importacao/forms.py
class PreviewForm(forms.Form):
    linhas = forms.MultipleChoiceField(
        widget=forms.MultipleHiddenInput,
        required=False,   # importante
    )



def depara_form_factory(model):
    """Retorna um ModelForm estilizado para criar/editar De/Para do 'model' informado."""
    verbose = getattr(model._meta, "verbose_name", "Destino")

    class _DeParaForm(forms.ModelForm):
        # campo extra (não é do model DePara) para escolher o alvo
        target = forms.ModelChoiceField(
            queryset=model.objects.all(),
            label=verbose,
            widget=forms.Select(attrs={"class": "form-select"}),
        )

        class Meta:
            model = DePara
            # NÃO incluir 'target' aqui (não é campo do model)
            fields = ["layout", "codigo_externo", "descricao_externa", "observacao", "ativo"]
            labels = {
                "layout": "Layout",
                "codigo_externo": "Código externo",
                "descricao_externa": "Descrição externa",
                "observacao": "Observação",
                "ativo": "Ativo",
            }
            widgets = {
                "layout": forms.Select(attrs={"class": "form-select"}),
                "codigo_externo": forms.TextInput(attrs={"class": "form-control"}),
                "descricao_externa": forms.TextInput(attrs={"class": "form-control"}),
                "observacao": forms.TextInput(attrs={"class": "form-control"}),
                "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # quando editando, preencher o select com o target atual
            if self.instance.pk and self.instance.target:
                self.fields["target"].initial = self.instance.target

        def clean(self):
            cleaned = super().clean()
            layout = cleaned.get("layout")
            codigo = (cleaned.get("codigo_externo") or "").strip().lower()
            tgt = cleaned.get("target")
            if layout and codigo and tgt:
                ct = ContentType.objects.get_for_model(model)
                qs = DePara.objects.filter(layout=layout, target_ct=ct, codigo_externo=codigo)
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise ValidationError(
                        "Já existe um De/Para para este layout e código externo."
                    )
            return cleaned

        def save(self, commit=True):
            inst = super().save(commit=False)
            inst.target_ct = ContentType.objects.get_for_model(model)
            inst.target_id = self.cleaned_data["target"].pk
            inst.codigo_externo = (inst.codigo_externo or "").strip().lower()
            if commit:
                inst.save()
            return inst

    return _DeParaForm
