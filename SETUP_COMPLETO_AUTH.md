# Setup Completo do Sistema de Autenticação

Guia passo-a-passo para configurar e testar o sistema de autenticação com Appwrite.

---

## 📋 Pré-requisitos

- ✅ Python 3.8+ instalado
- ✅ Node.js 16+ instalado
- ✅ Conta no Appwrite Cloud (https://cloud.appwrite.io)
- ✅ Projeto Appwrite criado (ID: `68dc49bf000cebd54b85`)

---

## 🚀 Passo 1: Configurar Appwrite Cloud

### 1.1 Criar Database

1. Acesse: https://cloud.appwrite.io/console/project-68dc49bf000cebd54b85/databases
2. Clique em **"Create Database"**
3. Configure:
   - **Database ID**: `papprefeito_db` (exatamente este nome)
   - **Name**: `PapPrefeito Database`
4. Clique em **"Create"**

### 1.2 Criar Collection "users"

1. Dentro do database `papprefeito_db`, clique em **"Create Collection"**
2. Configure:
   - **Collection ID**: `users` (exatamente este nome)
   - **Name**: `Users` ou `Usuários`
3. Clique em **"Create"**

### 1.3 Configurar Atributos da Collection

Na aba **"Attributes"** da collection `users`, crie os seguintes atributos **NESTA ORDEM**:

#### Atributo 1: email
- Type: **String**
- Key: `email`
- Size: `255`
- Required: ✅ **Yes**
- Array: ❌ No

#### Atributo 2: nome
- Type: **String**
- Key: `nome`
- Size: `255`
- Required: ✅ **Yes**
- Array: ❌ No

#### Atributo 3: hashed_password
- Type: **String**
- Key: `hashed_password`
- Size: `255`
- Required: ✅ **Yes**
- Array: ❌ No

#### Atributo 4: is_active
- Type: **Boolean**
- Key: `is_active`
- Required: ✅ **Yes**
- Default: `true`

#### Atributo 5: is_superuser
- Type: **Boolean**
- Key: `is_superuser`
- Required: ✅ **Yes**
- Default: `false`

#### Atributo 6: created_at
- Type: **String**
- Key: `created_at`
- Size: `50`
- Required: ✅ **Yes**
- Array: ❌ No

#### Atributo 7: updated_at
- Type: **String**
- Key: `updated_at`
- Size: `50`
- Required: ❌ **No**
- Array: ❌ No

### 1.4 Criar Índice para Email

Na aba **"Indexes"** da collection `users`:

1. Clique em **"Create Index"**
2. Configure:
   - **Key**: `email_unique`
   - **Type**: **Unique**
   - **Attributes**: Selecione `email`
   - **Order**: `ASC`
3. Clique em **"Create"**

### 1.5 Configurar Permissões

Na aba **"Settings"** da collection `users`:

1. **Document Security**: ✅ Enabled
2. **Permissions**:
   - **Create**: `any` (permite registro público)
   - **Read**: `users` (apenas usuários autenticados)
   - **Update**: `users` (apenas usuários autenticados)
   - **Delete**: `users` (apenas usuários autenticados)

---

## 🔧 Passo 2: Configurar Backend

### 2.1 Verificar arquivo .env

O arquivo `.env` no backend já deve estar configurado com:

```env
# Appwrite
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=68dc49bf000cebd54b85
APPWRITE_API_KEY=sua_api_key_aqui
APPWRITE_DATABASE_ID=papprefeito_db

# Autenticação
SECRET_KEY=sua_secret_key_gerada
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

✅ Se sim, prossiga para o próximo passo.

### 2.2 Instalar dependências

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2.3 Testar conexão com Appwrite

```bash
python test_appwrite_connection.py
```

**Resultado esperado:**
```
════════════════════════════════════════════════════════════
TESTE DE CONEXÃO COM APPWRITE
════════════════════════════════════════════════════════════

1. Verificando configurações...
   ✓ Endpoint: https://cloud.appwrite.io/v1
   ✓ Project ID: 68dc49bf000cebd54b85
   ...

4. Verificando collection 'users'...
   ✓ Collection 'users' encontrada!
   ✓ Nome: Users
   ✓ Atributos: 7
   ...

════════════════════════════════════════════════════════════
✓ TESTE CONCLUÍDO COM SUCESSO!
════════════════════════════════════════════════════════════
```

**Se houver erros:**
- Collection não encontrada → Volte ao Passo 1.2
- Atributos faltando → Volte ao Passo 1.3
- Erro de conexão → Verifique API Key e Project ID

### 2.4 Testar fluxo de autenticação

```bash
python test_auth_flow.py
```

**Resultado esperado:**
```
╔══════════════════════════════════════════════════════════╗
║          TESTE COMPLETO DO SISTEMA DE AUTENTICAÇÃO       ║
╚══════════════════════════════════════════════════════════╝

1. TESTANDO FUNÇÕES DE SEGURANÇA
   ✓ Hash gerado: ...
   ✓ Senha verificada corretamente
   ✓ Access token gerado: ...
   ✓ Refresh token gerado: ...
   ...

2. TESTANDO USERSERVICE (INTEGRAÇÃO COM APPWRITE)
   ✓ Usuário criado com sucesso!
   ✓ Autenticação com credenciais corretas: SUCESSO
   ...

════════════════════════════════════════════════════════════
✓ TODOS OS TESTES PASSARAM COM SUCESSO!
════════════════════════════════════════════════════════════
```

**Se houver erros:**
- Erro ao criar usuário → Verifique atributos da collection
- Erro de hash → Execute o Passo 3 (bcrypt)
- Erro de autenticação → Verifique SECRET_KEY no .env

---

## 🔐 Passo 3: Verificar Bcrypt (se necessário)

Se houver erros relacionados a bcrypt/passlib, execute:

```bash
# Verificar versão atual
pip show bcrypt passlib

# Se necessário, reinstalar com versão compatível
pip uninstall -y bcrypt
pip install 'bcrypt<4.2.0'
pip install --upgrade passlib
```

Teste novamente:
```bash
python test_auth_flow.py
```

---

## 🎯 Passo 4: Iniciar o Sistema

### 4.1 Iniciar Backend

```bash
cd backend
source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload --port 8000
```

Acesse: http://localhost:8000/docs para ver a documentação da API

### 4.2 Iniciar Frontend

```bash
cd frontend
npm install  # se ainda não instalou
npm run dev
```

Acesse: http://localhost:5173

---

## 🧪 Passo 5: Testar no Frontend

### 5.1 Criar primeira conta

1. Acesse: http://localhost:5173/register
2. Preencha:
   - **Email**: seu@email.com
   - **Nome**: Seu Nome
   - **Senha**: Senha123! (mínimo 8 caracteres, maiúscula, minúscula, número)
3. Clique em **"Registrar"**

**Resultado esperado:** Redirecionamento para página de login

### 5.2 Fazer login

1. Acesse: http://localhost:5173/login
2. Entre com email e senha
3. Clique em **"Entrar"**

**Resultado esperado:** Redirecionamento para /dashboard (ou página principal)

### 5.3 Verificar autenticação

- Abra o DevTools (F12)
- Vá em **Application** → **Local Storage**
- Procure por `auth-storage`
- Deve conter: `user`, `accessToken`, `refreshToken`, `isAuthenticated: true`

---

## 👨‍💼 Passo 6: Criar Superusuário (Opcional)

Para tornar um usuário administrador:

1. Acesse o Appwrite Console
2. Navegue até **Databases** → `papprefeito_db` → `users`
3. Encontre o documento do seu usuário
4. Clique em **"..."** → **"Update Document"**
5. Altere `is_superuser` de `false` para `true`
6. Clique em **"Update"**

Agora esse usuário tem privilégios de administrador.

---

## 📡 Testando a API (opcional)

### Teste 1: Registro via API

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "nome": "Usuario Teste",
    "password": "Teste123!"
  }'
```

### Teste 2: Login via API

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Teste123!"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "refresh_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Teste 3: Obter perfil

```bash
# Substitua YOUR_ACCESS_TOKEN pelo token recebido no login
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ✅ Checklist Final

Marque conforme completar:

- [ ] Database `papprefeito_db` criado no Appwrite
- [ ] Collection `users` criada com 7 atributos
- [ ] Índice único criado para `email`
- [ ] Permissões configuradas (Create: any, Read/Update/Delete: users)
- [ ] Arquivo `.env` configurado no backend
- [ ] Dependências Python instaladas
- [ ] `python test_appwrite_connection.py` executado com sucesso
- [ ] `python test_auth_flow.py` executado com sucesso
- [ ] Backend iniciado e rodando na porta 8000
- [ ] Frontend iniciado e rodando na porta 5173
- [ ] Conta criada via /register
- [ ] Login realizado com sucesso
- [ ] Token armazenado no localStorage
- [ ] (Opcional) Superusuário criado via Appwrite Console

---

## 🐛 Troubleshooting

### Erro: "Collection not found"
**Solução:** Verifique se a Collection ID é exatamente `users` (minúsculas)

### Erro: "Email já cadastrado"
**Solução:** O índice único está funcionando. Use outro email ou delete o documento no Appwrite

### Erro: "Não foi possível validar as credenciais"
**Solução:** Verifique se `SECRET_KEY` está configurada no `.env`

### Erro: "Database not found"
**Solução:** Verifique se o Database ID é exatamente `papprefeito_db`

### Erro de permissão ao criar usuário
**Solução:** Verifique se Create está permitido para `any` nas permissões da collection

### Erro com bcrypt
**Solução:** Execute:
```bash
pip uninstall -y bcrypt
pip install 'bcrypt<4.2.0'
```

### Backend não inicia
**Solução:**
1. Verifique se o venv está ativado
2. Verifique se todas as dependências estão instaladas
3. Verifique erros no terminal

### Frontend não conecta ao backend
**Solução:**
1. Verifique se o backend está rodando na porta 8000
2. Verifique `VITE_API_BASE_URL` no `.env` do frontend
3. Verifique CORS no backend

---

## 📚 Documentação Adicional

- [APPWRITE_SETUP.md](./APPWRITE_SETUP.md) - Guia detalhado do Appwrite
- [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) - Documentação completa do sistema
- [Appwrite Docs](https://appwrite.io/docs) - Documentação oficial do Appwrite
- [FastAPI Docs](https://fastapi.tiangolo.com) - Documentação do FastAPI

---

## 🎉 Sucesso!

Se você chegou até aqui e todos os testes passaram, parabéns!

O sistema de autenticação está **100% funcional** e pronto para uso em produção (após ajustes de segurança).

**Próximos passos sugeridos:**
1. Implementar recuperação de senha
2. Adicionar verificação de email
3. Implementar rate limiting
4. Adicionar logs de auditoria
5. Configurar testes automatizados

---

**Desenvolvido para o projeto PapPrefeito** 🏛️
