from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Empresa, Parceiro
from .forms import EmpresaForm


class CadastrosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")

    def login(self):
        self.client.login(username="user", password="pass")

    def test_empresa_list_authenticated(self):
        self.login()
        resp = self.client.get(reverse("cadastros:empresas_lista"))
        self.assertEqual(resp.status_code, 200)

    def test_cnpj_invalido(self):
        form = EmpresaForm(
            data={
                "razao_social": "Teste",
                "cnpj": "12345678901234",
                "endereco": "Rua",
                "numero": "1",
                "bairro": "Bairro",
                "cidade": "Cidade",
                "estado": "SP",
                "cep": "12345678",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("cnpj", form.errors)

    def test_empresa_crud(self):
        self.login()
        data = {
            "razao_social": "Empresa Teste",
            "nome_fantasia": "",
            "cnpj": "11222333000181",
            "ie": "",
            "im": "",
            "endereco": "Rua",
            "numero": "1",
            "complemento": "",
            "bairro": "Bairro",
            "cidade": "Cidade",
            "estado": "SP",
            "cep": "12345678",
            "telefone": "",
            "email": "",
            "site": "",
            "ativo": "on",
        }
        resp = self.client.post(reverse("cadastros:empresas_criar"), data, follow=True)
        self.assertRedirects(resp, reverse("cadastros:empresas_lista"))
        self.assertContains(resp, "Empresa criada com sucesso.")
        self.assertEqual(Empresa.objects.count(), 1)
        empresa = Empresa.objects.first()
        data["razao_social"] = "Empresa X"
        resp = self.client.post(
            reverse("cadastros:empresas_editar", args=[empresa.pk]), data, follow=True
        )
        self.assertRedirects(resp, reverse("cadastros:empresas_lista"))
        self.assertContains(resp, "Empresa atualizada com sucesso.")
        empresa.refresh_from_db()
        self.assertEqual(empresa.razao_social, "Empresa X")
        resp = self.client.post(
            reverse("cadastros:empresas_excluir", args=[empresa.pk]), follow=True
        )
        self.assertRedirects(resp, reverse("cadastros:empresas_lista"))
        self.assertContains(resp, "Empresa excluída com sucesso.")
        self.assertEqual(Empresa.objects.count(), 0)

    def test_parceiro_boolean_filters(self):
        self.login()
        p1 = Parceiro.objects.create(
            razao_social="P1",
            cnpj="04252011000110",
            endereco="Rua",
            numero="1",
            bairro="Bairro",
            cidade="Cidade",
            estado="SP",
            cep="12345678",
            is_cliente=True,
        )
        p2 = Parceiro.objects.create(
            razao_social="P2",
            cnpj="19131243000197",
            endereco="Rua",
            numero="1",
            bairro="Bairro",
            cidade="Cidade",
            estado="SP",
            cep="12345678",
            is_fornecedor=True,
        )
        resp = self.client.get(reverse("cadastros:parceiros_lista"), {"cliente": "1"})
        self.assertContains(resp, "P1")
        self.assertNotContains(resp, "P2")
        resp = self.client.get(reverse("cadastros:parceiros_lista"), {"fornecedor": "1"})
        self.assertContains(resp, "P2")
        self.assertNotContains(resp, "P1")
