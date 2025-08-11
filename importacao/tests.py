from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .models import LayoutImportacao, DePara
from .services import bulk_upsert, resolver, get_ct_for_model
from .forms import depara_form_factory
from contabill.models import ContaContabil, CentroCusto


class DeParaServiceTests(TestCase):
    def setUp(self):
        self.layout = LayoutImportacao.objects.create(
            nome="Layout",
            origem_sistema="X",
            descricao="desc",
            tipo_arquivo="csv",
        )
        self.conta = ContaContabil.objects.create(
            codigo="1.01.01.0001",
            descricao="Conta",
            tipo="A",
            natureza="D",
            ordem=1,
            nivel=5,
        )

    def test_bulk_upsert_and_resolver(self):
        created, updated = bulk_upsert(
            self.layout.id,
            ContaContabil,
            [
                {
                    "codigo_externo": "ext1",
                    "descricao_externa": "Conta X",
                    "target_id": self.conta.id,
                }
            ],
        )
        self.assertEqual(created, 1)
        self.assertEqual(updated, 0)
        self.assertEqual(
            resolver(self.layout.id, ContaContabil, "ext1"), self.conta.id
        )
        self.assertIsNone(resolver(self.layout.id, ContaContabil, "none"))

    def test_unique_constraint(self):
        ct = get_ct_for_model(ContaContabil)
        DePara.objects.create(
            layout=self.layout,
            target_ct=ct,
            target_id=self.conta.id,
            codigo_externo="dup",
        )
        with self.assertRaises(Exception):
            DePara.objects.create(
                layout=self.layout,
                target_ct=ct,
                target_id=self.conta.id,
                codigo_externo="dup",
            )

    def test_manual_form_creation(self):
        form_class = depara_form_factory(ContaContabil)
        form = form_class(
            data={
                "layout": self.layout.id,
                "codigo_externo": "manual",
                "descricao_externa": "Manual",
                "observacao": "",
                "target": self.conta.id,
                "ativo": True,
            }
        )
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.target_id, self.conta.id)


class WizardFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "u@example.com", "pass")
        self.client = Client()
        self.client.login(username="user", password="pass")
        self.layout = LayoutImportacao.objects.create(
            nome="Lay1",
            origem_sistema="X",
            descricao="desc",
            tipo_arquivo="csv",
        )
        self.conta = ContaContabil.objects.create(
            codigo="1.01.01.0001",
            descricao="Conta",
            tipo="A",
            natureza="D",
            ordem=1,
            nivel=5,
        )
        self.centro = CentroCusto.objects.create(
            codigo="100",
            descricao="Centro",
            tipo="O",
        )

    def test_wizard_happy_path(self):
        csv_content = "codigo_externo,descricao_externa,destino\ncex,Conta X,1.01.01.0001\n"
        file = SimpleUploadedFile("contas.csv", csv_content.encode("utf-8"), content_type="text/csv")
        resp = self.client.post(
            reverse("importacao:wizard"),
            {"layout": self.layout.id, "target": "contas", "arquivo": file},
        )
        self.assertEqual(resp.status_code, 302)
        resp = self.client.post(reverse("importacao:wizard_preview"), {"linhas": ["0"]})
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(reverse("importacao:wizard_apply"))
        self.assertContains(resp, "Criados")
        self.assertEqual(DePara.objects.count(), 1)

    def test_search_endpoint(self):
        url = reverse("importacao:search", args=["contas"])
        resp = self.client.get(url, {"q": "1.01"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("1.01", resp.content.decode())

    def test_bulk_upsert_centro_custo(self):
        created, updated = bulk_upsert(
            self.layout.id,
            CentroCusto,
            [
                {
                    "codigo_externo": "ext-centro",
                    "descricao_externa": "Centro X",
                    "target_id": self.centro.id,
                }
            ],
        )
        self.assertEqual(created, 1)