from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date

from cadastros.models import Empresa
from .models import (
    ContaContabil,
    Projeto,
    Periodo,
    Filial,
)


def criar_empresa():
    return Empresa.objects.create(
        razao_social="Empresa",
        nome_fantasia="",
        cnpj="12345678901234",
        ie="",
        im="",
        endereco="Rua",
        numero="1",
        complemento="",
        bairro="Bairro",
        cidade="Cidade",
        estado="SP",
        cep="12345678",
        telefone="",
        email="",
        site="",
        ativo=True,
    )


class ContaContabilTests(TestCase):
    def setUp(self):
        self.n1 = ContaContabil(codigo="1", descricao="Ativo", tipo="S", natureza="D")
        self.n1.full_clean(); self.n1.save()
        self.n2 = ContaContabil(codigo="1.01", descricao="Circulante", tipo="S", natureza="D", conta_pai=self.n1)
        self.n2.full_clean(); self.n2.save()
        self.n3 = ContaContabil(codigo="1.01.02", descricao="Disponível", tipo="S", natureza="D", conta_pai=self.n2)
        self.n3.full_clean(); self.n3.save()
        self.n4 = ContaContabil(codigo="1.01.02.003", descricao="Caixa", tipo="S", natureza="D", conta_pai=self.n3)
        self.n4.full_clean(); self.n4.save()

    def test_codigo_mascara(self):
        c = ContaContabil(codigo="1.1", descricao="Teste", tipo="S", natureza="D")
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_tipo_nivel_e_conta_pai(self):
        # Conta analítica válida
        c = ContaContabil(codigo="1.01.02.003.0001", descricao="Caixa Filial", tipo="A", natureza="D", conta_pai=self.n4)
        c.full_clean(); c.save()
        # Conta analítica com final 0000
        with self.assertRaises(ValidationError):
            ContaContabil(codigo="1.01.02.003.0000", descricao="Inválida", tipo="A", natureza="D", conta_pai=self.n4).full_clean()
        # Nível incompatível com conta pai
        with self.assertRaises(ValidationError):
            ContaContabil(codigo="1.01.02.003.0002", descricao="Erro", tipo="A", natureza="D", conta_pai=self.n3).full_clean()
        # Sintética em nível 5
        with self.assertRaises(ValidationError):
            ContaContabil(codigo="1.01.02.003.0003", descricao="Erro", tipo="S", natureza="D", conta_pai=self.n4).full_clean()


class ProjetoTests(TestCase):
    def test_datas(self):
        p = Projeto(codigo="P1", descricao="Proj", data_inicio=date(2023,1,1), data_fim=date(2023,1,2))
        p.full_clean()
        p.data_fim = date(2022,12,31)
        with self.assertRaises(ValidationError):
            p.full_clean()


class PeriodoTests(TestCase):
    def setUp(self):
        self.empresa = criar_empresa()

    def test_intervalo_e_unicidade(self):
        Periodo.objects.create(codigo="2023-01", data_inicio=date(2023,1,1), data_fim=date(2023,1,31), empresa=self.empresa, status="A")
        with self.assertRaises(ValidationError):
            Periodo(codigo="2023-01", data_inicio=date(2023,2,1), data_fim=date(2023,2,28), empresa=self.empresa, status="A").full_clean()
        with self.assertRaises(ValidationError):
            Periodo(codigo="2023-02", data_inicio=date(2023,3,1), data_fim=date(2023,2,1), empresa=self.empresa, status="A").full_clean()


class FilialTests(TestCase):
    def test_unicidade(self):
        empresa = criar_empresa()
        Filial.objects.create(empresa=empresa, codigo="001", descricao="Filial 1")
        with self.assertRaises(ValidationError):
            Filial(empresa=empresa, codigo="001", descricao="Outra").full_clean()

