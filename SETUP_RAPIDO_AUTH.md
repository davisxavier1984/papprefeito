# 🚀 Setup Rápido - Sistema de Autenticação

Este guia mostra como colocar o sistema de autenticação em funcionamento rapidamente.

## ✅ Status da Configuração

### Backend
- ✅ Código implementado
- ✅ Dependências instaladas
- ✅ Arquivo `.env` configurado
- ✅ Testes passando

### Frontend
- ✅ Código implementado
- ✅ Dependências instaladas (zustand)
- ✅ Store e serviços configurados
- ✅ Componentes prontos

### Appwrite
- ⚠️ **PENDENTE**: Criar collection `users` no Appwrite

## 🎯 Próximos Passos (em ordem)

### 1. Criar Collection no Appwrite (5 minutos)

**⚠️ IMPORTANTE:** Esta é a ÚNICA etapa que falta para o sistema funcionar!

Siga o guia detalhado: [APPWRITE_SETUP.md](./APPWRITE_SETUP.md)

**Resumo rápido:**
1. Acesse https://cloud.appwrite.io
2. Navegue até Database → `papprefeito_db`
3. Crie collection `users` com os atributos:
   - `email` (String, 255, required, unique)
   - `nome` (String, 255, required)
   - `hashed_password` (String, 255, required)
   - `is_active` (Boolean, required, default: true)
   - `is_superuser` (Boolean, required, default: false)
   - `created_at` (String, 50, required)
   - `updated_at` (String, 50, optional)
4. Crie índice único para `email`

### 2. Iniciar o Backend

```bash
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
uvicorn app.main:app --reload --port 8000
```

O backend estará disponível em:
- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs

### 3. Iniciar o Frontend

```bash
cd frontend
npm run dev
```

O frontend estará disponível em:
- App: http://localhost:5173

### 4. Testar o Sistema

#### Opção A: Via Interface Web
1. Acesse http://localhost:5173/register
2. Crie uma conta
3. Faça login
4. Teste as rotas protegidas

#### Opção B: Via API (curl)

**Registrar usuário:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "nome": "Administrador",
    "password": "Admin123!"
  }'
```

**Fazer login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!"
  }'
```

Você receberá um `access_token` e `refresh_token`.

**Acessar rota protegida:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

#### Opção C: Via Swagger UI

1. Acesse http://localhost:8000/docs
2. Clique em `/api/auth/register` → Try it out
3. Preencha os dados e execute
4. Use `/api/auth/login` para obter tokens
5. Clique no botão "Authorize" (🔒) no topo
6. Cole o `access_token` e clique em Authorize
7. Agora pode testar todas as rotas protegidas

### 5. Criar Superusuário

Para acessar rotas administrativas, você precisa de um superusuário:

1. Crie um usuário normalmente (passo 4)
2. Acesse o Appwrite Console
3. Navegue até Database → `papprefeito_db` → `users`
4. Encontre seu usuário
5. Edite e mude `is_superuser` para `true`

## 📋 Checklist de Configuração

- [ ] Collection `users` criada no Appwrite
- [ ] Índice único para `email` criado
- [ ] Backend iniciado sem erros
- [ ] Frontend iniciado sem erros
- [ ] Usuário de teste criado com sucesso
- [ ] Login funcionando
- [ ] Token sendo gerado
- [ ] Rotas protegidas acessíveis com token
- [ ] Primeiro superusuário criado

## 🔧 Configurações Atuais

### Backend (.env)
```env
SECRET_KEY=2VWixHCyDUBzYTKPK0E2Bs49cm9EZeWcMMpcOrpY_CI
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APPWRITE_DATABASE_ID=papprefeito_db
```

### Endpoints de Autenticação

Todos os endpoints estão sob `/api/auth`:

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/register` | Registrar novo usuário | ❌ |
| POST | `/login` | Login | ❌ |
| POST | `/refresh` | Renovar token | ✅ (refresh token) |
| GET | `/me` | Obter perfil | ✅ |
| PUT | `/me` | Atualizar perfil | ✅ |
| POST | `/me/change-password` | Mudar senha | ✅ |
| DELETE | `/me` | Desativar conta | ✅ |
| POST | `/logout` | Logout | ✅ |

### Componentes Frontend Disponíveis

- `LoginForm.tsx` - Formulário de login
- `RegisterForm.tsx` - Formulário de registro
- `UserProfile.tsx` - Perfil do usuário
- `ProtectedRoute.tsx` - HOC para proteger rotas

### Store Zustand

```typescript
import { useAuthStore } from './stores/authStore';

// No seu componente
const { user, isAuthenticated, login, logout } = useAuthStore();
```

### Serviço de Autenticação

```typescript
import { authService } from './services/authService';

// Login
const { user, tokens } = await authService.login({ email, password });

// Logout
await authService.logout();
```

## 🐛 Troubleshooting

### Backend não inicia
- Verifique se o venv está ativado
- Confirme que todas as dependências estão instaladas: `pip install -r requirements.txt`

### "Collection not found"
- Verifique se criou a collection `users` no Appwrite
- Confirme que o Collection ID é exatamente `users`

### Erro de JWT
- Verifique se a `SECRET_KEY` está configurada no `.env`
- Confirme que o `.env` está no diretório `backend/`

### Erro de importação (bcrypt)
- Execute: `pip install bcrypt==4.1.3`

### Frontend não conecta com backend
- Verifique se o backend está rodando na porta 8000
- Confirme o `.env` do frontend: `VITE_API_BASE_URL=http://localhost:8000/api`

## 📚 Documentação Adicional

- [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) - Guia completo do sistema
- [APPWRITE_SETUP.md](./APPWRITE_SETUP.md) - Instruções detalhadas do Appwrite
- http://localhost:8000/docs - Documentação interativa da API

## 🎉 Pronto!

Após seguir estes passos, seu sistema de autenticação estará 100% funcional!

**Tempo estimado:** 10-15 minutos (sendo 5 minutos só para criar a collection no Appwrite)
