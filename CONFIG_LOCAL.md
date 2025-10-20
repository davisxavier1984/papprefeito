# 🏠 Configuração para Ambiente Local

Este documento descreve a configuração completa para rodar o sistema **localmente** em sua máquina.

## ✅ Configuração Concluída

A autenticação já está 100% configurada para ambiente local!

### Arquivos .env Configurados

#### Backend (.env)
```env
# Desenvolvimento Local
ALLOWED_HOSTS=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"]

# Autenticação JWT
SECRET_KEY=2VWixHCyDUBzYTKPK0E2Bs49cm9EZeWcMMpcOrpY_CI
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Appwrite Cloud
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=68dc49bf000cebd54b85
APPWRITE_DATABASE_ID=papprefeito_db
```

#### Frontend (.env)
```env
# Desenvolvimento Local
VITE_API_BASE_URL=http://localhost:8000/api
```

## 🚀 Como Rodar Localmente

### Pré-requisito: Collection no Appwrite

⚠️ **IMPORTANTE:** Você precisa criar a collection `users` no Appwrite Cloud uma única vez.

Siga: [APPWRITE_SETUP.md](./APPWRITE_SETUP.md)

### Passo 1: Iniciar o Backend

```bash
# Navegar até a pasta do backend
cd backend

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

✅ Backend rodando em: **http://localhost:8000**
📚 Documentação da API: **http://localhost:8000/docs**

### Passo 2: Iniciar o Frontend (em outro terminal)

```bash
# Navegar até a pasta do frontend
cd frontend

# Iniciar servidor de desenvolvimento
npm run dev
```

✅ Frontend rodando em: **http://localhost:5173**

### Passo 3: Testar o Sistema

#### Opção 1: Interface Web
1. Abra http://localhost:5173/register
2. Crie uma conta de teste
3. Faça login
4. Teste as funcionalidades

#### Opção 2: API via Swagger
1. Abra http://localhost:8000/docs
2. Teste o endpoint `POST /api/auth/register`
3. Depois teste `POST /api/auth/login`
4. Use o botão "Authorize" 🔒 para autenticar
5. Teste os endpoints protegidos

#### Opção 3: cURL

**Registrar usuário:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@local.dev",
    "nome": "Usuário Teste",
    "password": "Teste123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@local.dev",
    "password": "Teste123!"
  }'
```

**Obter perfil (use o token recebido no login):**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

## 📋 Checklist Rápido

- [x] Backend .env configurado para localhost
- [x] Frontend .env configurado para localhost
- [x] Dependências Python instaladas
- [x] Dependências Node instaladas
- [x] Testes de autenticação passando
- [ ] Collection `users` criada no Appwrite (faça uma vez)
- [ ] Backend rodando na porta 8000
- [ ] Frontend rodando na porta 5173
- [ ] Primeiro usuário criado e testado

## 🔧 Portas Utilizadas

| Serviço | Porta | URL |
|---------|-------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend Dev | 5173 | http://localhost:5173 |
| Swagger Docs | 8000 | http://localhost:8000/docs |
| Appwrite Cloud | - | https://cloud.appwrite.io |

## 🎯 Endpoints Disponíveis

Base URL: `http://localhost:8000/api/auth`

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/register` | Criar nova conta | ❌ Não |
| POST | `/login` | Fazer login | ❌ Não |
| POST | `/refresh` | Renovar token | ✅ Refresh Token |
| GET | `/me` | Ver perfil | ✅ Access Token |
| PUT | `/me` | Atualizar perfil | ✅ Access Token |
| POST | `/me/change-password` | Mudar senha | ✅ Access Token |
| DELETE | `/me` | Desativar conta | ✅ Access Token |
| POST | `/logout` | Fazer logout | ✅ Access Token |

## 🐛 Troubleshooting Local

### Backend não inicia

**Erro: "No module named 'app'"**
```bash
# Certifique-se de estar na pasta backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Erro: bcrypt/passlib**
```bash
pip install bcrypt==4.1.3
pip install passlib[bcrypt]==1.7.4
```

### Frontend não conecta

**Erro: CORS**
- Verifique se o backend .env tem: `ALLOWED_HOSTS=["http://localhost:5173", ...]`
- Reinicie o backend após alterar o .env

**Erro: 404 na API**
- Verifique se o frontend .env tem: `VITE_API_BASE_URL=http://localhost:8000/api`
- Reinicie o frontend: `Ctrl+C` e depois `npm run dev`

### Appwrite

**Erro: "Collection not found"**
- Crie a collection `users` seguindo [APPWRITE_SETUP.md](./APPWRITE_SETUP.md)
- Verifique se o Collection ID é exatamente `users`

**Erro: "Document already exists" / "Email já cadastrado"**
- ✅ Isso significa que o índice único está funcionando!
- Use outro email ou delete o documento no Appwrite Console

### Autenticação

**Token expirado**
- Access tokens expiram em 30 minutos
- Use o refresh token para renovar
- Ou faça login novamente

**Erro 401/403**
- Verifique se o token está sendo enviado corretamente no header
- Use o formato: `Authorization: Bearer SEU_TOKEN`

## 🔐 Segurança no Ambiente Local

**Configurações atuais (apenas para desenvolvimento local):**

✅ SECRET_KEY única gerada
✅ CORS configurado apenas para localhost
✅ Senhas com hash bcrypt
✅ Tokens JWT com expiração
✅ HTTPS no Appwrite Cloud

**⚠️ Para produção:** Você precisará gerar nova SECRET_KEY e configurar CORS adequadamente.

## 📚 Documentação Adicional

- [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) - Guia completo do sistema
- [APPWRITE_SETUP.md](./APPWRITE_SETUP.md) - Como configurar collection no Appwrite
- [SETUP_RAPIDO_AUTH.md](./SETUP_RAPIDO_AUTH.md) - Setup rápido

## ✨ Próximos Passos

1. **Crie a collection no Appwrite** (uma vez só) - [Guia aqui](./APPWRITE_SETUP.md)
2. **Inicie o backend** - Terminal 1
3. **Inicie o frontend** - Terminal 2
4. **Teste criando uma conta** - http://localhost:5173/register
5. **Pronto!** Sistema funcionando localmente 🎉

## 💡 Dica

Mantenha dois terminais abertos:
- **Terminal 1:** Backend (porta 8000)
- **Terminal 2:** Frontend (porta 5173)

Assim você pode ver os logs de ambos em tempo real enquanto desenvolve!
