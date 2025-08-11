from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class LayoutImportacao(models.Model):
    TIPO_ARQUIVO_CHOICES = [
        ("csv", "csv"),
        ("xlsx", "xlsx"),
        ("xml", "xml"),
        ("api", "api"),
    ]

    nome = models.CharField(max_length=100, unique=True)
    origem_sistema = models.CharField(max_length=50)
    descricao = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=20, choices=TIPO_ARQUIVO_CHOICES)
    delimitador = models.CharField(max_length=5, default=";")
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class DePara(models.Model):
    layout = models.ForeignKey(LayoutImportacao, on_delete=models.CASCADE)
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_ct", "target_id")

    codigo_externo = models.CharField(max_length=50)
    descricao_externa = models.CharField(max_length=255, blank=True)
    observacao = models.CharField(max_length=255, blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["layout", "target_ct", "codigo_externo"],
                name="uq_depara_layout_target_codigo",
            )
        ]
        indexes = [
            models.Index(fields=["layout", "target_ct"]),
            models.Index(fields=["codigo_externo"]),
        ]

    def save(self, *args, **kwargs):
        if self.codigo_externo:
            self.codigo_externo = self.codigo_externo.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.codigo_externo


class DeParaProxyManager(models.Manager):
    def __init__(self, target_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_model = target_model

    def get_queryset(self):
        ct = ContentType.objects.get_for_model(self.target_model)
        return super().get_queryset().filter(target_ct=ct)


# Proxy models for UX/admin
from contabill.models import (
    ContaContabil,
    CentroCusto,
    Filial,
    Projeto,
    Moeda,
    HistoricoPadrao,
)
from cadastros.models import Empresa, Parceiro


class DeParaContaContabil(DePara):
    objects = DeParaProxyManager(ContaContabil)

    class Meta:
        proxy = True
        verbose_name = "De/Para Conta Contábil"
        verbose_name_plural = "De/Para Plano de Contas"


class DeParaCentroCusto(DePara):
    objects = DeParaProxyManager(CentroCusto)

    class Meta:
        proxy = True
        verbose_name = "De/Para Centro de Custo"
        verbose_name_plural = "De/Para Centros de Custo"


class DeParaEmpresa(DePara):
    objects = DeParaProxyManager(Empresa)

    class Meta:
        proxy = True
        verbose_name = "De/Para Empresa"
        verbose_name_plural = "De/Para Empresas"


class DeParaFilial(DePara):
    objects = DeParaProxyManager(Filial)

    class Meta:
        proxy = True
        verbose_name = "De/Para Filial"
        verbose_name_plural = "De/Para Filiais"


class DeParaProjeto(DePara):
    objects = DeParaProxyManager(Projeto)

    class Meta:
        proxy = True
        verbose_name = "De/Para Projeto"
        verbose_name_plural = "De/Para Projetos"


class DeParaMoeda(DePara):
    objects = DeParaProxyManager(Moeda)

    class Meta:
        proxy = True
        verbose_name = "De/Para Moeda"
        verbose_name_plural = "De/Para Moedas"


class DeParaHistoricoPadrao(DePara):
    objects = DeParaProxyManager(HistoricoPadrao)

    class Meta:
        proxy = True
        verbose_name = "De/Para Histórico Padrão"
        verbose_name_plural = "De/Para Históricos Padrão"


class DeParaParceiroNegocio(DePara):
    objects = DeParaProxyManager(Parceiro)

    class Meta:
        proxy = True
        verbose_name = "De/Para Parceiro de Negócio"
        verbose_name_plural = "De/Para Parceiros de Negócio"