from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ledger.models.transactions import TransactionModel
from .models import OrdemServico, Manejo, RateioCusto, Compra, Venda, EstoqueProduto
from datetime import datetime

@receiver(post_save, sender=OrdemServico)
def processar_ordem_servico(sender, instance, created, **kwargs):
    if created and instance.status == "aprovada":
        if instance.equipamento and instance.horas_equipamento:
            tx = TransactionModel.objects.create(
                ledger=instance.centro_custo.ledger,
                account=AccountModel.objects.get(name="Depreciation"),
                amount=instance.equipamento.valor_compra * 0.1 / 1000 * instance.horas_equipamento,
                tx_type="debit",
                description=f"Depreciation {instance.equipamento.nome}"
            )
            RateioCusto.objects.create(
                cultura=instance.cultura,
                tipo_custo="depreciacao",
                valor_rateado=tx.amount,
                data=datetime.now().date(),
                descricao=f"Depreciation {instance.equipamento.nome}",
                transaction=tx
            )
            if instance.equipamento.consumo_combustivel:
                tx_fuel = TransactionModel.objects.create(
                    ledger=instance.centro_custo.ledger,
                    account=AccountModel.objects.get(name="Fuel"),
                    amount=instance.equipamento.consumo_combustivel * instance.horas_equipamento * 5.0,
                    tx_type="debit",
                    description=f"Fuel {instance.equipamento.nome}"
                )
                RateioCusto.objects.create(
                    cultura=instance.cultura,
                    tipo_custo="combustivel",
                    valor_rateado=tx_fuel.amount,
                    data=datetime.now().date(),
                    descricao=f"Fuel {instance.equipamento.nome}",
                    transaction=tx_fuel
                )
        if instance.responsavel:
            tx_labor = TransactionModel.objects.create(
                ledger=instance.centro_custo.ledger,
                account=AccountModel.objects.get(name="Labor"),
                amount=instance.custo_operacao * 0.3,
                tx_type="debit",
                description=f"Labor {instance.responsavel.nome}"
            )
            RateioCusto.objects.create(
                cultura=instance.cultura,
                tipo_custo="mao_de_obra",
                valor_rateado=tx_labor.amount,
                data=datetime.now().date(),
                descricao=f"Labor {instance.responsavel.nome}",
                transaction=tx_labor
            )
        if instance.equipamento_terceiro and instance.custo_aluguel:
            tx_rental = TransactionModel.objects.create(
                ledger=instance.centro_custo.ledger,
                account=AccountModel.objects.get(name="Equipment Rental"),
                amount=instance.custo_aluguel,
                tx_type="debit",
                description="Third-party equipment rental"
            )
            RateioCusto.objects.create(
                cultura=instance.cultura,
                tipo_custo="aluguel_equipamento",
                valor_rateado=tx_rental.amount,
                data=datetime.now().date(),
                descricao="Third-party equipment rental",
                transaction=tx_rental
            )

@receiver(post_save, sender=Manejo)
def processar_manejo(sender, instance, created, **kwargs):
    if created and instance.status == "aprovada":
        if instance.ordem_servico.insumo and instance.ordem_servico.quantidade_insumo:
            instance.ordem_servico.insumo.quantidade_estoque -= instance.ordem_servico.quantidade_insumo
            instance.ordem_servico.insumo.save()
        tx = TransactionModel.objects.create(
            ledger=instance.ordem_servico.centro_custo.ledger,
            account=AccountModel.objects.get(name="Operating Expenses"),
            amount=instance.ordem_servico.custo_operacao,
            tx_type="debit",
            description=f"Handling operation {instance.ordem_servico.numero}"
        )
        instance.ordem_servico.cultura.rateio_custo.create(
            tipo_custo="operacao",
            valor_rateado=tx.amount,
            data=datetime.now().date(),
            descricao=f"Handling {instance.ordem_servico.numero}",
            transaction=tx
        )

@receiver(post_save, sender=Venda)
def processar_venda(sender, instance, created, **kwargs):
    if created:
        instance.colheita.quantidade -= instance.quantidade_vendida
        instance.colheita.save()
        tx = TransactionModel.objects.create(
            ledger=instance.centro_custo.ledger,
            account=AccountModel.objects.get(name="Revenue"),
            amount=instance.quantidade_vendida * instance.preco_unitario,
            tx_type="credit",
            description=f"Sale {instance.nfe_numero}"
        )
        instance.centro_custo.rateio_custo.create(
            cultura=instance.colheita.cultura,
            tipo_custo="venda",
            valor_rateado=tx.amount,
            data=instance.data_venda,
            descricao=f"Sale {instance.nfe_numero}",
            transaction=tx
        )

@receiver(post_save, sender=Compra)
def processar_compra(sender, instance, created, **kwargs):
    if created:
        tx = TransactionModel.objects.create(
            ledger=instance.centro_custo.ledger,
            account=AccountModel.objects.get(name="Purchases"),
            amount=instance.valor_total,
            tx_type="debit",
            description=f"Purchase {instance.nfe_numero}"
        )
        instance.centro_custo.rateio_custo.create(
            cultura=None,
            tipo_custo="compra",
            valor_rateado=tx.amount,
            data=instance.data_compra,
            descricao=f"Purchase {instance.nfe_numero}",
            transaction=tx
        )