from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseBadRequest

from ..forms.lancamentos import (
    LancamentoContabilForm,
    LancamentoItemForm,
    LancamentoItemFormSet,
    RateioCentroCustoFormSet,
    RateioProjetoFormSet,
)
from ..models import LancamentoContabil, LancamentoItem
from ..services.saldo import recalcular_saldos_por_periodo, recalcular_rateios_cc_projeto


class LancamentoContabilListView(LoginRequiredMixin, ListView):
    model = LancamentoContabil
    template_name = "contabill/lancamentos/lista.html"
    paginate_by = 10


class LancamentoContabilCreateView(LoginRequiredMixin, CreateView):
    model = LancamentoContabil
    form_class = LancamentoContabilForm
    template_name = "contabill/lancamentos/form.html"
    success_url = reverse_lazy("contabill:lancamentos_lista")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        base_instance = self.object if self.object else LancamentoContabil()
        ctx["itens_formset"] = LancamentoItemFormSet(instance=base_instance, prefix="itens")
        ctx["form_novo"] = LancamentoItemForm(prefix="novo", initial={"moeda": 1, "tipo_dc": "D"})
        return ctx

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
            try:
                self.object.validar()
            except ValidationError as exc:
                form.add_error(None, exc)
                transaction.set_rollback(True)
                return self.form_invalid(form)
        messages.success(self.request, "Lançamento salvo com sucesso.")
        return super().form_valid(form)


class LancamentoContabilUpdateView(LancamentoContabilCreateView, UpdateView):
    def get_object(self, queryset=None):
        return LancamentoContabil.objects.get(pk=self.kwargs["pk"])


class LancamentoContabilDeleteView(LoginRequiredMixin, DeleteView):
    model = LancamentoContabil
    template_name = "contabill/lancamentos/confirm_delete.html"
    success_url = reverse_lazy("contabill:lancamentos_lista")


class RecalcularSaldoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        filial_id = request.POST.get("filial_id")
        periodo_id = request.POST.get("periodo_id")
        recalcular_saldos_por_periodo(filial_id, periodo_id)
        recalcular_rateios_cc_projeto(filial_id, periodo_id)
        messages.success(request, "Saldos recalculados.")
        return redirect("contabill:lancamentos_lista")


class LancamentoItemCreateHX(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        lanc_id = request.POST.get("lancamento_id")
        if not lanc_id:
            return HttpResponseBadRequest("lancamento_id ausente")
        lanc = get_object_or_404(LancamentoContabil, pk=lanc_id)

        # form de inserção rápida usa prefixo "novo"
        form_novo = LancamentoItemForm(request.POST, prefix="novo")
        if form_novo.is_valid():
            item = form_novo.save(commit=False)
            item.lancamento = lanc
            item.filial = lanc.filial  # herdado do cabeçalho (não mostrar no detalhe)
            item.save()
            # (se houver validações de CC/Projeto nesta etapa, manter)

            itens_formset = LancamentoItemFormSet(instance=lanc, prefix="itens")
            form_novo = LancamentoItemForm(prefix="novo", initial={"moeda": 1, "tipo_dc": "D"})
        else:
            itens_formset = LancamentoItemFormSet(instance=lanc, prefix="itens")

        return render(
            request,
            "contabill/lancamentos/_grid_itens.html",
            {"formset": itens_formset, "form_novo": form_novo},
        )


class RateioCentroCustoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.GET.get("item"))
        formset = RateioCentroCustoFormSet(instance=item, prefix=f"cc-{item.pk}")
        return render(request, "contabill/lancamentos/_grid_cc.html", {"formset": formset, "item": item})

    def post(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.POST.get("item"))
        formset = RateioCentroCustoFormSet(request.POST, instance=item, prefix=f"cc-{item.pk}")
        if formset.is_valid():
            formset.save()
        return render(request, "contabill/lancamentos/_grid_cc.html", {"formset": formset, "item": item})


class RateioProjetoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.GET.get("item"))
        formset = RateioProjetoFormSet(instance=item, prefix=f"prj-{item.pk}")
        return render(request, "contabill/lancamentos/_grid_projeto.html", {"formset": formset, "item": item})

    def post(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.POST.get("item"))
        formset = RateioProjetoFormSet(request.POST, instance=item, prefix=f"prj-{item.pk}")
        if formset.is_valid():
            formset.save()
        return render(request, "contabill/lancamentos/_grid_projeto.html", {"formset": formset, "item": item})

