# Preenchimento que aprende com o consultor — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ACS calculado como o consultor calcula, respostas do Ministério guardadas no SQLite, municípios parecidos no modal (Demais/Promoção) e painel admin de acerto do automático.

**Architecture:** Backend FastAPI: regra do ACS em `regras_perda.py`; tabela `respostas_ministerio` gravada dentro de `SaudeAPIClient.consultar_financiamento`; dois módulos puros (`parecidos.py`, `acerto.py`) testados com pytest; dois endpoints finos em `preenchimento.py`. Frontend React: bloco de parecidos no modal de preenchimento e página admin nova.

**Tech Stack:** Python 3.10, FastAPI, SQLAlchemy 2 async + aiosqlite, Pydantic 2, pytest; React 19, TS, Ant Design 5, TanStack Query 5, `node --test`.

**Spec:** `docs/superpowers/specs/2026-09-24-aprendizado-preenchimento-design.md`

## Modo de execução

Orquestração pela sessão principal, **um agente por vez** (implementador → revisor → próxima tarefa). **Subagente não lança subagente.** Branch: `fix/revisao-frontend` (continua a partir de `016dacd`).

## Global Constraints

- **Testes do backend** rodam SOMENTE com o ambiente isolado: `cd backend && $PY -m pytest -q tests/<arquivo>` onde `PY=/tmp/claude-1000/-home-davi-python-MG-papprefeito-dev/dc7dd45f-fcf4-41cf-b694-10517c426158/scratchpad/venv-test/bin/python`. **Nunca** instalar nada em `backend/.venv` nem em `backend/venv` (o `.venv` é o da produção).
- **Nunca** conectar ao banco de produção (`backend/papprefeito.db`) nem escrever em `backend/municipios_editados.json` durante o desenvolvimento. Testes que usam banco criam SQLite em `tmp_path`.
- **Nunca** rodar `npm run build` em `frontend/`; build de verificação só com `npx vite build --outDir /tmp/claude-1000/maispap-build`.
- Nenhuma dependência nova (frontend nem backend). Testes async sem pytest-asyncio: usar `asyncio.run(...)` dentro do teste.
- Frontend: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint .` → testes passando, tsc limpo, eslint ≤ 16 erros e nenhum novo em arquivo tocado.
- Backend: toda a suíte `cd backend && $PY -m pytest -q tests/test_regras_perda.py tests/test_respostas_ministerio.py tests/test_parecidos.py tests/test_acerto.py` passando ao fim de cada tarefa (os arquivos que já existirem).
- Textos e comentários em pt-BR com acentuação; seguir o estilo do arquivo vizinho.
- Commits `feat|fix(escopo): ...` em pt-BR terminando com:
  ```
  Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_0136kHzr4LrYg6XUKHvYpm6X
  ```

## Review Focus

1. **ACS com credenciados menores que pagos** → componente principal 0, nunca negativo; teto não soma os mesmos ACS duas vezes. Teste: Task 1.
2. **Falha ao gravar a resposta do Ministério** (banco travado, tabela ausente) → a consulta devolve os dados normalmente. Teste: Task 2, `test_gravar_resposta_nao_propaga_erro`.
3. **Histórico com itens de origem `regra`/`estimativa`** → não entram nos parecidos nem no acerto (evita o sistema aprender com ele mesmo). Testes: Tasks 3 e 4.
4. **Resposta do Ministério sem `pagamentos` ou sem `qtPopulacao`** → registro ignorado nos parecidos, contado em `sem_resposta` no acerto. Testes: Tasks 3 e 4.
5. **Plano sem nenhum informado > 0** → `erro_mediano`/`razao_soma` = `None`, sem divisão por zero, e sem alerta falso. Teste: Task 4.

---

### Task 1: Regra do ACS (credenciados − pagos; teto opcional)

**Files:**
- Modify: `backend/app/services/regras_perda.py:92-98` (`regra_acs`) e `:201` (`regra_id`)
- Modify: `backend/tests/test_regras_perda.py:54-57`
- Modify: `docs/analises/regras-preenchimento-completo.md` (linha **ACS** da tabela "Regras por plano" e tabela de validação)

**Interfaces:**
- Produces: componentes `acs_credenciados` (incluído) e `acs_teto` (não incluído); `regra_id` do ACS = `acs_v2`.

- [ ] **Step 1: Trocar o teste antigo pelos novos (falham)**

Em `backend/tests/test_regras_perda.py`, substituir `test_acs_usa_teto_menos_pagos_e_nunca_negativo` por:

```python
def test_acs_usa_credenciados_menos_pagos_e_nunca_negativo():
    acs = _planos()['acs']  # 44 credenciados, 44 pagos, teto 29
    assert acs.total_sugerido == 0
    assert acs.regra_id == 'acs_v2'
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=50)
    assert _planos(p)['acs'].total_sugerido == 6 * 3242.00
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=40)  # menos credenciados que pagos
    assert _planos(p)['acs'].total_sugerido == 0


def test_acs_teto_fica_desmarcado_e_nao_conta_duas_vezes():
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=50, qtTetoAcs=60)
    comps = {c.id: c for c in _planos(p)['acs'].componentes}
    assert comps['acs_credenciados'].incluido and comps['acs_credenciados'].quantidade == 6
    assert not comps['acs_teto'].incluido and comps['acs_teto'].quantidade == 10  # 60 − 50
    assert _planos(p)['acs'].total_sugerido == 6 * 3242.00


def test_acs_caso_real_do_historico():
    # 292070 (Maraú) 202512: 46 credenciados, 39 pagos, teto 64; o consultor informou 22.694,00
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=46, qtAcsDiretoPgto=39, qtTetoAcs=64)
    assert _planos(p)['acs'].total_sugerido == 22694.00
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && $PY -m pytest -q tests/test_regras_perda.py`
Expected: FAIL (`regra_id` é `acs_v1`; não existe `acs_credenciados`).

- [ ] **Step 3: Implementar**

Em `backend/app/services/regras_perda.py`, substituir `regra_acs` por:

```python
def regra_acs(p: Dict[str, Any], valores: Valores) -> List[ComponenteSugestao]:
    """ACS credenciados ainda não pagos (como o consultor preenche); o teto é opcional."""
    teto, pagos = int(_n(p, 'qtTetoAcs')), int(_n(p, 'qtAcsDiretoPgto'))
    cred = int(_n(p, 'qtAcsDiretoCredenciado'))
    valor = _v(valores, 'acs_valor')
    return [
        _componente('acs_credenciados', 'ACS credenciados ainda não pagos', max(cred - pagos, 0), valor,
                    editavel=True, detalhe=f"Credenciados {cred}, pagos {pagos}, teto {teto}"),
        # Acima do que já está credenciado ou pago, para não contar os mesmos ACS duas vezes
        _componente('acs_teto', 'ACS até o teto (acima dos credenciados)', max(teto - max(cred, pagos), 0), valor,
                    incluido=False, editavel=True),
    ]
```

E na montagem do `regra_id` (fim de `sugerir`), trocar a linha por:

```python
        regra_id = ({'emulti': 'emulti_estimativa_v1', 'acs': 'acs_v2'}.get(tipo, f"{tipo}_v1")) if componentes else None
