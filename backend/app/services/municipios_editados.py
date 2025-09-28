"""
Serviço para gerenciamento de dados editados de municípios
Migração do sistema de arquivos JSON para gestão via API
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.models.schemas import MunicipioEditado, MunicipioEditadoCreate, MunicipioEditadoUpdate
from app.utils.logger import logger


class MunicipioEditadoService:
    """Serviço para gerenciar dados editados de municípios"""

    def __init__(self):
        self.data_file = settings.EDITED_DATA_FILE

    def _load_data(self) -> Dict[str, Any]:
        """Carrega dados do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar dados editados: {str(e)}")
            return {}

    def _save_data(self, data: Dict[str, Any]) -> bool:
        """Salva dados no arquivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados editados: {str(e)}")
            return False

    def _get_municipio_key(self, codigo_ibge: str, competencia: str) -> str:
        """Gera chave única para o município"""
        return f"{codigo_ibge}_{competencia}"

    def get_all_editados(self) -> List[MunicipioEditado]:
        """
        Retorna todos os dados editados

        Returns:
            List[MunicipioEditado]: Lista de municípios editados
        """
        try:
            data = self._load_data()
            editados = []

            for key, value in data.items():
                if '_' in key:
                    codigo_ibge, competencia = key.split('_', 1)
                    editados.append(MunicipioEditado(
                        codigo_ibge=codigo_ibge,
                        competencia=competencia,
                        perca_recurso_mensal=value.get('perca_recurso_mensal', []),
                        data_edicao=datetime.fromisoformat(
                            value.get('data_edicao', datetime.now().isoformat())
                        )
                    ))

            return editados

        except Exception as e:
            logger.error(f"Erro ao buscar dados editados: {str(e)}")
            return []

    def get_editado(self, codigo_ibge: str, competencia: str) -> Optional[MunicipioEditado]:
        """
        Retorna dados editados de um município específico

        Args:
            codigo_ibge: Código IBGE do município
            competencia: Competência

        Returns:
            MunicipioEditado: Dados editados ou None se não encontrado
        """
        try:
            data = self._load_data()
            key = self._get_municipio_key(codigo_ibge, competencia)

            if key in data:
                value = data[key]
                return MunicipioEditado(
                    codigo_ibge=codigo_ibge,
                    competencia=competencia,
                    perca_recurso_mensal=value.get('perca_recurso_mensal', []),
                    data_edicao=datetime.fromisoformat(
                        value.get('data_edicao', datetime.now().isoformat())
                    )
                )

            return None

        except Exception as e:
            logger.error(f"Erro ao buscar dados editados para {codigo_ibge}_{competencia}: {str(e)}")
            return None

    def create_editado(self, municipio_data: MunicipioEditadoCreate) -> Optional[MunicipioEditado]:
        """
        Cria novos dados editados para um município

        Args:
            municipio_data: Dados do município a criar

        Returns:
            MunicipioEditado: Dados criados ou None em caso de erro
        """
        try:
            data = self._load_data()
            key = self._get_municipio_key(municipio_data.codigo_ibge, municipio_data.competencia)

            # Verificar se já existe
            if key in data:
                logger.warning(f"Dados editados já existem para {key}")
                return None

            # Criar novos dados
            now = datetime.now()
            data[key] = {
                'perca_recurso_mensal': municipio_data.perca_recurso_mensal,
                'data_edicao': now.isoformat()
            }

            if self._save_data(data):
                return MunicipioEditado(
                    codigo_ibge=municipio_data.codigo_ibge,
                    competencia=municipio_data.competencia,
                    perca_recurso_mensal=municipio_data.perca_recurso_mensal,
                    data_edicao=now
                )

            return None

        except Exception as e:
            logger.error(f"Erro ao criar dados editados: {str(e)}")
            return None

    def update_editado(
        self,
        codigo_ibge: str,
        competencia: str,
        update_data: MunicipioEditadoUpdate
    ) -> Optional[MunicipioEditado]:
        """
        Atualiza dados editados de um município

        Args:
            codigo_ibge: Código IBGE do município
            competencia: Competência
            update_data: Dados para atualização

        Returns:
            MunicipioEditado: Dados atualizados ou None em caso de erro
        """
        try:
            data = self._load_data()
            key = self._get_municipio_key(codigo_ibge, competencia)

            if key not in data:
                logger.warning(f"Dados editados não encontrados para {key}")
                return None

            # Atualizar dados
            now = datetime.now()
            data[key].update({
                'perca_recurso_mensal': update_data.perca_recurso_mensal,
                'data_edicao': now.isoformat()
            })

            if self._save_data(data):
                return MunicipioEditado(
                    codigo_ibge=codigo_ibge,
                    competencia=competencia,
                    perca_recurso_mensal=update_data.perca_recurso_mensal,
                    data_edicao=now
                )

            return None

        except Exception as e:
            logger.error(f"Erro ao atualizar dados editados: {str(e)}")
            return None

    def delete_editado(self, codigo_ibge: str, competencia: str) -> bool:
        """
        Remove dados editados de um município

        Args:
            codigo_ibge: Código IBGE do município
            competencia: Competência

        Returns:
            bool: True se removido com sucesso
        """
        try:
            data = self._load_data()
            key = self._get_municipio_key(codigo_ibge, competencia)

            if key in data:
                del data[key]
                return self._save_data(data)

            logger.warning(f"Dados editados não encontrados para {key}")
            return False

        except Exception as e:
            logger.error(f"Erro ao deletar dados editados: {str(e)}")
            return False

    def upsert_editado(self, municipio_data: MunicipioEditadoCreate) -> Optional[MunicipioEditado]:
        """
        Cria ou atualiza dados editados (upsert)

        Args:
            municipio_data: Dados do município

        Returns:
            MunicipioEditado: Dados salvos ou None em caso de erro
        """
        try:
            data = self._load_data()
            key = self._get_municipio_key(municipio_data.codigo_ibge, municipio_data.competencia)

            # Criar ou atualizar dados
            now = datetime.now()
            data[key] = {
                'perca_recurso_mensal': municipio_data.perca_recurso_mensal,
                'data_edicao': now.isoformat()
            }

            if self._save_data(data):
                return MunicipioEditado(
                    codigo_ibge=municipio_data.codigo_ibge,
                    competencia=municipio_data.competencia,
                    perca_recurso_mensal=municipio_data.perca_recurso_mensal,
                    data_edicao=now
                )

            return None

        except Exception as e:
            logger.error(f"Erro ao fazer upsert dos dados editados: {str(e)}")
            return None


# Instância global do serviço
municipio_editado_service = MunicipioEditadoService()