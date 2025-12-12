# Guia do Sistema de Autenticação

Este documento descreve o sistema completo de autenticação implementado no projeto papprefeito-dev.

## Índice

1. [Visão Geral](#visão-geral)
2. [Backend](#backend)
3. [Frontend](#frontend)
4. [Configuração](#configuração)
5. [Uso](#uso)
6. [Próximos Passos](#próximos-passos)

## Visão Geral

O sistema de autenticação foi implementado usando:

- **Backend**: FastAPI com JWT (JSON Web Tokens)
- **Frontend**: React com Zustand para gerenciamento de estado
- **Armazenamento**: Appwrite Cloud Database
- **Segurança**: Bcrypt para hash de senhas, tokens com expiração

### Funcionalidades Implementadas

✅ Registro de usuários com validação de senha forte
✅ Login com email e senha
✅ Tokens JWT (access e refresh)
✅ Refresh automático de tokens
✅ Proteção de rotas
✅ Perfil de usuário (visualização e edição)
✅ Alteração de senha
✅ Desativação de conta
✅ Persistência de sessão (localStorage)
✅ Tratamento de erros 401/403

---

## Backend

### Estrutura de Arquivos

```
backend/app/
├── core/
│   ├── config.py           # Configurações (SECRET_KEY, JWT settings)
│   ├── security.py         # Funções de hash e JWT
│   ├── dependencies.py     # Dependências FastAPI (get_current_user, etc)
│   └── appwrite_client.py  # Cliente Appwrite
├── models/
│   └── schemas.py          # Schemas Pydantic (User, Token, Login, etc)
├── services/
│   └── user_service.py     # Lógica de negócio de usuários
└── api/
    ├── router.py           # Router principal
    └── endpoints/
        └── auth.py         # Endpoints de autenticação
```

### Endpoints Disponíveis

#### **POST** `/api/auth/register`
Registra um novo usuário.

**Request:**
```json
{
  "email": "usuario@example.com",
  "nome": "Nome Completo",
  "password": "Senha123"
}
```

**Response:**
```json
{
  "id": "user_id",
  "email": "usuario@example.com",
  "nome": "Nome Completo",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-19T..."
}
```

#### **POST** `/api/auth/login`
Autentica um usuário.

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "Senha123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### **POST** `/api/auth/refresh`
Renova o access token.

**Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### **GET** `/api/auth/me`
Obtém dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer {access_token}
```

#### **PUT** `/api/auth/me`
Atualiza dados do usuário autenticado.

#### **POST** `/api/auth/me/change-password`
Altera a senha do usuário.

#### **DELETE** `/api/auth/me`
Desativa a conta do usuário.

#### **POST** `/api/auth/logout`
Realiza logout (limpa tokens no cliente).

### Protegendo Rotas no Backend

```python
from fastapi import Depends
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.models.schemas import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Olá {current_user.nome}!"}

@router.get("/admin")
async def admin_route(current_user: User = Depends(get_current_superuser)):
    return {"message": "Área administrativa"}
```

---

## Frontend

### Estrutura de Arquivos

```
frontend/src/
├── stores/
│   └── authStore.ts          # Zustand store para autenticação
├── services/
│   └── authService.ts        # Cliente API de autenticação
└── components/
    └── Auth/
        ├── LoginForm.tsx          # Formulário de login
        ├── RegisterForm.tsx       # Formulário de registro
        ├── ProtectedRoute.tsx     # Proteção de rotas
        └── UserProfile.tsx        # Perfil do usuário
```

### Store Zustand

```typescript
import { useAuthStore } from './stores/authStore';

// Acessar estado
const { user, isAuthenticated, isLoading } = useAuthStore();

// Ações
const { login, logout, updateUser, setTokens } = useAuthStore();
```

### Serviço de Autenticação

```typescript
import { authService } from './services/authService';

// Login
const { user, tokens } = await authService.login({
  email: 'user@example.com',
  password: 'Senha123'
});

// Logout
await authService.logout();

// Obter usuário atual
const user = await authService.getCurrentUser();

// Atualizar perfil
const updatedUser = await authService.updateProfile({
  nome: 'Novo Nome'
});
```

### Configurando Rotas

**Exemplo de configuração com React Router:**

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LoginForm } from './components/Auth/LoginForm';
import { RegisterForm } from './components/Auth/RegisterForm';
import { UserProfile } from './components/Auth/UserProfile';
import { ProtectedRoute } from './components/Auth/ProtectedRoute';
import { Dashboard } from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />

        {/* Rotas protegidas */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <UserProfile />
            </ProtectedRoute>
          }
        />

        {/* Rota apenas para admin */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute requireSuperuser>
              <AdminPanel />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
```

### Componente de Logout

```typescript
import { Button } from 'antd';
import { LogoutOutlined } from '@ant-design/icons';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';

export const LogoutButton = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  return (
    <Button
      icon={<LogoutOutlined />}
      onClick={handleLogout}
    >
      Sair
    </Button>
  );
};
```

---

## Configuração

### 1. Configurar Collection no Appwrite

Você precisa criar uma collection chamada `users` no Appwrite com os seguintes atributos:

| Atributo | Tipo | Obrigatório | Tamanho |
|----------|------|-------------|---------|
| email | String | Sim | 255 |
| nome | String | Sim | 255 |
| hashed_password | String | Sim | 255 |
| is_active | Boolean | Sim | - |
| is_superuser | Boolean | Sim | - |
| created_at | String (DateTime) | Sim | 50 |
| updated_at | String (DateTime) | Não | 50 |

**Índices:**
- email (unique, key)

### 2. Variáveis de Ambiente - Backend

Criar/editar arquivo `.env` no backend:

```env
# Secret key para JWT (gere uma chave forte!)
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao

# Algoritmo JWT
ALGORITHM=HS256

# Tempo de expiração dos tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Appwrite
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=seu-project-id
APPWRITE_API_KEY=sua-api-key
APPWRITE_DATABASE_ID=papprefeito_db
```

**⚠️ IMPORTANTE:** Gere uma SECRET_KEY forte para produção:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Variáveis de Ambiente - Frontend

Criar/editar arquivo `.env` no frontend:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## Uso

### 1. Iniciar o Backend

```bash
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
uvicorn app.main:app --reload --port 8000
```

### 2. Iniciar o Frontend

```bash
cd frontend
npm run dev
```

### 3. Acessar a Aplicação

- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs

### 4. Criar Primeiro Usuário

Acesse a rota `/register` no frontend ou faça um POST para `/api/auth/register`:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "nome": "Administrador",
    "password": "Admin123!"
  }'
```

**Para tornar um usuário superuser**, edite manualmente no Appwrite Database:
1. Acesse o Appwrite Console
2. Navegue até a collection `users`
3. Encontre o documento do usuário
4. Altere `is_superuser` para `true`

---

## Próximos Passos

### Melhorias Sugeridas

1. **Rate Limiting**
   - Implementar limite de tentativas de login
   - Proteção contra brute force

2. **Recuperação de Senha**
   - Endpoint para solicitar reset de senha
   - Envio de email com token de recuperação

3. **Verificação de Email**
   - Envio de email de confirmação no registro
   - Ativação de conta via link

4. **Two-Factor Authentication (2FA)**
   - Autenticação de dois fatores via TOTP
   - Códigos de backup

5. **Auditoria**
   - Log de ações sensíveis
   - Histórico de logins

6. **Testes**
   - Testes unitários para endpoints
   - Testes de integração
   - Testes E2E no frontend

7. **Blacklist de Tokens**
   - Implementar revogação de tokens
   - Lista negra de tokens no Redis

8. **OAuth/Social Login**
   - Login com Google, GitHub, etc.
   - Integração com provedores OAuth

---

## Segurança

### Boas Práticas Implementadas

✅ Senhas hasheadas com bcrypt
✅ Tokens JWT com expiração
✅ Refresh tokens para renovação segura
✅ HTTPS obrigatório em produção
✅ Validação de entrada rigorosa
✅ CORS configurado
✅ Tokens armazenados apenas em memória/localStorage seguro

### Checklist de Segurança para Produção

- [ ] Alterar SECRET_KEY para uma chave forte e única
- [ ] Configurar HTTPS
- [ ] Ativar CORS apenas para domínios confiáveis
- [ ] Implementar rate limiting
- [ ] Configurar logs de auditoria
- [ ] Revisar permissões do Appwrite
- [ ] Implementar monitoramento de tentativas de login
- [ ] Adicionar captcha no registro/login
- [ ] Implementar política de expiração de senhas
- [ ] Configurar backup automático do banco de dados

---

## Suporte

Para dúvidas ou problemas:

1. Verifique a documentação da API em `/docs`
2. Consulte os logs do backend
3. Verifique o console do navegador para erros do frontend
4. Revise as configurações do Appwrite

## Licença

Este sistema foi desenvolvido como parte do projeto papprefeito-dev.
