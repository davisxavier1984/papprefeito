# Configuração do Appwrite para Autenticação

Este guia descreve como configurar a collection de usuários no Appwrite Cloud.

## Pré-requisitos

- Conta no Appwrite Cloud (https://cloud.appwrite.io)
- Projeto criado (ID: `68dc49bf000cebd54b85`)
- Database criado (ID: `papprefeito_db`)

## Passo 1: Criar Collection `users`

1. Acesse o Appwrite Console: https://cloud.appwrite.io
2. Selecione seu projeto
3. Navegue até **Databases** → `papprefeito_db`
4. Clique em **Create Collection**
5. Configure:
   - **Collection ID**: `users` (exatamente este nome)
   - **Collection Name**: `Users` ou `Usuários`

## Passo 2: Configurar Permissões da Collection

Na aba **Settings** da collection:

- **Document Security**: Enabled
- **Permissions**:
  - **Create**: `any` (permitir registro público)
  - **Read**: `users` (apenas usuários autenticados)
  - **Update**: `users` (apenas usuários autenticados)
  - **Delete**: `users` (apenas usuários autenticados)

## Passo 3: Criar Atributos

Na aba **Attributes**, crie os seguintes atributos **NESTA ORDEM**:

### 1. email (String)
- **Type**: String
- **Key**: `email`
- **Size**: 255
- **Required**: ✅ Yes
- **Default**: (deixe vazio)
- **Array**: ❌ No

### 2. nome (String)
- **Type**: String
- **Key**: `nome`
- **Size**: 255
- **Required**: ✅ Yes
- **Default**: (deixe vazio)
- **Array**: ❌ No

### 3. hashed_password (String)
- **Type**: String
- **Key**: `hashed_password`
- **Size**: 255
- **Required**: ✅ Yes
- **Default**: (deixe vazio)
- **Array**: ❌ No

### 4. is_active (Boolean)
- **Type**: Boolean
- **Key**: `is_active`
- **Required**: ✅ Yes
- **Default**: `true`

### 5. is_superuser (Boolean)
- **Type**: Boolean
- **Key**: `is_superuser`
- **Required**: ✅ Yes
- **Default**: `false`

### 6. created_at (String)
- **Type**: String
- **Key**: `created_at`
- **Size**: 50
- **Required**: ✅ Yes
- **Default**: (deixe vazio)
- **Array**: ❌ No

### 7. updated_at (String)
- **Type**: String
- **Key**: `updated_at`
- **Size**: 50
- **Required**: ❌ No
- **Default**: (deixe vazio)
- **Array**: ❌ No

## Passo 4: Criar Índice para Email

Na aba **Indexes**, crie um índice para garantir que emails sejam únicos:

1. Clique em **Create Index**
2. Configure:
   - **Key**: `email_unique` (ou qualquer nome descritivo)
   - **Type**: `Unique`
   - **Attributes**: selecione `email`
   - **Order**: `ASC`

## Passo 5: Verificar Configuração

Verifique se a estrutura está correta:

```
Collection: users
├── Attributes:
│   ├── email (String, 255, required)
│   ├── nome (String, 255, required)
│   ├── hashed_password (String, 255, required)
│   ├── is_active (Boolean, required, default: true)
│   ├── is_superuser (Boolean, required, default: false)
│   ├── created_at (String, 50, required)
│   └── updated_at (String, 50, optional)
└── Indexes:
    └── email_unique (Unique, ASC)
```

## Passo 6: Testar a Configuração

Após configurar a collection, você pode testar o sistema:

### Iniciar o Backend

```bash
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
uvicorn app.main:app --reload --port 8000
```

### Testar Registro via API

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "nome": "Usuário Teste",
    "password": "Senha123!"
  }'
```

Resposta esperada:
```json
{
  "id": "...",
  "email": "teste@example.com",
  "nome": "Usuário Teste",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-20T..."
}
```

### Testar Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Senha123!"
  }'
```

Resposta esperada:
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "refresh_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Criar Primeiro Superusuário

Após criar um usuário via API ou frontend, você pode torná-lo superusuário:

1. Acesse o Appwrite Console
2. Navegue até **Databases** → `papprefeito_db` → `users`
3. Encontre o documento do usuário criado
4. Clique em **Edit**
5. Altere `is_superuser` de `false` para `true`
6. Clique em **Update**

## Próximos Passos

Com a collection configurada:

1. ✅ Inicie o backend (porta 8000)
2. ✅ Inicie o frontend (porta 5173)
3. ✅ Acesse `/register` para criar uma conta
4. ✅ Faça login e teste as rotas protegidas
5. ✅ Torne seu usuário superadmin seguindo as instruções acima

## Troubleshooting

### Erro: "Collection not found"
- Verifique se o Collection ID é exatamente `users`
- Confirme que o Database ID está correto no `.env`

### Erro: "Email já cadastrado"
- O índice único está funcionando
- Use outro email ou delete o documento existente

### Erro: "Não foi possível validar as credenciais"
- Verifique se a `SECRET_KEY` está configurada no `.env`
- Confirme que os tokens não expiraram

### Erro de permissão ao criar usuário
- Verifique as permissões da collection
- Garanta que `Create` está permitido para `any`

## Documentação Adicional

Para mais informações, consulte:
- [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) - Documentação completa do sistema
- [Appwrite Documentation](https://appwrite.io/docs) - Documentação oficial do Appwrite
