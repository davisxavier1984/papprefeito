# 🔐 Sistema de Autorização de Usuários - Guia Rápido

## ✅ O que foi implementado

- ✅ Campo `is_authorized` adicionado ao modelo User
- ✅ Novos usuários são criados **não autorizados** por padrão
- ✅ Login bloqueado para usuários não autorizados
- ✅ 5 novos endpoints de administração para gerenciar usuários
- ✅ Scripts auxiliares para configuração
- ✅ Testes automatizados

## 🚀 Setup Rápido (3 passos)

### 1. Adicionar campo no banco de dados

```bash
cd backend
source ../venv/bin/activate  # ou: source .venv/bin/activate
python3 add_authorization_field.py
```

Responda "s" quando perguntar se deseja autorizar superusuários existentes.

### 2. Criar primeiro superusuário (se necessário)

```bash
python3 create_first_superuser.py
```

Preencha: email, nome e senha (mín. 8 caracteres).

### 3. Testar

```bash
python3 test_authorization.py
```

Se tudo estiver OK, você verá: ✅ TODOS OS TESTES PASSARAM!

## 📡 Novos Endpoints de Admin

Todos requerem token de superusuário no header `Authorization: Bearer {token}`:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/auth/admin/users/pending` | Lista usuários pendentes de autorização |
| GET | `/api/auth/admin/users` | Lista todos os usuários |
| PUT | `/api/auth/admin/users/{id}/authorize` | Autoriza um usuário |
| PUT | `/api/auth/admin/users/{id}/revoke` | Revoga autorização |
| PUT | `/api/auth/admin/users/{id}/superuser?is_superuser=true` | Promove/rebaixa superusuário |

## 🔄 Fluxo de Uso

```
1. Usuário faz registro → is_authorized = false
2. Usuário tenta login  → Erro: "Aguardando autorização do administrador"
3. Admin acessa API     → GET /api/auth/admin/users/pending
4. Admin autoriza       → PUT /api/auth/admin/users/{id}/authorize
5. Usuário faz login    → ✅ Sucesso!
```

## 🧪 Como Testar

### Via CLI (curl)

```bash
# 1. Login como admin
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SuaSenha123"}'

# 2. Salvar o token retornado
TOKEN="cole_aqui_o_access_token"

# 3. Listar usuários pendentes
curl -X GET "http://localhost:8000/api/auth/admin/users/pending" \
  -H "Authorization: Bearer $TOKEN"

# 4. Autorizar usuário
curl -X PUT "http://localhost:8000/api/auth/admin/users/{user_id}/authorize" \
  -H "Authorization: Bearer $TOKEN"
```

### Via Swagger UI

1. Inicie o servidor: `uvicorn app.main:app --reload`
2. Acesse: http://localhost:8000/docs
3. Clique em "Authorize" e cole seu token
4. Teste os novos endpoints em "Autenticação"

## 📁 Arquivos Criados/Modificados

### Modificados:
- ✏️ `app/models/schemas.py` - Adicionado campo `is_authorized` e novos schemas
- ✏️ `app/services/user_service.py` - Adicionados métodos de autorização
- ✏️ `app/api/endpoints/auth.py` - Adicionados 5 novos endpoints de admin

### Criados:
- 📄 `add_authorization_field.py` - Script para adicionar campo no Appwrite
- 📄 `create_first_superuser.py` - Script para criar admin inicial
- 📄 `test_authorization.py` - Testes automatizados
- 📄 `AUTORIZACAO_USUARIOS.md` - Documentação completa
- 📄 `README_AUTORIZACAO.md` - Este guia rápido

## ⚠️ Avisos Importantes

1. **Execute os scripts na ordem**: primeiro `add_authorization_field.py`, depois `create_first_superuser.py`
2. **Superusuários existentes**: O script perguntará se deseja autorizá-los automaticamente
3. **Novos registros**: Todos virão com `is_authorized = false` por padrão
4. **Segurança**: Admins não podem remover suas próprias permissões

## 🐛 Problemas Comuns

**"Aguardando autorização do administrador"**
→ Normal! Peça a um admin para autorizar via API

**"Permissões insuficientes"**
→ Você não é superusuário. Peça para ser promovido

**"Campo is_authorized não existe"**
→ Execute: `python3 add_authorization_field.py`

## 📞 Próximas Melhorias (Opcional)

- [ ] Interface de admin no frontend
- [ ] Email de notificação quando usuário for autorizado
- [ ] Logs de auditoria para ações de admin
- [ ] Sistema de roles mais granular

---

**Criado em:** 2025-10-20
**Versão:** 1.0
