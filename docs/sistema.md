\# Documentação do Sistema Agropecuário



Sistema para gestão de fazendas em Gameleira de Goiás, com suporte a culturas como soja, milho, tomate, etc. Desenvolvido em Django com PyNFe, django-ledger e integração com IA (Grok 2.0).



\## Fluxo do Sistema

1\. \*\*Cadastro da Fazenda e Áreas\*\*: Registra fazendas e talhões com coordenadas e mapas Google Earth.

2\. \*\*Planejamento de Lavouras\*\*: Define culturas com validação de datas e sobreposição (5% tolerância).

3\. \*\*Operações de Manejo\*\*: Registra preparo, plantio, pulverização, colheita via app/WhatsApp com aprovação via IA.

4\. \*\*Manutenção de Máquinas\*\*: Calcula depreciação e custos.

5\. \*\*Colheita e Estoque\*\*: Atualiza estoque com validação de capacidade.

6\. \*\*Comercial e Financeiro\*\*: Gera NF-e e contas a pagar/receber.

7\. \*\*Relatórios\*\*: Custos e lucros por área/cultura.



\## Regras de Negócio

\- CPF/CNPJ: 11/14 dígitos.

\- Áreas arrendadas: Exigem proprietário e contrato.

\- Sobreposição: Até 5% com alerta.

\- Manejo: Ordem de serviço ou registro a posteriori com aprovação.

\- Estoque: Valida capacidade de armazenamento.

\- Financeiro: Rateio proporcional à área.



\## Comportamentos

\- Validações: Bloqueia datas inválidas, estoque insuficiente, etc.

\- Aprovações: Manejo exige validação do administrador via IA.

\- Relatórios: Recalcula totais por filtros.



\## Melhorias

\- Fluxo de caixa projetado.

\- Mapas interativos (Google Earth).

\- Alertas automáticos (WhatsApp/e-mail).

\- Integração Grok 2.0 para automação.



\## Fluxograma Geral

```mermaid

graph TD

&nbsp;   A\[Fazenda] --> B\[Áreas / Talhões<br>: mapas via Google Earth]

&nbsp;   B --> C\[Centros de Custo:<br> tipo\_area, propriedade]

&nbsp;   B --> D\[Culturas / Safras:<br> principal/safrinha, sobreposição com 5% tolerância]

&nbsp;   D --> E\[Manejo:<br>preparo, plantio, pulverização, manual, colheita]

&nbsp;   E --> F\[Ordem de Serviço:<br>planejada, funcionário, insumos, aprovação via Grok 2.0]

&nbsp;   E --> G\[Serviço Executado:<br>registro a posteriori, aprovação via Grok 2.0]

&nbsp;   F --> H\[Rateio de Custos:<br>depreciação, combustível, mão de obra, juros]

&nbsp;   G --> H

&nbsp;   E --> I\[Colheita:<br>máquinas próprias ou terceiros]

&nbsp;   I --> J\[Estoque / Armazenamento:<br>capacidade definida por silo]

&nbsp;   J --> K\[Venda / Comercial:<br>NF-e, XML]

&nbsp;   K --> L\[Financeiro:<br>contas a pagar/receber, quitação após vencimento]

&nbsp;   H --> L

&nbsp;   L --> M\[Relatórios:<br>por tipo\_area, propriedade, talhão]

