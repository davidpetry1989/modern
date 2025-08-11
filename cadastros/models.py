from django.db import models
from django.core.validators import RegexValidator

UF_CHOICES = [
    ("AC", "AC"), ("AL", "AL"), ("AP", "AP"), ("AM", "AM"), ("BA", "BA"),
    ("CE", "CE"), ("DF", "DF"), ("ES", "ES"), ("GO", "GO"), ("MA", "MA"),
    ("MT", "MT"), ("MS", "MS"), ("MG", "MG"), ("PA", "PA"), ("PB", "PB"),
    ("PR", "PR"), ("PE", "PE"), ("PI", "PI"), ("RJ", "RJ"), ("RN", "RN"),
    ("RS", "RS"), ("RO", "RO"), ("RR", "RR"), ("SC", "SC"), ("SP", "SP"),
    ("SE", "SE"), ("TO", "TO"),
]

class PessoaJuridicaBase(models.Model):
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(r"^\d{14}$", "CNPJ deve conter 14 dígitos")],
    )
    ie = models.CharField(max_length=30, blank=True)
    im = models.CharField(max_length=30, blank=True)
    endereco = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=UF_CHOICES)
    cep = models.CharField(
        max_length=8,
        validators=[RegexValidator(r"^\d{8}$", "CEP deve conter 8 dígitos")],
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\d+$", "Telefone inválido")],
    )
    email = models.EmailField(blank=True)
    site = models.URLField(blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["razao_social"]
        indexes = [models.Index(fields=["cnpj"])]

    def __str__(self):
        return f"{self.razao_social} ({self.cnpj})"


class Empresa(PessoaJuridicaBase):
    pass


class Parceiro(PessoaJuridicaBase):
    is_cliente = models.BooleanField(default=False)
    is_fornecedor = models.BooleanField(default=False)
    is_transportadora = models.BooleanField(default=False)
    is_contador = models.BooleanField(default=False)
