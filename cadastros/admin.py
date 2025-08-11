from django.contrib import admin
from .models import Empresa, Parceiro


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        "razao_social",
        "cnpj",
        "cidade",
        "estado",
        "grupo_empresarial",
        "ativo",
        "created_at",
    )
    list_filter = ("estado", "ativo", "grupo_empresarial", "created_at")
    search_fields = ("razao_social", "nome_fantasia", "cnpj", "cidade", "bairro")


@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "cnpj", "cidade", "estado", "ativo", "created_at")
    list_filter = ("estado", "ativo", "created_at")
    search_fields = ("razao_social", "nome_fantasia", "cnpj", "cidade", "bairro")
