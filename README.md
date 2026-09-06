# Order Management

Aplicação Full Stack para gerenciamento de produtos, pedidos, estoque e logs de auditoria. O projeto foi desenvolvido como um desafio técnico, com foco em organização de código, regras de negócio, consistência dos dados e facilidade de execução local.

---

### Sobre a aplicação

- Cadastro, consulta, atualização e exclusão de produtos.
- Criação de pedidos com múltiplos produtos.
- Atualização e exclusão de pedidos com reconciliação automática do estoque.
- Bloqueio de operações que resultariam em estoque negativo.
- Histórico paginado de operações e movimentações de estoque.
- Interface com estados de carregamento, feedback de sucesso e tratamento de erros.
- API documentada com Swagger e respostas de listagem paginadas.

---

### Tecnologias utilizadas

#### Frontend

- React 19.2
- TypeScript 6.0
- Vite 8.2
- TanStack React Query 5.102
- React Hook Form 7.87
- Zod 4.5
- Axios 1.20
- Tailwind CSS 4.3

#### Backend e banco de dados

- Python 3.13
- FastAPI 0.141
- SQLAlchemy 2.0
- Alembic 1.19
- Psycopg 3.3
- PostgreSQL 17
- Pytest 9.1

#### Ambiente

- Node.js 24
- Docker Compose
- Cursor ou Visual Studio Code, com Dev Containers

As versões completas das dependências estão registradas em `apps/api/requirements.txt` e `apps/web/package-lock.json`.

---

### Pré-requisitos

O caminho recomendado utiliza:

- Docker com Docker Compose;
- Cursor ou Visual Studio Code;
- extensão Dev Containers instalada.

O Antigravity IDE **não é compatível** com Dev Containers. Para abrir e executar este projeto no ambiente containerizado, use Cursor ou Visual Studio Code.

Não é necessário instalar Python, Node.js ou PostgreSQL diretamente na máquina ao utilizar o Dev Container.

---

### Configuração do ambiente

Clone o repositório e acesse a pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>
```

Crie o arquivo de variáveis de ambiente a partir do exemplo:

```bash
cp .env.example .env
```

As configurações padrão utilizam dois bancos separados:

- `order_management`: desenvolvimento;
- `order_management_test`: testes automatizados.

Essa separação impede que a execução dos testes altere os dados usados durante o desenvolvimento.

---

### Executando com Dev Container

Abra a pasta no Cursor ou no Visual Studio Code e execute o comando `Dev Containers: Reopen in Container`. Não utilize o Antigravity IDE para esse fluxo: ele não oferece suporte adequado a Dev Containers.

Na primeira inicialização, o ambiente automaticamente:

- instala as dependências do backend e do frontend;
- executa as migrations nos bancos de desenvolvimento e teste;
- inicia a API FastAPI;
- inicia o frontend Vite.

Após a inicialização, acesse:

- Frontend: [http://localhost:5173](http://localhost:5173)
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

### Executando com Docker Compose

Também é possível iniciar o projeto sem abrir o Visual Studio Code:

```bash
docker compose up -d
docker compose exec workspace bash .devcontainer/post-start.sh
```

Para acompanhar os serviços iniciados pelo script:

```bash
docker compose exec workspace tail -f /tmp/order-management-api.log
docker compose exec workspace tail -f /tmp/order-management-web.log
```

Para encerrar os containers:

```bash
docker compose down
```

O volume do banco de desenvolvimento é preservado. O banco de testes utiliza armazenamento temporário e é recriado com o container.

---

### Execução manual dos serviços

Dentro do container, a API pode ser iniciada com:

```bash
python -m uvicorn app.main:app \
  --app-dir apps/api \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

Em outro terminal, inicie o frontend:

```bash
npm run dev --prefix apps/web -- --host 0.0.0.0 --port 5173
```

A URL consumida pelo frontend é definida por `VITE_API_URL` no arquivo `.env`.

---

### Banco de dados e migrations

