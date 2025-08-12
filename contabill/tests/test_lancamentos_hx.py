import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone
from contabill.models import (
    LancamentoContabil, LancamentoItem, ContaContabil,
    HistoricoPadrao, Filial, Moeda
)


@pytest.mark.django_db
def test_hx_add_item_updates_grid(client: Client):
    user = User.objects.create_user("u", password="p")
    client.login(username="u", password="p")

    filial = Filial.objects.create(nome="Matriz")
    moeda = Moeda.objects.create(codigo="1", nome="REAL")
    conta = ContaContabil.objects.create(codigo="1.01", descricao="Conta teste", classificacao="A", natureza="D", status=True)
    hist = HistoricoPadrao.objects.create(descricao="LANÇAMENTOS")

    lanc = LancamentoContabil.objects.create(
        data_lancamento=timezone.localdate(),
        data_competencia=timezone.localdate(),
        filial=filial, usuario=user, tipo_lancamento="0", origem="0", status=True
    )

    url = reverse("contabill:lancamentos_item_create")
    resp = client.post(url, data={
        "lancamento_id": lanc.id,
        "novo-conta_contabil": conta.id,
        "novo-historico": hist.id,
        "novo-moeda": moeda.id,
        "novo-tipo_dc": "D",
        "novo-valor": "100,00",
    }, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Conta teste" in html
    assert LancamentoItem.objects.filter(lancamento=lanc).count() == 1
