from django.db import models
from django.core.exceptions import ValidationError
from django_ledger.models.accounts import AccountModel
from django_ledger.models.entity import EntityModel
from django_ledger.models.ledger import LedgerModel
from django_ledger.models.transactions import TransactionModel
from datetime import datetime
import json

class Fazenda(models.Model):
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=14)
    proprietario = models.CharField(max_length=255)
    inscricao_estadual = models.CharField(max_length=20, blank=True)
    endereco = models.TextField()
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    pais = models.CharField(max_length=100, default="Brasil")
    coordenadas = models.JSONField(blank=True, null=True)
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="fazendas")

    def clean(self):
        if len(self.cpf_cnpj) not in [11, 14]:
            raise ValidationError("CPF must have 11 digits or CNPJ 14 digits.")

    def __str__(self):
        return self.nome

class CentroCusto(models.Model):
    nome = models.CharField(max_length=255)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE, related_name="centros_custo")
    tipo = models.CharField(max_length=50)
    tipo_area = models.CharField(max_length=20, choices=[("irrigada", "Irrigated"), ("sequeiro", "Dryland"), ("ambas", "Both")])
    propriedade = models.CharField(max_length=20, choices=[("propria", "Owned"), ("arrendada", "Leased"), ("ambas", "Both")])
    ledger = models.ForeignKey(LedgerModel, on_delete=models.CASCADE, related_name="centros_custo")

    def __str__(self):
        return f"{self.nome} ({self.fazenda.nome})"

class Area(models.Model):
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE, related_name="areas")
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=[("irrigada", "Irrigated"), ("sequeiro", "Dryland")])
    tamanho = models.FloatField()
    propriedade = models.CharField(max_length=20, choices=[("propria", "Owned"), ("arrendada", "Leased"), ("talhao", "Plot")])
    proprietario = models.CharField(max_length=255, blank=True)
    custo_arrendamento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    contrato_inicio = models.DateField(blank=True, null=True)
    contrato_fim = models.DateField(blank=True, null=True)
    pivo = models.ForeignKey("PivoCentral", on_delete=models.SET_NULL, blank=True, null=True, related_name="areas")
    coordenadas = models.JSONField(blank=True, null=True)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)
    permite_sobreposicao = models.BooleanField(default=False)

    def clean(self):
        if self.propriedade == "arrendada" and not (self.proprietario and self.custo_arrendamento and self.contrato_inicio and self.contrato_fim):
            raise ValidationError("Required fields for leased area not filled.")
        if self.pivo and self.tipo != "irrigada":
            raise ValidationError("Pivot can only be associated with irrigated area.")

    def __str__(self):
        return f"{self.nome} ({self.fazenda.nome})"

class Talhao(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="talhoes")
    nome = models.CharField(max_length=255)
    tamanho = models.FloatField()
    coordenadas = models.JSONField(blank=True, null=True)
    coordenadas_sobreposicao = models.JSONField(blank=True, null=True)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)

    def clean(self):
        if not self.area.permite_sobreposicao and self.tamanho > self.area.tamanho * 1.05:
            raise ValidationError("Plot size exceeds parent area (5% tolerance).")

    def __str__(self):
        return f"{self.nome} ({self.area.nome})"

class PivoCentral(models.Model):
    nome = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="pivos")
    talhoes = models.ManyToManyField(Talhao, blank=True)
    area_coberta = models.FloatField()
    consumo_agua = models.FloatField()
    data_manutencao = models.DateField(blank=True, null=True)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)
    usado_como_sequeiro = models.BooleanField(default=False)

    def clean(self):
        if self.area_coberta > self.area.tamanho:
            raise ValidationError("Pivot coverage area exceeds area size.")

    def __str__(self):
        return self.nome

class Cultura(models.Model):
    nome = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="culturas")
    talhao = models.ManyToManyField(Talhao, blank=True)
    safra = models.CharField(max_length=20, choices=[("principal", "Main"), ("safrinha", "Second")])
    percentual_area = models.FloatField()
    produtividade_esperada = models.FloatField()
    ciclo_cultivo = models.IntegerField()
    data_plantio = models.DateField()
    data_colheita_prevista = models.DateField()
    custo_hectare = models.DecimalField(max_digits=10, decimal_places=2)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)

    def clean(self):
        if self.data_colheita_prevista <= self.data_plantio:
            raise ValidationError("Harvest date must be after planting date.")
        if self.area.tipo == "sequeiro" and not self.area.permite_sobreposicao:
            if self.data_plantio.month < 11 and self.data_plantio.month > 5:
                raise ValidationError("Dryland planting only from November to May.")
        total_percentual = sum(c.percentual_area for c in self.area.culturas.all() if c.id != self.id) + self.percentual_area
        if not self.area.permite_sobreposicao and total_percentual > 100:
            raise ValidationError("Total percentage exceeds 100% without overlap.")

    def __str__(self):
        return f"{self.nome} ({self.area.nome})"

