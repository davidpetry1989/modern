from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from urllib.parse import urlencode

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
from .forms import (
    ContaContabilForm,
    CentroCustoForm,
    GrupoEmpresarialForm,
    FilialForm,
    ProjetoForm,
    MoedaForm,
    HistoricoPadraoForm,
    PeriodoForm,
)


# --------- Conta Contábil ---------
class ContaContabilListView(LoginRequiredMixin, ListView):
    model = ContaContabil
    template_name = "contabill/contas/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        # filtros específicos
        codigo = self.request.GET.get("codigo")
        descricao = self.request.GET.get("descricao")
        if codigo:
            qs = qs.filter(codigo__icontains=codigo)
        if descricao:
            qs = qs.filter(descricao__icontains=descricao)

        # busca livre (continua valendo)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(codigo__icontains=q) | Q(descricao__icontains=q))

        # demais filtros já existentes
        filters = {
            "tipo": self.request.GET.get("tipo"),
            "natureza": self.request.GET.get("natureza"),
            "classificacao": self.request.GET.get("classificacao"),
            "status": self.request.GET.get("status"),
            "nivel": self.request.GET.get("nivel"),
        }
        for field, value in filters.items():
            if value not in (None, ""):
                qs = qs.filter(**{field: value})

        return qs

    # (opcional) preservar filtros na paginação
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring"] = urlencode(params)
        return ctx



class ContaContabilCreateView(LoginRequiredMixin, CreateView):
    model = ContaContabil
    form_class = ContaContabilForm
    template_name = "contabill/contas/form.html"
    success_url = reverse_lazy("contabill:contas_lista")

    def form_valid(self, form):
        messages.success(self.request, "Conta criada com sucesso.")
        return super().form_valid(form)


class ContaContabilUpdateView(LoginRequiredMixin, UpdateView):
    model = ContaContabil
    form_class = ContaContabilForm
    template_name = "contabill/contas/form.html"
    success_url = reverse_lazy("contabill:contas_lista")

    def form_valid(self, form):
        messages.success(self.request, "Conta atualizada com sucesso.")
        return super().form_valid(form)


