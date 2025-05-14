# FastAPI Perfis

A API para gerenciar perfis de usuários utilizando FastAPI e PostgreSQL.

## Instruções de uso

1. Clone o repositório e entre na pasta clonada.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Crie um banco de dados PostgreSQL com o nome `perfis_db` e configure as variáveis de ambiente `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_PORT` de acordo com as suas necessidades.
4. Execute o comando `uvicorn main:app --reload` para iniciar a API em modo de desenvolvimento.
5. Acesse a documentação da API em `http://localhost:8000/docs`.

## Endpoints

### Perfil

- `POST /perfil`: Cria um novo perfil com os dados informados no corpo da requisição.
- `GET /perfil`: Retorna os dados do perfil do usuário autenticado.
- `PUT /perfil`: Atualiza os dados do perfil do usuário autenticado.
- `DELETE /perfil`: Remove o perfil do usuário autenticado.

### Imagem do perfil

- `GET /perfil/imagem`: Retorna a imagem do perfil do usuário autenticado.

## Autenticação

A API utiliza um token JWT para autenticar as requisições. O token é gerado com o email do usuário como payload.

### Endpoint para gerar um token de teste

- `POST /generate-test-token`: Gera um token JWT com o email informado no corpo da requisição. Este endpoint é apenas para testes e não deve ser usado em produção.

## Banco de dados

A API utiliza o banco de dados PostgreSQL para armazenar os perfis dos usuários.

## Configuração

A API utiliza as variáveis de ambiente para configurar a conexão com o banco de dados PostgreSQL.

- `POSTGRES_HOST`: O endereço do host do banco de dados.
- `POSTGRES_USER`: O nome do usuário do banco de dados.
- `POSTGRES_PASSWORD`: A senha do usuário do banco de dados.
- `POSTGRES_DB`: O nome do banco de dados.
- `POSTGRES_PORT`: A porta do banco de dados.

## Imagem do perfil

- `GET /perfil/imagem`: Retorna a imagem do perfil do usuário autenticado.
