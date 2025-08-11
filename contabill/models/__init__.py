from django.db import models
from django.core.exceptions import ValidationError
import re


class BaseModel(models.Model):
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GrupoEmpresarial(BaseModel):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ContaContabil(BaseModel):
    TIPO_CHOICES = [("A", "Analítica"), ("S", "Sintética")]
    NATUREZA_CHOICES = [("D", "Devedora"), ("C", "Credora")]
    CLASSIFICACAO_CHOICES = [
        ("A", "Ativo"),
        ("P", "Passivo"),
        ("L", "Patrimônio Líquido"),
        ("R", "Receita"),
        ("D", "Despesa"),
        ("C", "Custo"),
        ("O", "Outros"),
    ]

    codigo = models.CharField(max_length=100, unique=True, db_index=True)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    natureza = models.CharField(max_length=1, choices=NATUREZA_CHOICES)
    ordem = models.IntegerField(default=0)
    nivel = models.IntegerField()
    conta_pai = models.ForeignKey(
        "self", null=True, blank=True, related_name="filhas", on_delete=models.PROTECT
    )
    classificacao = models.CharField(
        max_length=1, choices=CLASSIFICACAO_CHOICES, blank=True
    )

    class Meta:
        ordering = ["codigo"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["conta_pai"]),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

    def clean(self):
        super().clean()
        codigo = self.codigo or ""
        patterns = {
            1: r"^\d$",
            2: r"^\d\.\d{2}$",
            3: r"^\d\.\d{2}\.\d{2}$",
            4: r"^\d\.\d{2}\.\d{2}\.\d{3}$",
            5: r"^\d\.\d{2}\.\d{2}\.\d{3}\.\d{4}$",
        }
        nivel = None
        for n, pattern in patterns.items():
            if re.match(pattern, codigo):
                nivel = n
                break
        if not nivel:
            raise ValidationError({"codigo": "Código inválido para o nível."})
        self.nivel = nivel

        if self.conta_pai:
            if self.conta_pai.nivel + 1 != self.nivel:
                raise ValidationError(
                    {"conta_pai": "Nível incompatível com a conta pai."}
                )
            if not codigo.startswith(self.conta_pai.codigo + "."):
                raise ValidationError(
                    {"codigo": "Código deve iniciar com o código da conta pai."}
                )
            if self.conta_pai.tipo != "S":
                raise ValidationError(
                    {"conta_pai": "Conta pai deve ser Sintética."}
                )

        if self.tipo == "S" and self.nivel == 5:
            raise ValidationError({"tipo": "Conta sintética apenas níveis 1-4."})
        if self.tipo == "A" and self.nivel != 5:
            raise ValidationError({"tipo": "Conta analítica apenas nível 5."})

        if self.tipo == "A":
            last = codigo.split(".")[-1]
            if last == "0000":
                raise ValidationError(
                    {"codigo": "Conta analítica não pode terminar com 0000."}
                )

        if not self.classificacao:
            first = codigo[0]
            mapping = {"1": "A", "2": "P", "3": "L", "4": "R", "5": "D"}
            if first in mapping:
                self.classificacao = mapping[first]
            elif first in ["6", "7", "8"]:
                self.classificacao = "C"
            else:
                self.classificacao = "O"


class CentroCusto(BaseModel):
    TIPO_CHOICES = [
        ("O", "Operacional"),
        ("A", "Administrativo"),
        ("C", "Comercial"),
        ("K", "Outros"),
    ]

    codigo = models.CharField(max_length=100, unique=True, db_index=True)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    centro_custo_pai = models.ForeignKey(
        "self", null=True, blank=True, related_name="filhos", on_delete=models.PROTECT
    )
    nivel = models.IntegerField(default=1)

    class Meta:
        ordering = ["codigo"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["centro_custo_pai"]),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

    def clean(self):
        super().clean()
        if self.centro_custo_pai:
            if self.centro_custo_pai == self:
                raise ValidationError({"centro_custo_pai": "Ciclo inválido."})
            ancestor = self.centro_custo_pai
            while ancestor:
                if ancestor == self:
                    raise ValidationError({"centro_custo_pai": "Ciclo inválido."})
                ancestor = ancestor.centro_custo_pai
            self.nivel = self.centro_custo_pai.nivel + 1
        else:
            self.nivel = 1


class Filial(BaseModel):
    empresa = models.ForeignKey(
        "cadastros.Empresa", on_delete=models.CASCADE, related_name="filiais"
    )
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=100)

    class Meta:
        unique_together = (("empresa", "codigo"),)
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "codigo"], name="uniq_filial_empresa_codigo"
            )
        ]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["empresa"]),
        ]
        ordering = ["empresa", "codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class Projeto(BaseModel):
    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    descricao = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    class Meta:
        ordering = ["codigo"]
        indexes = [models.Index(fields=["codigo"])]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

    def clean(self):
        super().clean()
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError({"data_fim": "Data fim deve ser maior ou igual ao início."})


class Moeda(BaseModel):
    codigo = models.CharField(max_length=10, unique=True, db_index=True)
    descricao = models.CharField(max_length=100)
    simbolo = models.CharField(max_length=10)

    class Meta:
        ordering = ["codigo"]
        indexes = [models.Index(fields=["codigo"])]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class HistoricoPadrao(BaseModel):
    TIPO_CHOICES = [
        ("padrao", "Padrão"),
        ("recorrente", "Recorrente"),
        ("provisao", "Provisão"),
    ]

    descricao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    class Meta:
        ordering = ["descricao"]

    def __str__(self):
        return self.descricao


class Periodo(BaseModel):
    STATUS_CHOICES = [
        ("A", "Aberto"),
        ("F", "Fechado"),
        ("B", "Bloqueado"),
    ]

    codigo = models.CharField(max_length=10)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    empresa = models.ForeignKey(
        "cadastros.Empresa", null=True, blank=True, on_delete=models.CASCADE
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    bloqueio_lancamento = models.BooleanField(default=False)
    observacao = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "codigo"], name="uniq_periodo_empresa_codigo"
            )
        ]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["empresa"]),
        ]
        ordering = ["codigo"]

    def __str__(self):
        return self.codigo

    def clean(self):
        super().clean()
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError({"data_fim": "Data fim deve ser maior ou igual ao início."})


# Importa modelos de lançamentos
from .lancamentos import (
    LancamentoContabil,
    LancamentoItem,
    RateioLancamentoItemCentroCusto,
    RateioLancamentoItemProjeto,
    SaldoContaPeriodo,
    SaldoCentroCustoPeriodo,
    SaldoProjetoPeriodo,
)

