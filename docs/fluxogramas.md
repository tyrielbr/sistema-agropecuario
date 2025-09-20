# Fluxogramas dos Módulos do Sistema Agropecuário

Abaixo estão os fluxogramas de cada módulo, descrevendo o fluxo de informações. Copie para [mermaid.live](https://mermaid.live) para visualização.

## Comercial e NF-e
```mermaid
graph LR
    A[Cadastro Fornecedor/Cliente] --> B[Registro Compra/Venda]
    B --> C[Consulta NF-e via PyNFe]
    C --> D[Validação Pagamento/Condições]
    D --> E[Atualização Estoque]
    D --> F[Transação em Financeiro]
    F --> G[Relatório Vendas/Compras]
    E --> G
    G --> H[Notificação Administrador]
```

## Financeiro
```mermaid
graph LR
    A[Transações de Outros Módulos] --> B[Registro Conta Pagar/Receber]
    B --> C[Quitação com Anexo/Alerta]
    C --> D[Rateio Custos (Depreciação/Juros)]
    D --> E[Cálculo Fluxo Caixa Real/Projetado]
    E --> F[Relatório por Período]
    F --> G[Alerta Vencimento/Notificação IA]
```

## Agrícola (Manejo)
```mermaid
graph LR
    A[Ordem de Serviço Planeada] --> C[Registro via App/WhatsApp/Grok 2.0]
    B[Serviço Executado a Posteriori] --> C
    C --> D[Validação Procedimento/Tipo Manejo]
    D --> E[Aprovação Administrador]
    E --> F[Rateio Custos/Atualização Estoque]
    F --> G[Relatório Manejo por Área/Talhão]
```

## Fazendas (Áreas e Talhões)
```mermaid
graph LR
    A[Cadastro Fazenda] --> B[Registro Áreas/Talhões]
    B --> C[Validação Sobreposição/Tamanho (5% tolerância)]
    C --> D[Associação Centros de Custo]
    D --> E[Mapa Interativo (Google Earth)]
    E --> F[Relatório por Área/Talhão]
```

## Estoque
```mermaid
graph LR
    A[Entrada Insumos/Produtos] --> B[Movimentação Estoque]
    B --> C[Validação Capacidade Armazenamento]
    C --> D[Atualização Automática Quantidade]
    D --> E[Alerta Estoque Baixo]
    E --> F[Relatório Estoque por Local]
```

## Administrativo (Centros de Custos)
```mermaid
graph LR
    A[Cadastro Centros de Custo] --> B[Distinção por Tipo Área/Propriedade]
    B --> C[Rateio Custos entre Módulos]
    C --> D[Validação Alocação Despesas]
    D --> E[Relatório Filtrado por Área/Talhão]
```

## Máquinas e Implementos
```mermaid
graph LR
    A[Cadastro Máquinas/Implementos] --> B[Registro Uso em Manejo/Colheita]
    B --> C[Cálculo Depreciação/Consumo]
    C --> D[Manutenção / Ordens de Serviço]
    D --> E[Relatório Uso e Custos]
    E --> F[Rateio para Financeiro]
```

## Interface (Front-end com IA)
```mermaid
graph LR
    A[Input Usuário (App/Web/WhatsApp)] --> B[Processamento via Grok 2.0]
    B --> C[Aprovação Administrador]
    C --> D[Atualização Módulos (Manejo, Estoque, Financeiro)]
    D --> E[Dashboards / Relatórios]
    E --> F[Notificações / Alertas]
    F --> A
```

## Fluxograma Geral
```mermaid
graph LR
    A[Fazendas (Áreas/Talhões)] --> B[Agrícola (Manejo)]
    A --> C[Máquinas/Implementos]
    B --> D[Estoque]
    B --> E[Administrativo (Centros de Custo)]
    C --> B
    D --> F[Comercial / NFE]
    E --> G[Financeiro]
    F --> G
    H[Módulo Interface / IA] --> A
    H --> B
    H --> F
    H --> G
    G --> H
```