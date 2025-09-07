"""
Cliente robusto para comunicação com a API de financiamento da saúde - papprefeito
"""
import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout, ConnectionError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Nome do arquivo JSON para armazenar os dados da API
DATA_FILE = "data_cache_papprefeito.json"

class APIClient:
    """Cliente robusto para comunicação com a API de financiamento da saúde."""
    
    def __init__(self):
        self.base_url = "https://relatorioaps-prd.saude.gov.br/financiamento/pagamento"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Cria uma sessão HTTP com configurações de retry e timeout."""
        session = requests.Session()
        
        # Configurar estratégia de retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers padrão
        session.headers.update({
            "Accept": "application/json",
            "User-Agent": "papprefeito-ConsultaDados/1.0"
        })
        
        return session
    
    def validar_dados_api(self, dados: Dict[Any, Any]) -> bool:
        """Valida se os dados retornados da API estão no formato esperado."""
        if not isinstance(dados, dict):
            return False
        
        # Verificar se contém pelo menos uma das chaves esperadas
        expected_keys = ['resumosPlanosOrcamentarios', 'pagamentos']
        return any(key in dados for key in expected_keys)

def load_data_from_json() -> Dict[str, Any]:
    """Carrega os dados do arquivo JSON de cache. Retorna um dicionário vazio se o arquivo não existir."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
            
        # Validar dados carregados
        api_client = APIClient()
        if not api_client.validar_dados_api(dados):
            st.warning("⚠️ Dados em cache podem estar corrompidos.")
            return {}
            
        return dados
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.warning("⚠️ Erro ao decodificar o arquivo de cache. O arquivo pode estar corrompido.")
        return {}

def consultar_api(codigo_ibge: str, competencia: str) -> Optional[Dict[str, Any]]:
    """Consulta a API de financiamento da saúde e salva os dados em um arquivo JSON."""
    
    # Validar parâmetros de entrada
    if not codigo_ibge or not competencia:
        st.error("❌ Código IBGE e competência são obrigatórios.")
        return None
    
    if len(codigo_ibge) < 6:
        st.error("❌ Código IBGE deve ter pelo menos 6 dígitos.")
        return None
    
    if len(competencia) != 6 or not competencia.isdigit():
        st.error("❌ Competência deve estar no formato AAAAMM (6 dígitos).")
        return None
    
    # Atualizar session_state
    if 'competencia' in st.session_state:
        st.session_state['competencia'] = competencia

    api_client = APIClient()
    
    params = {
        "unidadeGeografica": "MUNICIPIO",
        "coUf": codigo_ibge[:2],
        "coMunicipio": codigo_ibge[:6],
        "nuParcelaInicio": competencia,
        "nuParcelaFim": competencia,
        "tipoRelatorio": "COMPLETO"
    }
    
    try:
        # Mostrar progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Conectando à API...")
        progress_bar.progress(25)
        
        # Fazer requisição com timeout
        response = api_client.session.get(
            api_client.base_url, 
            params=params, 
            timeout=30,
            verify=True
        )
        
        progress_bar.progress(50)
        status_text.text("📥 Recebendo dados...")
        
        response.raise_for_status()
        dados = response.json()
        
        progress_bar.progress(75)
        status_text.text("✅ Validando dados...")
        
        # Validar dados recebidos
        if not api_client.validar_dados_api(dados):
            st.error("❌ Dados recebidos da API estão em formato inválido.")
            return None
        
        # Verificar se há dados relevantes
        resumos = dados.get('resumosPlanosOrcamentarios', [])
        pagamentos = dados.get('pagamentos', [])
        
        if not resumos and not pagamentos:
            st.warning("⚠️ Nenhum dado encontrado para os parâmetros informados.")
            return None
        
        progress_bar.progress(90)
        status_text.text("💾 Salvando cache...")
        
        # Salvar dados em cache
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        
        progress_bar.progress(100)
        status_text.text("✅ Consulta concluída com sucesso!")
        
        # Limpar elementos de progresso após um breve delay
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"✅ Dados da competência {competencia} para o IBGE {codigo_ibge} consultados com sucesso!")
        return dados
        
    except Timeout:
        st.error("⏱️ Timeout na consulta à API. Tente novamente em alguns minutos.")
        return None
    except ConnectionError:
        st.error("🌐 Erro de conexão. Verifique sua conexão com a internet.")
        return None
    except requests.exceptions.SSLError:
        st.error("🔒 Erro de certificado SSL. Verifique a configuração do servidor.")
        return None
    except RequestException as e:
        st.error(f"❌ Erro na consulta à API: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("❌ Erro ao decodificar resposta da API. Dados podem estar corrompidos.")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        return None