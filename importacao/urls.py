from django.urls import path

from . import views

app_name = "importacao"

urlpatterns = [
    path("", views.LayoutListView.as_view(), name="layout_list"),
    path("layouts/", views.LayoutListView.as_view(), name="layout_list"),
    path("layouts/novo/", views.LayoutCreateView.as_view(), name="layout_add"),
    path(
        "layouts/<int:pk>/editar/",
        views.LayoutUpdateView.as_view(),
        name="layout_edit",
    ),
    path("wizard/", views.LayoutSelectView.as_view(), name="wizard"),
    path("wizard/preview/", views.PreviewMapView.as_view(), name="wizard_preview"),
    path("wizard/apply/", views.ApplyView.as_view(), name="wizard_apply"),
    path("search/<str:target>/", views.SearchView.as_view(), name="search"),
    path("depara/contas/", views.DeParaListView.as_view(), {"target": "contas"}, name="depara_contas_lista"),
    path("depara/centros/", views.DeParaListView.as_view(), {"target": "centros"}, name="depara_centros_lista"),
    path("depara/empresas/", views.DeParaListView.as_view(), {"target": "empresas"}, name="depara_empresas_lista"),
    path("depara/filiais/", views.DeParaListView.as_view(), {"target": "filiais"}, name="depara_filiais_lista"),
    path("depara/projetos/", views.DeParaListView.as_view(), {"target": "projetos"}, name="depara_projetos_lista"),
    path("depara/moedas/", views.DeParaListView.as_view(), {"target": "moedas"}, name="depara_moedas_lista"),
    path("depara/historicos/", views.DeParaListView.as_view(), {"target": "historicos"}, name="depara_historicos_lista"),
    path("depara/parceiros/", views.DeParaListView.as_view(), {"target": "parceiros"}, name="depara_parceiros_lista"),
    path("depara/<str:target>/", views.DeParaListView.as_view(), name="depara_list"),
]