```

- [ ] **Step 4: Rodar os testes**

Run: `cd backend && $PY -m pytest -q tests/test_regras_perda.py`
Expected: PASS (todos).

- [ ] **Step 5: Documento de regras**

Em `docs/analises/regras-preenchimento-completo.md`: na tabela "Regras por plano", linha **ACS** passa a `| **ACS** | **(ACS diretos credenciados − pagos) × valor por ACS** (R$ 3.242). O teto (teto − credenciados) aparece como componente opcional, desmarcado | Trocado em 24/09/2026: bate ao centavo em 49 de 87 registros do histórico (a regra do teto batia em 3 de 51) |`. Na tabela de validação, a linha do ACS passa a `| ACS (credenciados − pagos) | 56% (49/87) | erro mediano 4% nos preenchidos |`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/regras_perda.py backend/tests/test_regras_perda.py docs/analises/regras-preenchimento-completo.md
git commit -m "feat(regras): ACS por credenciados menos pagos, teto como opcional"
```

---

### Task 2: Tabela `respostas_ministerio` e gravação a cada consulta

**Files:**
- Modify: `backend/app/models/db_models.py` (novo modelo no fim)
- Modify: `backend/app/core/database.py:25` (import do modelo no `init_db`)
- Create: `backend/app/services/respostas_ministerio.py`
- Modify: `backend/app/services/api_client.py` (depois do bloco "Persistir cache local", antes de `return dados`)
- Modify: `backend/app/core/dependencies.py` (dependency `get_respostas_service`)
- Create: `backend/scripts/carregar_respostas_ministerio.py`
- Test: `backend/tests/test_respostas_ministerio.py`

**Interfaces:**
- Produces: `RespostaMinisterioDB`; `RespostasMinisterioService(session)` com `async salvar(codigo_ibge: str, competencia: str, dados: dict) -> None`, `async obter(codigo_ibge, competencia) -> Optional[dict]`, `async todas() -> Dict[Tuple[str, str], dict]`; `async gravar_resposta(codigo_ibge, competencia, dados, session_factory=async_session) -> None` (nunca lança); `get_respostas_service(session) -> RespostasMinisterioService`.

- [ ] **Step 1: Testes (falham)**

`backend/tests/test_respostas_ministerio.py`:

```python
"""Respostas do Ministério guardadas no SQLite (banco temporário, nunca o de produção)."""
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.services.respostas_ministerio import RespostasMinisterioService, gravar_resposta


def _fabrica(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'teste.db'}")

    async def criar():
        from app.models.db_models import RespostaMinisterioDB  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(criar())
    return async_sessionmaker(engine, expire_on_commit=False)


def test_salvar_obter_e_substituir(tmp_path):
    fabrica = _fabrica(tmp_path)

    async def fluxo():
        async with fabrica() as s:
            svc = RespostasMinisterioService(s)
            await svc.salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 1}]})
            await svc.salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 2}]})
            await svc.salvar('292940', '202606', {'pagamentos': []})
            assert (await svc.obter('290240', '202512'))['pagamentos'][0]['qtPopulacao'] == 2
            assert await svc.obter('999999', '202512') is None
            assert set(await svc.todas()) == {('290240', '202512'), ('292940', '202606')}
    asyncio.run(fluxo())


def test_gravar_resposta_usa_a_fabrica(tmp_path):
    fabrica = _fabrica(tmp_path)
    asyncio.run(gravar_resposta('290240', '202512', {'x': 1}, session_factory=fabrica))

    async def ler():
        async with fabrica() as s:
            return await RespostasMinisterioService(s).obter('290240', '202512')
    assert asyncio.run(ler()) == {'x': 1}


def test_gravar_resposta_nao_propaga_erro(tmp_path):
    # Banco sem a tabela: a gravação falha, mas a consulta não pode quebrar
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'vazio.db'}")
    fabrica = async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(gravar_resposta('290240', '202512', {'x': 1}, session_factory=fabrica))
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && $PY -m pytest -q tests/test_respostas_ministerio.py`
Expected: FAIL (`ModuleNotFoundError: app.services.respostas_ministerio`).

- [ ] **Step 3: Modelo**

No fim de `backend/app/models/db_models.py`:

```python
class RespostaMinisterioDB(Base):
    """Última resposta da API de financiamento do Ministério por município e competência.

    Base do painel de acerto e dos municípios parecidos (aprendizado com o consultor).
    """
    __tablename__ = "respostas_ministerio"

    codigo_ibge: Mapped[str] = mapped_column(String(10), primary_key=True)
    competencia: Mapped[str] = mapped_column(String(6), primary_key=True)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)  # JSON bruto
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

Em `backend/app/core/database.py`, no `init_db`, acrescentar `RespostaMinisterioDB` ao import dos modelos.

- [ ] **Step 4: Serviço**

`backend/app/services/respostas_ministerio.py`:

```python
"""
Respostas da API de financiamento do Ministério guardadas no SQLite.

Gravadas a cada consulta (SaudeAPIClient.consultar_financiamento). Servem para o sistema
se comparar com o que o consultor informou, sem consultar o Ministério de novo.
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.db_models import RespostaMinisterioDB
from app.utils.logger import logger


class RespostasMinisterioService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def salvar(self, codigo_ibge: str, competencia: str, dados: Dict[str, Any]) -> None:
        row = await self.session.get(RespostaMinisterioDB, (codigo_ibge, competencia))
        texto = json.dumps(dados, ensure_ascii=False)
        if row:
            row.resposta = texto
            row.atualizado_em = datetime.utcnow()
        else:
            self.session.add(RespostaMinisterioDB(codigo_ibge=codigo_ibge, competencia=competencia, resposta=texto))
        await self.session.commit()

    async def obter(self, codigo_ibge: str, competencia: str) -> Optional[Dict[str, Any]]:
        row = await self.session.get(RespostaMinisterioDB, (codigo_ibge, competencia))
        return json.loads(row.resposta) if row else None

    async def todas(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        rows = (await self.session.execute(select(RespostaMinisterioDB))).scalars().all()
        return {(r.codigo_ibge, r.competencia): json.loads(r.resposta) for r in rows}


async def gravar_resposta(codigo_ibge: str, competencia: str, dados: Dict[str, Any],
                          session_factory=async_session) -> None:
    """Grava sem nunca quebrar a consulta: uma falha aqui só gera aviso no log."""
    try:
        async with session_factory() as session:
            await RespostasMinisterioService(session).salvar(codigo_ibge, competencia, dados)
    except Exception as exc:
        logger.warning(f"Não foi possível guardar a resposta do Ministério de {codigo_ibge}/{competencia}: {exc}")
```

- [ ] **Step 5: Rodar os testes**

Run: `cd backend && $PY -m pytest -q tests/test_respostas_ministerio.py`
Expected: PASS (3).

- [ ] **Step 6: Gravar a cada consulta**

Em `backend/app/services/api_client.py`, logo antes de `# Retornar JSON bruto da API externa (completo)`:

```python
                # Guarda a resposta para o painel de acerto e os municípios parecidos
                from app.services.respostas_ministerio import gravar_resposta
                await gravar_resposta(codigo_ibge[:6], competencia, dados)
```

(Import local para não criar import circular no carregamento do módulo; se não houver ciclo, mova para o topo e registre no relatório.)

Em `backend/app/core/dependencies.py`, junto de `get_valores_service`:

```python
def get_respostas_service(session: AsyncSession = Depends(get_session)) -> RespostasMinisterioService:
    return RespostasMinisterioService(session)
```

(com o import `from app.services.respostas_ministerio import RespostasMinisterioService`).

- [ ] **Step 7: Script de carga inicial**

`backend/scripts/carregar_respostas_ministerio.py`:

```python
#!/usr/bin/env python3
"""
Carga inicial de respostas_ministerio para as perdas já salvas.

