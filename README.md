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

| Tecnologia     | Papel                                       |
| -------------- | ------------------------------------------- |
| Django + DRF   | Backend e API REST                          |
| Pydantic       | Validação de dados de entrada               |
| PostgreSQL     | Banco de dados relacional                   |
| Docker Compose | Orquestração dos contêineres                |
| Nginx          | Proxy reverso, performance e escalabilidade |
| Pytest         | Testes automatizados com TDD                |

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


## 🔌 Extensibilidade: Adaptando para Novas APIs e Endpoints

A arquitetura deste projeto foi desenhada de forma modular para permitir a integração com novas fontes de dados (outras APIs) ou novos endpoints da mesma API (como "eventos passados") com o mínimo de esforço. A chave para essa extensibilidade está na separação de responsabilidades:

-   **Camada de Serviço (`services`):** Cuida de toda a comunicação com a API externa.
-   **Camada de Validação (`schemas`):** Define a estrutura de dados esperada da API e a valida.
-   **Comando (`management/commands`):** Orquestra o fluxo: chama o serviço, valida os dados e os mapeia para o nosso modelo de banco de dados.
-   **Modelo (`models`):** É a nossa representação interna e canônica de um evento, independente da fonte.

---

### **Cenário: Adicionar uma API Completamente Nova (Ex: Eventbrite)**

Este cenário demonstra o poder total da arquitetura de camadas.

1.  **Crie um Novo Serviço (`eventbrite_service.py`):**
    Crie um arquivo `apps/events/services/eventbrite_service.py`. Esta nova classe, `EventbriteService`, será responsável por toda a lógica específica da Eventbrite:
    -   URL base diferente.
    -   Método de autenticação diferente (ex: outro header, OAuth).
    -   Lógica de paginação diferente (ex: parâmetros de query diferentes).
    O importante é que seu método público, `fetch_events()`, ainda retorne uma lista de dicionários, no formato que a API da Eventbrite fornecer.

2.  **Crie um Novo Schema de Validação (`EventbriteEventSchema`):**
    Os dados da Eventbrite terão uma estrutura diferente. Portanto, em `apps/events/schemas.py`, crie um novo schema Pydantic:
    ```python
    # apps/events/schemas.py
    class EventbriteEventSchema(BaseModel):
        id: str
        name: dict # Na Eventbrite, o nome pode ser um objeto com {'text': 'Nome do Evento'}
        start: dict # Pode ser um objeto com {'timezone': '...', 'local': '...'}
        # ... outros campos específicos da Eventbrite

        @field_validator('name', mode='before')
        def get_name_text(cls, value):
            return value.get('text', '') if isinstance(value, dict) else value
        
        # ... outros validadores ...
    ```

3.  **Crie um Novo Comando (`import_eventbrite_events.py`):**
    Este novo comando irá orquestrar o fluxo para a nova API:
    -   Importará e instanciará o `EventbriteService`.
    -   Usará o `EventbriteEventSchema` para validar os dados.
    -   **Mapeará** os dados validados da Eventbrite para o nosso modelo `Event`.

4.  **Mapeie os Dados para o Modelo Canônico:**
    Dentro do novo comando, após a validação, você fará o mapeamento final. Isso garante que, independentemente da fonte, os dados sejam armazenados de forma consistente em nosso banco de dados.

    ```python
    # dentro do novo comando import_eventbrite_events.py
    # ...
    validated_event = EventbriteEventSchema.model_validate(event_data)

    Event.objects.update_or_create(
        # Criamos um ID único para evitar colisões com IDs da Sympla
        event_id=f"eventbrite-{validated_event.id}",
        defaults={
            'name': validated_event.name,
            'start_date': validated_event.start['local'], # Exemplo
            # ... mapeamento de outros campos ...
            'load_batch': batch, # O lote de carga é reutilizado
        }
    )
    ```