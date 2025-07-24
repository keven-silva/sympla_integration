# 🧩 Integração de Eventos Sympla

Serviço containerizado em **Django** para importar, validar e armazenar eventos da API pública da Sympla. Projetado com TDD, validação desacoplada via **Pydantic** e arquitetura resiliente orientada a serviços.

---

## ✅ Funcionalidades

- 🔄 **ETL Completo**: Extrai, transforma e carrega eventos da Sympla para um banco PostgreSQL.
- 🛡️ **Validação Robusta**: Usa Pydantic para garantir integridade dos dados e tratar eventos online/presenciais.
- 🗃️ **Versionamento de Cargas**: Cada execução é registrada com um modelo `LoadBatch` auditável.
- 🚫 **Deduplicação**: Evita registros duplicados via `event_id`.
- 🧾 **API REST**: Exposição dos eventos em endpoint de leitura.
- 📄 **Logging Abrangente**: Registra erros, eventos ignorados e importações com sucesso.
- 🐳 **Ambiente Dockerizado**: Django + PostgreSQL + Nginx via Docker Compose.
- 🧪 **Testes Automatizados**: Desenvolvido com TDD e cobertura para serviços, comandos, modelos e validações.

---

## 🛠️ Arquitetura e Tecnologias

| Tecnologia     | Papel                                           |
|----------------|--------------------------------------------------|
| Django + DRF   | Backend e API REST                              |
| Pydantic       | Validação de dados de entrada                   |
| PostgreSQL     | Banco de dados relacional                       |
| Docker Compose | Orquestração dos contêineres                    |
| Nginx          | Proxy reverso, performance e escalabilidade     |
| Pytest         | Testes automatizados com TDD                    |

---

## 🚀 Iniciando o Projeto

### Pré-requisitos

- [Git](https://git-scm.com/)
- Python 3.12+
- Docker e Docker Compose (para execução em contêiner)

---

### 🔧 Opção 1: Execução Local com SQLite

#### Usando Poetry (Recomendado)

```bash
git clone https://github.com/keven-silva/sympla_integration.git
cd sympla_integration

cp .env.local.example .env  # Adicione o token da API Sympla

poetry install
poetry shell
python manage.py migrate
python manage.py import_sympla_events
python manage.py runserver
```
Acesse: http://localhost:8000/api/events/

### 🐳 Opção 2: Execução com Docker (Ambiente Dockerizado)

```bash
git clone https://github.com/keven-silva/sympla_integration.git
cd sympla_integration

cp .env.docker.example .env  # Adicione o token da API

docker-compose up --build -d
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py import_sympla_events
```
Acesse:

  - API: `http://localhost/api/events/`

  - Documentação Swagger: `http://localhost/swagger/`

### 🧪 Rodando os Testes

  - Localmente:
    ```bash
    pytest
    ```
  - Com Docker:
    ```bash
    docker-compose exec app pytest
    ```

### 🧠 Justificativas Técnicas

- **Camada de Serviço Isolada:** Facilita testes, manutenção e aderência ao SRP.

- **Validação com Pydantic:** Separação clara da lógica de negócios e schemas, com mensagens de erro descritivas.

- **Versionamento com LoadBatch:** Permite rastrear execuções, depurar e manter histórico confiável.

- **Nginx + Docker:** Performance otimizada, escalabilidade e facilidade de setup com um comando.