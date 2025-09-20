# Fluxo do Sistema Agropecuário

Este documento descreve o fluxo textual do **Sistema Agropecuário**, desenvolvido em Django para gestão de fazendas em Gameleira de Goiás, com suporte a culturas como soja, milho, tomate, entre outras. O sistema integra módulos para Comercial/NF-e, Financeiro, Agrícola (Manejo), Fazendas (Áreas/Talhões), Estoque, Administrativo (Centros de Custos), Máquinas/Implementos e Interface com IA (Grok 2.0). Ele utiliza bibliotecas como PyNFe para emissão de notas fiscais, django-ledger para contabilidade e python-decouple para configuração segura.

## Fluxo Geral do Sistema

O sistema gerencia o ciclo completo de uma fazenda, desde o cadastro de propriedades até a geração de relatórios financeiros e agrícolas. O fluxo começa com o cadastro de fazendas e áreas, passa pelo planejamento e execução de safras, manejo, colheita, estoque, vendas e contabilidade, com validações automáticas e aprovações via IA. Abaixo, detalhamos cada etapa e módulo.

1. **Cadastro da Fazenda e Áreas**:
   - O usuário cadastra fazendas com informações como nome, localização e coordenadas geográficas.
   - Áreas e talhões são registrados com mapas interativos (Google Earth), incluindo validação de sobreposição (tolerância de 5%).
   - Áreas arrendadas exigem dados do proprietário e contrato.

2. **Planejamento de Lavouras**:
   - Define culturas (ex.: soja, milho) e safras (principal ou safrinha), com validação de datas para evitar conflitos sazonais.
   - Associa talhões a culturas, verificando compatibilidade de solo e clima.

3. **Operações de Manejo**:
   - Registra atividades como preparo do solo, plantio, pulverização e colheita.
   - Suporta ordens de serviço planejadas ou registros a posteriori via app, WhatsApp ou integração com Grok 2.0.
   - Cada operação é validada (ex.: tipo de manejo, insumos disponíveis) e aprovada pelo administrador, com suporte de IA para sugestões.

4. **Manutenção de Máquinas**:
   - Registra máquinas e implementos, calculando depreciação e custos de manutenção.
   - Associa uso em operações de manejo ou colheita, com rateio de custos.

5. **Colheita e Estoque**:
   - A colheita é registrada, atualizando o estoque automaticamente com validação de capacidade de armazenamento (silos).
   - Alertas são gerados para estoque baixo ou excedente.

6. **Comercial e Financeiro**:
   - Gera e valida NF-e (via PyNFe) para vendas e compras, integrando com o módulo de estoque.
   - Registra contas a pagar/receber no django-ledger, com rateio de custos (ex.: depreciação, juros) e relatórios de fluxo de caixa.

7. **Relatórios**:
   - Gera relatórios detalhados por área, talhão, cultura, período ou centro de custo.
   - Inclui análises de custos, lucros e produtividade, com filtros dinâmicos.

## Detalhes por Módulo

### Comercial e NF-e
- **Descrição**: Gerencia vendas e compras, emitindo e validando Notas Fiscais Eletrônicas (NF-e) via PyNFe.
- **Fluxo**:
  1. Cadastro de fornecedores/clientes (CPF/CNPJ com 11/14 dígitos).
  2. Registro de compra/venda com detalhes do produto e condições de pagamento.
  3. Consulta e validação de NF-e (XML) via PyNFe.
  4. Atualização automática do estoque após validação.
  5. Registro de transações financeiras (contas a pagar/receber).
  6. Geração de relatórios de vendas/compras.
  7. Envio de notificações ao administrador.
- **Regras**:
  - CPF/CNPJ deve ser válido.
  - NF-e exige validação antes de atualizar estoque ou financeiro.
- **Comportamentos**:
  - Bloqueia transações com dados inválidos (ex.: CPF incorreto).
  - Notifica administrador para aprovações manuais, se necessário.

### Financeiro
- **Descrição**: Controla contas a pagar/receber e fluxo de caixa, usando django-ledger.
- **Fluxo**:
  1. Recebe transações de outros módulos (ex.: compras, manejo).
  2. Registra contas a pagar/receber com anexos (ex.: boletos).
  3. Processa quitações com alertas de vencimento.
  4. Realiza rateio de custos (depreciação, juros, mão de obra).
  5. Calcula fluxo de caixa real e projetado.
  6. Gera relatórios financeiros por período.
  7. Envia alertas via IA (Grok 2.0) para vencimentos ou inconsistências.
- **Regras**:
  - Rateio proporcional à área ou talhão.
  - Quitações exigem confirmação documental.
- **Comportamentos**:
  - Bloqueia quitações com dados incompletos.
  - Recalcula totais automaticamente ao aplicar filtros.

### Agrícola (Manejo)
- **Descrição**: Gerencia operações agrícolas (preparo, plantio, pulverização, colheita).
- **Fluxo**:
  1. Cria ordens de serviço planejadas ou registra serviços a posteriori (via app/WhatsApp/Grok 2.0).
  2. Valida procedimento e tipo de manejo (ex.: insumos compatíveis).
  3. Envia para aprovação do administrador, com sugestões da IA.
  4. Atualiza estoque e rateia custos após aprovação.
  5. Gera relatórios de manejo por área/talhão.
- **Regras**:
  - Ordens de serviço exigem funcionário e insumos associados.
  - Aprovação obrigatória para execução.
- **Comportamentos**:
  - Bloqueia manejo com datas inválidas ou insumos insuficientes.
  - Notifica administrador para revisões.

