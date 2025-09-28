"""
Serviço para consulta de dados de municípios brasileiros
Baseado na biblioteca pyUFbr
"""
from typing import List, Optional
from pyUFbr.baseuf import ufbr

from app.models.schemas import UF, Municipio
from app.utils.logger import logger


class MunicipioService:
    """Serviço para consulta de municípios e UFs"""

    def get_ufs(self) -> List[UF]:
        """
        Retorna lista de todas as UFs

        Returns:
            List[UF]: Lista de Unidades Federativas
        """
        try:
            ufs_data = []
            ufs_list = ufbr.list_uf

            for uf_sigla in sorted(ufs_list):
                try:
                    uf_obj = ufbr.get_uf(uf_sigla)
                    ufs_data.append(UF(
                        codigo=str(uf_obj.codigo),
                        nome=uf_obj.nome,
                        sigla=uf_obj.sigla
                    ))
                except Exception as e:
                    logger.warning(f"Erro ao processar UF {uf_sigla}: {str(e)}")
                    # Fallback com dados básicos
                    ufs_data.append(UF(
                        codigo="00",
                        nome=uf_sigla,
                        sigla=uf_sigla
                    ))

            return ufs_data

        except Exception as e:
            logger.error(f"Erro ao buscar UFs: {str(e)}")
            return []

    def get_municipios_por_uf(self, uf_sigla: str) -> List[Municipio]:
        """
        Retorna lista de municípios de uma UF

        Args:
            uf_sigla: Sigla da UF (ex: 'MG', 'SP')

        Returns:
            List[Municipio]: Lista de municípios da UF
        """
        try:
            municipios_data = []
            municipios_list = ufbr.list_cidades(uf_sigla)

            for municipio_nome in sorted(municipios_list):
                try:
                    codigo_ibge = self.get_codigo_ibge(municipio_nome)
                    if codigo_ibge:
                        municipios_data.append(Municipio(
                            codigo_ibge=codigo_ibge,
                            nome=municipio_nome,
                            uf=uf_sigla.upper()
                        ))
                except Exception as e:
                    logger.warning(f"Erro ao processar município {municipio_nome}: {str(e)}")

            return municipios_data

        except Exception as e:
            logger.error(f"Erro ao buscar municípios da UF {uf_sigla}: {str(e)}")
            return []

    def get_codigo_ibge(self, municipio_nome: str) -> Optional[str]:
        """
        Obtém código IBGE do município

        Args:
            municipio_nome: Nome do município

        Returns:
            str: Código IBGE (6 dígitos) ou None se não encontrado
        """
        try:
            cidade = ufbr.get_cidade(municipio_nome)
            if cidade and hasattr(cidade, 'codigo'):
                # Remove último dígito conforme lógica original
                codigo_ibge = str(int(float(cidade.codigo)))[:-1]
                return codigo_ibge
            return None

        except Exception as e:
            logger.error(f"Erro ao obter código IBGE para {municipio_nome}: {str(e)}")
            return None

    def get_municipio_por_codigo(self, codigo_ibge: str) -> Optional[Municipio]:
        """
        Busca município pelo código IBGE

        Args:
            codigo_ibge: Código IBGE do município

        Returns:
            Municipio: Dados do município ou None se não encontrado
        """
        try:
            # Esta funcionalidade requereria busca reversa na pyUFbr
            # Por enquanto, retornamos None para implementação futura
            logger.info(f"Busca reversa por código IBGE {codigo_ibge} não implementada")
            return None

        except Exception as e:
            logger.error(f"Erro ao buscar município por código {codigo_ibge}: {str(e)}")
            return None

    def validate_uf(self, uf_sigla: str) -> bool:
        """
        Valida se a UF existe

        Args:
            uf_sigla: Sigla da UF

        Returns:
            bool: True se a UF for válida
        """
        try:
            return uf_sigla.upper() in ufbr.list_uf
        except Exception:
            return False

    def validate_codigo_ibge(self, codigo_ibge: str) -> bool:
        """
        Valida formato do código IBGE

        Args:
            codigo_ibge: Código IBGE a validar

        Returns:
            bool: True se o formato for válido
        """
        try:
            return (
                len(codigo_ibge) >= 6
                and codigo_ibge.isdigit()
                and codigo_ibge != "000000"
            )
        except Exception:
            return False


# Instância global do serviço
municipio_service = MunicipioService()