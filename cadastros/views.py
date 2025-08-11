from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Empresa, Parceiro
from .forms import EmpresaForm, ParceiroForm


class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = "cadastros/empresas/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(razao_social__icontains=q)
                | Q(nome_fantasia__icontains=q)
                | Q(cnpj__icontains=q)
                | Q(cidade__icontains=q)
                | Q(estado__icontains=q)
            )
        ativo = self.request.GET.get("ativo")
        if ativo in ["1", "0"]:
            qs = qs.filter(ativo=ativo == "1")
        return qs


class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "cadastros/empresas/form.html"
    success_url = reverse_lazy("cadastros:empresas_lista")

    def form_valid(self, form):
        messages.success(self.request, "Empresa criada com sucesso.")
        return super().form_valid(form)


class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "cadastros/empresas/form.html"
    success_url = reverse_lazy("cadastros:empresas_lista")

    def form_valid(self, form):
        messages.success(self.request, "Empresa atualizada com sucesso.")
        return super().form_valid(form)


class EmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = Empresa
    template_name = "cadastros/empresas/confirm_delete.html"
    success_url = reverse_lazy("cadastros:empresas_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Empresa excluída com sucesso.")
        return super().delete(request, *args, **kwargs)


class ParceiroListView(LoginRequiredMixin, ListView):
    model = Parceiro
    template_name = "cadastros/parceiros/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(razao_social__icontains=q)
                | Q(nome_fantasia__icontains=q)
                | Q(cnpj__icontains=q)
                | Q(cidade__icontains=q)
                | Q(estado__icontains=q)
            )
        ativo = self.request.GET.get("ativo")
        if ativo in ["1", "0"]:
            qs = qs.filter(ativo=ativo == "1")
        for param, field in [
            ("cliente", "is_cliente"),
            ("fornecedor", "is_fornecedor"),
            ("transportadora", "is_transportadora"),
            ("contador", "is_contador"),
        ]:
            value = self.request.GET.get(param)
            if value in ["1", "0"]:
                qs = qs.filter(**{field: value == "1"})
        return qs


class ParceiroCreateView(LoginRequiredMixin, CreateView):
    model = Parceiro
    form_class = ParceiroForm
    template_name = "cadastros/parceiros/form.html"
    success_url = reverse_lazy("cadastros:parceiros_lista")

    def form_valid(self, form):
        messages.success(self.request, "Parceiro criado com sucesso.")
        return super().form_valid(form)


class ParceiroUpdateView(LoginRequiredMixin, UpdateView):
    model = Parceiro
    form_class = ParceiroForm
    template_name = "cadastros/parceiros/form.html"
    success_url = reverse_lazy("cadastros:parceiros_lista")

    def form_valid(self, form):
        messages.success(self.request, "Parceiro atualizado com sucesso.")
        return super().form_valid(form)


class ParceiroDeleteView(LoginRequiredMixin, DeleteView):
    model = Parceiro
    template_name = "cadastros/parceiros/confirm_delete.html"
    success_url = reverse_lazy("cadastros:parceiros_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Parceiro excluído com sucesso.")
        return super().delete(request, *args, **kwargs)