class ContaContabilDeleteView(LoginRequiredMixin, DeleteView):
    model = ContaContabil
    template_name = "contabill/contas/confirm_delete.html"
    success_url = reverse_lazy("contabill:contas_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Conta excluída com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Centro de Custo ---------
class CentroCustoListView(LoginRequiredMixin, ListView):
    model = CentroCusto
    template_name = "contabill/centros/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(codigo__icontains=q) | Q(descricao__icontains=q))
        for field in ["tipo", "status", "nivel"]:
            value = self.request.GET.get(field)
            if value:
                qs = qs.filter(**{field: value})
        return qs


class CentroCustoCreateView(LoginRequiredMixin, CreateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = "contabill/centros/form.html"
    success_url = reverse_lazy("contabill:centros_lista")

    def form_valid(self, form):
        messages.success(self.request, "Centro de custo criado com sucesso.")
        return super().form_valid(form)


class CentroCustoUpdateView(LoginRequiredMixin, UpdateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = "contabill/centros/form.html"
    success_url = reverse_lazy("contabill:centros_lista")

    def form_valid(self, form):
        messages.success(self.request, "Centro de custo atualizado com sucesso.")
        return super().form_valid(form)


class CentroCustoDeleteView(LoginRequiredMixin, DeleteView):
    model = CentroCusto
    template_name = "contabill/centros/confirm_delete.html"
    success_url = reverse_lazy("contabill:centros_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Centro de custo excluído com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Grupo Empresarial ---------
class GrupoEmpresarialListView(LoginRequiredMixin, ListView):
    model = GrupoEmpresarial
    template_name = "contabill/grupos/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q)
        status = self.request.GET.get("status")
        if status in ["1", "0"]:
            qs = qs.filter(status=status == "1")
        return qs


class GrupoEmpresarialCreateView(LoginRequiredMixin, CreateView):
    model = GrupoEmpresarial
    form_class = GrupoEmpresarialForm
    template_name = "contabill/grupos/form.html"
    success_url = reverse_lazy("contabill:grupos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Grupo criado com sucesso.")
        return super().form_valid(form)


class GrupoEmpresarialUpdateView(LoginRequiredMixin, UpdateView):
    model = GrupoEmpresarial
    form_class = GrupoEmpresarialForm
    template_name = "contabill/grupos/form.html"
    success_url = reverse_lazy("contabill:grupos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Grupo atualizado com sucesso.")
        return super().form_valid(form)


class GrupoEmpresarialDeleteView(LoginRequiredMixin, DeleteView):
    model = GrupoEmpresarial
    template_name = "contabill/grupos/confirm_delete.html"
    success_url = reverse_lazy("contabill:grupos_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Grupo excluído com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Filial ---------
class FilialListView(LoginRequiredMixin, ListView):
    model = Filial
    template_name = "contabill/filiais/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(codigo__icontains=q) | Q(descricao__icontains=q))
        empresa = self.request.GET.get("empresa")
        if empresa:
            qs = qs.filter(empresa_id=empresa)
        status = self.request.GET.get("status")
        if status in ["1", "0"]:
            qs = qs.filter(status=status == "1")
        return qs


class FilialCreateView(LoginRequiredMixin, CreateView):
    model = Filial
    form_class = FilialForm
    template_name = "contabill/filiais/form.html"
    success_url = reverse_lazy("contabill:filiais_lista")

    def form_valid(self, form):
        messages.success(self.request, "Filial criada com sucesso.")
        return super().form_valid(form)


class FilialUpdateView(LoginRequiredMixin, UpdateView):
    model = Filial
    form_class = FilialForm
    template_name = "contabill/filiais/form.html"
    success_url = reverse_lazy("contabill:filiais_lista")

    def form_valid(self, form):
        messages.success(self.request, "Filial atualizada com sucesso.")
        return super().form_valid(form)


class FilialDeleteView(LoginRequiredMixin, DeleteView):
    model = Filial
    template_name = "contabill/filiais/confirm_delete.html"
    success_url = reverse_lazy("contabill:filiais_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Filial excluída com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Projeto ---------
class ProjetoListView(LoginRequiredMixin, ListView):
    model = Projeto
    template_name = "contabill/projetos/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(codigo__icontains=q) | Q(descricao__icontains=q))
        status = self.request.GET.get("status")
        if status in ["1", "0"]:
            qs = qs.filter(status=status == "1")
        inicio = self.request.GET.get("inicio")
        fim = self.request.GET.get("fim")
        if inicio:
            qs = qs.filter(data_inicio__gte=inicio)
        if fim:
            qs = qs.filter(data_fim__lte=fim)
        return qs


class ProjetoCreateView(LoginRequiredMixin, CreateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = "contabill/projetos/form.html"
    success_url = reverse_lazy("contabill:projetos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Projeto criado com sucesso.")
        return super().form_valid(form)


class ProjetoUpdateView(LoginRequiredMixin, UpdateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = "contabill/projetos/form.html"
    success_url = reverse_lazy("contabill:projetos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Projeto atualizado com sucesso.")
        return super().form_valid(form)


class ProjetoDeleteView(LoginRequiredMixin, DeleteView):
    model = Projeto
    template_name = "contabill/projetos/confirm_delete.html"
    success_url = reverse_lazy("contabill:projetos_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Projeto excluído com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Moeda ---------
class MoedaListView(LoginRequiredMixin, ListView):
    model = Moeda
    template_name = "contabill/moedas/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(codigo__icontains=q) | Q(descricao__icontains=q))
        status = self.request.GET.get("status")
        if status in ["1", "0"]:
            qs = qs.filter(status=status == "1")
        return qs


class MoedaCreateView(LoginRequiredMixin, CreateView):
    model = Moeda
    form_class = MoedaForm
    template_name = "contabill/moedas/form.html"
    success_url = reverse_lazy("contabill:moedas_lista")

    def form_valid(self, form):
        messages.success(self.request, "Moeda criada com sucesso.")
        return super().form_valid(form)


class MoedaUpdateView(LoginRequiredMixin, UpdateView):
    model = Moeda
    form_class = MoedaForm
    template_name = "contabill/moedas/form.html"
    success_url = reverse_lazy("contabill:moedas_lista")

    def form_valid(self, form):
        messages.success(self.request, "Moeda atualizada com sucesso.")
        return super().form_valid(form)


class MoedaDeleteView(LoginRequiredMixin, DeleteView):
    model = Moeda
    template_name = "contabill/moedas/confirm_delete.html"
    success_url = reverse_lazy("contabill:moedas_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Moeda excluída com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Historico Padrão ---------
class HistoricoPadraoListView(LoginRequiredMixin, ListView):
    model = HistoricoPadrao
    template_name = "contabill/historicos/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(descricao__icontains=q)
        tipo = self.request.GET.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo)
        status = self.request.GET.get("status")
        if status in ["1", "0"]:
            qs = qs.filter(status=status == "1")
        return qs


class HistoricoPadraoCreateView(LoginRequiredMixin, CreateView):
    model = HistoricoPadrao
    form_class = HistoricoPadraoForm
    template_name = "contabill/historicos/form.html"
    success_url = reverse_lazy("contabill:historicos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Histórico criado com sucesso.")
        return super().form_valid(form)


class HistoricoPadraoUpdateView(LoginRequiredMixin, UpdateView):
    model = HistoricoPadrao
    form_class = HistoricoPadraoForm
    template_name = "contabill/historicos/form.html"
    success_url = reverse_lazy("contabill:historicos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Histórico atualizado com sucesso.")
        return super().form_valid(form)


class HistoricoPadraoDeleteView(LoginRequiredMixin, DeleteView):
    model = HistoricoPadrao
    template_name = "contabill/historicos/confirm_delete.html"
    success_url = reverse_lazy("contabill:historicos_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Histórico excluído com sucesso.")
        return super().delete(request, *args, **kwargs)


# --------- Periodo ---------
class PeriodoListView(LoginRequiredMixin, ListView):
    model = Periodo
    template_name = "contabill/periodos/lista.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(codigo__icontains=q)
        empresa = self.request.GET.get("empresa")
        if empresa:
            qs = qs.filter(empresa_id=empresa)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class PeriodoCreateView(LoginRequiredMixin, CreateView):
    model = Periodo
    form_class = PeriodoForm
    template_name = "contabill/periodos/form.html"
    success_url = reverse_lazy("contabill:periodos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Período criado com sucesso.")
        return super().form_valid(form)


class PeriodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Periodo
    form_class = PeriodoForm
    template_name = "contabill/periodos/form.html"
    success_url = reverse_lazy("contabill:periodos_lista")

    def form_valid(self, form):
        messages.success(self.request, "Período atualizado com sucesso.")
        return super().form_valid(form)


class PeriodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Periodo
    template_name = "contabill/periodos/confirm_delete.html"
    success_url = reverse_lazy("contabill:periodos_lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Período excluído com sucesso.")
        return super().delete(request, *args, **kwargs)
