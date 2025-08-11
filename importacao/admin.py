from django.contrib import admin
from .models import (
    LayoutImportacao,
    DeParaContaContabil,
    DeParaCentroCusto,
    DeParaEmpresa,
    DeParaFilial,
    DeParaProjeto,
    DeParaMoeda,
    DeParaHistoricoPadrao,
    DeParaParceiroNegocio,
)


@admin.register(LayoutImportacao)
class LayoutImportacaoAdmin(admin.ModelAdmin):
    search_fields = ("nome", "origem_sistema")
    list_display = ("nome", "origem_sistema", "tipo_arquivo", "ativo", "updated_at")
    list_filter = ("origem_sistema", "tipo_arquivo", "ativo")


class DeParaBaseAdmin(admin.ModelAdmin):
    list_display = (
        "layout",
        "codigo_externo",
        "descricao_externa",
        "target",
        "ativo",
        "updated_at",
    )
    list_filter = ("layout", "ativo")
    actions = ["desativar", "reativar"]

    def desativar(self, request, queryset):
        queryset.update(ativo=False)

    desativar.short_description = "Desativar selecionados"

    def reativar(self, request, queryset):
        queryset.update(ativo=True)

    reativar.short_description = "Reativar selecionados"


@admin.register(DeParaContaContabil)
class DeParaContaContabilAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__codigo",
        "target__descricao",
    )


@admin.register(DeParaCentroCusto)
class DeParaCentroCustoAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__codigo",
        "target__descricao",
    )


@admin.register(DeParaEmpresa)
class DeParaEmpresaAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__razao_social",
        "target__cnpj",
    )


@admin.register(DeParaFilial)
class DeParaFilialAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__codigo",
        "target__descricao",
        "target__empresa__razao_social",
    )


@admin.register(DeParaProjeto)
class DeParaProjetoAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__codigo",
        "target__descricao",
    )


@admin.register(DeParaMoeda)
class DeParaMoedaAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__codigo",
        "target__descricao",
        "target__simbolo",
    )


@admin.register(DeParaHistoricoPadrao)
class DeParaHistoricoPadraoAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__descricao",
    )


@admin.register(DeParaParceiroNegocio)
class DeParaParceiroNegocioAdmin(DeParaBaseAdmin):
    search_fields = (
        "codigo_externo",
        "descricao_externa",
        "target__razao_social",
        "target__cnpj",
    )