"""
Valores de referência do financiamento federal da APS, por vigência (story 3.3).

Os valores mudam por portaria, então ficam no banco (tabela `valores_referencia`),
editáveis pelo administrador. O catálogo abaixo define as chaves e os valores iniciais,
confirmados para 2025 (pagamentos do Ministério + pesquisa); veja
docs/analises/regras-preenchimento-completo.md.
"""
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ValorReferenciaDB
from app.utils.logger import logger

VIGENCIA_INICIAL = "202405"  # início do modelo da Portaria GM/MS 3.493/2024
ANO_CONFIRMADO_INICIAL = "2025"  # os valores iniciais foram conferidos com os pagamentos de 2025

# chave: (descrição, valor inicial, fonte)
CATALOGO: Dict[str, Tuple[str, str, str]] = {
    "acs_valor": ("ACS: valor mensal por agente", "3242.00", "Usuário (Ministério pagou 3.036 em 2025)"),
    "esf_fixo_estrato_1": ("eSF: componente fixo por equipe, estrato 1", "18000.00", "Pagamentos do Ministério"),
    "esf_fixo_estrato_2": ("eSF: componente fixo por equipe, estrato 2", "16000.00", "Pagamentos do Ministério"),
    "esf_fixo_estrato_3": ("eSF: componente fixo por equipe, estrato 3", "14000.00", "Pagamentos do Ministério"),
    "esf_fixo_estrato_4": ("eSF: componente fixo por equipe, estrato 4", "12000.00", "Pagamentos do Ministério"),
    "esf_vinculo_otimo": ("eSF: vínculo e acompanhamento ÓTIMO por equipe", "8000.00", "Inferido do histórico (BOM = 6.000)"),
    "esf_qualidade_otimo": ("eSF: qualidade ÓTIMO por equipe", "8000.00", "Inferido do histórico (BOM = 6.000)"),
    "esf_constante_usuario": ("eSF: constante do usuário somada caso a caso", "14058.00", "Usuário"),
    "sb_qualidade_otimo": ("eSB 40h: qualidade ÓTIMO por equipe", "3673.50", "Portaria 3.493/2024 (Anexo XCIX-B)"),
    "sb_qualidade_bom": ("eSB 40h: qualidade BOM por equipe", "2755.13", "Portaria 3.493/2024 (Anexo XCIX-B)"),
    "sesb_custeio": ("SESB: custeio mensal", "7200.00", "Portaria GM/MS 751/2023"),
    "sesb_populacao_max": ("SESB: população máxima do município", "20000", "Portaria GM/MS 751/2023"),
    "uom_custeio": ("UOM: custeio mensal por unidade", "9360.00", "Pagamentos do Ministério"),
    "lrpd_faixa_1": ("LRPD: faixa 1", "11250.00", "Pagamentos do Ministério"),
    "lrpd_faixa_2": ("LRPD: faixa 2", "18000.00", "Pagamentos do Ministério"),
    "lrpd_faixa_3": ("LRPD: faixa 3", "27000.00", "Pagamentos do Ministério"),
    "lrpd_faixa_4": ("LRPD: faixa 4", "33750.00", "Pagamentos do Ministério"),
    "emulti_custeio_estrategica": ("eMulti Estratégica: custeio mensal", "12000.00", "Portaria GM/MS 635/2023"),
    "emulti_custeio_complementar": ("eMulti Complementar: custeio mensal", "24000.00", "Portaria GM/MS 635/2023"),
    "emulti_custeio_ampliada": ("eMulti Ampliada: custeio mensal", "36000.00", "Portaria GM/MS 635/2023"),
    "emulti_qualidade_bom_pct": ("eMulti: qualidade BOM (fração do custeio)", "0.1875", "Pagamentos do Ministério"),
    "emulti_profissionais_por_equipe": ("eMulti: profissionais elegíveis por equipe estimada", "6", "Calibrado no histórico (story 3.6)"),
}


class ValoresReferenciaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def semear_padrao(self) -> int:
        """Grava os valores iniciais das chaves que ainda não existem. Idempotente."""
        existentes = set((await self.session.execute(select(ValorReferenciaDB.chave))).scalars().all())
        novas = [
            ValorReferenciaDB(chave=chave, vigente_desde=VIGENCIA_INICIAL, valor=valor, fonte=fonte)
            for chave, (_desc, valor, fonte) in CATALOGO.items() if chave not in existentes
        ]
        if novas:
            self.session.add_all(novas)
            await self.session.commit()
            logger.info(f"Valores de referência iniciais gravados: {len(novas)}")
        return len(novas)

    async def listar(self) -> List[ValorReferenciaDB]:
        result = await self.session.execute(
            select(ValorReferenciaDB).order_by(ValorReferenciaDB.chave, ValorReferenciaDB.vigente_desde)
        )
        return list(result.scalars().all())

    async def vigentes(self, competencia: str) -> Dict[str, Tuple[Decimal, str]]:
        """Valor vigente de cada chave na competência: {chave: (valor, vigente_desde)}."""
        vig: Dict[str, Tuple[Decimal, str]] = {}
        for row in await self.listar():
            if row.vigente_desde <= competencia:
                vig[row.chave] = (Decimal(row.valor), row.vigente_desde)
        return vig

    async def cadastrar(self, chave: str, vigente_desde: str, valor: Decimal,
                        fonte: Optional[str], usuario_id: Optional[str]) -> ValorReferenciaDB:
        """Cria (ou substitui) o valor de uma chave a partir de uma competência."""
        existente = (await self.session.execute(
            select(ValorReferenciaDB).where(
                ValorReferenciaDB.chave == chave, ValorReferenciaDB.vigente_desde == vigente_desde)
        )).scalar_one_or_none()
        if existente:
            existente.valor, existente.fonte, existente.usuario_id = str(valor), fonte, usuario_id
            row = existente
        else:
            row = ValorReferenciaDB(chave=chave, vigente_desde=vigente_desde, valor=str(valor),
                                    fonte=fonte, usuario_id=usuario_id)
            self.session.add(row)
        await self.session.commit()
        return row

    async def remover(self, id_: int) -> bool:
        row = await self.session.get(ValorReferenciaDB, id_)
        if not row:
            return False
        # A vigência inicial não pode ser removida: toda chave precisa de um valor
        if row.vigente_desde == VIGENCIA_INICIAL:
            raise ValueError("A vigência inicial não pode ser removida; cadastre uma nova vigência")
        await self.session.delete(row)
        await self.session.commit()
        return True
