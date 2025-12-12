# Gestão de Usuários - Frontend

## Visão Geral

Sistema completo de gestão de usuários para administradores (superusuários) do sistema PAP Prefeito.

## Estrutura Implementada

### 📁 Arquivos Criados

```
frontend/src/
├── services/
│   └── userManagementService.ts       # Serviço de API para gestão de usuários
├── components/
│   └── Admin/
│       ├── UserTable.tsx              # Tabela de listagem de usuários
│       ├── CreateUserModal.tsx        # Modal para criar novo usuário
│       └── EditUserModal.tsx          # Modal para editar usuário
└── pages/
    └── Admin/
        └── UserManagement.tsx         # Página principal de administração
```

### 📝 Arquivos Modificados

- `frontend/src/App.tsx` - Adicionada rota `/admin/users` protegida por superusuário
- `frontend/src/components/Layout/Header.tsx` - Adicionado menu dropdown com navegação e opção "Gestão de Usuários"
- `frontend/package.json` - Adicionada dependência `dayjs`

## Funcionalidades

### 🔐 Controle de Acesso

- Apenas **superusuários** podem acessar a página de gestão
- Proteção de rota através do componente `ProtectedRoute` com `requireSuperuser`
- Menu "Gestão de Usuários" só aparece para superusuários

### 📊 Dashboard de Estatísticas

Exibe cards com:
- Total de usuários cadastrados
- Usuários ativos
- Usuários inativos
- Número de superusuários

### 🔍 Filtros e Busca

- **Busca por texto**: Nome ou email
- **Filtro por status**: Ativos/Inativos
- **Filtro por tipo**: Superusuários/Usuários comuns
- Botão "Buscar" para aplicar filtros

### 👥 Tabela de Usuários

Colunas:
- Nome (com ícone diferenciado para superusuários)
- Email
- Tipo (Badge: Superusuário/Usuário)
- Status (Badge: Ativo/Inativo)
- Data de criação
- Ações (Editar, Ativar/Desativar, Deletar)

Recursos:
- Ordenação por colunas
- Filtros inline por tipo e status
- Paginação configurável (10, 20, 50, 100 itens)
- Confirmação antes de ações destrutivas

### ➕ Criar Usuário

Modal com campos:
- Nome completo (mínimo 3 caracteres)
- Email (com validação)
- Senha (validação de força)
  - Mínimo 8 caracteres
  - Letra maiúscula
  - Letra minúscula
  - Número
- Nível de autorização (Municipal/Estadual/Federal)
- Toggle para superusuário

### ✏️ Editar Usuário

Modal com campos:
- Nome completo
- Email
- Nível de autorização
- Status ativo/inativo
- Tipo (superusuário)

### 🗑️ Ações sobre Usuários

- **Editar**: Abre modal com dados preenchidos
- **Ativar/Desativar**: Altera status com confirmação
- **Deletar**: Remove permanentemente com confirmação dupla

## Navegação

### Menu do Usuário (Header)

Clique no avatar do usuário no canto superior direito para acessar:

- **Dashboard** - Volta para a tela principal
- **Meu Perfil** - Editar dados pessoais
- **Gestão de Usuários** _(apenas superusuários)_ - Administração de usuários
- **Sair** - Logout do sistema

## Como Usar

### Acessar a Gestão de Usuários

1. Faça login com uma conta de **superusuário**
2. Clique no seu avatar no canto superior direito
3. Selecione "Gestão de Usuários"
4. Você será redirecionado para `/admin/users`

### Criar um Novo Usuário

1. Na página de gestão, clique em **"Novo Usuário"**
2. Preencha todos os campos obrigatórios
3. Defina o nível de autorização
4. Marque "Superusuário" se necessário
5. Clique em **"Criar"**

### Editar um Usuário

1. Na tabela, localize o usuário
2. Clique no botão azul de **edição** (ícone de lápis)
3. Modifique os dados necessários
4. Clique em **"Salvar"**

### Desativar/Ativar um Usuário

1. Na tabela, localize o usuário
2. Clique no botão de **ativar/desativar**
3. Confirme a ação

### Deletar um Usuário

1. Na tabela, localize o usuário
2. Clique no botão vermelho de **deletar** (ícone de lixeira)
3. Confirme a ação (esta ação é **irreversível**)

## Endpoints da API Utilizados

```
GET    /api/users/              - Lista usuários (com filtros opcionais)
GET    /api/users/:id           - Obtém detalhes de um usuário
POST   /api/users/              - Cria novo usuário
PUT    /api/users/:id           - Atualiza usuário existente
DELETE /api/users/:id           - Deleta usuário permanentemente
```

## Segurança

- Todas as requisições exigem token JWT válido
- Endpoint protegido no backend para apenas superusuários
- Validação de formulários no frontend
- Confirmações antes de ações destrutivas
- Senhas com requisitos de força

## Visual e UX

- Interface consistente com o tema MAIS GESTOR
- Ícones intuitivos (Ant Design Icons)
- Feedback visual para todas as ações
- Mensagens de sucesso/erro claras
- Design responsivo
- Cores diferenciadas:
  - Superusuários: Ouro (#f59e0b)
  - Usuários comuns: Azul (#0ea5e9)
  - Status ativo: Verde (#22c55e)
  - Status inativo: Vermelho (#ef4444)

## Tecnologias

- React 19
- TypeScript
- Ant Design 5
- React Router DOM 7
- Axios
- dayjs (formatação de datas)
- Zustand (gerenciamento de estado)

## Próximos Passos Sugeridos

- [ ] Adicionar busca em tempo real (debounce)
- [ ] Exportar lista de usuários (CSV/Excel)
- [ ] Logs de auditoria de ações administrativas
- [ ] Envio de email de boas-vindas ao criar usuário
- [ ] Reset de senha por email
- [ ] Filtros avançados (por data de criação, última atividade, etc)
- [ ] Bulk actions (ativar/desativar múltiplos usuários)
