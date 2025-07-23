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
    Agora, abra o arquivo `.env` e **adicione seu token real da API da Sympla** e outras configurações:
    ```dotenv
    # .env
    # Segurança do Django
    SECRET_KEY='sua-chave-secreta-do-django'
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Banco de Dados
    POSTGRES_DB=sympla_events_db
    POSTGRES_USER=sympla_user
    POSTGRES_PASSWORD=strongpassword
    POSTGRES_HOST=db
    POSTGRES_PORT=5432

    # API da Sympla
    SYMPLA_API_TOKEN="SEU_TOKEN_REAL_DA_API_DA_SYMPLA_AQUI"
    SYMPLA_BASE_URL="[https://api.sympla.com.br/public/v3/events](https://api.sympla.com.br/public/v3/events)"
    ```

3.  **Construa e inicie os contêineres:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Aplique as migrações do banco de dados:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

## Como Usar

### 1. Execute o Comando de Importação

Para buscar eventos da API da Sympla e popular seu banco de dados local, execute:
```bash
docker-compose exec web python manage.py import_sympla_events