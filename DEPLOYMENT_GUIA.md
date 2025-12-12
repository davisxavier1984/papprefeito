# �배 Guia de Deployment - Gestão de Usuários

## ⚠️ Situação Atual

A implementação dos novos endpoints de gestão de usuários foi concluída **localmente**, mas o servidor de **produção** (`api-maispap.dasix.site`) ainda não foi atualizado.

### ❌ Por que o erro 404 ocorre:

```
POST https://api-maispap.dasix.site/api/users/ → 404 Not Found
```

O servidor de produção ainda está rodando o código **antigo** que não tem os endpoints `/api/users/*`.

---

## ✅ O que foi implementado (LOCAL)

### Novos Endpoints:
- ✅ `GET /api/users/` - Listar usuários com filtros
- ✅ `GET /api/users/{id}` - Obter detalhes
- ✅ `POST /api/users/` - Criar usuário
- ✅ `PUT /api/users/{id}` - Atualizar usuário
- ✅ `DELETE /api/users/{id}` - Deletar usuário (soft delete)

### Arquivos Modificados:
1. `backend/app/api/endpoints/users.py` (NOVO)
2. `backend/app/api/router.py` (EDITADO)
3. `backend/app/models/schemas.py` (EDITADO)
4. `backend/app/services/user_service.py` (EDITADO)
5. `frontend/src/services/userManagementService.ts` (CORRIGIDO)

---

## 🚀 Como Fazer Deploy

### Pré-requisitos:
- Acesso SSH ao servidor de produção
- Permissões para reiniciar o serviço do backend

### Passos:

#### 1. **SSH para o Servidor**
```bash
ssh usuario@api-maispap.dasix.site
```

#### 2. **Navegar para o Diretório do Projeto**
```bash
cd /path/to/papprefeito-dev
```

#### 3. **Ativar o Ambiente Virtual**
```bash
source .venv/bin/activate  # ou source venv/bin/activate
```

#### 4. **Atualizar o Código**
```bash
# Se estiver usando Git:
git pull origin dev  # ou a branch que você usa

# OU copiar manualmente os arquivos:
# cp -r /local/path/backend/* backend/
```

#### 5. **Verificar se Tudo está OK (Opcional)**
```bash
cd backend
python3 test_users_endpoints.py
```

Expected output:
```
✅ Imports: PASSOU
✅ UserUpdate Schema: PASSOU
✅ UserService.list_users: PASSOU

✅ TODOS OS TESTES PASSARAM!
```

#### 6. **Reiniciar o Serviço Backend**

Se usar **systemd**:
```bash
sudo systemctl restart papprefeito-backend
```

Se usar **Docker**:
```bash
docker-compose restart backend
# ou
docker-compose up -d backend
```

Se usar **manual** (Uvicorn):
```bash
# Kill o processo antigo:
pkill -f "uvicorn.*papprefeito"

# Iniciar novamente:
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. **Verificar se Está Rodando**
```bash
curl http://localhost:8000/api/users/
# Deve retornar erro 401 (requer autenticação) ou 200 com lista vazia
```

#### 8. **Fazer Deploy do Frontend (OPCIONAL)**

Se também atualizou o frontend:

```bash
cd frontend
pnpm install  # atualizar dependências
pnpm run build  # build para produção

# Copiar arquivos para o servidor web (nginx, apache, etc)
cp -r dist/* /var/www/papprefeito/
```

---

## 🧪 Testes Após Deployment

### Teste 1: Verificar se endpoints existem
```bash
# Login primeiro
TOKEN=$(curl -X POST "http://api-maispap.dasix.site/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"YourPassword123"}' \
  | jq -r '.access_token')

# Listar usuários
curl -X GET "http://api-maispap.dasix.site/api/users/" \
  -H "Authorization: Bearer $TOKEN"
```

### Teste 2: Verificar criação de usuário
```bash
curl -X POST "http://api-maispap.dasix.site/api/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "nome": "Usuário Teste",
    "password": "SenhaForte123"
  }'
```

### Teste 3: Verificar deleção
```bash
curl -X DELETE "http://api-maispap.dasix.site/api/users/{user_id}" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔧 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'app'`
**Solução:** Certifique-se de estar no diretório `backend` ao rodar o servidor.

### Erro: `ImportError: cannot import name 'users'`
**Solução:** O arquivo `backend/app/api/endpoints/users.py` não foi copiado. Verifique se está lá.

### Erro: Endpoints retornam 404 ainda após deploy
**Solução:**
1. Verifique se o código foi atualizado: `git status`
2. Reinicie o serviço: `sudo systemctl restart papprefeito-backend`
3. Limpe cache: `systemctl restart nginx` (se usar nginx)
4. Verifique logs: `journalctl -u papprefeito-backend -f`

### Erro: 401 Unauthorized ao testar
**Solução:** Normal! Você precisa enviar um token JWT válido. Faça login primeiro.

---

## 📋 Checklist de Deployment

- [ ] Código foi atualizado (`git pull` ou cópia manual)
- [ ] Arquivo `backend/app/api/endpoints/users.py` existe
- [ ] Arquivo `backend/app/api/router.py` foi atualizado
- [ ] Testes passam: `python3 test_users_endpoints.py`
- [ ] Serviço backend foi reiniciado
- [ ] Frontend foi reconstruído (se necessário)
- [ ] Endpoints `/api/users/*` respondem corretamente
- [ ] Gestão de usuários funciona no navegador

---

## 📞 Problemas?

Se continuar com erro 404:

1. **Verifique se está na URL correta:**
   - ❌ Errado: `https://api-maispap.dasix.site/api/users` (sem barra)
   - ✅ Correto: `https://api-maispap.dasix.site/api/users/` (com barra)

2. **Verifique os logs do servidor:**
   ```bash
   tail -f /var/log/papprefeito-backend.log
   # ou
   journalctl -u papprefeito-backend -f
   ```

3. **Teste com curl:**
   ```bash
   curl -v https://api-maispap.dasix.site/api/users/ \
     -H "Authorization: Bearer seu_token_aqui"
   ```

4. **Reinicie tudo:**
   ```bash
   sudo systemctl restart papprefeito-backend
   sudo systemctl restart nginx  # se usar nginx
   ```

---

**Última atualização:** 2025-10-26
**Status da Implementação:** ✅ Código implementado e testado localmente
**Status do Deployment:** ⏳ Aguardando deploy em produção
