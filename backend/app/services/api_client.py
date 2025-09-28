"""
Serviço de consulta à API externa do governo
Migração da lógica de api_client.py para FastAPI
"""
import httpx
import json
import asyncio
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.schemas import DadosFinanciamento, FinanciamentoParams
from app.utils.logger import logger


class SaudeAPIClient:
    """Cliente para comunicação com a API de financiamento da saúde"""

    def __init__(self):
        self.base_url = settings.SAUDE_API_BASE_URL
        self.timeout = settings.SAUDE_API_TIMEOUT

    def get_latest_competencia(self) -> str:
        """Retorna a última competência disponível no sistema (formato AAAAMM)"""
        hoje = datetime.now()
        # Subtrair um mês (apenas sugestão padrão)
        if hoje.month == 1:
            mes_anterior = datetime(hoje.year - 1, 12, 1)
        else:
            mes_anterior = datetime(hoje.year, hoje.month - 1, 1)

        return mes_anterior.strftime("%Y%m")

    def _validate_response_data(self, dados: Dict[Any, Any]) -> bool:
        """Valida se os dados retornados da API estão no formato esperado"""
        if not isinstance(dados, dict):
            return False

        expected_keys = ['resumosPlanosOrcamentarios', 'pagamentos']
        return any(key in dados for key in expected_keys)

    async def consultar_financiamento(
        self,
        codigo_ibge: str,
        competencia: str
    ) -> Optional[Dict[str, Any]]:
        """
        Consulta a API de financiamento da saúde

        Args:
            codigo_ibge: Código IBGE do município (6 dígitos)
            competencia: Competência no formato AAAAMM

        Returns:
            dict: JSON bruto retornado pela API externa ou None em caso de erro
        """
        # Validar parâmetros
        if not codigo_ibge or not competencia:
            logger.error("Código IBGE e competência são obrigatórios")
            return None

        if len(codigo_ibge) < 6:
            logger.error("Código IBGE deve ter pelo menos 6 dígitos")
            return None

        if len(competencia) != 6 or not competencia.isdigit():
            logger.error("Competência deve estar no formato AAAAMM (6 dígitos)")
            return None

        # Parâmetros da requisição
        params = {
            "unidadeGeografica": "MUNICIPIO",
            # Envia chaves alternativas para maximizar compatibilidade
            "coUf": codigo_ibge[:2],
            "coUfIbge": codigo_ibge[:2],
            "coMunicipio": codigo_ibge[:6],
            "coMunicipioIbge": codigo_ibge[:6],
            "nuParcelaInicio": competencia,
            "nuParcelaFim": competencia,
            "tipoRelatorio": "COMPLETO"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Consultando API para município {codigo_ibge}, competência {competencia}")

                # Configurar headers
                headers = {
                    "Accept": "application/json",
                    "User-Agent": "papprefeito-ConsultaDados/1.0"
                }

                response = await client.get(
                    self.base_url,
                    params=params,
                    headers=headers
                )

                response.raise_for_status()
                dados = response.json()

                # Validar dados recebidos
                if not self._validate_response_data(dados):
                    logger.error("Dados recebidos da API estão em formato inválido")
                    return None

                # Verificar se há dados relevantes
                resumos = dados.get('resumosPlanosOrcamentarios', [])
                pagamentos = dados.get('pagamentos', [])

                if not resumos and not pagamentos:
                    logger.warning("Nenhum dado encontrado para os parâmetros informados")
                    return None

                logger.info(f"Dados consultados com sucesso: {len(resumos)} resumos, {len(pagamentos)} pagamentos")

                # Persistir cache local em JSON (compatível com app atual)
                try:
                    cache_path = settings.DATA_CACHE_FILE
                    abs_path = os.path.abspath(cache_path)
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)
                    logger.info(f"Cache salvo em {abs_path}")
                except Exception as e:
                    logger.warning(f"Falha ao salvar cache local: {str(e)}")

                # Retornar JSON bruto da API externa (completo)
                return dados

        except httpx.TimeoutException:
            logger.error("Timeout na consulta à API")
            return None
        except httpx.ConnectError:
            logger.error("Erro de conexão com a API")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP na consulta à API: {e.response.status_code}")
            return None
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar resposta da API")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na consulta à API: {str(e)}")
            return None

    async def test_connection(self) -> bool:
        """Testa a conectividade com a API externa"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Fazer uma requisição simples para testar conectividade
                response = await client.get(self.base_url, timeout=10)
                return response.status_code == 200
        except Exception:
            return False


# Instância global do cliente
saude_api_client = SaudeAPIClient()
