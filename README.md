# ⚡ Pokédex TCG — Backend & Série Temporal de Preços

Backend de alta maturidade para catálogo, monitoramento de séries temporais de preços e gestão de portfólio do **Pokémon Trading Card Game físico**, construído com **Python 3.12+, FastAPI, SQLAlchemy 2.0, PostgreSQL 17, Redis 7 e Apache Kafka 3.8 (KRaft)**.

---

## 🏛️ Arquitetura e Decisões de Engenharia

O projeto foi estruturado sob os princípios de **Domain-Driven Design (DDD)** e **Clean Architecture (Hexagonal)**, separando estritamente os Bounded Contexts da aplicação:

### 1. Bounded Context de Catálogo & Mercado
- **Domínio Puro (DDD):** Regras de negócio sem dependências de frameworks. Distinção estrita entre `Entities` (identidade e ciclo de vida) e `Value Objects` imutáveis (`Money`, `PriceSnapshot`).
- **Precisão Financeira:** Preços nunca utilizam `float`. Toda a aritmética monetária é encapsulada em `Money` com precisão exata via `Decimal(10, 2)`.
- **Persistência Append-Only:** Cotações históricas nunca sofrem `UPDATE` ou `DELETE`, preservando a integridade cronológica para gráficos e séries temporais.
- **Idempotência no Catálogo:** Ingestão resiliente via Upsert atômico do PostgreSQL (`ON CONFLICT DO UPDATE`), impedindo duplicidade caso a sincronização seja reexecutada.
- **Performance com Cache-Aside (Redis):** Consultas de histórico com controle de TTL e estratégia *Fail-Open* (resiliência contra indisponibilidade temporária do Redis).
- **Arquitetura Orientada a Eventos com Apache Kafka (KRaft):** Detecção diária de volatilidade de mercado (> 10% em 24h) com emissão assíncrona no tópico `price-changed`, particionado por `card_id` e consumidor com idempotência via Redis (`SET ... NX`).

### 2. Bounded Context de Identidade & Portfólio do Usuário
- **Segurança de Nível Sênior:** Hashing de senhas com algoritmo moderno **Argon2id** (via `pwdlib`), proteção contra *timing attacks* e autenticação via padrão **OAuth2 Password Bearer** com tokens **JWT (PyJWT)**.
- **Portfólio Persistido:** Usuários salvam suas cartas físicas e quantidades no banco de dados.
- **Valuation em Tempo Real (Open/Closed Principle):** O endpoint `GET /portfolio` reutiliza o motor de cálculo da aplicação para consultar as cotações mais recentes e exibir o valor de mercado atualizado do patrimônio do colecionador.

---

## 📡 Endpoints da API

| Módulo | Método | Rota | Descrição | Autenticação |
|---|---|---|---|---|
| **Auth** | `POST` | `/auth/register` | Cadastro de novo usuário | Pública |
| **Auth** | `POST` | `/auth/login` | Login (OAuth2) e emissão de token JWT | Pública |
| **Cards** | `GET` | `/cards` | Listar catálogo com filtros e paginação | Pública (Rate Limit) |
| **Cards** | `GET` | `/cards/{id}/price-history` | Série temporal de preços (Cache Redis) | Pública (Rate Limit) |
| **Collection** | `POST` | `/collection/value` | Calculadora aberta de valor de cartas | Pública (Rate Limit) |
| **Portfolio** | `GET` | `/portfolio` | Patrimônio atualizado do usuário logado | **Bearer JWT** |
| **Portfolio** | `POST` | `/portfolio/items` | Adicionar carta à coleção salva | **Bearer JWT** |
| **Health** | `GET` | `/health` | Sonda de integridade da API | Pública |

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python 3.12+
- Docker e Docker Desktop

### 1. Inicializar os Serviços (PostgreSQL, Redis, Kafka)
```bash
docker compose up -d
```

### 2. Configurar o Ambiente Python
```bash
python -m venv .venv
```
Ativar o ambiente virtual:
- No Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
- No Linux/Mac: `source .venv/bin/activate`

Instalar as dependências:
```bash
python -m pip install -r requirements.txt
```

### 3. Rodar as Migrations do Banco
```bash
python -m alembic upgrade head
```

### 4. Executar os Testes Automatizados (24 testes)
```bash
python -m pytest
```

### 5. Iniciar a API com Documentação Swagger
```bash
python -m uvicorn src.infrastructure.web.main:app --reload --port 8000
```
Acesse a documentação interativa em: **http://localhost:8000/docs**