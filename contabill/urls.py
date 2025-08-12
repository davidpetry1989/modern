from django.urls import path

from .views import (
    ContaContabilListView,
    ContaContabilCreateView,
    ContaContabilUpdateView,
    ContaContabilDeleteView,
    CentroCustoListView,
    CentroCustoCreateView,
    CentroCustoUpdateView,
    CentroCustoDeleteView,
    GrupoEmpresarialListView,
    GrupoEmpresarialCreateView,
    GrupoEmpresarialUpdateView,
    GrupoEmpresarialDeleteView,
    FilialListView,
    FilialCreateView,
    FilialUpdateView,
    FilialDeleteView,
    ProjetoListView,
    ProjetoCreateView,
    ProjetoUpdateView,
    ProjetoDeleteView,
    MoedaListView,
    MoedaCreateView,
    MoedaUpdateView,
    MoedaDeleteView,
    HistoricoPadraoListView,
    HistoricoPadraoCreateView,
    HistoricoPadraoUpdateView,
    HistoricoPadraoDeleteView,
    PeriodoListView,
    PeriodoCreateView,
    PeriodoUpdateView,
    PeriodoDeleteView,
)
from .views.lancamentos import (
    LancamentoContabilListView,
    LancamentoContabilCreateView,
    LancamentoContabilUpdateView,
    LancamentoContabilDeleteView,
    RecalcularSaldoView,
    LancamentoItemCreateView,
    RateioCentroCustoView,
    RateioProjetoView,
)

app_name = "contabill"

urlpatterns = [
    path("contas/", ContaContabilListView.as_view(), name="contas_lista"),
    path("contas/novo/", ContaContabilCreateView.as_view(), name="contas_criar"),
    path("contas/<int:pk>/editar/", ContaContabilUpdateView.as_view(), name="contas_editar"),
    path("contas/<int:pk>/excluir/", ContaContabilDeleteView.as_view(), name="contas_excluir"),

    path("centros/", CentroCustoListView.as_view(), name="centros_lista"),
    path("centros/novo/", CentroCustoCreateView.as_view(), name="centros_criar"),
    path("centros/<int:pk>/editar/", CentroCustoUpdateView.as_view(), name="centros_editar"),
    path("centros/<int:pk>/excluir/", CentroCustoDeleteView.as_view(), name="centros_excluir"),

    path("grupos/", GrupoEmpresarialListView.as_view(), name="grupos_lista"),
    path("grupos/novo/", GrupoEmpresarialCreateView.as_view(), name="grupos_criar"),
    path("grupos/<int:pk>/editar/", GrupoEmpresarialUpdateView.as_view(), name="grupos_editar"),
    path("grupos/<int:pk>/excluir/", GrupoEmpresarialDeleteView.as_view(), name="grupos_excluir"),

    path("filiais/", FilialListView.as_view(), name="filiais_lista"),
    path("filiais/novo/", FilialCreateView.as_view(), name="filiais_criar"),
    path("filiais/<int:pk>/editar/", FilialUpdateView.as_view(), name="filiais_editar"),
    path("filiais/<int:pk>/excluir/", FilialDeleteView.as_view(), name="filiais_excluir"),

    path("projetos/", ProjetoListView.as_view(), name="projetos_lista"),
    path("projetos/novo/", ProjetoCreateView.as_view(), name="projetos_criar"),
    path("projetos/<int:pk>/editar/", ProjetoUpdateView.as_view(), name="projetos_editar"),
    path("projetos/<int:pk>/excluir/", ProjetoDeleteView.as_view(), name="projetos_excluir"),

    path("moedas/", MoedaListView.as_view(), name="moedas_lista"),
    path("moedas/novo/", MoedaCreateView.as_view(), name="moedas_criar"),
    path("moedas/<int:pk>/editar/", MoedaUpdateView.as_view(), name="moedas_editar"),
    path("moedas/<int:pk>/excluir/", MoedaDeleteView.as_view(), name="moedas_excluir"),

    path("historicos/", HistoricoPadraoListView.as_view(), name="historicos_lista"),
    path("historicos/novo/", HistoricoPadraoCreateView.as_view(), name="historicos_criar"),
    path("historicos/<int:pk>/editar/", HistoricoPadraoUpdateView.as_view(), name="historicos_editar"),
    path("historicos/<int:pk>/excluir/", HistoricoPadraoDeleteView.as_view(), name="historicos_excluir"),

    path("periodos/", PeriodoListView.as_view(), name="periodos_lista"),
    path("periodos/novo/", PeriodoCreateView.as_view(), name="periodos_criar"),
    path("periodos/<int:pk>/editar/", PeriodoUpdateView.as_view(), name="periodos_editar"),
    path("periodos/<int:pk>/excluir/", PeriodoDeleteView.as_view(), name="periodos_excluir"),

    path("lancamentos/", LancamentoContabilListView.as_view(), name="lancamentos_lista"),
    path("lancamentos/novo/", LancamentoContabilCreateView.as_view(), name="lancamentos_novo"),
    path(
        "lancamentos/<int:pk>/editar/",
        LancamentoContabilUpdateView.as_view(),
        name="lancamentos_editar",
    ),
    path(
        "lancamentos/<int:pk>/excluir/",
        LancamentoContabilDeleteView.as_view(),
        name="lancamentos_excluir",
    ),
    path(
        "lancamentos/recalcular-saldo/",
        RecalcularSaldoView.as_view(),
        name="lancamentos_recalcular_saldo",
    ),
    path(
        "lancamentos/item/novo/",
        LancamentoItemCreateView.as_view(),
        name="lancamentos_item_create",
    ),
    path(
        "lancamentos/rateio-cc/",
        RateioCentroCustoView.as_view(),
        name="lancamentos_rateio_cc",
    ),
    path(
        "lancamentos/rateio-cc/salvar/",
        RateioCentroCustoView.as_view(),
        name="lancamentos_rateio_cc_save",
    ),
    path(
        "lancamentos/rateio-projeto/",
        RateioProjetoView.as_view(),
        name="lancamentos_rateio_projeto",
    ),
    path(
        "lancamentos/rateio-projeto/salvar/",
        RateioProjetoView.as_view(),
        name="lancamentos_rateio_projeto_save",
    ),
]
