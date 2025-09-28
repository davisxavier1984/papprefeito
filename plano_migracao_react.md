# Plano de Migração: Sistema papprefeito Streamlit → React

## Análise de Viabilidade

### Sistema Atual (Streamlit)
- **Frontend**: Streamlit (Python)
- **Backend**: Integrado na mesma aplicação
- **Funcionalidades**: Consulta API, visualização de dados, edição inline, cache local
- **Persistência**: Arquivos JSON locais
- **Arquivos principais**:
  - `app.py` - Interface principal Streamlit
  - `api_client.py` - Cliente para API do governo
  - `formatting.py` - Formatação de dados
  - Cache em `data_cache_papprefeito.json`
  - Dados editados em `municipios_editados.json`

### Vantagens da Migração para React

1. **Performance**: React oferece melhor responsividade e experiência do usuário
2. **Escalabilidade**: Arquitetura mais modular e reutilizável
3. **Flexibilidade**: Maior controle sobre UI/UX e customizações
4. **Ecossistema**: Acesso a bibliotecas React robustas (Ant Design, Material-UI, etc.)
5. **Deploy**: Mais opções de hospedagem e otimização
6. **Manutenibilidade**: Código mais organizado e testável

### Desafios da Migração

1. **Backend separado**: Necessário criar API REST/GraphQL
2. **Complexidade**: Arquitetura distribuída vs monolítica atual
3. **Estado**: Gerenciamento de estado mais complexo
4. **Desenvolvimento**: Duas tecnologias em vez de uma
5. **Curva de aprendizado**: Se a equipe não tem experiência com React

## Arquitetura Proposta

### Frontend (React)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Ant Design ou Material-UI
- **Estado**: Redux Toolkit ou Zustand
- **HTTP Client**: Axios ou React Query
- **Roteamento**: React Router

### Backend (API)
- **Framework**: FastAPI (Python) - mantém compatibilidade com código atual
- **Banco de Dados**: PostgreSQL para dados persistentes
- **Cache**: Redis para performance
- **Autenticação**: JWT (se necessário)
- **Documentação**: Swagger/OpenAPI automático

### Infraestrutura
- **Frontend**: Vercel, Netlify ou AWS S3
- **Backend**: Railway, Heroku ou AWS
- **Banco**: PostgreSQL hospedado
- **Cache**: Redis hospedado

## Plano de Migração

### Fase 1: Setup Backend (1-2 semanas)
**Objetivo**: Criar API REST robusta

#### Tarefas:
- [ ] Setup projeto FastAPI com estrutura modular
- [ ] Migrar lógica de `api_client.py` para endpoints REST
- [ ] Implementar modelo de dados para municípios
- [ ] Criar endpoints principais:
  - `GET /api/ufs` - Lista UFs
  - `GET /api/municipios/{uf}` - Lista municípios por UF
  - `GET /api/dados/{codigo_ibge}/{competencia}` - Consulta dados governo
  - `POST/PUT/DELETE /api/municipios-editados` - CRUD dados editados
- [ ] Sistema de cache com Redis
- [ ] Configurar banco PostgreSQL
- [ ] Testes unitários da API
- [ ] Documentação Swagger

### Fase 2: Frontend React (2-3 semanas)
**Objetivo**: Implementar interface React completa

#### Tarefas:
- [ ] Setup React + TypeScript + Vite
- [ ] Configurar estrutura de pastas e padrões
- [ ] Implementar componentes base:
  - Layout principal
  - Sidebar de seleção
  - Componente de seleção UF/Município
  - Tabela editável de dados financeiros
  - Cards de métricas
  - Sistema de loading/erro
- [ ] Implementar gerenciamento de estado
- [ ] Integração com API backend
- [ ] Implementar funcionalidades de edição inline
- [ ] Sistema de cache offline (opcional)
- [ ] Responsividade mobile

### Fase 3: Funcionalidades Avançadas (1 semana)
**Objetivo**: Polimento e otimizações

#### Tarefas:
- [ ] Implementar validações robustas (frontend + backend)
- [ ] Sistema de notificações (sucesso/erro)
- [ ] Otimizações de performance
- [ ] Implementar filtros avançados
- [ ] Sistema de exportação (PDF/Excel)
- [ ] Melhorias na UX/UI
- [ ] Testes E2E com Cypress

### Fase 4: Deploy e Testes (1 semana)
**Objetivo**: Colocar em produção

#### Tarefas:
- [ ] Configuração de CI/CD (GitHub Actions)
- [ ] Deploy backend em produção
- [ ] Deploy frontend em produção
- [ ] Configuração de monitoramento
- [ ] Migração de dados existentes
- [ ] Testes de carga
- [ ] Documentação de uso
- [ ] Treinamento da equipe

## Estimativas

- **Tempo total**: 5-7 semanas
- **Recursos**: 1-2 desenvolvedores
- **Investimento**: Médio (hospedagem + banco)

## Componentes React Principais

### 1. `App.tsx` - Componente raiz
```typescript
// Roteamento, providers globais, layout
```

### 2. `pages/Dashboard.tsx` - Página principal
```typescript
// Substitui app.py principal
```

### 3. `components/MunicipioSelector.tsx` - Seleção UF/Município
```typescript
// Dropdowns de seleção
```

### 4. `components/DataTable.tsx` - Tabela editável
```typescript
// Tabela com edição inline dos valores
```

### 5. `components/MetricsCards.tsx` - Cards de métricas
```typescript
// Exibição de totais e estatísticas
```

### 6. `services/api.ts` - Cliente HTTP
```typescript
// Substitui api_client.py
```

### 7. `stores/municipioStore.ts` - Gerenciamento de estado
```typescript
// Estado global da aplicação
```

## API Endpoints Necessários

### Dados Básicos
- `GET /api/ufs` - Lista UFs
- `GET /api/municipios/:uf` - Municípios por UF
- `GET /api/competencias` - Competências disponíveis

### Dados Principais
- `GET /api/financiamento/:codigo/:competencia` - Dados do governo
- `GET /api/municipios-editados` - Dados editados salvos
- `POST /api/municipios-editados` - Salvar edições
- `PUT /api/municipios-editados/:id` - Atualizar edições
- `DELETE /api/municipios-editados/:id` - Remover edições

### Utilitários
- `GET /api/health` - Status da API
- `GET /api/cache/clear` - Limpar cache (admin)

## Recomendação Final

**A migração é VIÁVEL e RECOMENDADA** pelos seguintes motivos:

1. ✅ **Código bem estruturado**: O sistema atual já separa responsabilidades
2. ✅ **Funcionalidades claras**: Escopo bem definido facilita migração
3. ✅ **Melhor UX**: React permitirá interface mais fluida
4. ✅ **Escalabilidade**: Arquitetura preparada para crescimento
5. ✅ **Manutenibilidade**: Código mais organizaado e testável

### Próximos Passos Sugeridos:
1. Aprovação do plano pela equipe
2. Definição de cronograma detalhado
3. Setup dos ambientes de desenvolvimento
4. Início da Fase 1 (Backend)

---
*Documento gerado em: 28/09/2025*
*Sistema analisado: papprefeito v1.0*