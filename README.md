# ⚡ Pokédex TCG — Backend & Série Temporal de Preços

Backend de alta maturidade para catálogo e monitoramento de séries temporais de preços do **Pokémon Trading Card Game físico**, construído com **Python, FastAPI, SQLAlchemy 2.0, PostgreSQL, Redis e Apache Kafka**.

---

## 🏛️ Arquitetura e Decisões de Engenharia

O projeto foi desenhado sob os princípios de **Domain-Driven Design (DDD)** e **Clean Architecture (Hexagonal)**:

- **Domínio Puro (DDD):** Regras de negócio isoladas sem dependências de frameworks. Distinção estrita entre `Entities` (identidade e ciclo de vida) e `Value Objects` imutáveis (`Money`, `PriceSnapshot`).
- **Precisão Financeira:** Preços nunca utilizam `float`. Toda a aritmética é encapsulada em `Money` com `Decimal(10, 2)`.
- **Persistência Append-Only:** Cotações históricas nunca sofrem `UPDATE` ou `DELETE`, preservando a integridade cronológica para análise de mercado e gráficos.
- **Idempotência (PostgreSQL ON CONFLICT):** Ingestão de catálogo resiliente com Upsert atômico, garantindo que execuções repetidas não gerem duplicações.
- **Cache-Aside com Redis:** Consultas de histórico com controle de TTL e estratégia *Fail-Open* (resiliência contra indisponibilidade do Redis).
- **Event-Driven Architecture com Apache Kafka (KRaft):** Detecção de volatilidade (> 10% em 24h) com disparo assíncrono no tópico `price-changed`, particionado por `card_id` e consumidor com idempotência via Redis (`SET ... NX`).
- **Segurança:** Proteção de endpoints contra abuso via Rate Limiting em Redis.

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

### 4. Executar os Testes Automatizados (22 testes)
```bash
python -m pytest
```

### 5. Iniciar a API com Documentação Swagger
```bash
python -m uvicorn src.infrastructure.web.main:app --reload --port 8000
```
Acesse a documentação interativa em: **http://localhost:8000/docs**