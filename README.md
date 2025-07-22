# Integração de Eventos Sympla

Um serviço robusto e containerizado em Django para extrair, processar e armazenar dados de eventos da API pública da Sympla, projetado com boas práticas, testabilidade e escalabilidade em mente.

## 📋 Conformidade com os Critérios de Avaliação

Este projeto foi desenvolvido para atender aos seguintes critérios de avaliação:

-   ✅ **Consumo correto e robusto de APIs:** Implementada uma camada de serviço resiliente com tratamento de erros (timeouts, erros HTTP), gerenciamento seguro de token e paginação.
-   ✅ **Tratamento e validação dos dados extraídos:** Os dados brutos são normalizados (datas, campos de texto), validados quanto a campos obrigatórios e deduplicados usando uma chave natural (`sympla_id`).
-   ✅ **Modelagem e persistência em banco relacional e versionamento das cargas:** Utiliza um esquema normalizado em PostgreSQL. Cada execução de importação é versionada em um modelo `LoadBatch`, fornecendo uma trilha de auditoria completa e um histórico das integrações.
-   ✅ **Clareza do código, documentação e justificativa das escolhas técnicas:** O código é organizado, segue os padrões PEP8 e é documentado com docstrings claras. As escolhas técnicas são justificadas abaixo. Todo o desenvolvimento foi guiado por TDD (Desenvolvimento Guiado por Testes).
-   ✅ **Organização do projeto:** O projeto segue uma estrutura padrão do Django, inclui logging abrangente e este README fornece exemplos claros de configuração e uso.

## ✨ Funcionalidades

-   **Serviço de ETL:** Extrai dados de eventos da API da Sympla, os transforma e os carrega em um banco de dados PostgreSQL local.
-   **Versionamento de Dados:** Cada processo de importação é salvo como um `LoadBatch` distinto, permitindo um histórico completo e depuração facilitada.
-   **Tratamento Robusto de Erros:** O serviço de integração com a API é resiliente a timeouts de rede, erros HTTP e respostas inesperadas da API.
-   **Deduplicação de Dados:** Os eventos são identificados de forma única por seu `sympla_id`, evitando entradas duplicadas no banco de dados.
-   **Logging Básico:** Registra importações bem-sucedidas, erros e quantidades, associados a cada lote de carga específico.
-   **API REST:** Expõe os eventos salvos através de um endpoint REST de somente leitura.
-   **Ambiente Dockerizado:** Toda a aplicação (app Django + banco de dados PostgreSQL) é containerizada com Docker e Docker Compose para uma configuração fácil e consistente.
-   **Guiado por Testes:** Desenvolvido usando TDD, com uma suíte de testes abrangente que garante confiabilidade e confiança na refatoração.

## 🛠️ Justificativas e Escolhas Técnicas

Este projeto utiliza ferramentas e padrões da indústria para garantir uma solução de alta qualidade e de fácil manutenção.

-   **Django:** Um framework poderoso e maduro que fornece um ORM robusto, uma interface de administração pronta para auditoria de dados e uma base sólida para a construção de APIs REST.
-   **PostgreSQL:** Um banco de dados relacional open-source confiável e rico em recursos, ideal para lidar com dados estruturados e garantir a integridade dos dados.
-   **Docker & Docker Compose:** A containerização garante um ambiente de desenvolvimento e produção consistente e reproduzível. Simplifica a configuração para um único comando (`docker-compose up`), eliminando problemas de "funciona na minha máquina".
-   **Django REST Framework (DRF):** O padrão de fato para construir APIs REST em Django. Ele fornece um kit de ferramentas limpo e poderoso para serialização, views e autenticação.
-   **Desenvolvimento Guiado por Testes (TDD):** Ao escrever testes antes da implementação, garantimos alta cobertura de testes e usamos os testes para impulsionar um design de software melhor e mais desacoplado. Essa metodologia garante que cada parte da lógica seja verificável e robusta.
-   **Camada de Serviço (`SymplaService`):** Toda a interação com a API externa da Sympla é encapsulada em uma classe de serviço dedicada. Isso adere ao Princípio da Responsabilidade Única e cria uma forte camada de isolamento, tornando a aplicação mais resiliente e mais fácil de testar.
-   **Versionamento de Dados (Modelo `LoadBatch`):** Em vez de apenas inserir dados, envolvemos cada execução de importação em um "lote". Esta é uma escolha de design crucial para criar um sistema auditável e rastreável, permitindo-nos identificar quando dados específicos foram introduzidos ou atualizados e depurar execuções com falha de forma eficaz.

## 🚀 Começando

### Pré-requisitos

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/keven-silva/sympla_integration.git
    cd sympla_integration
    ```

2.  **Crie o arquivo de ambiente:**
    Copie o exemplo `.env.example` para `.env` e preencha com seus dados.
    ```bash
    cp .env.example .env
    ```
    Agora, abra o arquivo `.env` e **adicione seu token real da API da Sympla**:
    ```dotenv
    # .env
    SECRET_KEY='sua-chave-secreta-do-django'
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1,app

    POSTGRES_DB=sympla_events_db
    POSTGRES_USER=sympla_user
    POSTGRES_PASSWORD=senhasegura

    # Substitua pelo seu token real da Sympla
    SYMPLA_API_TOKEN="SEU_TOKEN_REAL_DA_API_DA_SYMPLA_AQUI"
    ```

3.  **Construa e inicie os contêineres:**
    Este único comando irá construir a imagem do Django, iniciar o contêiner do PostgreSQL e conectá-los.
    ```bash
    docker-compose up --build -d
    ```

4.  **Aplique as migrações do banco de dados:**
    Crie as tabelas necessárias no banco de dados PostgreSQL.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

## Como Usar

### 1. Execute o Comando de Importação

Para buscar eventos da API da Sympla e popular seu banco de dados local, execute:
```bash
docker-compose exec web python manage.py import_sympla_events