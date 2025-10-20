# 🗺️ Como Navegar no Appwrite Console (Guia Visual)

## Passo 1: Acessar o Console

1. Acesse: **https://cloud.appwrite.io**
2. Faça login
3. Você verá a **lista de projetos**

## Passo 2: Identificar seu Projeto

Procure por um projeto com:
- **Project ID**: `68dc49bf000cebd54b85`
- Ou nome relacionado a "papprefeito" ou "MaisPAP"

Clique no **card/cartão do projeto** para abrir.

---

## 🎯 O que você deve ver ao abrir o projeto:

### Menu Lateral Esquerdo (ou no topo)

Você deve ver estas opções:
- 🏠 **Overview** (Visão geral)
- 👥 **Auth** (Autenticação)
- 🗄️ **Databases** ← **CLIQUE AQUI**
- ⚡ **Functions** (Funções)
- 📦 **Storage** (Armazenamento)
- 📧 **Messaging** (Mensagens)
- ⚙️ **Settings** (Configurações)

---

## 🗄️ Ao clicar em "Databases"

Você deve ver uma **lista de databases**, incluindo:
- **`papprefeito_db`** ← Este é o seu database

### Se não vir "Databases" no menu:

**Opção A**: Pode estar em um submenu ou dropdown
- Procure por "Products" ou "Services"
- Ou um ícone de hamburger (☰)

**Opção B**: Pode estar em outra visualização
- Procure no topo por abas ou tabs
- Ou por um menu dropdown com o nome do projeto

---

## 📊 Dentro do Database `papprefeito_db`

Quando você clicar em `papprefeito_db`, deve ver:

### Opções no Topo:
- **Collections** ← Você está aqui
- **Settings**
- Possivelmente: "Documents", "Queries", etc.

### Lista de Collections:
Você deve ver 2 collections:
1. ✅ `edicoes_municipios` (já existia)
2. ✅ `users` (acabamos de criar)

---

## ⚙️ Configurar Permissões da Collection `users`

### Passo 1: Clicar na collection
Clique em **`users`** na lista de collections

### Passo 2: Procurar "Settings"
Procure por uma aba ou menu com:
- **"Settings"** ou **"Configurações"**
- Pode estar no topo da página
- Ou em um menu de três pontinhos (⋮ ou ···)

### Passo 3: Encontrar "Permissions"
Dentro de Settings, role a página até encontrar:
- **"Permissions"** ou **"Permissões"**
- **"Security"** ou **"Segurança"**
- **"Access Control"** ou **"Controle de Acesso"**

### Passo 4: Configurar

Você verá algo como:

```
Permissions (Document-level)
[ ] None
[x] Document Security

Permissions:
┌─────────────────────────────────────┐
│ Create                              │
│ [ Add role ]                        │
│                                     │
│ Read                                │
│ [ Add role ]                        │
│                                     │
│ Update                              │
│ [ Add role ]                        │
│                                     │
│ Delete                              │
│ [ Add role ]                        │
└─────────────────────────────────────┘
```

Para cada operação, clique em **"Add role"** e selecione:
- **Create**: Selecione `Any`
- **Read**: Selecione `Users`
- **Update**: Selecione `Users`
- **Delete**: Selecione `Users`

---

## 🔍 Ainda não encontrou?

Se você não está vendo as opções esperadas, me diga:

### O que você vê quando:

**1. Abre https://cloud.appwrite.io e faz login?**
- [ ] Lista de projetos
- [ ] Painel de um projeto específico
- [ ] Outra coisa: _____________

**2. Depois de clicar no seu projeto, qual menu você vê?**
- [ ] Menu lateral esquerdo
- [ ] Menu no topo (horizontal)
- [ ] Sem menu visível
- [ ] Outro: _____________

**3. Quando clica em "Databases", o que aparece?**
- [ ] Lista de databases
- [ ] Lista de collections diretamente
- [ ] Mensagem de erro
- [ ] Outra coisa: _____________

**4. Após clicar em `papprefeito_db`, você vê:**
- [ ] Collections: edicoes_municipios e users
- [ ] Apenas edicoes_municipios
- [ ] Nenhuma collection
- [ ] Outra coisa: _____________

---

## 💡 Alternativa: Configurar via Script

Se não conseguir encontrar as opções no console, podemos tentar configurar as permissões via API. Mas primeiro, preciso saber exatamente o que você está vendo.

---

## 📸 Dica Útil

Se quiser, você pode:
1. Tirar um print da tela do Appwrite
2. Salvar em `/tmp/appwrite_screen.png`
3. Eu posso ver a imagem e te ajudar melhor!

---

**Me diga:** O que você vê quando acessa o Appwrite? Consigo te guiar melhor sabendo exatamente qual interface você está vendo! 🎯
