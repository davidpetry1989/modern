from decimal import Decimal

from django.db.models import Sum, Case, When

from ..models import (
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    RateioLancamentoItemProjeto,
    SaldoContaPeriodo,
    SaldoCentroCustoPeriodo,
    SaldoProjetoPeriodo,
    Periodo,
)


def _faixa_periodo(periodo):
    return periodo.data_inicio, periodo.data_fim


def recalcular_saldos_por_periodo(filial_id, periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    inicio, fim = _faixa_periodo(periodo)
    itens = LancamentoItem.objects.filter(
        lancamento__filial_id=filial_id,
        lancamento__data_competencia__range=(inicio, fim),
        lancamento__status=True,
        status=True,
    )
    movimentos = itens.values("conta_contabil_id").annotate(
        debito=Sum(Case(When(tipo_dc="D", then="valor"), default=Decimal("0.00"))),
        credito=Sum(Case(When(tipo_dc="C", then="valor"), default=Decimal("0.00"))),
    )
    for mov in movimentos:
        saldo, _ = SaldoContaPeriodo.objects.get_or_create(
            conta_contabil_id=mov["conta_contabil_id"],
            filial_id=filial_id,
            periodo_id=periodo_id,
            defaults={"saldo_inicial": Decimal("0.00")},
        )
        saldo.debito = mov["debito"] or Decimal("0.00")
        saldo.credito = mov["credito"] or Decimal("0.00")
        saldo.saldo_final = saldo.saldo_inicial + saldo.debito - saldo.credito
        saldo.save()


def recalcular_rateios_cc_projeto(filial_id, periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    inicio, fim = _faixa_periodo(periodo)
    itens = LancamentoItem.objects.filter(
        lancamento__filial_id=filial_id,
        lancamento__data_competencia__range=(inicio, fim),
        lancamento__status=True,
        status=True,
    )
    itens_ids = list(itens.values_list("id", flat=True))

    # Centro de Custo
    cc_agreg = (
        RateioLancamentoItemCentroCusto.objects.filter(lancamento_item_id__in=itens_ids)
        .values("lancamento_item__conta_contabil_id", "centro_custo_id")
        .annotate(
            debito=Sum(Case(When(lancamento_item__tipo_dc="D", then="valor"), default=Decimal("0.00"))),
            credito=Sum(Case(When(lancamento_item__tipo_dc="C", then="valor"), default=Decimal("0.00"))),
        )
    )
    for mov in cc_agreg:
        saldo_conta, _ = SaldoContaPeriodo.objects.get_or_create(
            conta_contabil_id=mov["lancamento_item__conta_contabil_id"],
            filial_id=filial_id,
            periodo_id=periodo_id,
            defaults={"saldo_inicial": Decimal("0.00")},
        )
        saldo_cc, _ = SaldoCentroCustoPeriodo.objects.get_or_create(
            saldo_conta_periodo=saldo_conta,
            centro_custo_id=mov["centro_custo_id"],
            periodo_id=periodo_id,
            defaults={}
        )
        saldo_cc.debito = mov["debito"] or Decimal("0.00")
        saldo_cc.credito = mov["credito"] or Decimal("0.00")
        saldo_cc.saldo_final = saldo_cc.saldo_inicial + saldo_cc.debito - saldo_cc.credito
        saldo_cc.save()

    # Projeto
    proj_agreg = (
        RateioLancamentoItemProjeto.objects.filter(lancamento_item_id__in=itens_ids)
        .values("lancamento_item__conta_contabil_id", "projeto_id")
        .annotate(
            debito=Sum(Case(When(lancamento_item__tipo_dc="D", then="valor"), default=Decimal("0.00"))),
            credito=Sum(Case(When(lancamento_item__tipo_dc="C", then="valor"), default=Decimal("0.00"))),
        )
    )
    for mov in proj_agreg:
        saldo_conta, _ = SaldoContaPeriodo.objects.get_or_create(
            conta_contabil_id=mov["lancamento_item__conta_contabil_id"],
            filial_id=filial_id,
            periodo_id=periodo_id,
            defaults={"saldo_inicial": Decimal("0.00")},
        )
        saldo_proj, _ = SaldoProjetoPeriodo.objects.get_or_create(
            saldo_conta_periodo=saldo_conta,
            projeto_id=mov["projeto_id"],
            periodo_id=periodo_id,
            defaults={}
        )
        saldo_proj.debito = mov["debito"] or Decimal("0.00")
        saldo_proj.credito = mov["credito"] or Decimal("0.00")
        saldo_proj.saldo_final = (
            saldo_proj.saldo_inicial + saldo_proj.debito - saldo_proj.credito
        )
        saldo_proj.save()

