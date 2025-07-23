# Integração de Eventos Sympla

Um serviço robusto e containerizado em Django para extrair, processar e armazenar dados de eventos da API pública da Sympla. O projeto é projetado com boas práticas, como TDD, uma camada de serviço isolada e um sistema de validação de dados desacoplado e resiliente.

## 📋 Conformidade com os Critérios de Avaliação

Este projeto foi desenvolvido para atender aos seguintes critérios de avaliação:

-   ✅ **Consumo correto e robusto de APIs:** Implementada uma camada de serviço resiliente com tratamento de erros (timeouts, erros HTTP), gerenciamento seguro de token e paginação automática.
-   ✅ **Tratamento e validação dos dados extraídos:** Utiliza **Pydantic** para definir esquemas de dados explícitos, garantindo que os dados da API sejam validados, tipados e normalizados antes de serem processados. O sistema lida com diferentes tipos de eventos (ex: presenciais vs. online) e ignora registros inválidos de forma resiliente, sem interromper a importação.
-   ✅ **Modelagem e persistência em banco relacional e versionamento das cargas:** Utiliza um esquema normalizado em PostgreSQL. Cada execução de importação é versionada em um modelo `LoadBatch`, fornecendo uma trilha de auditoria completa e um histórico das integrações.
-   ✅ **Clareza do código, documentação e justificativa das escolhas técnicas:** O código é organizado, segue os padrões PEP8 e é documentado com docstrings claras. As escolhas técnicas são justificadas abaixo. Todo o desenvolvimento foi guiado por TDD (Desenvolvimento Guiado por Testes).
-   ✅ **Organização do projeto:** O projeto segue uma estrutura padrão do Django, inclui logging abrangente e este README fornece exemplos claros de configuração e uso.

## ✨ Funcionalidades

-   **Serviço de ETL:** Extrai dados de eventos da API da Sympla, os transforma e os carrega em um banco de dados PostgreSQL local.
-   **Camada de Validação Dedicada:** Usa **Pydantic** para garantir a integridade e o formato dos dados recebidos, tratando diferentes tipos de eventos (online vs. presencial) de forma explícita.
-   **Versionamento de Dados:** Cada processo de importação é salvo como um `LoadBatch` distinto, permitindo um histórico completo e depuração facilitada.
-   **Tratamento Robusto de Erros:** O serviço de integração é resiliente a falhas de rede e o comando de importação ignora eventos individuais com dados malformados sem parar o processo geral.
-   **Deduplicação de Dados:** Os eventos são identificados de forma única por seu `event_id`, evitando entradas duplicadas no banco de dados.
-   **Logging Básico:** Registra importações bem-sucedidas, erros e avisos (como eventos ignorados), associados a cada lote de carga específico.
-   **API REST:** Expõe os eventos salvos através de um endpoint REST de somente leitura.
-   **Ambiente Dockerizado:** Toda a aplicação (Django app + PostgreSQL database + Nginx) é containerizada com Docker e Docker Compose para uma configuração fácil e consistente.
-   **Guiado por Testes:** Desenvolvido usando TDD, com uma suíte de testes abrangente que cobre modelos, serviços, schemas de validação e comandos.

## 🛠️ Justificativas e Escolhas Técnicas

Este projeto utiliza ferramentas e padrões da indústria para garantir uma solução de alta qualidade e de fácil manutenção.

-   **Django & DRF:** Frameworks poderosos e maduros que fornecem um ORM robusto, admin, e uma base sólida para a construção de APIs REST.
-   **PostgreSQL:** Um banco de dados relacional open-source confiável e rico em recursos, ideal para lidar com dados estruturados.
-   **Docker & Docker Compose:** A containerização garante um ambiente de desenvolvimento e produção consistente e reproduzível, simplificando o setup para um único comando.
-   **Nginx como Proxy Reverso:** O contêiner `nginx` atua como o ponto de entrada da nossa aplicação (o "portão da frente"). Ele é um servidor web de alta performance que fica na frente do Gunicorn/Django e é responsável por:
    -   **Servir Arquivos Estáticos:** Em produção, o Nginx é extremamente eficiente para entregar arquivos como CSS, JavaScript e imagens diretamente, liberando a aplicação Django para focar apenas na lógica de negócio.
    -   **Balanceamento de Carga e Escalabilidade:** Embora tenhamos apenas uma instância da aplicação (`app`) agora, esta arquitetura permite escalar horizontalmente no futuro. O Nginx pode ser configurado para distribuir o tráfego entre múltiplas instâncias da aplicação sem qualquer alteração no código Django.
    -   **Segurança e Performance:** O Nginx pode ser configurado para lidar com conexões HTTPS (terminação SSL), aplicar limites de requisição (rate limiting) para prevenir ataques e servir respostas em cache, melhorando a segurança e a performance geral.
-   **Desenvolvimento Guiado por Testes (TDD):** Ao escrever testes antes da implementação, garantimos alta cobertura de testes e usamos os testes para impulsionar um design de software melhor e mais desacoplado.
-   **Pydantic para Validação:** A escolha de usar Pydantic para a validação de dados de entrada foi deliberada. Em vez de lógica manual ou de sobrecarregar os Serializers do DRF, Pydantic oferece uma sintaxe limpa e auto-documentada baseada em type hints, performance excepcional e mensagens de erro detalhadas, criando uma camada de validação desacoplada e altamente testável.
-   **Camada de Serviço (`SymplaService`):** Toda a interação com a API externa é encapsulada em uma classe de serviço dedicada. Isso adere ao Princípio da Responsabilidade Única e cria uma forte camada de isolamento.
-   **Versionamento de Dados (Modelo `LoadBatch`):** Envolvemos cada execução de importação em um "lote". Esta é uma escolha de design crucial para criar um sistema auditável e rastreável, permitindo-nos identificar quando dados específicos foram introduzidos ou atualizados e depurar execuções com falha de forma eficaz.

