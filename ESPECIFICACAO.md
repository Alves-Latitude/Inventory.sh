# Especificação do Projeto — Inventário de Componentes de Servidores

**Versão:** 1.1  
**Data:** 2026-05-12  
**Status:** Rascunho aprovado

---

## 1. Visão Geral

Sistema web para controle de inventário de componentes de servidores distribuídos em múltiplos Data Centers (Colocations). O sistema permitirá o registro de entrada, rastreamento de status e histórico de descarte de componentes como discos e memórias RAM.

| Item | Detalhe |
|------|---------|
| Tipo | Aplicação web (acesso via navegador) |
| Idioma da interface | Português — PT-BR |
| Usuários esperados | ~30 |
| Empresa | Única (sem multi-tenancy) |
| Data Centers | Mais de 10 localizações |
| Hospedagem | Servidor interno Linux (Ubuntu/Debian/CentOS) |
| Prazo estimado | Alguns meses |
| Ponto de partida | Do zero — sem sistema legado a migrar |

---

## 2. Usuários e Perfis de Acesso

Existem dois perfis de usuário:

### Admin
- Cadastrar, editar e remover usuários (nome, e-mail, senha, perfil)
- Cadastrar e editar Data Centers
- **Cadastrar, editar e remover tipos de componentes**
- Configurar limites mínimos de estoque por tipo e por DC
- Tudo que o perfil **User** pode fazer

### User
- Visualizar o inventário de componentes
- Cadastrar novos componentes
- Editar informações de componentes existentes
- Registrar movimentações (entrada no DC e instalação)
- Gerar e exportar relatórios em CSV

---

## 3. Data Centers (Colocations)

Cada Data Center possui os seguintes dados:

| Campo | Obrigatório | Exemplo |
|-------|-------------|---------|
| Nome | Sim | "DC São Paulo 01" |
| Cidade / Endereço | Sim | "São Paulo, SP" |
| Identificador único (código) | Sim | "SP01" |
| Observações | Não | Campo de texto livre |

Os componentes do inventário sempre pertencem a um Data Center específico.

---

## 4. Gerenciamento de Tipos de Componentes

Os **tipos de componentes são configuráveis pelos admins**. O sistema começa pré-configurado com os tipos abaixo, mas admins podem adicionar novos tipos ou remover tipos sem uso.

### Tipos pré-configurados (com campos específicos)

| Tipo | Campos específicos |
|------|--------------------|
| Disco (HDD/SSD/NVMe) | Capacidade, Tipo (HDD/SSD/NVMe), Interface (SATA/SAS/NVMe) |
| Memória RAM | Capacidade, Tipo (DDR4/DDR5/ECC DDR4/ECC DDR5), Velocidade (MHz) |
| CPU (Processador) | *(apenas campos comuns)* |
| Fonte de Alimentação (PSU) | *(apenas campos comuns)* |

### Tipos adicionais criados por admins

Quando um admin cria um novo tipo (ex: "Placa de Rede", "GPU", "HBA"), esse tipo terá apenas os **campos comuns** mais um campo de texto livre **"Especificações"** para qualquer detalhe adicional.

> **Regra de remoção:** Um tipo de componente só pode ser removido se não houver nenhum componente cadastrado com aquele tipo.

---

## 5. Campos dos Componentes

### 5.1 Campos comuns (todos os tipos)

| Campo | Obrigatório | Valores / Exemplo |
|-------|-------------|-------------------|
| Tipo de componente | Sim | Seleção da lista de tipos cadastrados |
| Fabricante e Modelo | Sim | "Seagate Exos X18", "Kingston 16GB DDR4" |
| Status | Sim | Em estoque / Instalado / Defeituoso / Descartado |
| Data Center | Sim | Seleção da lista de DCs cadastrados |
| Data de entrada no estoque | Sim | Preenchida automaticamente |
| Observações | Não | Campo de texto livre |

### 5.2 Disco (HDD / SSD / NVMe) — campos específicos adicionais

| Campo | Obrigatório | Valores possíveis |
|-------|-------------|-------------------|
| Capacidade | Sim | 500GB, 1TB, 2TB, 4TB, 8TB, 12TB, 16TB, 18TB |
| Tipo | Sim | HDD / SSD / NVMe |
| Interface | Sim | SATA / SAS / NVMe |

### 5.3 Memória RAM — campos específicos adicionais

| Campo | Obrigatório | Valores possíveis |
|-------|-------------|-------------------|
| Capacidade | Sim | 8GB, 16GB, 32GB, 64GB, 128GB |
| Tipo | Sim | DDR4 / DDR5 / ECC DDR4 / ECC DDR5 |
| Velocidade | Sim | 2133MHz, 2400MHz, 2666MHz, 3200MHz, 4800MHz |

### 5.4 Tipos criados por admins — campo adicional

| Campo | Obrigatório | Exemplo |
|-------|-------------|---------|
| Especificações | Não | "10GbE, PCIe 3.0 x4, Dual Port" |

