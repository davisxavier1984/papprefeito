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
        # Fallback com lista completa das UFs brasileiras
        ufs_fallback = [
            {'codigo': '12', 'nome': 'Acre', 'sigla': 'AC'},
            {'codigo': '27', 'nome': 'Alagoas', 'sigla': 'AL'},
            {'codigo': '16', 'nome': 'Amapá', 'sigla': 'AP'},
            {'codigo': '13', 'nome': 'Amazonas', 'sigla': 'AM'},
            {'codigo': '29', 'nome': 'Bahia', 'sigla': 'BA'},
            {'codigo': '23', 'nome': 'Ceará', 'sigla': 'CE'},
            {'codigo': '53', 'nome': 'Distrito Federal', 'sigla': 'DF'},
            {'codigo': '32', 'nome': 'Espírito Santo', 'sigla': 'ES'},
            {'codigo': '52', 'nome': 'Goiás', 'sigla': 'GO'},
            {'codigo': '21', 'nome': 'Maranhão', 'sigla': 'MA'},
            {'codigo': '51', 'nome': 'Mato Grosso', 'sigla': 'MT'},
            {'codigo': '50', 'nome': 'Mato Grosso do Sul', 'sigla': 'MS'},
            {'codigo': '31', 'nome': 'Minas Gerais', 'sigla': 'MG'},
            {'codigo': '15', 'nome': 'Pará', 'sigla': 'PA'},
            {'codigo': '25', 'nome': 'Paraíba', 'sigla': 'PB'},
            {'codigo': '41', 'nome': 'Paraná', 'sigla': 'PR'},
            {'codigo': '26', 'nome': 'Pernambuco', 'sigla': 'PE'},
            {'codigo': '22', 'nome': 'Piauí', 'sigla': 'PI'},
            {'codigo': '33', 'nome': 'Rio de Janeiro', 'sigla': 'RJ'},
            {'codigo': '24', 'nome': 'Rio Grande do Norte', 'sigla': 'RN'},
            {'codigo': '43', 'nome': 'Rio Grande do Sul', 'sigla': 'RS'},
            {'codigo': '11', 'nome': 'Rondônia', 'sigla': 'RO'},
            {'codigo': '14', 'nome': 'Roraima', 'sigla': 'RR'},
            {'codigo': '42', 'nome': 'Santa Catarina', 'sigla': 'SC'},
            {'codigo': '35', 'nome': 'São Paulo', 'sigla': 'SP'},
            {'codigo': '28', 'nome': 'Sergipe', 'sigla': 'SE'},
            {'codigo': '17', 'nome': 'Tocantins', 'sigla': 'TO'},
        ]

        try:
            ufs_data = []
            logger.info("Tentando obter UFs da biblioteca pyUFbr...")

            # Primeira tentativa: usar pyUFbr
            ufs_list = ufbr.list_uf
            logger.info(f"pyUFbr retornou {len(ufs_list)} UFs: {list(ufs_list)}")

            for uf_sigla in sorted(ufs_list):
                try:
                    uf_dict = ufbr._get_uf_by_sigla(uf_sigla)
                    # Buscar código no fallback já que pyUFbr não fornece
                    fallback_uf = next((uf for uf in ufs_fallback if uf['sigla'] == uf_sigla), None)
                    codigo = fallback_uf['codigo'] if fallback_uf else '00'

                    ufs_data.append(UF(
                        codigo=codigo,
                        nome=uf_dict['nome'],
                        sigla=uf_dict['sigla']
                    ))
                    logger.debug(f"UF {uf_sigla} processada com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao processar UF {uf_sigla} via pyUFbr: {str(e)}")
                    # Buscar no fallback
                    fallback_uf = next((uf for uf in ufs_fallback if uf['sigla'] == uf_sigla), None)
                    if fallback_uf:
                        ufs_data.append(UF(
                            codigo=fallback_uf['codigo'],
                            nome=fallback_uf['nome'],
                            sigla=fallback_uf['sigla']
                        ))
                        logger.info(f"UF {uf_sigla} adicionada via fallback")

            if ufs_data:
                logger.info(f"Retornando {len(ufs_data)} UFs da biblioteca pyUFbr")
                return ufs_data

        except Exception as e:
            logger.error(f"Erro ao buscar UFs via pyUFbr: {str(e)}")

        # Se chegou aqui, usar o fallback completo
        logger.warning("Usando lista fallback completa de UFs")
        ufs_data = []
        for uf_info in ufs_fallback:
            ufs_data.append(UF(
                codigo=uf_info['codigo'],
                nome=uf_info['nome'],
                sigla=uf_info['sigla']
            ))

        logger.info(f"Retornando {len(ufs_data)} UFs via fallback")
        return ufs_data

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