from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from contabill.models import (
    ContaContabil,
    CentroCusto,
    Projeto,
    Filial,
    Moeda,
    HistoricoPadrao,
    Periodo,
    LancamentoContabil,
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    RateioLancamentoItemProjeto,
    SaldoContaPeriodo,
    SaldoCentroCustoPeriodo,
    SaldoProjetoPeriodo,
)
from contabill.tests import criar_empresa
from contabill.services.saldo import (
    recalcular_saldos_por_periodo,
    recalcular_rateios_cc_projeto,
)


class LancamentoTests(TestCase):
    def setUp(self):
        self.empresa = criar_empresa()
        self.filial = Filial.objects.create(empresa=self.empresa, codigo="001", descricao="Filial")
        self.moeda = Moeda.objects.create(codigo="BRL", descricao="Real", simbolo="R$")
        self.historico = HistoricoPadrao.objects.create(descricao="Hist", tipo="padrao")
        self.periodo = Periodo.objects.create(
            codigo="202401",
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 1, 31),
            empresa=self.empresa,
            status="A",
        )
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="123")

        self.n1 = ContaContabil(codigo="1", descricao="Ativo", tipo="S", natureza="D")
        self.n1.full_clean(); self.n1.save()
        self.n2 = ContaContabil(codigo="1.01", descricao="Circulante", tipo="S", natureza="D", conta_pai=self.n1)
        self.n2.full_clean(); self.n2.save()
        self.n3 = ContaContabil(codigo="1.01.02", descricao="Disponível", tipo="S", natureza="D", conta_pai=self.n2)
        self.n3.full_clean(); self.n3.save()
        self.n4 = ContaContabil(codigo="1.01.02.003", descricao="Caixa", tipo="S", natureza="D", conta_pai=self.n3)
        self.n4.full_clean(); self.n4.save()
        self.conta_d = ContaContabil(
            codigo="1.01.02.003.0001",
            descricao="Conta D",
            tipo="A",
            natureza="D",
            conta_pai=self.n4,
            classificacao="R",
        )
        self.conta_d.full_clean(); self.conta_d.save()
        self.conta_c = ContaContabil(
            codigo="1.01.02.003.0002",
            descricao="Conta C",
            tipo="A",
            natureza="D",
            conta_pai=self.n4,
            classificacao="R",
        )
        self.conta_c.full_clean(); self.conta_c.save()
        self.cc = CentroCusto.objects.create(codigo="CC1", descricao="CC", tipo="O")
        self.proj = Projeto.objects.create(
            codigo="P1",
            descricao="Proj",
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 12, 31),
        )

    def criar_lancamento(self):
        return LancamentoContabil.objects.create(
            data_lancamento=date(2024, 1, 5),
            data_competencia=date(2024, 1, 5),
            tipo_lancamento="0",
            origem="0",
            filial=self.filial,
            usuario=self.user,
        )

    def preparar_itens(self, lancamento, valor_debito=Decimal("100"), valor_credito=Decimal("100")):
        item_d = LancamentoItem.objects.create(
            lancamento=lancamento,
            conta_contabil=self.conta_d,
            filial=self.filial,
            moeda=self.moeda,
            valor=valor_debito,
            tipo_dc="D",
            historico=self.historico,
        )
        item_c = LancamentoItem.objects.create(
            lancamento=lancamento,
            conta_contabil=self.conta_c,
            filial=self.filial,
            moeda=self.moeda,
            valor=valor_credito,
            tipo_dc="C",
            historico=self.historico,
        )
        return item_d, item_c

    def test_lancamento_balanceado(self):
        lanc = self.criar_lancamento()
        item_d, item_c = self.preparar_itens(lanc)
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100"))
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("100"))
        try:
            lanc.validar()
        except ValidationError:
            self.fail("Lançamento balanceado não deveria falhar")

    def test_lancamento_desbalanceado(self):
        lanc = self.criar_lancamento()
        item_d, item_c = self.preparar_itens(lanc, valor_credito=Decimal("50"))
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100"))
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("50"))
        with self.assertRaises(ValidationError):
            lanc.validar()

    def test_rateio_obrigatorio(self):
        lanc = self.criar_lancamento()
        item_d, item_c = self.preparar_itens(lanc)
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("100"))
        with self.assertRaises(ValidationError):
            lanc.validar()
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100"))
        lanc.validar()  # agora deve passar

    def test_somatorio_rateios(self):
        lanc = self.criar_lancamento()
        item_d, item_c = self.preparar_itens(lanc)
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100"))
        RateioLancamentoItemProjeto.objects.create(lancamento_item=item_d, projeto=self.proj, valor=Decimal("50"))
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("100"))
        RateioLancamentoItemProjeto.objects.create(lancamento_item=item_c, projeto=self.proj, valor=Decimal("100"))
        with self.assertRaises(ValidationError):
            lanc.validar()

    def test_recalcular_saldo(self):
        lanc = self.criar_lancamento()
        item_d, item_c = self.preparar_itens(lanc)
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100"))
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("100"))
        lanc.validar()
        recalcular_saldos_por_periodo(self.filial.id, self.periodo.id)
        recalcular_rateios_cc_projeto(self.filial.id, self.periodo.id)
        saldo = SaldoContaPeriodo.objects.get(conta_contabil=self.conta_d, filial=self.filial, periodo=self.periodo)
        self.assertEqual(saldo.debito, Decimal("100"))
        saldo_cc = SaldoCentroCustoPeriodo.objects.get(saldo_conta_periodo=saldo, centro_custo=self.cc, periodo=self.periodo)
        self.assertEqual(saldo_cc.debito, Decimal("100"))

    def test_varios_itens(self):
        lanc = self.criar_lancamento()
        item_d, item_c = self.preparar_itens(lanc)
        LancamentoItem.objects.create(
            lancamento=lanc,
            conta_contabil=self.conta_d,
            filial=self.filial,
            moeda=self.moeda,
            valor=Decimal("50"),
            tipo_dc="D",
            historico=self.historico,
        )
        LancamentoItem.objects.create(
            lancamento=lanc,
            conta_contabil=self.conta_c,
            filial=self.filial,
            moeda=self.moeda,
            valor=Decimal("50"),
            tipo_dc="C",
            historico=self.historico,
        )
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100"))
        RateioLancamentoItemCentroCusto.objects.create(lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("100"))
        lanc.validar()

    def test_incluir_itens_incremental(self):
        lanc = self.criar_lancamento()
        item_d = LancamentoItem.objects.create(
            lancamento=lanc,
            conta_contabil=self.conta_d,
            filial=self.filial,
            moeda=self.moeda,
            valor=Decimal("100"),
            tipo_dc="D",
            historico=self.historico,
        )
        RateioLancamentoItemCentroCusto.objects.create(
            lancamento_item=item_d, centro_custo=self.cc, valor=Decimal("100")
        )
        with self.assertRaises(ValidationError):
            lanc.validar()
        item_c = LancamentoItem.objects.create(
            lancamento=lanc,
            conta_contabil=self.conta_c,
            filial=self.filial,
            moeda=self.moeda,
            valor=Decimal("100"),
            tipo_dc="C",
            historico=self.historico,
        )
        RateioLancamentoItemCentroCusto.objects.create(
            lancamento_item=item_c, centro_custo=self.cc, valor=Decimal("100")
        )
        lanc.validar()


