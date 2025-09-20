# Sistema Agropecuário

Sistema em Django para gestão de fazendas, com módulos para Comercial/NF-e, Financeiro, Agrícola (Manejo), Fazendas (Áreas/Talhões), Estoque, Administrativo (Centros de Custos), Máquinas/Implementos e Interface com IA (Grok 2.0). Desenvolvido para fazendas em Gameleira de Goiás, com suporte a culturas como soja, milho, tomate, etc.

## Funcionalidades
- **Comercial/NF-e**: Emissão e validação de NF-e via PyNFe.
- **Financeiro**: Contas a pagar/receber com django-ledger.
- **Agrícola**: Manejo (preparo, plantio, colheita) com ordens de serviço e aprovação via IA.
- **Fazendas**: Gestão de áreas/talhões com mapas Google Earth.
- **Estoque**: Controle de insumos e produtos.
- **Administrativo**: Rateio de custos por centros.
- **Máquinas**: Depreciação e manutenção.
- **Interface**: Front-end com integração a IA (Grok 2.0).

## Instalação
1. Clone o repositório: `git clone https://github.com/tyrielbr/sistema-agropecuario.git`
2. Crie ambiente virtual: `python -m venv venv`
3. Instale dependências: `pip install -r requirements.txt`
4. Configure banco PostgreSQL e `settings.py`.
5. Rode migrations: `python manage.py migrate`
6. Inicie: `python manage.py runserver`

## Documentação Completa
- [Fluxogramas dos Módulos](docs/fluxogramas.md)
- [Detalhes do Sistema](docs/sistema.md)

## Licença
MIT