class Insumo(models.Model):
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[
        ("fungicida", "Fungicide"), ("herbicida", "Herbicide"), ("inseticida", "Insecticide"),
        ("adjuvante", "Adjuvant"), ("biologico", "Biological"), ("adubacao_foliar", "Foliar Fertilization"),
        ("outro", "Other")
    ])
    unidade_medida = models.CharField(max_length=20)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.FloatField(default=0)

    def __str__(self):
        return self.nome

class Equipamento(models.Model):
    nome = models.CharField(max_length=255)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE, related_name="equipamentos")
    tipo = models.CharField(max_length=50)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    ano = models.IntegerField()
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2)
    consumo_combustivel = models.FloatField(blank=True, null=True)
    horas_uso = models.FloatField(default=0)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nome

class Implemento(models.Model):
    nome = models.CharField(max_length=255)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE, related_name="implementos")
    tipo = models.CharField(max_length=50)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nome

class Funcionario(models.Model):
    nome = models.CharField(max_length=255)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE, related_name="funcionarios")
    funcao = models.CharField(max_length=50)
    salario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

class OrdemServico(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    data_emissao = models.DateField(default=datetime.now)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)
    cultura = models.ForeignKey(Cultura, on_delete=models.CASCADE)
    talhao = models.ForeignKey(Talhao, on_delete=models.CASCADE)
    tipo_manejo = models.CharField(max_length=50, choices=[
        ("preparo_solo", "Soil Preparation"), ("plantio", "Planting"), 
        ("pulverizacao", "Spraying"), ("aplicacao_manual", "Manual Application"), 
        ("colheita", "Harvest")
    ])
    subtipo_manejo = models.CharField(max_length=50, blank=True, choices=[
        ("abertura_area", "Area Opening"), ("limpeza_solo", "Soil Cleaning"),
        ("correcao_solo", "Soil Correction"), ("adubacao_variavel", "Variable Fertilization"),
        ("adubacao_fixa", "Fixed Fertilization"), ("tratamento_semente", "Seed Treatment"),
        ("plantio_direto", "Direct Planting"), ("plantio_com_adubacao", "Planting with Fertilization"),
        ("plantio_sem_adubacao", "Planting without Fertilization"), ("plantio_mudas", "Seedling Planting"),
        ("aerea_aviao", "Aerial (Airplane)"), ("autopropelido", "Self-Propelled"),
        ("implemento_barra", "Implement Bar"), ("drone", "Drone"), ("manual", "Manual")
    ])
    insumo = models.ForeignKey(Insumo, on_delete=models.SET_NULL, blank=True, null=True)
    quantidade_insumo = models.FloatField(blank=True, null=True)
    metodo_aplicacao = models.CharField(max_length=50, blank=True)
    area_aplicada = models.FloatField()
    custo_operacao = models.DecimalField(max_digits=10, decimal_places=2)
    responsavel = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, blank=True, null=True)
    pivo = models.ForeignKey(PivoCentral, on_delete=models.SET_NULL, blank=True, null=True)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, blank=True, null=True)
    implemento = models.ForeignKey(Implemento, on_delete=models.SET_NULL, blank=True, null=True)
    horas_equipamento = models.FloatField(blank=True, null=True)
    equipamento_terceiro = models.BooleanField(default=False)
    custo_aluguel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comentarios = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("pendente", "Pending"), ("aprovada", "Approved"), ("executada", "Executed")], default="pendente")
    data_prazo = models.DateField()
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)

    def clean(self):
        if self.pivo and self.cultura.area.tipo != "irrigada":
            raise ValidationError("Pivot can only be used in irrigated area.")
        if self.insumo and self.quantidade_insumo > self.insumo.quantidade_estoque:
            raise ValidationError("Input quantity exceeds stock.")
        if self.equipamento_terceiro and not self.custo_aluguel:
            raise ValidationError("Rental cost required for third-party equipment.")
        if self.tipo_manejo == "colheita" and not (self.equipamento or self.equipamento_terceiro):
            raise ValidationError("Harvest requires own or third-party equipment.")

    def __str__(self):
        return f"OS {self.numero} ({self.cultura.nome})"

