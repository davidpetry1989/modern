from django.urls import path
from . import views

app_name = "cadastros"

urlpatterns = [
    # Empresas
    path("empresas/", views.EmpresaListView.as_view(), name="empresas_lista"),
    path("empresas/nova/", views.EmpresaCreateView.as_view(), name="empresas_criar"),
    path("empresas/<int:pk>/editar/", views.EmpresaUpdateView.as_view(), name="empresas_editar"),
    path("empresas/<int:pk>/excluir/", views.EmpresaDeleteView.as_view(), name="empresas_excluir"),
    # Parceiros
    path("parceiros/", views.ParceiroListView.as_view(), name="parceiros_lista"),
    path("parceiros/novo/", views.ParceiroCreateView.as_view(), name="parceiros_criar"),
    path("parceiros/<int:pk>/editar/", views.ParceiroUpdateView.as_view(), name="parceiros_editar"),
    path("parceiros/<int:pk>/excluir/", views.ParceiroDeleteView.as_view(), name="parceiros_excluir"),
]
