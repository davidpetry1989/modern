import csv
from io import TextIOWrapper
from typing import Dict, List

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    FormView,
    ListView,
    CreateView,
    UpdateView,
    TemplateView,
)

from .forms import (
    LayoutForm,
    LayoutSelectForm,
    PreviewForm,
    TARGET_CHOICES,
    depara_form_factory,
)
from .models import LayoutImportacao, DePara
from .services import bulk_upsert

from contabill.models import (
    ContaContabil,
    CentroCusto,
    Filial,
    Projeto,
    Moeda,
    HistoricoPadrao,
)
from cadastros.models import Empresa, Parceiro


# ------------------------------------------
# Mapeamento de "target" -> modelo destino
# ------------------------------------------
TARGET_MODEL_MAP = {
    "contas": ContaContabil,
    "centros": CentroCusto,
    "empresas": Empresa,
    "filiais": Filial,
    "projetos": Projeto,
    "moedas": Moeda,
    "historicos": HistoricoPadrao,
    "parceiros": Parceiro,
}


# ------------------------------------------
# Layouts
# ------------------------------------------
class LayoutListView(LoginRequiredMixin, ListView):
    model = LayoutImportacao
    template_name = "importacao/layout_list.html"
    context_object_name = "layouts"
    paginate_by = 20


class LayoutCreateView(LoginRequiredMixin, CreateView):
    model = LayoutImportacao
    form_class = LayoutForm
    template_name = "importacao/layout_form.html"
    success_url = reverse_lazy("importacao:layout_list")

    def form_valid(self, form):
        messages.success(self.request, "Layout criado com sucesso.")
        return super().form_valid(form)


class LayoutUpdateView(LoginRequiredMixin, UpdateView):
    model = LayoutImportacao
    form_class = LayoutForm
    template_name = "importacao/layout_form.html"
    success_url = reverse_lazy("importacao:layout_list")

    def form_valid(self, form):
        messages.success(self.request, "Layout atualizado com sucesso.")
        return super().form_valid(form)


# ------------------------------------------
# Wizard - Passo 1 (seleção de layout/arquivo)
# ------------------------------------------
class LayoutSelectView(LoginRequiredMixin, FormView):
    template_name = "importacao/wizard_step1.html"
    form_class = LayoutSelectForm
    success_url = reverse_lazy("importacao:wizard_preview")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["step"] = 1
        return ctx

    def form_valid(self, form):
        layout = form.cleaned_data["layout"]
        target = form.cleaned_data["target"]
        arquivo = form.cleaned_data["arquivo"]

        rows: List[Dict] = []

        if layout.tipo_arquivo == "csv":
            # Leitura CSV
            data = TextIOWrapper(arquivo.file, encoding="utf-8")
            reader = csv.DictReader(data, delimiter=layout.delimitador)
            for i, row in enumerate(reader):
                if i >= 50:  # limita prévia a 50 linhas
                    break
                rows.append(row)
        else:
            messages.error(self.request, "Tipo de arquivo não suportado neste exemplo.")
            return redirect("importacao:wizard")

        self.request.session["importacao_data"] = {
            "layout_id": layout.id,
            "target": target,
            "rows": rows,
        }
        return super().form_valid(form)


# ------------------------------------------
# Wizard - Passo 2 (pré-visualização)
# ------------------------------------------
class PreviewMapView(LoginRequiredMixin, FormView):
    template_name = "importacao/wizard_step2.html"
    form_class = PreviewForm
    success_url = reverse_lazy("importacao:wizard_apply")

    def _parse_rows_and_choices(self):
        """
        Constrói as linhas da prévia e retorna (rows_parsed, indices_validos)
        onde indices_validos são strings dos índices que possuem target_id.
        """
        data = self.request.session.get("importacao_data")
        if not data:
            return [], []

        target_key = data["target"]
        model = TARGET_MODEL_MAP[target_key]
        rows = data["rows"]

        parsed, indices = [], []
        for i, row in enumerate(rows):
            code_ext = row.get("codigo_externo") or row.get("codigo") or ""
            desc_ext = row.get("descricao_externa") or row.get("descricao") or ""
            dest_code = (
                row.get("destino")
                or row.get("codigo_destino")
                or row.get("codigo_interno")
            )

            target_obj = None
            if dest_code:
                try:
                    target_obj = model.objects.get(codigo=dest_code)
                except Exception:
                    target_obj = None

            target_id = target_obj.id if target_obj else None
            parsed.append(
                {
                    "codigo_externo": code_ext,
                    "descricao_externa": desc_ext,
                    "destino": target_obj,
                    "target_id": target_id,
                }
            )
            if target_id:
                indices.append(str(i))

        return parsed, indices

    # Garanta que as choices do campo "linhas" existam ANTES da validação do POST
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        _, indices = self._parse_rows_and_choices()
        form.fields["linhas"].choices = [(i, i) for i in indices]
        form.fields["linhas"].required = False
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["step"] = 2

        data = self.request.session.get("importacao_data")
        if not data:
            return ctx

        rows, indices = self._parse_rows_and_choices()
        ctx["rows"] = rows
        ctx["tem_candidatos"] = bool(indices)
        ctx["layout"] = LayoutImportacao.objects.get(id=data["layout_id"])
        ctx["target_label"] = dict(TARGET_CHOICES)[data["target"]]
        ctx["target"] = data["target"]
        return ctx

    def form_valid(self, form):
        data = self.request.session.get("importacao_data")
        if not data:
            messages.error(self.request, "Sessão expirada.")
            return redirect("importacao:wizard")

        selected = [int(i) for i in (form.cleaned_data.get("linhas") or [])]
        data["selected"] = selected
        self.request.session["importacao_data"] = data

        if not selected:
            messages.info(self.request, "Nenhuma linha selecionada. Nada a aplicar.")
        return super().form_valid(form)