class Manejo(models.Model):
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name="manejos")
    data_operacao = models.DateField(default=datetime.now)
    comentarios = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("pendente", "Pending"), ("aprovada", "Approved")], default="pendente")

    def clean(self):
        if self.ordem_servico.status != "aprovada":
            raise ValidationError("Service order must be approved before handling.")

    def __str__(self):
        return f"Handling {self.ordem_servico.numero} ({self.data_operacao})"

class RateioCusto(models.Model):
    cultura = models.ForeignKey(Cultura, on_delete=models.CASCADE)
    tipo_custo = models.CharField(max_length=50, choices=[
        ("depreciacao", "Depreciation"), ("combustivel", "Fuel"), 
        ("mao_de_obra", "Labor"), ("juros", "Interest")
    ])
    valor_rateado = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=datetime.now)
    descricao = models.TextField()
    transaction = models.ForeignKey(TransactionModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo_custo} ({self.cultura.nome})"

class ArmazenagemLocal(models.Model):
    nome = models.CharField(max_length=255)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)
    capacidade = models.FloatField()
    unidade_medida = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

class EstoqueProduto(models.Model):
    cultura = models.ForeignKey(Cultura, on_delete=models.CASCADE)
    quantidade = models.FloatField()
    unidade_medida = models.CharField(max_length=20)
    local = models.ForeignKey(ArmazenagemLocal, on_delete=models.CASCADE)

    def clean(self):
        if self.quantidade > self.local.capacidade:
            raise ValidationError("Quantity exceeds local capacity.")

    def __str__(self):
        return f"{self.cultura.nome} ({self.quantidade} {self.unidade_medida})"

class Contato(models.Model):
    tipo = models.CharField(max_length=50, choices=[
        ("fornecedor", "Supplier"), ("cliente", "Customer"), 
        ("prestador", "Service Provider"), ("fabricante", "Manufacturer"), ("outro", "Other")
    ])
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=14, blank=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.TextField(blank=True)
    observacao = models.TextField(blank=True)

    def clean(self):
        if self.cpf_cnpj and len(self.cpf_cnpj) not in [11, 14]:
            raise ValidationError("CPF must have 11 digits or CNPJ 14 digits.")

    def __str__(self):
        return self.nome

class Compra(models.Model):
    fornecedor = models.ForeignKey(Contato, on_delete=models.CASCADE)
    nfe_numero = models.CharField(max_length=44, blank=True)
    data_compra = models.DateField(default=datetime.now)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    xml_nfe = models.TextField(blank=True)
    condicoes_pagamento = models.CharField(max_length=50, choices=[("vista", "Cash"), ("prazo", "Credit")])
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)
    transaction = models.ForeignKey(TransactionModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"Purchase {self.nfe_numero} ({self.fornecedor.nome})"

class Venda(models.Model):
    colheita = models.ForeignKey(EstoqueProduto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Contato, on_delete=models.CASCADE)
    quantidade_vendida = models.FloatField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data_venda = models.DateField(default=datetime.now)
    nfe_numero = models.CharField(max_length=44, blank=True)
    nfe_serie = models.CharField(max_length=3, blank=True)
    nfe_data_emissao = models.DateField(blank=True, null=True)
    nfe_valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    xml_nfe = models.TextField(blank=True)
    condicoes_pagamento = models.CharField(max_length=50, choices=[("vista", "Cash"), ("prazo", "Credit")])
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, blank=True, null=True)
    transaction = models.ForeignKey(TransactionModel, on_delete=models.CASCADE)

    def clean(self):
        if self.quantidade_vendida > self.colheita.quantidade:
            raise ValidationError("Sold quantity exceeds stock.")

    def __str__(self):
        return f"Sale {self.nfe_numero} ({self.cliente.nome})"

class NFeConsulta(models.Model):
    cpf = models.CharField(max_length=14)
    data_consulta = models.DateTimeField(default=datetime.now)
    status = models.CharField(max_length=50)
    erro_mensagem = models.TextField(blank=True)
    ultimo_nsu = models.CharField(max_length=20)
    max_nsu = models.CharField(max_length=20)

    def __str__(self):
        return f"NF-e Query {self.cpf} ({self.data_consulta})"

class ContaBancaria(models.Model):
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=10)
    conta = models.CharField(max_length=20)
    tipo_conta = models.CharField(max_length=50)
    titular = models.CharField(max_length=255)
    cpf_cnpj_titular = models.CharField(max_length=14)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.banco} ({self.conta})"