Uso (no servidor, uma vez): cd backend && .venv/bin/python scripts/carregar_respostas_ministerio.py [desde=202512]
Consulta o Ministério (só leitura) para cada município/competência salvo a partir de `desde`
que ainda não tenha resposta guardada. A gravação acontece dentro da própria consulta.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session, init_db  # noqa: E402
from app.services.api_client import saude_api_client  # noqa: E402
from app.services.municipios_editados import municipio_editado_service  # noqa: E402
from app.services.respostas_ministerio import RespostasMinisterioService  # noqa: E402


async def main(desde: str) -> None:
    await init_db()
    async with async_session() as session:
        existentes = set(await RespostasMinisterioService(session).todas())
    pendentes = sorted({(e.codigo_ibge, e.competencia) for e in municipio_editado_service.get_all_editados()
                        if e.competencia >= desde} - existentes)
    print(f"{len(pendentes)} consultas pendentes")
    falhas = 0
    for ibge, comp in pendentes:
        dados = await saude_api_client.consultar_financiamento(ibge, comp)
        falhas += dados is None
        print(f"{ibge}/{comp}: {'ok' if dados else 'sem dados'}")
        await asyncio.sleep(0.4)
    print(f"Concluído. Sem dados: {falhas}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "202512"))
```

Não executar o script (ele usa o banco de produção). Verificar só que importa: `cd backend && $PY -c "import ast,sys; ast.parse(open('scripts/carregar_respostas_ministerio.py').read())"`.

- [ ] **Step 8: Suíte e commit**

Run: `cd backend && $PY -m pytest -q tests/test_regras_perda.py tests/test_respostas_ministerio.py`
Expected: PASS.

```bash
git add backend/app/models/db_models.py backend/app/core/database.py backend/app/services/respostas_ministerio.py backend/app/services/api_client.py backend/app/core/dependencies.py backend/scripts/carregar_respostas_ministerio.py backend/tests/test_respostas_ministerio.py
git commit -m "feat(ministerio): guardar a resposta de cada consulta no SQLite"
```

---

### Task 3: Módulo puro de municípios parecidos

**Files:**
- Create: `backend/app/services/parecidos.py`
- Test: `backend/tests/test_parecidos.py`

**Interfaces:**
- Consumes: `filtrar_resumos_municipais` de `app.services.regras_perda`.
- Produces: `PREFIXOS_PARECIDOS: Tuple[str, str]` = (`'Demais programas'`, `'Incentivo financeiro da APS - Promoção'`); `@dataclass Perfil(uf, municipio, populacao, equipes, recebe: Dict[str, float])`; `perfil(resposta: dict) -> Optional[Perfil]`; `distancia(a: Perfil, b: Perfil, prefixo: str) -> float`; `@dataclass Exemplo(codigo_ibge, competencia, municipio, uf, valor, distancia)`; `parecidos(alvo_ibge: str, alvo: Perfil, historico: Iterable[Tuple[str, str, Perfil, List[dict]]], prefixo: str, k: int = 3) -> List[Exemplo]`; `mediana(exemplos: List[Exemplo]) -> Optional[float]`.

- [ ] **Step 1: Testes (falham)**

`backend/tests/test_parecidos.py`:

```python
"""Municípios parecidos: mesma medida da simulação de 24/09/2026."""
from app.services.parecidos import Perfil, distancia, mediana, parecidos, perfil

DEMAIS = 'Demais programas'


def _resposta(pop, equipes, uf='BA', demais=0.0, nome='X'):
    return {
        'pagamentos': [{'qtPopulacao': pop, 'qtEsfTotalPgto': equipes, 'qtEapTotalPgto': 0,
                        'sgUf': uf, 'noMunicipio': nome}],
        'resumosPlanosOrcamentarios': [
            {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': demais},
            {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'dsEsferaAdministrativa': 'ESTADUAL', 'vlIntegral': 999999},
        ],
    }


def _itens(valor, origem='manual'):
    return [{'plano': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'valor': valor, 'origem': origem}]


def test_perfil_le_populacao_equipes_e_so_resumos_municipais():
    p = perfil(_resposta(10000, 4, demais=500, nome='Boninal'))
    assert (p.populacao, p.equipes, p.uf, p.municipio) == (10000, 4, 'BA', 'Boninal')
    assert sum(p.recebe.values()) == 500


def test_perfil_incompleto_e_none():
    assert perfil({'pagamentos': [], 'resumosPlanosOrcamentarios': []}) is None
    assert perfil({'pagamentos': [{'qtPopulacao': 0}]}) is None


def test_distancia_penaliza_outra_uf_e_cresce_com_a_populacao():
    a = perfil(_resposta(10000, 4))
    assert distancia(a, perfil(_resposta(10000, 4)), DEMAIS) == 0
    assert distancia(a, perfil(_resposta(10000, 4, uf='SP')), DEMAIS) == 0.5
    assert distancia(a, perfil(_resposta(20000, 4)), DEMAIS) < distancia(a, perfil(_resposta(200000, 4)), DEMAIS)


def test_parecidos_so_manual_positivo_outro_municipio_e_ordenado():
    alvo = perfil(_resposta(10000, 4))
    hist = [
        ('111111', '202606', perfil(_resposta(10000, 4)), _itens(19900)),
        ('222222', '202606', perfil(_resposta(50000, 4)), _itens(27300)),
        ('333333', '202606', perfil(_resposta(10000, 4)), _itens(5000, origem='regra')),  # não é do consultor
        ('444444', '202606', perfil(_resposta(10000, 4)), _itens(0)),                    # consultor pôs zero
        ('555555', '202606', perfil(_resposta(10000, 4)), _itens(60000)),               # mesmo município do alvo
        ('666666', '202606', perfil(_resposta(900000, 90)), _itens(107200)),
    ]
    ex = parecidos('555555', alvo, hist, DEMAIS, k=3)
    assert [e.codigo_ibge for e in ex] == ['111111', '222222', '666666']
    assert mediana(ex) == 27300


def test_mediana_vazia():
    assert mediana([]) is None
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && $PY -m pytest -q tests/test_parecidos.py`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implementar**

`backend/app/services/parecidos.py`:

```python
"""
Municípios parecidos (Demais programas e Promoção à saúde).

O consultor preenche esses planos por julgamento: não há regra nos dados do Ministério.
Aqui procuramos, no histórico, os municípios mais parecidos em que ele preencheu à mão,
com a mesma medida validada na simulação de 24/09/2026.
"""
import math
import statistics
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.services.regras_perda import filtrar_resumos_municipais

PREFIXOS_PARECIDOS: Tuple[str, str] = ('Demais programas', 'Incentivo financeiro da APS - Promoção')


@dataclass
class Perfil:
    uf: str
    municipio: str
    populacao: float
    equipes: float
    recebe: Dict[str, float]


@dataclass
class Exemplo:
    codigo_ibge: str
    competencia: str
    municipio: str
    uf: str
    valor: float
    distancia: float


def perfil(resposta: Dict[str, Any]) -> Optional[Perfil]:
    """Perfil do município na resposta do Ministério; None se faltar pagamento ou população."""
    pagamentos = resposta.get('pagamentos') or []
    p = pagamentos[0] if pagamentos else {}
    if not float(p.get('qtPopulacao') or 0):
        return None
    recebe: Dict[str, float] = {}
    for r in filtrar_resumos_municipais(resposta.get('resumosPlanosOrcamentarios') or []):
        nome = r.get('dsPlanoOrcamentario') or ''
        recebe[nome] = recebe.get(nome, 0.0) + float(r.get('vlIntegral') or 0)
    return Perfil(
        uf=p.get('sgUf') or '', municipio=p.get('noMunicipio') or '',
        populacao=float(p['qtPopulacao']),
        equipes=float(p.get('qtEsfTotalPgto') or 0) + float(p.get('qtEapTotalPgto') or 0),
        recebe=recebe,
    )


def _recebe(p: Perfil, prefixo: str) -> float:
    return sum(v for nome, v in p.recebe.items() if nome.startswith(prefixo))


def _vetor(p: Perfil, prefixo: str) -> List[float]:
    return [
        math.log10(p.populacao),
        math.log1p(p.equipes),
        math.log1p(_recebe(p, PREFIXOS_PARECIDOS[0])) / 3,
        math.log1p(_recebe(p, PREFIXOS_PARECIDOS[1])) / 3,
        math.log1p(_recebe(p, prefixo)) / 3,
    ]


def distancia(a: Perfil, b: Perfil, prefixo: str) -> float:
    base = math.sqrt(sum((x - y) ** 2 for x, y in zip(_vetor(a, prefixo), _vetor(b, prefixo))))
    return base + (0.5 if a.uf != b.uf else 0.0)


def parecidos(alvo_ibge: str, alvo: Perfil, historico: Iterable[Tuple[str, str, Perfil, List[Dict[str, Any]]]],
              prefixo: str, k: int = 3) -> List[Exemplo]:
    """Os k municípios mais parecidos em que o consultor preencheu o plano à mão com valor > 0."""
    candidatos = []
    for ibge, comp, perf, itens in historico:
        if ibge == alvo_ibge:
            continue
        item = next((i for i in itens if (i.get('plano') or '').startswith(prefixo)), None)
        if not item or item.get('origem', 'manual') != 'manual' or not item.get('valor'):
            continue
        candidatos.append(Exemplo(codigo_ibge=ibge, competencia=comp, municipio=perf.municipio, uf=perf.uf,
                                  valor=float(item['valor']), distancia=round(distancia(alvo, perf, prefixo), 3)))
    return sorted(candidatos, key=lambda e: e.distancia)[:k]


def mediana(exemplos: List[Exemplo]) -> Optional[float]:
    return round(statistics.median(e.valor for e in exemplos), 2) if exemplos else None
```

- [ ] **Step 4: Rodar os testes**

Run: `cd backend && $PY -m pytest -q tests/test_parecidos.py`
Expected: PASS (5).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/parecidos.py backend/tests/test_parecidos.py
git commit -m "feat(preenchimento): municípios parecidos pelo histórico do consultor"
```

---

### Task 4: Módulo puro de acerto do automático

**Files:**
- Create: `backend/app/services/acerto.py`
- Test: `backend/tests/test_acerto.py`

**Interfaces:**
- Consumes: `PlanoSugestao` (`tipo`, `total_sugerido`) de `app.models.schemas`; `PREFIXOS_PARECIDOS` (Task 3).
- Produces: `PLANOS_ACERTO: Dict[str, Tuple[str, str]]` (tipo → (rótulo, prefixo do plano)); `metricas(pares: List[Tuple[float, float]]) -> Dict[str, Any]` com chaves `registros, exatos, erro_mediano, dentro_25, zero_certo, razao_soma, alerta`; `comparar(entradas: Iterable[Tuple[List[PlanoSugestao], List[dict]]]) -> Dict[str, List[Tuple[float, float]]]`; `contar_preenchidos(itens_por_registro: Iterable[List[dict]]) -> Dict[str, Dict[str, int]]` (prefixo Demais/Promoção → `{registros, preenchidos}`).

- [ ] **Step 1: Testes (falham)**

`backend/tests/test_acerto.py`:

```python
"""Métricas do painel de acerto do automático."""
from app.models.schemas import PlanoSugestao
from app.services.acerto import comparar, contar_preenchidos, metricas


def test_metricas_basicas():
    m = metricas([(100, 100), (120, 100), (0, 0), (50, 0), (0, 200)])
    assert m['registros'] == 5
    assert m['exatos'] == 2                 # (100,100) e (0,0)
    assert m['zero_certo'] == 3             # (100,100), (120,100), (0,0)
    assert m['dentro_25'] == 2              # entre os 3 com informado > 0: 0%, 20%, 100%
    assert m['erro_mediano'] == 0.2
    assert m['razao_soma'] == round(270 / 400, 4)
    assert m['alerta'] is True              # razão fora de [0,8; 1,25]


def test_metricas_sem_informado_nao_divide_por_zero():
    m = metricas([(0, 0), (10, 0)])
    assert m['erro_mediano'] is None and m['razao_soma'] is None and m['alerta'] is False


def test_metricas_vazias():
    assert metricas([])['registros'] == 0


def _sug(tipo, total):
    return PlanoSugestao(indice=0, plano='p', tipo=tipo, aplicavel=True, total_sugerido=total)


def test_comparar_so_itens_manuais_e_por_tipo():
    entradas = [
        ([_sug('acs', 6484), _sug('esf', 24000)],
         [{'plano': 'Agentes Comunitários de Saúde', 'valor': 6484, 'origem': 'manual'},
          {'plano': 'Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP', 'valor': 24000,
           'origem': 'regra'}]),
    ]
    pares = comparar(entradas)
    assert pares['acs'] == [(6484, 6484)]
    assert pares['esf'] == []                # item de origem regra não conta


def test_contar_preenchidos_demais_e_promocao():
    itens = [
        [{'plano': 'Demais programas, serviços e equipes da Atenção Primária à Saúde', 'valor': 19900, 'origem': 'manual'}],
        [{'plano': 'Demais programas, serviços e equipes da Atenção Primária à Saúde', 'valor': 0, 'origem': 'manual'},
         {'plano': 'Incentivo financeiro da APS - Promoção à saúde', 'valor': 5000, 'origem': 'manual'}],
    ]
    c = contar_preenchidos(itens)
    assert c['Demais programas'] == {'registros': 2, 'preenchidos': 1}
    assert c['Incentivo financeiro da APS - Promoção'] == {'registros': 1, 'preenchidos': 1}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && $PY -m pytest -q tests/test_acerto.py`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implementar**

`backend/app/services/acerto.py`:

```python
"""
Acerto do preenchimento automático em relação ao consultor.

Compara, plano a plano, o total que a regra sugere com o valor que o consultor informou
à mão. Só itens de origem "manual" entram: o que veio da própria regra não mede nada.
"""
import statistics
from typing import Any, Dict, Iterable, List, Tuple

from app.models.schemas import PlanoSugestao
from app.services.parecidos import PREFIXOS_PARECIDOS

PLANOS_ACERTO: Dict[str, Tuple[str, str]] = {
    'esf': ('eSF/eAP', 'Equipes de Saúde da Família'),
    'sb': ('Saúde Bucal', 'Atenção à Saúde Bucal'),
    'acs': ('ACS', 'Agentes Comunitários'),
}
FAIXA_SOMA = (0.8, 1.25)
ERRO_MAXIMO = 0.5


def metricas(pares: List[Tuple[float, float]]) -> Dict[str, Any]:
    """pares = (sugerido, informado)."""
    positivos = [(s, i) for s, i in pares if i > 0]
    erros = [abs(s - i) / i for s, i in positivos]
    soma_inf = sum(i for _, i in pares)
    erro_mediano = round(statistics.median(erros), 4) if erros else None
    razao = round(sum(s for s, _ in pares) / soma_inf, 4) if soma_inf else None
    alerta = bool((razao is not None and not FAIXA_SOMA[0] <= razao <= FAIXA_SOMA[1])
                  or (erro_mediano is not None and erro_mediano > ERRO_MAXIMO))
    return {
        'registros': len(pares),
        'exatos': sum(abs(s - i) < 1 for s, i in pares),
        'erro_mediano': erro_mediano,
        'dentro_25': sum(e <= 0.25 for e in erros),
        'zero_certo': sum((s > 0) == (i > 0) for s, i in pares),
        'razao_soma': razao,
        'alerta': alerta,
    }


def comparar(entradas: Iterable[Tuple[List[PlanoSugestao], List[Dict[str, Any]]]]) -> Dict[str, List[Tuple[float, float]]]:
    pares: Dict[str, List[Tuple[float, float]]] = {tipo: [] for tipo in PLANOS_ACERTO}
    for sugestoes, itens in entradas:
        total = {s.tipo: s.total_sugerido for s in sugestoes}
        for tipo, (_, prefixo) in PLANOS_ACERTO.items():
            item = next((i for i in itens if (i.get('plano') or '').startswith(prefixo)), None)
            if item and item.get('origem', 'manual') == 'manual' and tipo in total:
                pares[tipo].append((float(total[tipo]), float(item.get('valor') or 0)))
    return pares


def contar_preenchidos(itens_por_registro: Iterable[List[Dict[str, Any]]]) -> Dict[str, Dict[str, int]]:
    contagem = {p: {'registros': 0, 'preenchidos': 0} for p in PREFIXOS_PARECIDOS}
    for itens in itens_por_registro:
        for prefixo in PREFIXOS_PARECIDOS:
            item = next((i for i in itens if (i.get('plano') or '').startswith(prefixo)), None)
            if item and item.get('origem', 'manual') == 'manual':
                contagem[prefixo]['registros'] += 1
                contagem[prefixo]['preenchidos'] += bool(item.get('valor'))
    return contagem
```

- [ ] **Step 4: Rodar os testes**

Run: `cd backend && $PY -m pytest -q tests/test_acerto.py`
Expected: PASS (5).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/acerto.py backend/tests/test_acerto.py
git commit -m "feat(preenchimento): métricas de acerto do automático contra o consultor"
```

---

### Task 5: Endpoints `parecidos` e `acerto`

**Files:**
- Modify: `backend/app/models/schemas.py` (schemas novos depois de `SugestaoResposta`)
- Modify: `backend/app/api/endpoints/preenchimento.py`
- Test: `backend/tests/test_acerto.py` e `backend/tests/test_parecidos.py` (um teste de montagem cada)

**Interfaces:**
- Consumes: Tasks 2–4; `municipio_editado_service.get_all_editados()` (itens como `ItemPerda` Pydantic → converter com `.model_dump()`); `ValoresReferenciaService.vigentes(competencia)`; `sugerir`.
- Produces: `GET /api/preenchimento/{codigo_ibge}/{competencia}/parecidos` → `ParecidosResposta`; `GET /api/preenchimento/acerto?desde=AAAAMM` (superusuário) → `AcertoResposta`; funções puras `montar_parecidos(codigo_ibge, competencia, dados, historico) -> ParecidosResposta` e `montar_acerto(entradas, itens_por_registro, desde, sem_resposta) -> AcertoResposta` em `preenchimento.py`.

- [ ] **Step 1: Schemas**

Em `backend/app/models/schemas.py`, depois de `SugestaoResposta`:

```python
class ExemploParecido(BaseModel):
    codigo_ibge: str
    competencia: str
    municipio: str
    uf: str
    valor: float
    distancia: float


class PlanoParecidos(BaseModel):
    indice: int = Field(..., description="Posição do plano na tabela")
    plano: str
    mediana: Optional[float] = None
    exemplos: List[ExemploParecido] = Field(default_factory=list)


class ParecidosResposta(BaseModel):
    codigo_ibge: str
    competencia: str
    planos: List[PlanoParecidos]


class MetricasPlano(BaseModel):
    tipo: str
    plano: str
    registros: int
    exatos: int
    erro_mediano: Optional[float] = None
    dentro_25: int
    zero_certo: int
    razao_soma: Optional[float] = None
    alerta: bool


class PreenchidosPlano(BaseModel):
    plano: str
    registros: int
    preenchidos: int


class AcertoResposta(BaseModel):
    desde: str
    planos: List[MetricasPlano]
    manuais: List[PreenchidosPlano]
    sem_resposta: int = Field(..., description="Registros sem resposta do Ministério guardada")
```

- [ ] **Step 2: Testes de montagem (falham)**

No fim de `backend/tests/test_parecidos.py`:

```python
def test_montar_parecidos_usa_posicao_dos_planos_municipais():
    from app.api.endpoints.preenchimento import montar_parecidos
    dados = {
        'pagamentos': [{'qtPopulacao': 10000, 'qtEsfTotalPgto': 4, 'sgUf': 'BA', 'noMunicipio': 'Alvo'}],
        'resumosPlanosOrcamentarios': [
            {'dsPlanoOrcamentario': 'Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': 1},
            {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': 0},
            {'dsPlanoOrcamentario': 'Incentivo financeiro da APS - Promoção à saúde',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': 0},
        ],
    }
    hist = [('111111', '202606', perfil(_resposta(10000, 4, nome='Boninal')), _itens(19900))]
    r = montar_parecidos('999999', '202606', dados, hist)
    assert [(p.indice, p.mediana) for p in r.planos] == [(1, 19900), (2, None)]
    assert r.planos[0].exemplos[0].municipio == 'Boninal'
```

No fim de `backend/tests/test_acerto.py`:

```python
def test_montar_acerto():
    from app.api.endpoints.preenchimento import montar_acerto
    entradas = [([_sug('acs', 6484)], [{'plano': 'Agentes Comunitários de Saúde', 'valor': 6484, 'origem': 'manual'}])]
    r = montar_acerto(entradas, [e[1] for e in entradas], '202512', sem_resposta=2)
    acs = next(p for p in r.planos if p.tipo == 'acs')
    assert (acs.registros, acs.exatos, acs.plano) == (1, 1, 'ACS')
    assert r.sem_resposta == 2 and r.desde == '202512'
    assert {m.plano for m in r.manuais} == {'Demais programas', 'Incentivo financeiro da APS - Promoção'}
```

Run: `cd backend && $PY -m pytest -q tests/test_parecidos.py tests/test_acerto.py`
Expected: FAIL (`ImportError: montar_parecidos`).

- [ ] **Step 3: Implementar em `preenchimento.py`**

Imports a acrescentar:

```python
from app.core.dependencies import get_respostas_service
from app.models.schemas import AcertoResposta, ExemploParecido, MetricasPlano, ParecidosResposta, PlanoParecidos, PreenchidosPlano
from app.services.acerto import PLANOS_ACERTO, comparar, contar_preenchidos, metricas
from app.services.municipios_editados import municipio_editado_service
from app.services.parecidos import PREFIXOS_PARECIDOS, mediana, parecidos, perfil
from app.services.regras_perda import filtrar_resumos_municipais
from app.services.respostas_ministerio import RespostasMinisterioService
```

Funções puras e helpers (antes das rotas):

```python
def _itens(editado) -> List[dict]:
    return [i.model_dump() if hasattr(i, 'model_dump') else dict(i) for i in (editado.itens or [])]


def montar_parecidos(codigo_ibge: str, competencia: str, dados: dict, historico) -> ParecidosResposta:
    alvo = perfil(dados)
    planos: List[PlanoParecidos] = []
    for indice, resumo in enumerate(filtrar_resumos_municipais(dados.get('resumosPlanosOrcamentarios') or [])):
        nome = resumo.get('dsPlanoOrcamentario') or ''
        prefixo = next((p for p in PREFIXOS_PARECIDOS if nome.startswith(p)), None)
        if not prefixo:
            continue
        exemplos = parecidos(codigo_ibge, alvo, historico, prefixo) if alvo else []
        planos.append(PlanoParecidos(indice=indice, plano=nome, mediana=mediana(exemplos),
                                     exemplos=[ExemploParecido(**vars(e)) for e in exemplos]))
    return ParecidosResposta(codigo_ibge=codigo_ibge, competencia=competencia, planos=planos)


def montar_acerto(entradas, itens_por_registro, desde: str, sem_resposta: int) -> AcertoResposta:
    pares = comparar(entradas)
    planos = [MetricasPlano(tipo=tipo, plano=rotulo, **metricas(pares[tipo]))
              for tipo, (rotulo, _) in PLANOS_ACERTO.items()]
    manuais = [PreenchidosPlano(plano=p, **c) for p, c in contar_preenchidos(itens_por_registro).items()]
    return AcertoResposta(desde=desde, planos=planos, manuais=manuais, sem_resposta=sem_resposta)
```

Rotas (a de `acerto` vem **antes** das rotas com `{codigo_ibge}`):

```python
@router.get("/acerto", response_model=AcertoResposta)
async def acerto_automatico(
    desde: str = Query("202512", pattern=r"^\d{6}$"),
    current_user: User = Depends(get_current_superuser),
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
    respostas_service: RespostasMinisterioService = Depends(get_respostas_service),
):
    """Quanto a regra atual se aproxima do que o consultor informou à mão (só leitura)."""
    editados = [e for e in municipio_editado_service.get_all_editados() if e.competencia >= desde and e.itens]
    respostas = await respostas_service.todas()
    valores_por_comp: dict = {}
    entradas, sem_resposta = [], 0
    for e in editados:
        dados = respostas.get((e.codigo_ibge, e.competencia))
        if not dados or not dados.get('pagamentos'):
            sem_resposta += 1
            continue
        if e.competencia not in valores_por_comp:
            valores_por_comp[e.competencia] = await valores_service.vigentes(e.competencia)
        try:
            sugestoes = sugerir(dados, valores_por_comp[e.competencia])
        except KeyError:
            sem_resposta += 1
            continue
        entradas.append((sugestoes, _itens(e)))
    return montar_acerto(entradas, [_itens(e) for e in editados], desde, sem_resposta)


@router.get("/{codigo_ibge}/{competencia}/parecidos", response_model=ParecidosResposta)
async def municipios_parecidos(
    codigo_ibge: str,
    competencia: str,
    respostas_service: RespostasMinisterioService = Depends(get_respostas_service),
):
    """Como o consultor preencheu Demais e Promoção em municípios parecidos (só leitura)."""
    dados = await respostas_service.obter(codigo_ibge, competencia)
    if not dados:
        dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados or not dados.get('resumosPlanosOrcamentarios'):
        raise HTTPException(status_code=404, detail="Sem dados de financiamento do Ministério para este município")
    respostas = await respostas_service.todas()
    historico = []
    for e in municipio_editado_service.get_all_editados():
        resposta = respostas.get((e.codigo_ibge, e.competencia))
        perf = perfil(resposta) if resposta else None
        if perf and e.itens:
            historico.append((e.codigo_ibge, e.competencia, perf, _itens(e)))
    return montar_parecidos(codigo_ibge, competencia, dados, historico)
```

- [ ] **Step 4: Rodar a suíte do backend**

Run: `cd backend && $PY -m pytest -q tests/test_regras_perda.py tests/test_respostas_ministerio.py tests/test_parecidos.py tests/test_acerto.py`
Expected: PASS. Conferir também que a app importa: `cd backend && $PY -c "import main"` (não sobe servidor, não conecta ao banco).

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/schemas.py backend/app/api/endpoints/preenchimento.py backend/tests/test_parecidos.py backend/tests/test_acerto.py
git commit -m "feat(preenchimento): endpoints de municípios parecidos e acerto do automático"
```

---

### Task 6: Parecidos no modal de preenchimento

**Files:**
- Modify: `frontend/src/types/index.ts` (tipos novos depois de `SugestaoAplicada`)
- Modify: `frontend/src/services/api.ts` (depois de `getSugestaoPreenchimento`)
- Create: `frontend/src/utils/parecidos.ts`
- Create: `frontend/tests/parecidos.test.ts`
- Modify: `frontend/src/components/DataTable/PreenchimentoAutomatico.tsx`

**Interfaces:**
- Consumes: `GET /preenchimento/{ibge}/{comp}/parecidos` (Task 5).
- Produces: tipos `ExemploParecido`, `PlanoParecidos`, `ParecidosResposta`, `MetricasPlano`, `PreenchidosPlano`, `AcertoResposta` (espelham os schemas da Task 5); `apiClient.getParecidos(codigoIbge, competencia): Promise<ParecidosResposta>`; `competenciaCurta(c: string): string` ('202606' → '06/2026'); `resumoParecidos(exemplos: ExemploParecido[], moeda: Intl.NumberFormat): string`; `REGRA_PARECIDOS = 'parecidos_v1'`.

- [ ] **Step 1: Tipos e API**

Em `frontend/src/types/index.ts`, depois de `SugestaoAplicada`:

```ts
export interface ExemploParecido {
  codigo_ibge: string;
  competencia: string;
  municipio: string;
  uf: string;
  valor: number;
  distancia: number;
}

export interface PlanoParecidos {
  indice: number;
  plano: string;
  mediana?: number | null;
  exemplos: ExemploParecido[];
}

export interface ParecidosResposta {
  codigo_ibge: string;
  competencia: string;
  planos: PlanoParecidos[];
}

export interface MetricasPlano {
  tipo: string;
  plano: string;
  registros: number;
  exatos: number;
  erro_mediano?: number | null;
  dentro_25: number;
  zero_certo: number;
  razao_soma?: number | null;
  alerta: boolean;
}

export interface PreenchidosPlano {
  plano: string;
  registros: number;
  preenchidos: number;
}

export interface AcertoResposta {
  desde: string;
  planos: MetricasPlano[];
  manuais: PreenchidosPlano[];
  sem_resposta: number;
}
```

Em `frontend/src/services/api.ts`, depois de `getSugestaoPreenchimento` (e importar os tipos novos no import de `../types`):

```ts
  async getParecidos(codigoIbge: string, competencia: string): Promise<ParecidosResposta> {
    const response = await this.client.get<ParecidosResposta>(
      `/preenchimento/${codigoIbge}/${competencia}/parecidos`
    );
    return response.data;
  }

  async getAcerto(desde: string): Promise<AcertoResposta> {
    const response = await this.client.get<AcertoResposta>('/preenchimento/acerto', { params: { desde } });
    return response.data;
  }
```

- [ ] **Step 2: Testes do utilitário (falham)**

`frontend/tests/parecidos.test.ts`:

```ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { competenciaCurta, resumoParecidos } from '../src/utils/parecidos.ts';

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

test('competência curta', () => {
  assert.equal(competenciaCurta('202606'), '06/2026');
});

test('resumo dos parecidos', () => {
  const texto = resumoParecidos(
    [
      { codigo_ibge: '1', competencia: '202606', municipio: 'MARICA', uf: 'RJ', valor: 27300, distancia: 0.1 },
      { codigo_ibge: '2', competencia: '202512', municipio: 'BARRA', uf: 'BA', valor: 25000, distancia: 0.2 },
    ],
    moeda
  );
  assert.match(texto, /^MARICA\/RJ 06\/2026 R\$\s27\.300,00 · BARRA\/BA 12\/2025 R\$\s25\.000,00$/);
});

test('sem exemplos', () => {
  assert.equal(resumoParecidos([], moeda), '');
});
```

Run: `cd frontend && npm test`
Expected: FAIL (módulo `parecidos.ts` não existe).

- [ ] **Step 3: Utilitário**

`frontend/src/utils/parecidos.ts`:

```ts
/**
 * Municípios parecidos (Demais programas e Promoção à saúde): formatação da linha do modal.
 */
import type { ExemploParecido } from '../types';

/** regra_id gravado quando o consultor aplica a mediana dos parecidos */
export const REGRA_PARECIDOS = 'parecidos_v1';

export const competenciaCurta = (c: string) => `${c.slice(4)}/${c.slice(0, 4)}`;

export const resumoParecidos = (exemplos: ExemploParecido[], moeda: Intl.NumberFormat) =>
  exemplos
    .map((e) => `${e.municipio}/${e.uf} ${competenciaCurta(e.competencia)} ${moeda.format(e.valor)}`)
    .join(' · ');
```

Run: `cd frontend && npm test`
Expected: PASS.

- [ ] **Step 4: Modal**

Em `PreenchimentoAutomatico.tsx`:

1. Imports: `PlanoParecidos` de `../../types`; `REGRA_PARECIDOS, resumoParecidos` de `../../utils/parecidos`.
2. Estados novos: `const [parecidos, setParecidos] = useState<Record<number, PlanoParecidos>>({});` e `const [usarMediana, setUsarMediana] = useState<Record<number, boolean>>({});`.
3. No effect de abertura (o que já limpa estado e usa `atual`), limpar os dois estados novos junto dos outros e, em paralelo à sugestão, buscar os parecidos — falha é silenciosa (o recurso é complementar):

```ts
    setParecidos({});
    setUsarMediana({});
    apiClient
      .getParecidos(selectedMunicipio.codigo_ibge, selectedCompetencia)
      .then((r) => {
        if (atual) setParecidos(Object.fromEntries(r.planos.map((p) => [p.indice, p])));
      })
      .catch(() => undefined);
```

4. Em `aplicar()`, depois do laço dos `aplicaveis` e antes de `setSugestoesAplicadas`:

```ts
    // Mediana dos municípios parecidos (Demais e Promoção), só onde o consultor escolheu usar
    for (const [indice, usar] of Object.entries(usarMediana)) {
      const i = Number(indice);
      const valor = parecidos[i]?.mediana;
      if (!usar || valor == null || i >= perdas.length) continue;
      perdas[i] = valor;
      sugestoes[i] = { regra_id: REGRA_PARECIDOS, valor_sugerido: valor, valor_aplicado: valor };
    }
```

5. Contagem do botão do rodapé: `const quantidadeAplicar = aplicaveis.length + Object.entries(usarMediana).filter(([i, u]) => u && parecidos[Number(i)]?.mediana != null).length;` — usar em `disabled={carregando || !quantidadeAplicar}` e no texto `Aplicar {quantidadeAplicar} plano(s) na tabela`.
6. No corpo do `Card` de plano não aplicável (`p.aplicavel` falso), depois de `<Text type="secondary">{p.observacao}</Text>`, envolver num `Space direction="vertical"` e acrescentar, quando houver `parecidos[p.indice]`:

```tsx
{parecidos[p.indice] && (
  parecidos[p.indice].exemplos.length ? (
    <Space direction="vertical" size={4} style={{ width: '100%' }}>
      <Text type="secondary">
        Municípios parecidos: {resumoParecidos(parecidos[p.indice].exemplos, moeda)}
      </Text>
      <Checkbox
        checked={!!usarMediana[p.indice]}
        onChange={(e) => setUsarMediana((u) => ({ ...u, [p.indice]: e.target.checked }))}
      >
        Usar a mediana: {moeda.format(parecidos[p.indice].mediana ?? 0)}
      </Checkbox>
    </Space>
  ) : (
    <Text type="secondary">Sem histórico parecido.</Text>
  )
)}
```

7. No `extra` do card não aplicável: quando `usarMediana[p.indice]`, mostrar `{moeda.format(valorAtual(p.indice))} → {moeda.format(parecidos[p.indice]?.mediana ?? 0)}` (mesmo padrão dos aplicáveis); senão, o `mantém …` atual.

- [ ] **Step 5: Verificar**

Run: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3`
Expected: testes PASS; tsc limpo; eslint ≤ 16 erros, nenhum novo em arquivo tocado.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/services/api.ts frontend/src/utils/parecidos.ts frontend/tests/parecidos.test.ts frontend/src/components/DataTable/PreenchimentoAutomatico.tsx
git commit -m "feat(preenchimento): municípios parecidos no modal para Demais e Promoção"
```

---

### Task 7: Página admin "Acerto do automático"

**Files:**
- Create: `frontend/src/pages/Admin/AcertoAutomatico.tsx`
- Modify: `frontend/src/App.tsx` (rota depois de `/admin/valores-referencia`, import junto de `ValoresReferencia`)
- Modify: `frontend/src/components/Layout/Sidebar.tsx:61-65` (item no Menu de admin)
- Modify: `frontend/src/components/Layout/Header.tsx:66-71` (item no dropdown de admin)

**Interfaces:**
- Consumes: `apiClient.getAcerto(desde)` e tipos `AcertoResposta`/`MetricasPlano` (Task 6); `competenciaValida` de `utils/municipiosLote`.

- [ ] **Step 1: Página**

`frontend/src/pages/Admin/AcertoAutomatico.tsx`:

```tsx
/**
 * Acerto do preenchimento automático em relação ao consultor.
 * Recalcula a regra atual sobre as perdas informadas à mão e mostra, por plano, quanto se aproxima.
 */

import React, { useState } from 'react';
import { Alert, Button, Card, Input, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import { competenciaValida } from '../../utils/municipiosLote';
import type { MetricasPlano } from '../../types';

const { Title, Text } = Typography;

const pct = (v?: number | null) => (v == null ? '—' : `${Math.round(v * 100)}%`);
const razao = (v?: number | null) => (v == null ? '—' : v.toLocaleString('pt-BR', { maximumFractionDigits: 2 }));

const colunas: ColumnsType<MetricasPlano> = [
  { title: 'Plano', dataIndex: 'plano' },
  { title: 'Registros', dataIndex: 'registros', align: 'right' },
  { title: 'Exatos', key: 'exatos', align: 'right', render: (_, m) => `${m.exatos} de ${m.registros}` },
  { title: 'Erro mediano', dataIndex: 'erro_mediano', align: 'right', render: pct },
  { title: 'Dentro de ±25%', dataIndex: 'dentro_25', align: 'right' },
  { title: 'Zero certo', key: 'zero', align: 'right', render: (_, m) => `${m.zero_certo} de ${m.registros}` },
  { title: 'Sugerido ÷ informado', dataIndex: 'razao_soma', align: 'right', render: razao },
  {
    title: 'Situação',
    key: 'alerta',
    render: (_, m) => (m.alerta ? <Tag color="orange">Afastado do consultor</Tag> : <Tag color="green">Ok</Tag>),
  },
];

const AcertoAutomatico: React.FC = () => {
  const [desde, setDesde] = useState('202512');
  const [consultado, setConsultado] = useState('202512');

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['acerto-automatico', consultado],
    queryFn: () => apiClient.getAcerto(consultado),
  });

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={2} style={{ marginBottom: 0 }}>Acerto do automático</Title>
        <Text type="secondary">
          Compara o preenchimento automático com o que o consultor informou à mão. Só valores digitados pelo consultor
          entram; o que veio da própria regra não conta.
        </Text>
      </div>

      <Card>
        <Space wrap>
          <Input
            addonBefore="Desde a competência"
            value={desde}
            maxLength={6}
            status={desde && !competenciaValida(desde) ? 'error' : undefined}
            onChange={(e) => setDesde(e.target.value.replace(/\D/g, ''))}
            style={{ width: 280 }}
          />
          <Button type="primary" disabled={!competenciaValida(desde)} onClick={() => setConsultado(desde)}>
            Atualizar
          </Button>
        </Space>
      </Card>

      {isError && (
        <Alert
          type="error"
          showIcon
          message="Não foi possível calcular o acerto."
          action={<Button size="small" onClick={() => refetch()}>Tentar novamente</Button>}
        />
      )}

      {data && data.sem_resposta > 0 && (
        <Alert
          type="info"
          showIcon
          message={`${data.sem_resposta} registro(s) ficaram de fora por não ter a resposta do Ministério guardada.`}
        />
      )}

      <Card title="Planos com regra">
        <Table size="small" rowKey="tipo" loading={isLoading} columns={colunas} dataSource={data?.planos ?? []}
               pagination={false} scroll={{ x: 800 }} />
      </Card>

      <Card title="Planos preenchidos só pelo consultor">
        <Space direction="vertical">
          {(data?.manuais ?? []).map((m) => (
            <Text key={m.plano}>
              {m.plano}: preenchido em {m.preenchidos} de {m.registros} registros
            </Text>
          ))}
        </Space>
      </Card>
    </Space>
  );
};

export default AcertoAutomatico;
```

- [ ] **Step 2: Rota e menus**

`frontend/src/App.tsx`: `import AcertoAutomatico from './pages/Admin/AcertoAutomatico';` e, depois da rota de `/admin/valores-referencia`, a mesma estrutura com `path="/admin/acerto-automatico"` e `<AcertoAutomatico />` dentro de `<ProtectedRoute requireSuperuser><AppLayout>…`.

`Sidebar.tsx`: no bloco de itens de superusuário, depois de "Valores de referência": `{ key: '/admin/acerto-automatico', icon: <LineChartOutlined />, label: 'Acerto do automático' },` e importar `LineChartOutlined` de `@ant-design/icons`.

`Header.tsx`: no dropdown de admin, depois do item `valores-referencia`: `{ key: 'acerto-automatico', icon: <LineChartOutlined />, label: 'Acerto do automático', onClick: () => navigate('/admin/acerto-automatico') }` e o import do ícone.

- [ ] **Step 3: Verificar**

Run: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3`
Expected: PASS; tsc limpo; eslint ≤ 16, nenhum novo nos arquivos tocados.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Admin/AcertoAutomatico.tsx frontend/src/App.tsx frontend/src/components/Layout/Sidebar.tsx frontend/src/components/Layout/Header.tsx
git commit -m "feat(admin): página de acerto do preenchimento automático"
```

---

## Depois da implementação (usuário, no servidor)

1. Reiniciar o backend (a tabela `respostas_ministerio` é criada no startup).
2. Carga inicial: `cd backend && .venv/bin/python scripts/carregar_respostas_ministerio.py 202512` (≈ 92 consultas de leitura ao Ministério).
3. Abrir Admin → Acerto do automático: o ACS deve aparecer com "Sugerido ÷ informado" bem mais perto de 1 do que os 3,40 da regra antiga.
4. No Dashboard, abrir "Preencher automaticamente" num município e conferir a linha de municípios parecidos em Demais/Promoção.
