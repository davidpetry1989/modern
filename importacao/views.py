import csv
from io import TextIOWrapper
from typing import Dict, List

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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

from .forms import LayoutForm, LayoutSelectForm, PreviewForm, TARGET_CHOICES
from .models import LayoutImportacao, DePara
from .services import bulk_upsert, resolver

from contabill.models import (
    ContaContabil,
    CentroCusto,
    Filial,
    Projeto,
    Moeda,
    HistoricoPadrao,
)
from cadastros.models import Empresa, Parceiro

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
        messages.success(self.request, "Layout criado com sucesso")
        return super().form_valid(form)


class LayoutUpdateView(LoginRequiredMixin, UpdateView):
    model = LayoutImportacao
    form_class = LayoutForm
    template_name = "importacao/layout_form.html"
    success_url = reverse_lazy("importacao:layout_list")

    def form_valid(self, form):
        messages.success(self.request, "Layout atualizado com sucesso")
        return super().form_valid(form)


class LayoutSelectView(LoginRequiredMixin, FormView):
    template_name = "importacao/wizard_step1.html"
    form_class = LayoutSelectForm
    success_url = reverse_lazy("importacao:wizard_preview")

    def form_valid(self, form):
        layout = form.cleaned_data["layout"]
        target = form.cleaned_data["target"]
        arquivo = form.cleaned_data["arquivo"]
        tipo = layout.tipo_arquivo
        rows: List[Dict] = []
        if tipo == "csv":
            data = TextIOWrapper(arquivo.file, encoding="utf-8")
            reader = csv.DictReader(data, delimiter=layout.delimitador)
            for i, row in enumerate(reader):
                if i >= 50:
                    break
                rows.append(row)
        else:
            messages.error(self.request, "Tipo de arquivo não suportado neste exemplo")
            return redirect("importacao:wizard")
        self.request.session["importacao_data"] = {
            "layout_id": layout.id,
            "target": target,
            "rows": rows,
        }
        return super().form_valid(form)


class PreviewMapView(LoginRequiredMixin, FormView):
    template_name = "importacao/wizard_step2.html"
    form_class = PreviewForm
    success_url = reverse_lazy("importacao:wizard_apply")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        data = self.request.session.get("importacao_data")
        if not data:
            return ctx
        layout_id = data["layout_id"]
        target_key = data["target"]
        model = TARGET_MODEL_MAP[target_key]
        rows = data["rows"]
        parsed = []
        for row in rows:
            code_ext = row.get("codigo_externo") or row.get("codigo") or ""
            desc_ext = row.get("descricao_externa") or row.get("descricao") or ""
            dest_code = row.get("destino") or row.get("codigo_destino") or row.get("codigo_interno")
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
        ctx["rows"] = parsed
        indices = [str(i) for i in range(len(parsed)) if parsed[i]["target_id"]]
        ctx["form"].fields["linhas"].choices = [(i, i) for i in indices]
        ctx["layout"] = LayoutImportacao.objects.get(id=layout_id)
        ctx["target_label"] = dict(TARGET_CHOICES)[target_key]
        ctx["target"] = target_key
        return ctx

    def form_valid(self, form):
        data = self.request.session.get("importacao_data")
        if not data:
            messages.error(self.request, "Sessão expirada")
            return redirect("importacao:wizard")
        selected = form.cleaned_data["linhas"]
        data["selected"] = [int(i) for i in selected]
        self.request.session["importacao_data"] = data
        return super().form_valid(form)


class ApplyView(LoginRequiredMixin, TemplateView):
    template_name = "importacao/wizard_step3.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        data = self.request.session.get("importacao_data")
        if not data:
            return ctx
        layout_id = data["layout_id"]
        target_key = data["target"]
        model = TARGET_MODEL_MAP[target_key]
        rows = data["rows"]
        selected = data.get("selected", [])
        to_apply = [rows[i] for i in selected]
        items = []
        for row in to_apply:
            code_ext = row.get("codigo_externo") or row.get("codigo") or ""
            desc_ext = row.get("descricao_externa") or row.get("descricao") or ""
            dest_code = row.get("destino") or row.get("codigo_destino") or row.get("codigo_interno")
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
        # limpar sessão
        if "importacao_data" in self.request.session:
            del self.request.session["importacao_data"]
        return ctx


class DeParaListView(LoginRequiredMixin, ListView):
    template_name = "importacao/depara_list.html"
    context_object_name = "itens"
    paginate_by = 50

    def get_queryset(self):
        target = self.kwargs["target"]
        model = TARGET_MODEL_MAP[target]
        ct = model
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
        return proxy.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["target"] = self.kwargs["target"]
        ctx["target_label"] = dict(TARGET_CHOICES)[self.kwargs["target"]]
        return ctx


class SearchView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        target = self.kwargs["target"]
        model = TARGET_MODEL_MAP[target]
        q = request.GET.get("q", "")
        qs = model.objects.all()
        if hasattr(model, "codigo"):
            qs = qs.filter(codigo__icontains=q)
        if hasattr(model, "descricao"):
            qs = qs | model.objects.filter(descricao__icontains=q)
        if hasattr(model, "razao_social"):
            qs = qs | model.objects.filter(razao_social__icontains=q)
        results = []
        for obj in qs[:20]:
            if hasattr(obj, "codigo"):
                label = f"{obj.codigo} - {getattr(obj, 'descricao', getattr(obj, 'razao_social', ''))}"
            else:
                label = str(obj)
            results.append({"id": obj.id, "label": label})
        return JsonResponse(results, safe=False)