# ------------------------------------------
# Wizard - Passo 3 (aplicação)
# ------------------------------------------
class ApplyView(LoginRequiredMixin, TemplateView):
    template_name = "importacao/wizard_step3.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["step"] = 3

        data = self.request.session.get("importacao_data")
        if not data:
            return ctx

        layout_id = data["layout_id"]
        target_key = data["target"]
        model = TARGET_MODEL_MAP[target_key]
        rows = data["rows"]
        selected = data.get("selected", [])

        # Constrói itens a aplicar
        items = []
        for i in selected:
            row = rows[i]
            code_ext = row.get("codigo_externo") or row.get("codigo") or ""
            desc_ext = row.get("descricao_externa") or row.get("descricao") or ""
            dest_code = (
                row.get("destino")
                or row.get("codigo_destino")
                or row.get("codigo_interno")
            )
            try:
                target_obj = model.objects.get(codigo=dest_code)
            except Exception:
                continue

            items.append(
                {
                    "codigo_externo": code_ext,
                    "descricao_externa": desc_ext,
                    "target_id": target_obj.id,
                }
            )

        created, updated = bulk_upsert(layout_id, model, items)
        ctx["created"] = created
        ctx["updated"] = updated
        ctx["ignored"] = len(selected) - created - updated
        ctx["layout"] = LayoutImportacao.objects.get(id=layout_id)
        ctx["target_label"] = dict(TARGET_CHOICES)[target_key]
        ctx["target"] = target_key

        # Limpa sessão do wizard
        if "importacao_data" in self.request.session:
            del self.request.session["importacao_data"]

        return ctx


# ------------------------------------------
# Listagem De/Para por tipo
# ------------------------------------------
class DeParaListView(LoginRequiredMixin, ListView):
    template_name = "importacao/depara_list.html"
    context_object_name = "itens"
    paginate_by = 50

    def get_queryset(self):
        target = self.kwargs["target"]
        from .models import (
            DeParaContaContabil,
            DeParaCentroCusto,
            DeParaEmpresa,
            DeParaFilial,
            DeParaProjeto,
            DeParaMoeda,
            DeParaHistoricoPadrao,
            DeParaParceiroNegocio,
        )

        proxy_map = {
            "contas": DeParaContaContabil,
            "centros": DeParaCentroCusto,
            "empresas": DeParaEmpresa,
            "filiais": DeParaFilial,
            "projetos": DeParaProjeto,
            "moedas": DeParaMoeda,
            "historicos": DeParaHistoricoPadrao,
            "parceiros": DeParaParceiroNegocio,
        }
        proxy = proxy_map[target]
        return proxy.objects.select_related("layout").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["target"] = self.kwargs["target"]
        ctx["target_label"] = dict(TARGET_CHOICES)[self.kwargs["target"]]
        return ctx


# ------------------------------------------
# CRUD De/Para (criar/editar)
# ------------------------------------------
class DeParaCreateView(LoginRequiredMixin, CreateView):
    template_name = "importacao/depara_form.html"
    model = DePara

    def dispatch(self, request, *args, **kwargs):
        self.target = kwargs["target"]
        self.target_model = TARGET_MODEL_MAP[self.target]
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return depara_form_factory(self.target_model)

    def get_success_url(self):
        return reverse("importacao:depara_list", args=[self.target])

    def form_valid(self, form):
        messages.success(self.request, "De/Para criado com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["target"] = self.target
        ctx["target_label"] = dict(TARGET_CHOICES)[self.target]
        return ctx


class DeParaUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "importacao/depara_form.html"
    model = DePara

    def dispatch(self, request, *args, **kwargs):
        self.target = kwargs["target"]
        self.target_model = TARGET_MODEL_MAP[self.target]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(self.target_model)
        return DePara.objects.filter(target_ct=ct)

    def get_form_class(self):
        return depara_form_factory(self.target_model)

    def get_success_url(self):
        return reverse("importacao:depara_list", args=[self.target])

    def form_valid(self, form):
        messages.success(self.request, "De/Para atualizado com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["target"] = self.target
        ctx["target_label"] = dict(TARGET_CHOICES)[self.target]
        return ctx


# ------------------------------------------
# Endpoint de busca para autocompletar/apoio
# ------------------------------------------
class SearchView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        target = self.kwargs["target"]
        model = TARGET_MODEL_MAP[target]
        q = (request.GET.get("q") or "").strip()

        cond = Q()
        if q:
            if hasattr(model, "codigo"):
                cond |= Q(codigo__icontains=q)
            if hasattr(model, "descricao"):
                cond |= Q(descricao__icontains=q)
            if hasattr(model, "razao_social"):
                cond |= Q(razao_social__icontains=q)

        qs = model.objects.filter(cond) if cond else model.objects.all()
        qs = qs[:20]

        results = []
        for obj in qs:
            if hasattr(obj, "codigo"):
                label_tail = getattr(obj, "descricao", getattr(obj, "razao_social", ""))
                label = f"{obj.codigo} - {label_tail}".strip(" -")
            else:
                label = str(obj)
            results.append({"id": obj.id, "label": label})
        return JsonResponse(results, safe=False)