### Fazendas (Áreas e Talhões)
- **Descrição**: Gerencia fazendas, áreas e talhões com mapas interativos.
- **Fluxo**:
  1. Cadastra fazendas com coordenadas.
  2. Registra áreas e talhões, validando sobreposição (tolerância de 5%).
  3. Associa talhões a centros de custo.
  4. Integra mapas Google Earth para visualização.
  5. Gera relatórios por área/talhão.
- **Regras**:
  - Áreas arrendadas exigem proprietário e contrato.
  - Sobreposição acima de 5% gera alerta.
- **Comportamentos**:
  - Bloqueia cadastros com coordenadas inválidas.
  - Atualiza mapas automaticamente.

### Estoque
- **Descrição**: Controla insumos e produtos armazenados.
- **Fluxo**:
  1. Registra entrada de insumos/produtos.
  2. Valida movimentações contra capacidade de armazenamento.
  3. Atualiza quantidades automaticamente.
  4. Gera alertas para estoque baixo ou excedente.
  5. Produz relatórios por local de armazenamento.
- **Regras**:
  - Capacidade de silos/armazéns é fixa.
  - Movimentações exigem validação.
- **Comportamentos**:
  - Bloqueia entradas se capacidade for excedida.
  - Notifica estoque baixo automaticamente.

### Administrativo (Centros de Custos)
- **Descrição**: Gerencia rateio de custos por centros (ex.: tipo de área, propriedade).
- **Fluxo**:
  1. Cadastra centros de custo.
  2. Associa custos de outros módulos (ex.: manejo, máquinas).
  3. Valida alocação de despesas.
  4. Gera relatórios filtrados por área/talhão.
- **Regras**:
  - Rateio proporcional à área ou atividade.
  - Validação obrigatória para alocação.
- **Comportamentos**:
  - Recalcula rateios dinamicamente.
  - Bloqueia alocações inválidas.

### Máquinas e Implementos
- **Descrição**: Gerencia máquinas, depreciação e manutenção.
- **Fluxo**:
  1. Cadastra máquinas/implementos.
  2. Registra uso em manejo ou colheita.
  3. Calcula depreciação e consumo (ex.: combustível).
  4. Gera ordens de serviço para manutenção.
  5. Produz relatórios de uso e custos.
  6. Rateia custos para o financeiro.
- **Regras**:
  - Depreciação baseada em tempo/uso.
  - Manutenção exige ordem de serviço.
- **Comportamentos**:
  - Bloqueia uso de máquinas em manutenção.
  - Atualiza custos automaticamente.

### Interface (Front-end com IA)
- **Descrição**: Integra inputs do usuário com Grok 2.0 para automação.
- **Fluxo**:
  1. Recebe inputs via app, web ou WhatsApp.
  2. Processa via Grok 2.0 para validação ou sugestões.
  3. Envia para aprovação do administrador.
  4. Atualiza módulos (manejo, estoque, financeiro).
  5. Gera dashboards e relatórios.
  6. Envia notificações/alertas.
- **Regras**:
  - Aprovação obrigatória para ações críticas.
  - Inputs via IA exigem validação.
- **Comportamentos**:
  - Gera alertas automáticos (ex.: vencimentos, estoque baixo).
  - Recalcula dashboards dinamicamente.

## Regras de Negócio
- **CPF/CNPJ**: 11 dígitos (CPF) ou 14 dígitos (CNPJ), com validação de formato.
- **Áreas arrendadas**: Exigem proprietário e contrato registrado.
- **Sobreposição de áreas**: Tolerância de 5%, com alerta para valores maiores.
- **Manejo**: Ordens de serviço ou registros a posteriori exigem aprovação do administrador.
- **Estoque**: Valida capacidade de silos/armazéns antes de entradas/saídas.
- **Financeiro**: Rateio de custos proporcional à área ou talhão; quitações exigem anexos.
- **Datas**: Validação para evitar conflitos sazonais ou datas inválidas.

## Comportamentos do Sistema
- **Validações**: Bloqueia ações com dados inválidos (ex.: CPF incorreto, estoque insuficiente, datas fora do período).
- **Aprovações**: Operações críticas (ex.: manejo, NF-e) exigem aprovação do administrador, com suporte de IA.
- **Relatórios**: Recalcula totais automaticamente com base em filtros (ex.: área, período).
- **Notificações**: Alertas para estoque baixo, vencimentos financeiros ou inconsistências, via app/WhatsApp/e-mail.
- **Integração com IA**: Grok 2.0 sugere aprovações e valida inputs automaticamente.

## Melhorias Propostas
- **Fluxo de Caixa Projetado**: Incluir projeções baseadas em histórico e safras futuras.
- **Mapas Interativos**: Melhorar integração com Google Earth para visualização em tempo real.
- **Alertas Automáticos**: Implementar notificações via WhatsApp/e-mail para eventos críticos.
- **Integração com Grok 2.0**: Expandir automação para sugestões de manejo e análise preditiva de custos.
- **Relatórios Avançados**: Adicionar gráficos interativos e exportação para PDF/Excel.

## Notas Técnicas
- **Tecnologias**: Django 4.2.16, PyNFe 0.6.0, django-ledger 0.7.10, python-decouple 3.8, PostgreSQL.
- **Ambiente**: Configurado para deploy em Heroku com PostgreSQL (essential-0).
- **Repositório**: [github.com/tyrielbr/sistema-agropecuario](https://github.com/tyrielbr/sistema-agropecuario).