# 🚀 Guia de Integração Appwrite - Sistema MaisPAP

## 📋 Visão Geral

Este documento descreve como configurar e usar a integração do Appwrite no sistema MaisPAP para gerenciar edições de municípios em um banco de dados real, substituindo os arquivos JSON locais.

## 🎯 Funcionalidades

- ✅ **Database real** no Appwrite (substitui JSON local)
- ✅ **API REST** para CRUD de edições
- ✅ **Autenticação pronta** (quando habilitada)
- ✅ **Permissões granulares**
- ✅ **Migração automática** de dados existentes
- ✅ **Setup automatizado** via scripts

## 📦 Pré-requisitos

1. **Conta no Appwrite Cloud** (gratuita)
   - Criar conta em: https://cloud.appwrite.io
   - Ou self-hosted via Docker

2. **API Key do Appwrite**
   - Acesse: https://cloud.appwrite.io/console/project-68dc49bf000cebd54b85/settings
   - Vá em "API Keys" → "Create API Key"
   - Permissões necessárias: `databases.read`, `databases.write`

## 🔧 Configuração

### 1. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o `.env` e adicione sua API Key do Appwrite:

```env
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=68dc49bf000cebd54b85
APPWRITE_API_KEY=sua_api_key_secreta_aqui  # ← ADICIONE AQUI
APPWRITE_DATABASE_ID=papprefeito_db
APPWRITE_COLLECTION_EDICOES_ID=edicoes_municipios
```

### 3. Executar setup do Appwrite

Este script cria automaticamente:
- Database
- Collection
- Attributes (campos)
- Index único

```bash
python backend/scripts/setup_appwrite.py
```

**Saída esperada:**
```
🚀 Iniciando setup do Appwrite...
📡 Endpoint: https://cloud.appwrite.io/v1
📦 Project ID: 68dc49bf000cebd54b85

1️⃣  Criando database...
✅ Database 'papprefeito_db' criado com sucesso!

2️⃣  Criando collection...
✅ Collection 'edicoes_municipios' criada com sucesso!

3️⃣  Criando attributes...
  ✅ Attribute 'codigo_municipio' criado
  ✅ Attribute 'competencia' criado
  ✅ Attribute 'perda_recurso_mensal' criado
  ...

✅ Setup do Appwrite concluído com sucesso!
```

### 4. Migrar dados existentes (opcional)

Se você já tem dados em `municipios_editados.json`, migre para o Appwrite:

```bash
python backend/scripts/migrate_json_to_appwrite.py
```

Este script:
- Lê dados do JSON local
- Migra para o Appwrite
- Cria backup automático do JSON original
- Mostra relatório de migração

## 📡 Endpoints da API

Após o setup, os seguintes endpoints estarão disponíveis:

### **GET** `/api/edicoes`
Lista todas as edições

**Query params:**
- `codigo_municipio` (opcional): Filtrar por município
- `limit` (padrão: 100): Número de resultados
- `offset` (padrão: 0): Paginação

**Exemplo:**
```bash
curl http://localhost:8000/api/edicoes?codigo_municipio=3106200
```

### **GET** `/api/edicoes/{codigo_municipio}/{competencia}`
Busca edição específica

**Exemplo:**
```bash
curl http://localhost:8000/api/edicoes/3106200/202409
```

### **POST** `/api/edicoes`
Salva ou atualiza edição

**Body:**
```json
{
  "codigo_municipio": "3106200",
  "competencia": "202409",
  "perda_recurso_mensal": [0.0, 1500.50, 2000.00],
  "usuario_id": "user_123"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/api/edicoes \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_municipio": "3106200",
    "competencia": "202409",
    "perda_recurso_mensal": [0.0, 1500.50, 2000.00]
  }'
```

### **DELETE** `/api/edicoes/{codigo_municipio}/{competencia}`
Deleta edição

**Exemplo:**
```bash
curl -X DELETE http://localhost:8000/api/edicoes/3106200/202409
```

## 🧪 Testando a API

### Via Swagger UI (recomendado)

1. Inicie o servidor:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Acesse: http://localhost:8000/docs

3. Teste os endpoints na seção "Edições Appwrite"

### Via curl

```bash
# Listar todas edições
curl http://localhost:8000/api/edicoes

# Buscar edição específica
curl http://localhost:8000/api/edicoes/3106200/202409

# Criar nova edição
curl -X POST http://localhost:8000/api/edicoes \
  -H "Content-Type: application/json" \
  -d '{"codigo_municipio":"3106200","competencia":"202409","perda_recurso_mensal":[100,200,300]}'
```

## 🗂️ Estrutura de Arquivos Criados

```
backend/
├── app/
│   ├── core/
│   │   ├── appwrite_client.py       # Cliente Appwrite (singleton)
│   │   └── config.py                # Configurações atualizadas
│   ├── services/
│   │   └── edicoes_service.py       # Serviço de CRUD
│   └── api/
│       └── endpoints/
│           └── edicoes.py           # Endpoints REST
├── scripts/
│   ├── setup_appwrite.py            # Setup automatizado
│   └── migrate_json_to_appwrite.py  # Migração de dados
├── requirements.txt                 # Dependências atualizadas
└── .env.example                     # Template de configuração
```

## 🔒 Segurança

⚠️ **IMPORTANTE:**

- **NUNCA** commite a API Key no Git
- A API Key está em `.env` (que está no `.gitignore`)
- Use variáveis de ambiente em produção
- Em produção, use secrets do GitHub/servidor

## 📊 Modelo de Dados

### Collection: `edicoes_municipios`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `codigo_municipio` | string(128) | ✅ | Código IBGE do município |
| `competencia` | string(6) | ✅ | Competência (AAAAMM) |
| `perda_recurso_mensal` | string(10000) | ✅ | JSON array com valores |
| `usuario_id` | string(128) | ❌ | ID do usuário |
| `created_at` | datetime | ✅ | Data de criação |
| `updated_at` | datetime | ✅ | Última atualização |

**Index único:** `municipio_competencia` (codigo_municipio + competencia)

## 🆘 Troubleshooting

### Erro: "APPWRITE_API_KEY não configurada"

**Solução:** Adicione a API Key no arquivo `.env`

### Erro: "Database already exists"

**Solução:** Normal! O script detecta e pula recursos já existentes.

### Erro: "Connection refused"

**Solução:** Verifique se está conectado à internet e se o endpoint está correto.

### Migração não encontra dados

**Solução:** Verifique se o arquivo `municipios_editados.json` existe em `backend/`

## 📚 Recursos Adicionais

- [Documentação Appwrite](https://appwrite.io/docs)
- [Python SDK Reference](https://appwrite.io/docs/sdks#python)
- [Console Appwrite](https://cloud.appwrite.io/console/project-68dc49bf000cebd54b85)

## 🤝 Suporte

Em caso de dúvidas ou problemas, consulte:
- Logs do servidor FastAPI
- Console do Appwrite
- Documentação oficial

---

**Desenvolvido para o Sistema MaisPAP** 🏛️