Para atualizar o banco de desenvolvimento até a migration mais recente:

```bash
alembic -c alembic.ini upgrade head
```

Para consultar a migration atual:

```bash
alembic -c alembic.ini current
```

As migrations ficam em `apps/api/migrations`. A configuração da conexão é obtida pela variável `DATABASE_URL`.

---

### Testes e validações

Execute os testes do backend a partir da raiz do projeto:

```bash
pytest -q
```

Antes da suíte começar, o banco indicado por `TEST_DATABASE_URL` é validado, recriado e migrado até a versão mais recente. Por segurança, o nome desse banco deve terminar com `_test` e sua URL não pode ser igual à URL de desenvolvimento.

Para validar o frontend:

```bash
npm run lint --prefix apps/web
npm run build --prefix apps/web
```

O projeto possui 66 testes automatizados no backend, cobrindo domínio, casos de uso, persistência e rotas HTTP.

---

### Arquitetura

O repositório está organizado como um monorepo:

```text
apps/
├── api/                  # FastAPI, regras de negócio, persistência e testes
└── web/                  # React, páginas, formulários e integração com a API
```

O backend utiliza DDD e Clean Architecture de forma pragmática. Cada módulo de negócio é dividido em:

- `domain`: entidades e contratos de repositório, sem dependência do FastAPI ou SQLAlchemy;
- `application`: casos de uso, regras da aplicação e erros;
- `infra/database`: implementação dos repositórios com SQLAlchemy;
- `infra/http`: routers, schemas, dependências, ViewModels e tratamento de exceções.

O fluxo principal do backend é:

```text
HTTP → Router → Caso de uso → Domínio/Contrato → Repositório → PostgreSQL
```

No frontend, páginas e seções separam a navegação, os fluxos de negócio e os componentes reutilizáveis. A comunicação HTTP é centralizada, enquanto o React Query controla cache, carregamento e atualização dos dados.

---

### Regras de pedido e estoque

- Todo pedido precisa ter pelo menos um item válido.
- A quantidade solicitada deve estar disponível em estoque.
- Criar um pedido reduz o estoque dos produtos.
- Atualizar um pedido considera a diferença entre os itens antigos e a nova coleção completa.
- Excluir um pedido devolve suas quantidades ao estoque.
- Produtos envolvidos em operações de estoque são bloqueados no banco durante a transação.
- A alteração do pedido, o ajuste de estoque e os logs de auditoria compartilham a mesma sessão e transação.

Se qualquer etapa falhar, toda a operação é revertida. Isso evita pedidos sem ajuste de estoque ou logs registrados parcialmente.

---

### Logs de auditoria

Os logs são append-only e registram:

- criação, atualização e exclusão de produtos;
- criação, atualização e exclusão de pedidos;
- movimentações de estoque.

A API expõe somente a listagem paginada em `GET /audit-logs`. Registros existentes antes da implementação da auditoria não são preenchidos retroativamente.

---

### Decisões e limitações

- A aplicação foi projetada para execução local e não inclui configuração de deploy.
- Autenticação e autorização não fazem parte do escopo do desafio.
- O CORS está configurado para o frontend local em `http://localhost:5173`.
- A interface prioriza os fluxos funcionais e não utiliza um design system complexo.
- O controle transacional e o bloqueio das linhas de produto reduzem conflitos em alterações simultâneas de estoque.
- Lacunas em sequências de IDs após rollback ou exclusão são um comportamento esperado do PostgreSQL.

---

### Estrutura principal

```text
.
├── .devcontainer/        # Configuração e inicialização do ambiente
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── core/     # Configuração e infraestrutura compartilhada
│   │   │   └── modules/  # Products, Orders e Audit Logs
│   │   ├── migrations/   # Histórico do schema
│   │   └── tests/        # Testes automatizados
│   └── web/
│       └── src/           # Interface React
├── alembic.ini
├── docker-compose.yml
└── .env.example
```
