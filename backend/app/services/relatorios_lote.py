"""
Geração de relatórios em lote (stories 3.4 e 3.5).

Cada lote roda em segundo plano: consulta o Ministério com concorrência limitada,
renderiza os PDFs numa thread (um por vez, o WeasyPrint é pesado e não bloqueia o
servidor) e grava tudo num ZIP temporário. Uma falha num município vai para o
`erros.txt` do ZIP e não interrompe os demais.

O estado dos lotes fica em memória: se o backend reiniciar, os lotes em andamento
se perdem (o usuário gera de novo). Os ZIPs antigos são apagados após LOTE_TTL.
"""
import asyncio
import os
import re
import shutil
import tempfile
import unicodedata
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.models.schemas import LoteConferenciaItem, LoteRequest, LoteStatus, MunicipioLote
from app.services.municipios_editados import municipio_editado_service
from app.services.relatorios_service import DadosNaoEncontrados, preencher_por_regras, preparar_dados, renderizar_pdf
from app.utils.logger import logger

CONSULTAS_SIMULTANEAS = 3   # chamadas simultâneas à API do Ministério
RENDERIZACOES_SIMULTANEAS = 1
LOTE_TTL = timedelta(hours=6)


def _slug(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+', '_', texto).strip('_')


def nome_arquivo(m: MunicipioLote, competencia: str, tipo: str) -> str:
    return f"{m.uf.upper()}_{_slug(m.nome)}_{competencia}_{tipo}.pdf"


def conferir(competencia: str, municipios: List[MunicipioLote]) -> List[LoteConferenciaItem]:
    """Situação das perdas salvas de cada município, sem consultar o Ministério."""
    itens = []
    for m in municipios:
        editado = municipio_editado_service.get_editado(m.codigo_ibge, competencia)
        if not editado:
            itens.append(LoteConferenciaItem(codigo_ibge=m.codigo_ibge, nome=m.nome, uf=m.uf, tem_perdas=False))
            continue
        origens: Dict[str, int] = {}
        for item in editado.itens or []:
            origens[item.origem] = origens.get(item.origem, 0) + 1
        itens.append(LoteConferenciaItem(
            codigo_ibge=m.codigo_ibge, nome=m.nome, uf=m.uf, tem_perdas=True,
            total_perda_mensal=float(sum(v or 0 for v in editado.perda_recurso_mensal)),
            origens=origens, data_edicao=editado.data_edicao,
        ))
    return itens


@dataclass
class Lote:
    id: str
    usuario_id: str
    pedido: LoteRequest
    pasta: str
    status: str = 'processando'
    processados: int = 0
    arquivos: int = 0
    calculados: int = 0
    erros: List[str] = field(default_factory=list)
    criado_em: datetime = field(default_factory=datetime.now)
    concluido_em: Optional[datetime] = None

    @property
    def zip_path(self) -> str:
        return os.path.join(self.pasta, f"relatorios_{self.pedido.competencia}.zip")

    def status_publico(self) -> LoteStatus:
        return LoteStatus(
            id=self.id, status=self.status, competencia=self.pedido.competencia,
            tipos=list(self.pedido.tipos), total=len(self.pedido.municipios),
            processados=self.processados, arquivos=self.arquivos, calculados=self.calculados,
            erros=list(self.erros),
            criado_em=self.criado_em, concluido_em=self.concluido_em,
        )


class GerenciadorLotes:
    def __init__(self):
        self._lotes: Dict[str, Lote] = {}
        self._tarefas: Dict[str, asyncio.Task] = {}
        self._render = asyncio.Semaphore(RENDERIZACOES_SIMULTANEAS)

    def criar(self, pedido: LoteRequest, usuario_id: str) -> Lote:
        self._limpar_antigos()
        lote = Lote(id=uuid.uuid4().hex, usuario_id=usuario_id, pedido=pedido,
                    pasta=tempfile.mkdtemp(prefix='maispap-lote-'))
        self._lotes[lote.id] = lote
        # Guarda a referência da task para ela não ser coletada antes de terminar
        self._tarefas[lote.id] = asyncio.create_task(self._processar(lote))
        logger.info(f"Lote {lote.id}: {len(pedido.municipios)} municípios, tipos {pedido.tipos}")
        return lote

    def obter(self, lote_id: str, usuario_id: str) -> Optional[Lote]:
        lote = self._lotes.get(lote_id)
        return lote if lote and lote.usuario_id == usuario_id else None

    def _limpar_antigos(self):
        limite = datetime.now() - LOTE_TTL
        for lote_id, lote in list(self._lotes.items()):
            if lote.status != 'processando' and lote.criado_em < limite:
                shutil.rmtree(lote.pasta, ignore_errors=True)
                self._lotes.pop(lote_id, None)
                self._tarefas.pop(lote_id, None)

    async def _processar(self, lote: Lote):
        pedido = lote.pedido
        consultas = asyncio.Semaphore(CONSULTAS_SIMULTANEAS)
        escrita = asyncio.Lock()
        try:
            with zipfile.ZipFile(lote.zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:

                async def um_municipio(m: MunicipioLote):
                    rotulo = f"{m.nome}/{m.uf} ({m.codigo_ibge})"
                    try:
                        sem_perdas = not municipio_editado_service.get_editado(m.codigo_ibge, pedido.competencia)
                        if sem_perdas and pedido.sem_perdas == 'ignorar':
                            lote.erros.append(f"{rotulo}: sem perdas salvas na competência (ignorado)")
                            return
                        if sem_perdas and pedido.sem_perdas == 'regras':
                            async with consultas:
                                calculou = await preencher_por_regras(m.codigo_ibge, pedido.competencia, lote.usuario_id)
                            if not calculou:
                                raise DadosNaoEncontrados("sem dados do Ministério")
                            lote.calculados += 1
                        async with consultas:
                            dados = await preparar_dados(m.codigo_ibge, pedido.competencia)
                        for tipo in pedido.tipos:
                            async with self._render:
                                pdf = await asyncio.to_thread(
                                    renderizar_pdf, tipo, dados, m.nome, m.uf, pedido.competencia
                                )
                            async with escrita:
                                zf.writestr(nome_arquivo(m, pedido.competencia, tipo), pdf)
                                lote.arquivos += 1
                    except DadosNaoEncontrados:
                        lote.erros.append(f"{rotulo}: sem dados de financiamento no Ministério")
                    except Exception as exc:  # um município não derruba o lote
                        logger.error(f"Lote {lote.id} - erro em {rotulo}: {exc}", exc_info=True)
                        lote.erros.append(f"{rotulo}: erro ao gerar ({type(exc).__name__})")
                    finally:
                        lote.processados += 1

                await asyncio.gather(*(um_municipio(m) for m in pedido.municipios))

                if lote.erros:
                    zf.writestr('erros.txt', '\n'.join(sorted(lote.erros)) + '\n')
            lote.status = 'concluido'
        except Exception as exc:
            logger.error(f"Lote {lote.id} falhou: {exc}", exc_info=True)
            lote.erros.append(f"Falha geral do lote: {type(exc).__name__}")
            lote.status = 'erro'
        finally:
            lote.concluido_em = datetime.now()
            logger.info(f"Lote {lote.id} {lote.status}: {lote.arquivos} arquivos, {len(lote.erros)} avisos")


gerenciador_lotes = GerenciadorLotes()
