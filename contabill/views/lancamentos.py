from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

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
        ctx["form_novo"] = LancamentoItemForm(prefix="novo")
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


class LancamentoItemCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        lancamento = get_object_or_404(LancamentoContabil, pk=request.POST.get("lancamento_id"))
        item_form = LancamentoItemForm(request.POST, prefix="novo")
        cc_formset = RateioCentroCustoFormSet(request.POST, prefix="cc")
        proj_formset = RateioProjetoFormSet(request.POST, prefix="projeto")
        if item_form.is_valid() and cc_formset.is_valid() and proj_formset.is_valid():
            item = item_form.save(commit=False)
            item.lancamento = lancamento
            item.filial = lancamento.filial
            item.save()
            cc_formset.instance = item
            proj_formset.instance = item
            cc_formset.save()
            proj_formset.save()
            try:
                item.validar_rateios()
            except ValidationError as exc:
                item.delete()
                item_form.add_error(None, exc)
        itens_formset = LancamentoItemFormSet(instance=lancamento, prefix="itens")
        context = {"formset": itens_formset, "form_novo": item_form if item_form.errors else LancamentoItemForm(prefix="novo")}
        response = render(request, "contabill/lancamentos/_grid_itens.html", context)
        if item_form.errors or cc_formset.non_form_errors() or proj_formset.non_form_errors():
            response.status_code = 400
        return response


class RateioCentroCustoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.GET.get("item"))
        formset = RateioCentroCustoFormSet(instance=item, prefix="cc")
        return render(request, "contabill/lancamentos/_grid_cc.html", {"formset": formset, "item": item})

    def post(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.POST.get("item"))
        formset = RateioCentroCustoFormSet(request.POST, instance=item, prefix="cc")
        if formset.is_valid():
            formset.save()
        return render(request, "contabill/lancamentos/_grid_cc.html", {"formset": formset, "item": item})


class RateioProjetoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.GET.get("item"))
        formset = RateioProjetoFormSet(instance=item, prefix="projeto")
        return render(request, "contabill/lancamentos/_grid_projeto.html", {"formset": formset, "item": item})

    def post(self, request, *args, **kwargs):
        item = get_object_or_404(LancamentoItem, pk=request.POST.get("item"))
        formset = RateioProjetoFormSet(request.POST, instance=item, prefix="projeto")
        if formset.is_valid():
            formset.save()
        return render(request, "contabill/lancamentos/_grid_projeto.html", {"formset": formset, "item": item})