---

## 6. Fluxo de Vida de um Componente

```
[Compra / Recebimento]
         │
         ▼
  ENTRADA NO ESTOQUE ──────────────────────────────┐
  (componente entra no DC)                          │
  Status: "Em estoque"                              │
         │                                          │
         ▼                                          │
    INSTALAÇÃO                                      │
  (componente é instalado em um servidor)           │
  Status: "Instalado"                               │
  Campo: nome do servidor (texto livre)             │
         │                                          │
         ▼                                          │
  [Falha detectada / necessidade de troca]          │
         │                                          │
         ▼                                          │
    DEFEITUOSO ──► DESCARTADO                       │
  (componente antigo é marcado ao registrar         │
   a instalação do novo)                            │
         │                                          │
         ▼                                          │
  Novo componente vindo do estoque ─────────────────┘
```

### Movimentações registráveis

| Tipo | Descrição | O que acontece |
|------|-----------|----------------|
| Entrada no DC | Componente chega ao Data Center | Status muda para "Em estoque" |
| Instalação | Componente é instalado em um servidor | Status muda para "Instalado"; peça antiga fica como "Defeituosa" |

**Nota:** Ao registrar uma instalação, o usuário informa o nome do servidor (campo de texto livre, ex: `servidor-web-01`) — o servidor em si não é um cadastro do sistema.

---

## 7. Relatórios

| Relatório | Descrição | Filtros disponíveis |
|-----------|-----------|---------------------|
| Estoque atual por tipo | Quantidade de cada tipo disponível em estoque | DC, tipo de componente |
| Histórico de trocas | Quantas instalações foram realizadas em um período | DC, período (mês/trimestre/ano), tipo |
| Itens defeituosos e descartados | Lista de componentes que saíram de uso com data | DC, período, tipo |
| Inventário por Data Center | Todos os componentes de um DC específico | DC, status, tipo |

**Formato de exportação:** CSV (arquivo de planilha compatível com Excel e Google Sheets).

---

## 8. Alertas

### Estoque Mínimo
- Quando a quantidade de um tipo de componente em um DC específico cair abaixo de um **limite configurável pelo Admin**, o sistema emite um alerta.
- **Exemplo:** "DC São Paulo 01 está com menos de 5 discos SSD disponíveis."
- **Canais de alerta:**
  - **Banner na interface** — visível ao fazer login e navegar pelo sistema
  - **E-mail** — enviado para os admins quando o limite for atingido

---

## 9. Fora do Escopo — Versão 1

Os itens abaixo **não fazem parte** da primeira versão do sistema:

- Controle de racks e posições (unidades U)
- Número de série ou código patrimonial de componentes
- Multi-empresa / multi-cliente (o sistema é para uma única empresa)
- Cadastro de servidores (servidores são apenas um campo de texto na movimentação)
- Integração com outros sistemas externos
- App mobile (somente web)
- Controle de cabos e switches/roteadores

---

## 10. Premissas Técnicas Recomendadas

> **Recomendação:** Django + PostgreSQL + Docker, rodando no servidor Linux interno.

### Por que esta escolha?

| Ferramenta | O que é | Por que foi escolhida |
|------------|---------|----------------------|
| **Django** (Python) | O "motor" do sistema — processa as regras e salva os dados | Inclui um painel de administração pronto, envia e-mails nativamente, exporta CSV com facilidade; amplamente usado em sistemas corporativos |
| **PostgreSQL** | O banco de dados onde tudo é armazenado | Gratuito e open-source. Suporta múltiplos usuários escrevendo ao mesmo tempo (ao contrário do SQLite, que trava o arquivo a cada escrita — problemático com ~30 usuários simultâneos) |
| **Docker** | Empacota o sistema para fácil instalação | Com um único comando, o sistema inteiro sobe no servidor Linux; sem configuração manual de dependências |
| **NGINX** | "Portão de entrada" que recebe as requisições do navegador | Padrão de mercado para servir aplicações web em Linux |

### Como ficaria a instalação

```
Servidor Linux
└── Docker
    ├── Container: Django (sistema)
    ├── Container: PostgreSQL (banco de dados)
    └── Container: NGINX (acesso web)
```

Um desenvolvedor consegue colocar tudo no ar com poucos comandos após configurar o servidor.

---

## 11. Próximos Passos

- [x] Definir hospedagem → Servidor interno Linux
- [x] Definir canal de alertas → Banner na tela + e-mail para admins
- [x] Definir formato de exportação → CSV
- [x] Definir stack tecnológica → Django + PostgreSQL + Docker
- [ ] Definir os valores padrão de estoque mínimo por tipo e DC
- [ ] Criar wireframes / protótipos das telas principais
- [ ] Contratar ou designar um desenvolvedor
- [ ] Iniciar desenvolvimento: login, cadastro de DCs e tipos de componentes
