# ⚡ Pokédex TCG — Backend & Série Temporal de Preços

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-3.8_KRaft-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-24_Passed-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Security](https://img.shields.io/badge/Security-JWT_%26_Argon2id-critical?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

Backend de alta maturidade para catálogo, monitoramento de séries temporais de preços e gestão de portfólio do **Pokémon Trading Card Game físico**, construído com **Python 3.12+, FastAPI, SQLAlchemy 2.0, PostgreSQL 17, Redis 7 e Apache Kafka 3.8 (KRaft)**.

---

## 🏛️ Arquitetura e Decisões de Engenharia

O projeto foi estruturado sob os princípios de **Domain-Driven Design (DDD)** e **Clean Architecture (Hexagonal)**, separando estritamente os Bounded Contexts