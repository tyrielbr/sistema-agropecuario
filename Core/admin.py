from django.contrib import admin
from .models import (
    Fazenda, CentroCusto, Area, Talhao, PivoCentral, Cultura, Insumo, Equipamento, 
    Implemento, Funcionario, OrdemServico, Manejo, RateioCusto, ArmazenagemLocal, 
    EstoqueProduto, Contato, Compra, Venda, NFeConsulta, ContaBancaria
)

@admin.register(Fazenda)
class FazendaAdmin(admin.ModelAdmin):
    list_display = ["nome", "cpf_cnpj", "cidade", "estado"]

@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ["nome", "fazenda", "tipo_area", "propriedade"]

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ["nome", "fazenda", "tipo", "tamanho", "permite_sobreposicao"]

@admin.register(Talhao)
class TalhaoAdmin(admin.ModelAdmin):
    list_display = ["nome", "area", "tamanho"]

@admin.register(PivoCentral)
class PivoCentralAdmin(admin.ModelAdmin):
    list_display = ["nome", "area", "area_coberta"]

@admin.register(Cultura)
class CulturaAdmin(admin.ModelAdmin):
    list_display = ["nome", "area", "safra", "data_plantio"]

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo", "quantidade_estoque"]

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ["nome", "fazenda", "tipo", "marca", "ano"]

@admin.register(Implemento)
class ImplementoAdmin(admin.ModelAdmin):
    list_display = ["nome", "fazenda", "tipo"]

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ["nome", "fazenda", "funcao"]

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ["numero", "cultura", "tipo_manejo", "status", "data_prazo"]

@admin.register(Manejo)
class ManejoAdmin(admin.ModelAdmin):
    list_display = ["ordem_servico", "data_operacao", "status"]

@admin.register(RateioCusto)
class RateioCustoAdmin(admin.ModelAdmin):
    list_display = ["cultura", "tipo_custo", "valor_rateado", "data"]

@admin.register(ArmazenagemLocal)
class ArmazenagemLocalAdmin(admin.ModelAdmin):
    list_display = ["nome", "fazenda", "capacidade"]

@admin.register(EstoqueProduto)
class EstoqueProdutoAdmin(admin.ModelAdmin):
    list_display = ["cultura", "quantidade", "local"]

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo", "cpf_cnpj"]

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ["fornecedor", "nfe_numero", "data_compra"]

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ["cliente", "nfe_numero", "data_venda"]

@admin.register(NFeConsulta)
class NFeConsultaAdmin(admin.ModelAdmin):
    list_display = ["cpf", "data_consulta", "status"]

@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ["banco", "conta", "titular"]