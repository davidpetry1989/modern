from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT, CASCADE

from . import ContaContabil, CentroCusto, Projeto, Filial, Moeda, HistoricoPadrao, Periodo


class LancamentoContabil(models.Model):
    TIPO_LANCAMENTO_CHOICES = [
        ("0", "Normal"),
        ("1", "Societário"),
        ("2", "Fiscal"),
        ("3", "Orçamentário"),
        ("4", "Zeramento"),
        ("5", "Ajuste"),
    ]

    ORIGEM_CHOICES = [
        ("0", "Manual"),
        ("1", "Integrado"),
        ("2", "Importado"),
        ("3", "Gerado"),
    ]

    data_lancamento = models.DateField()
    data_competencia = models.DateField()
    tipo_lancamento = models.CharField(max_length=1, choices=TIPO_LANCAMENTO_CHOICES)
    origem = models.CharField(max_length=1, choices=ORIGEM_CHOICES, default="0")
    numero_documento = models.CharField(max_length=50, blank=True)
    descricao = models.CharField(max_length=255, blank=True)
    codigo_externo = models.CharField(max_length=50, blank=True, db_index=True)
    filial = models.ForeignKey(Filial, on_delete=PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=PROTECT)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["data_competencia", "filial"]),
            models.Index(fields=["codigo_externo"]),
            models.Index(fields=["numero_documento"]),
        ]

    def __str__(self):
        return f"{self.id} - {self.data_lancamento}"

    def validar(self):
        total_d = Decimal("0.00")
        total_c = Decimal("0.00")
        itens = self.itens.filter(status=True)
        for item in itens:
            if item.tipo_dc == "D":
                total_d += item.valor
            else:
                total_c += item.valor
            item.validar_rateios()
        if total_d.quantize(Decimal("0.01")) != total_c.quantize(Decimal("0.01")):
            raise ValidationError("Débitos e créditos não estão balanceados")


class LancamentoItem(models.Model):
    TIPO_DC_CHOICES = [("D", "Débito"), ("C", "Crédito")]

    lancamento = models.ForeignKey(
        LancamentoContabil, on_delete=CASCADE, related_name="itens"
    )
    conta_contabil = models.ForeignKey(ContaContabil, on_delete=PROTECT)
    filial = models.ForeignKey(Filial, on_delete=PROTECT)
    moeda = models.ForeignKey(Moeda, on_delete=PROTECT)
    codigo_externo = models.CharField(max_length=50, blank=True)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    tipo_dc = models.CharField(max_length=1, choices=TIPO_DC_CHOICES)
    historico = models.ForeignKey(HistoricoPadrao, on_delete=PROTECT)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["lancamento"]),
            models.Index(fields=["conta_contabil", "tipo_dc"]),
            models.Index(fields=["filial", "moeda"]),
        ]

    def __str__(self):
        return f"Item {self.id} do lançamento {self.lancamento_id}"

    def validar_rateios(self):
        from django.core.exceptions import ValidationError

        valor_item = self.valor.quantize(Decimal("0.01"))
        rateios_cc = list(self.rateios_cc.all())
        rateios_proj = list(self.rateios_projeto.all())

        if self.conta_contabil.classificacao in {"R", "D", "C"}:
            if not rateios_cc:
                raise ValidationError("Rateio de centro de custo obrigatório")
        total_cc = sum((r.valor for r in rateios_cc), Decimal("0.00"))
        total_proj = sum((r.valor for r in rateios_proj), Decimal("0.00"))

        if rateios_cc:
            if total_cc.quantize(Decimal("0.01")) != valor_item:
                raise ValidationError("Rateios de centro de custo não fecham com o valor do item")
        if rateios_proj:
            if total_proj.quantize(Decimal("0.01")) != valor_item:
                raise ValidationError("Rateios de projeto não fecham com o valor do item")


class RateioLancamentoItemCentroCusto(models.Model):
    lancamento_item = models.ForeignKey(
        LancamentoItem, on_delete=CASCADE, related_name="rateios_cc"
    )
    centro_custo = models.ForeignKey(CentroCusto, on_delete=PROTECT)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lancamento_item", "centro_custo"],
                name="uniq_rateio_item_cc",
            )
        ]

    def __str__(self):
        return f"CC {self.centro_custo_id} - Item {self.lancamento_item_id}"


class RateioLancamentoItemProjeto(models.Model):
    lancamento_item = models.ForeignKey(
        LancamentoItem, on_delete=CASCADE, related_name="rateios_projeto"
    )
    projeto = models.ForeignKey(Projeto, on_delete=PROTECT)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lancamento_item", "projeto"],
                name="uniq_rateio_item_projeto",
            )
        ]

    def __str__(self):
        return f"Projeto {self.projeto_id} - Item {self.lancamento_item_id}"


class SaldoContaPeriodo(models.Model):
    conta_contabil = models.ForeignKey(ContaContabil, on_delete=CASCADE)
    filial = models.ForeignKey(Filial, on_delete=CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=CASCADE)
    saldo_inicial = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    debito = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credito = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["conta_contabil", "filial", "periodo"],
                name="uniq_saldo_conta_periodo",
            )
        ]
        indexes = [
            models.Index(fields=["filial", "periodo", "conta_contabil"]),
        ]

    def __str__(self):
        return f"Saldo {self.conta_contabil_id}/{self.periodo_id}"


class SaldoCentroCustoPeriodo(models.Model):
    saldo_conta_periodo = models.ForeignKey(
        SaldoContaPeriodo, on_delete=CASCADE, related_name="saldos_cc"
    )
    centro_custo = models.ForeignKey(CentroCusto, on_delete=CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=CASCADE)
    saldo_inicial = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    debito = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credito = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["saldo_conta_periodo", "centro_custo", "periodo"],
                name="uniq_saldo_cc_periodo",
            )
        ]

    def __str__(self):
        return f"Saldo CC {self.centro_custo_id}/{self.periodo_id}"


class SaldoProjetoPeriodo(models.Model):
    saldo_conta_periodo = models.ForeignKey(
        SaldoContaPeriodo, on_delete=CASCADE, related_name="saldos_projeto"
    )
    projeto = models.ForeignKey(Projeto, on_delete=CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=CASCADE)
    saldo_inicial = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    debito = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credito = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["saldo_conta_periodo", "projeto", "periodo"],
                name="uniq_saldo_projeto_periodo",
            )
        ]

    def __str__(self):
        return f"Saldo Projeto {self.projeto_id}/{self.periodo_id}"

