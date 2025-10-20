# 🎯 Como Criar a Collection 'users' no Appwrite

## Passo 1: Acessar o Appwrite Console

1. Acesse: **https://cloud.appwrite.io**
2. Faça login na sua conta
3. Você verá uma lista de projetos

## Passo 2: Selecionar seu Projeto

1. Procure pelo projeto com ID: **`68dc49bf000cebd54b85`**
2. Ou procure pelo nome do projeto (provavelmente "papprefeito" ou similar)
3. Clique no projeto para abrir

## Passo 3: Navegar até Databases

No menu lateral esquerdo, você verá várias opções:
- Auth
- **Databases** ← Clique aqui
- Functions
- Storage
- Messaging
- etc.

## Passo 4: Selecionar o Database

Após clicar em "Databases", você verá uma lista de databases.

Procure por: **`papprefeito_db`**

Clique nele para abrir.

## Passo 5: Você Está no Database Correto!

Agora você deve ver:
- **Nome do database**: `papprefeito_db` (no topo)
- **Abas**: Overview, Collections, Indexes, Settings
- **Lista de collections existentes**: Você deve ver `edicoes_municipios`

## Passo 6: Criar Nova Collection

### Opção A: Botão no canto superior direito
Procure por um botão **"Create Collection"** (geralmente azul/roxo) no canto superior direito.

### Opção B: Se não vir collections
Se a tela estiver vazia, procure por:
- Um botão grande **"Create your first collection"**
- Ou **"+ Create Collection"**

### Opção C: Menu de ações
- Procure por um ícone de "+" ou "Add"
- Ou clique em **"Collections"** na aba superior

## Passo 7: Preencher o Formulário

Quando o formulário abrir:

**Collection ID**: `users`
- ⚠️ IMPORTANTE: Escreva exatamente **`users`** (minúsculas, sem acentos)
- Este ID não pode ser alterado depois

**Name** (opcional): `Users` ou `Usuários`
- Este é apenas um nome de exibição, pode ser alterado depois

Clique em **"Create"**

## Passo 8: Adicionar Atributos

Após criar a collection, você será direcionado para a página da collection.

Procure pela aba **"Attributes"** (ou pode estar como "Schema")

### Adicionar cada atributo:

Clique em **"Create Attribute"** ou **"+ Add Attribute"**

Você verá opções de tipos: String, Integer, Boolean, DateTime, etc.

#### Atributo 1: email
1. Tipo: **String**
2. Key: `email`
3. Size: `255`
4. Required: ✅ Marque
5. Default: Deixe vazio
6. Clique em **"Create"**

#### Atributo 2: nome
1. Tipo: **String**
2. Key: `nome`
3. Size: `255`
4. Required: ✅ Marque
5. Clique em **"Create"**

#### Atributo 3: hashed_password
1. Tipo: **String**
2. Key: `hashed_password`
3. Size: `255`
4. Required: ✅ Marque
5. Clique em **"Create"**

#### Atributo 4: is_active
1. Tipo: **Boolean**
2. Key: `is_active`
3. Required: ✅ Marque
4. Default: `true` (marque ou selecione "true")
5. Clique em **"Create"**

#### Atributo 5: is_superuser
1. Tipo: **Boolean**
2. Key: `is_superuser`
3. Required: ✅ Marque
4. Default: `false`
5. Clique em **"Create"**

#### Atributo 6: created_at
1. Tipo: **String**
2. Key: `created_at`
3. Size: `50`
4. Required: ✅ Marque
5. Clique em **"Create"**

#### Atributo 7: updated_at
1. Tipo: **String**
2. Key: `updated_at`
3. Size: `50`
4. Required: ❌ NÃO marque
5. Clique em **"Create"**

## Passo 9: Criar Índice para Email

1. Vá para a aba **"Indexes"**
2. Clique em **"Create Index"**
3. Preencha:
   - **Key**: `email_unique` (ou qualquer nome)
   - **Type**: Selecione **"Unique"**
   - **Attributes**: Selecione `email` da lista
   - **Order**: `ASC`
4. Clique em **"Create"**

## Passo 10: Configurar Permissões

1. Vá para a aba **"Settings"**
2. Role até a seção **"Permissions"**
3. Ative **"Document Security"**
4. Configure as permissões:

### Para "Create":
- Clique em **"Add Role"**
- Selecione **"Any"** (permite qualquer pessoa criar - necessário para registro)

### Para "Read":
- Clique em **"Add Role"**
- Selecione **"Users"** (apenas usuários autenticados podem ler)

### Para "Update":
- Clique em **"Add Role"**
- Selecione **"Users"** (apenas usuários autenticados podem atualizar)

### Para "Delete":
- Clique em **"Add Role"**
- Selecione **"Users"** (apenas usuários autenticados podem deletar)

5. Clique em **"Update"** para salvar

---

## ✅ Verificar se Funcionou

Volte ao terminal e execute:

```bash
cd backend
source venv/bin/activate
python test_appwrite_connection.py
```

Você deve ver:

```
4. Verificando collection 'users'...
   ✓ Collection 'users' encontrada!
   ✓ Nome: Users
   ✓ Atributos: 7
```

Se ver isso, execute:

```bash
python test_auth_flow.py
```

---

## 🆘 Não Encontrou a Opção?

### Se não vir o botão "Create Collection":

1. **Verifique se está no database correto**: O nome deve ser `papprefeito_db`
2. **Verifique suas permissões**: Você é o dono do projeto?
3. **Tente atualizar a página**: F5 ou Ctrl+R
4. **Verifique se está na aba "Collections"**: Deve estar entre Overview e Settings

### Se o Appwrite mudou a interface:

1. Procure por ícones de "+" em qualquer lugar da tela
2. Procure por menus de contexto (⋮ ou ···)
3. Tente clicar com botão direito na lista de collections

### Link alternativo para tentar:

Tente acessar diretamente:
```
https://cloud.appwrite.io/console
```

Depois navegue: Project → Databases → papprefeito_db

---

## 📸 Referências Visuais

A interface do Appwrite geralmente tem:
- **Barra lateral esquerda**: Menu principal (Auth, Databases, Functions...)
- **Topo**: Nome do projeto e botões de ação
- **Centro**: Conteúdo principal (lista de databases ou collections)
- **Canto superior direito**: Botão principal de ação (Create Database, Create Collection, etc)

---

## ✅ Checklist de Criação

Use esta checklist para conferir:

- [ ] Acessei o Appwrite Console
- [ ] Selecionei o projeto correto
- [ ] Naveguei até Databases
- [ ] Abri o database `papprefeito_db`
- [ ] Cliquei em "Create Collection"
- [ ] Collection ID: `users` (minúsculas)
- [ ] Criei atributo: `email` (String, 255, required)
- [ ] Criei atributo: `nome` (String, 255, required)
- [ ] Criei atributo: `hashed_password` (String, 255, required)
- [ ] Criei atributo: `is_active` (Boolean, required, default: true)
- [ ] Criei atributo: `is_superuser` (Boolean, required, default: false)
- [ ] Criei atributo: `created_at` (String, 50, required)
- [ ] Criei atributo: `updated_at` (String, 50, NOT required)
- [ ] Criei índice único para `email`
- [ ] Configurei permissões (Create: any, Read/Update/Delete: users)
- [ ] Executei `python test_appwrite_connection.py` com sucesso
- [ ] Executei `python test_auth_flow.py` com sucesso

---

Precisa de mais ajuda? Me avise e posso criar um script para automatizar parte do processo ou te dar mais orientações específicas! 🚀
