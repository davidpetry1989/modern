from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ..forms.lancamentos import LancamentoContabilForm, LancamentoItemFormSet
from ..models import LancamentoContabil
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
        if self.request.POST:
            ctx["itens_formset"] = LancamentoItemFormSet(self.request.POST, instance=self.object)
        else:
            ctx["itens_formset"] = LancamentoItemFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context["itens_formset"]
        if not itens_formset.is_valid():
            return self.form_invalid(form)
        with transaction.atomic():
            self.object = form.save()
            itens_formset.instance = self.object
            itens_formset.save()
            try:
                self.object.validar()
            except ValidationError as exc:
                form.add_error(None, exc)
                transaction.set_rollback(True)
                return self.form_invalid(form)
            self.object.validar()
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

