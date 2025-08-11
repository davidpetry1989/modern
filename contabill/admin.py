from django.contrib import admin

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


@admin.register(GrupoEmpresarial)
class GrupoEmpresarialAdmin(admin.ModelAdmin):
    list_display = ("nome", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(ContaContabil)
class ContaContabilAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descricao",
        "tipo",
        "natureza",
        "classificacao",
        "status",
    )
    list_filter = ("tipo", "natureza", "classificacao", "status", "nivel")
    search_fields = ("codigo", "descricao")
    ordering = ("codigo",)


@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "tipo", "nivel", "status")
    list_filter = ("tipo", "status", "nivel")
    search_fields = ("codigo", "descricao")
    ordering = ("codigo",)


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ("empresa", "codigo", "descricao", "status")
    list_filter = ("empresa", "status")
    search_fields = ("codigo", "descricao")
    ordering = ("empresa", "codigo")


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "data_inicio", "data_fim", "status")
    list_filter = ("status",)
    search_fields = ("codigo", "descricao")
    ordering = ("codigo",)


@admin.register(Moeda)
class MoedaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "simbolo", "status")
    list_filter = ("status",)
    search_fields = ("codigo", "descricao")
    ordering = ("codigo",)


@admin.register(HistoricoPadrao)
class HistoricoPadraoAdmin(admin.ModelAdmin):
    list_display = ("descricao", "tipo", "status")
    list_filter = ("tipo", "status")
    search_fields = ("descricao",)
    ordering = ("descricao",)


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "empresa",
        "data_inicio",
        "data_fim",
        "status",
        "bloqueio_lancamento",
    )
    list_filter = ("status", "empresa")
    search_fields = ("codigo",)
    ordering = ("codigo",)

