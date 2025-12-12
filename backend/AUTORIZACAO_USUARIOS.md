# Sistema de Autorização de Usuários

Este documento explica como usar o sistema de autorização de usuários implementado no PAP Prefeito.

## 📋 Visão Geral

O sistema de autorização controla quais usuários podem acessar a aplicação. Apenas usuários autorizados podem fazer login e usar o sistema.

### Fluxo de Autorização

1. **Usuário se registra** → Status: `is_authorized: false`
2. **Usuário tenta fazer login** → Recebe erro: "Aguardando autorização do administrador"
3. **Administrador acessa o painel** → Vê lista de usuários pendentes
4. **Administrador autoriza o usuário** → Status: `is_authorized: true`
5. **Usuário pode fazer login** → Acesso liberado

## 🚀 Configuração Inicial

### 1. Adicionar campo `is_authorized` no Appwrite

Execute o script para adicionar o campo na collection de usuários:

```bash
cd backend
source ../.venv/bin/activate  # ou source venv/bin/activate
python3 add_authorization_field.py
```

O script irá:
- Adicionar o campo `is_authorized` (boolean, padrão: false)
- Perguntar se deseja marcar superusuários existentes como autorizados

### 2. Criar primeiro superusuário (se necessário)

Se você ainda não tem um superusuário autorizado, crie um:

```bash
python3 create_first_superuser.py
```

O script irá solicitar:
- Email
- Nome completo
- Senha (mínimo 8 caracteres, com maiúscula, minúscula e número)

O superusuário será criado já autorizado (`is_authorized: true`).

## 🔐 Endpoints de Administração

### Listar usuários pendentes

```http
GET /api/auth/admin/users/pending
Authorization: Bearer {access_token}
```

**Resposta:**
```json
{
  "total": 2,
  "users": [
    {
      "id": "user_id_1",
      "email": "usuario1@example.com",
      "nome": "Usuário 1",
      "is_active": true,
      "is_authorized": false,
      "is_superuser": false,
      "created_at": "2025-10-20T10:00:00Z"
    }
  ]
}
```

### Listar todos os usuários

```http
GET /api/auth/admin/users?skip=0&limit=100
Authorization: Bearer {access_token}
```

### Autorizar usuário

```http
PUT /api/auth/admin/users/{user_id}/authorize
Authorization: Bearer {access_token}
```

**Resposta:**
```json
{
  "id": "user_id",
  "email": "usuario@example.com",
  "nome": "Nome do Usuário",
  "is_active": true,
  "is_authorized": true,
  "is_superuser": false,
  "created_at": "2025-10-20T10:00:00Z"
}
```

### Revogar autorização

```http
PUT /api/auth/admin/users/{user_id}/revoke
Authorization: Bearer {access_token}
```

### Promover a superusuário

```http
PUT /api/auth/admin/users/{user_id}/superuser?is_superuser=true
Authorization: Bearer {access_token}
```

### Remover de superusuário

```http
PUT /api/auth/admin/users/{user_id}/superuser?is_superuser=false
Authorization: Bearer {access_token}
```

## 🛡️ Permissões

### Usuário Normal
- ✅ Pode fazer login (se autorizado)
- ✅ Pode acessar suas próprias informações
- ✅ Pode atualizar seu perfil
- ✅ Pode alterar sua senha
- ❌ Não pode acessar endpoints de administração

### Superusuário
- ✅ Todas as permissões de usuário normal
- ✅ Listar todos os usuários
- ✅ Listar usuários pendentes
- ✅ Autorizar/revogar usuários
- ✅ Promover/rebaixar superusuários
- ⚠️ Não pode remover suas próprias permissões de superusuário

## 📝 Exemplos de Uso

### Exemplo 1: Autorizar novo usuário

```bash
# 1. Listar usuários pendentes
curl -X GET "http://localhost:8000/api/auth/admin/users/pending" \
  -H "Authorization: Bearer {seu_token}"

# 2. Autorizar usuário específico
curl -X PUT "http://localhost:8000/api/auth/admin/users/{user_id}/authorize" \
  -H "Authorization: Bearer {seu_token}"
```

### Exemplo 2: Promover usuário a administrador

```bash
# 1. Primeiro, autorizar o usuário
curl -X PUT "http://localhost:8000/api/auth/admin/users/{user_id}/authorize" \
  -H "Authorization: Bearer {seu_token}"

# 2. Depois, promover a superusuário
curl -X PUT "http://localhost:8000/api/auth/admin/users/{user_id}/superuser?is_superuser=true" \
  -H "Authorization: Bearer {seu_token}"
```

## 🔍 Campos do Modelo User

```python
{
  "id": str,              # ID único do usuário
  "email": str,           # Email (único)
  "nome": str,            # Nome completo
  "is_active": bool,      # Se o usuário está ativo
  "is_authorized": bool,  # Se o usuário foi autorizado
  "is_superuser": bool,   # Se o usuário é administrador
  "created_at": datetime, # Data de criação
  "updated_at": datetime  # Data da última atualização
}
```

## ⚠️ Notas Importantes

1. **Novos usuários**: Sempre são criados com `is_authorized: false`
2. **Superusuários**: Devem ser criados com `is_authorized: true` usando o script
3. **Login**: Usuários não autorizados recebem erro 403 ao tentar fazer login
4. **Segurança**: Apenas superusuários podem gerenciar autorizações

## 🐛 Troubleshooting

### Erro: "Usuário aguardando autorização do administrador"

**Causa**: O usuário ainda não foi autorizado por um administrador.

**Solução**:
1. Peça a um administrador para autorizar seu acesso
2. Ou, se você é administrador, autorize o usuário via endpoint

### Erro: "Permissões insuficientes"

**Causa**: Você não tem permissões de superusuário.

**Solução**:
1. Peça a um administrador para promovê-lo
2. Ou use o endpoint `/auth/me` para verificar suas permissões

## 📚 Próximos Passos

Após configurar o sistema de autorização, você pode:

1. Criar uma interface de administração no frontend
2. Implementar notificações por email quando usuário for autorizado
3. Adicionar logs de auditoria para ações de administração
4. Implementar sistema de roles mais granular (opcional)