## 🚀 Começando

Este projeto pode ser executado de duas maneiras: **Localmente** (com Python/Poetry/Pip e SQLite) ou com **Docker** (com PostgreSQL e Nginx).

### Pré-requisitos Comuns
- Git
- Python 3.12+

---

### Opção 1: Rodando Localmente (Desenvolvimento Rápido com SQLite)

Esta abordagem é ideal para desenvolver e testar novas funcionalidades rapidamente, sem a necessidade de subir todo o ambiente Docker. Escolha a sub-seção que corresponde à sua ferramenta de preferência.

#### **1.1: Usando Poetry (Recomendado)**

**Pré-requisitos:** [Poetry](https://python-poetry.org/docs/#installation)

1.  **Clone o repositório e entre na pasta:**
    ```bash
    git clone https://github.com/keven-silva/sympla_integration.git
    cd sympla_integration
    ```

2.  **Crie o arquivo de ambiente (`.env`):**
    Um arquivo de exemplo para o setup local é fornecido. Copie-o:
    ```bash
    cp .env.local.example .env
    ```
    Este arquivo já está pré-configurado para usar SQLite. Você só precisa **adicionar seu token da API da Sympla**.

3.  **Instale as dependências:**
    O Poetry criará um ambiente virtual e instalará tudo que o projeto precisa.
    ```bash
    poetry install
    ```

4.  **Ative o Ambiente Virtual:**
    ```bash
    poetry shell
    ```

5.  **Aplique as migrações do banco de dados:**
    Este comando criará o arquivo `db.sqlite3` na raiz do projeto.
    ```bash
    python manage.py migrate
    ```

6.  **Execute a importação e inicie o servidor:**
    ```bash
    # Para importar os dados
    python manage.py import_sympla_events

    # Para iniciar o servidor de desenvolvimento
    python manage.py runserver
    ```
    A API estará disponível em `http://localhost:8000/api/events/`.

#### **1.2: Usando Pip e Venv (Padrão Python)**

**Pré-requisitos:** Python e Pip.

> **Nota:** Este método requer um arquivo `requirements.txt`. Se ele não existir no projeto, o mantenedor pode gerá-lo a partir do Poetry com o comando:
> `poetry export -f requirements.txt --output requirements.txt --without-hashes`

1.  **Clone o repositório e entre na pasta:**
    ```bash
    git clone https://github.com/keven-silva/sympla_integration.git
    cd sympla_integration
    ```
2.  **Crie o arquivo de ambiente (`.env`):**
    ```bash
    cp .env.local.example .env
    ```
    Lembre-se de **adicionar seu token da API da Sympla** no arquivo `.env`.

3.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    # Crie o ambiente
    python3 -m venv .venv

    # Ative o ambiente (Linux/macOS)
    source .venv/bin/activate

    # Ative o ambiente (Windows)
    .\.venv\Scripts\activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Execute a importação e inicie o servidor:**
    ```bash
    # Para importar os dados
    python manage.py import_sympla_events

    # Para iniciar o servidor de desenvolvimento
    python manage.py runserver
    ```
    A API estará disponível em `http://localhost:8000/api/events/`.

---

### Opção 2: Rodando com Docker e PostgreSQL (Ambiente similar à Produção)

Esta abordagem cria um ambiente completo e isolado, idêntico ao que seria usado em produção.

**Pré-requisitos:** Docker e Docker Compose.

1.  **Clone o repositório e entre na pasta:**
    ```bash
    git clone https://github.com/keven-silva/sympla_integration.git
    cd sympla_integration
    ```
2.  **Crie o arquivo de ambiente (`.env`):**
    Use o arquivo de exemplo para Docker:
    ```bash
    cp .env.docker.example .env
    ```
    Abra o arquivo `.env` e **adicione seu token da API da Sympla**. As credenciais do banco de dados já estão configuradas para funcionar com o `docker-compose.yml`.

3.  **Construa e inicie os contêineres:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Aplique as migrações do banco de dados:**
    ```bash
    docker-compose exec app python manage.py migrate
    ```

5.  **Execute a importação:**
    ```bash
    docker-compose exec app python manage.py import_sympla_events
    ```
    A API estará disponível em `http://localhost/` (ou a porta que você configurou para o Nginx no `docker-compose.yml`). O endpoint completo será, por exemplo, `http://localhost/api/events/`.


### Acesse a API e sua Documentação

Após a importação, você pode explorar a API e sua documentação interativa.

-   **Documentação Swagger UI (Recomendado):**
    Acesse a interface interativa onde você pode ver os endpoints, modelos e até mesmo testar as requisições diretamente do navegador.
    -   **URL:** `http://localhost/swagger/` (ou a porta que você configurou, ex: `http://localhost:8000/swagger/`)

-   **Endpoint da API de Eventos:**
    Para acessar os dados brutos da API.
    -   **URL:** `http://localhost/api/events/`
    -   **Método:** `GET`


## ✅ Executando os Testes

-   **Localmente (com Poetry ou Venv ativo):**
    ```bash
    pytest
    ```

-   **Com Docker:**
    ```bash
    docker-compose exec app pytest
    ```
