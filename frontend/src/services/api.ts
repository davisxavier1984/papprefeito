/**
 * Cliente API para comunicação com o backend FastAPI
 */

import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type {
  UF,
  Municipio,
  DadosFinanciamento,
  MunicipioEditado,
  MunicipioEditadoCreate,
  MunicipioEditadoUpdate,
  FinanciamentoParams,
  CompetenciaInfo,
  ApiError
} from '../types';

// Configuração base da API
const API_BASE_URL = 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 segundos
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para tratar erros globalmente
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        const apiError: ApiError = {
          success: false,
          message: error.response?.data?.detail || error.message || 'Erro na comunicação com a API',
          error_code: error.response?.status?.toString(),
          details: error.response?.data
        };
        return Promise.reject(apiError);
      }
    );
  }

  // ================================
  // ENDPOINTS DE MUNICÍPIOS
  // ================================

  /**
   * Lista todas as UFs do Brasil
   */
  async getUFs(): Promise<UF[]> {
    const response = await this.client.get<UF[]>('/municipios/ufs');
    return response.data;
  }

  /**
   * Lista municípios de uma UF específica
   */
  async getMunicipiosPorUF(uf: string): Promise<Municipio[]> {
    const response = await this.client.get<Municipio[]>(`/municipios/municipios/${uf.toUpperCase()}`);
    return response.data;
  }

  /**
   * Busca município pelo código IBGE
   */
  async getMunicipioPorCodigo(codigoIbge: string): Promise<Municipio> {
    const response = await this.client.get<Municipio>(`/municipios/municipio/codigo/${codigoIbge}`);
    return response.data;
  }

  /**
   * Valida se uma UF existe
   */
  async validarUF(uf: string): Promise<{ uf: string; valid: boolean; message: string }> {
    const response = await this.client.get(`/municipios/validate/uf/${uf}`);
    return response.data;
  }

  /**
   * Valida formato do código IBGE
   */
  async validarCodigoIbge(codigoIbge: string): Promise<{ codigo_ibge: string; valid: boolean; message: string }> {
    const response = await this.client.get(`/municipios/validate/codigo-ibge/${codigoIbge}`);
    return response.data;
  }

  // ================================
  // ENDPOINTS DE FINANCIAMENTO
  // ================================

  /**
   * Obtém a última competência disponível
   */
  async getUltimaCompetencia(): Promise<CompetenciaInfo> {
    const response = await this.client.get<CompetenciaInfo>('/financiamento/competencia/latest');
    return response.data;
  }

  /**
   * Consulta dados de financiamento por GET
   */
  async consultarDadosFinanciamento(
    codigoIbge: string,
    competencia: string,
    forceRefresh = false
  ): Promise<DadosFinanciamento> {
    const params = forceRefresh ? { force_refresh: true } : {};
    const response = await this.client.get<DadosFinanciamento>(
      `/financiamento/dados/${codigoIbge}/${competencia}`,
      { params }
    );
    return response.data;
  }

  /**
   * Consulta dados de financiamento por POST
   */
  async consultarDadosFinanciamentoPOST(params: FinanciamentoParams): Promise<DadosFinanciamento> {
    const response = await this.client.post<DadosFinanciamento>('/financiamento/dados/consultar', params);
    return response.data;
  }

  /**
   * Testa conexão com a API externa do governo
   */
  async testarConexaoAPI(): Promise<{
    connected: boolean;
    api_url: string;
    message: string;
    timestamp: string;
  }> {
    const response = await this.client.get('/financiamento/test-connection');
    return response.data;
  }

  // ================================
  // ENDPOINTS DE DADOS EDITADOS
  // ================================

  /**
   * Lista todos os municípios com dados editados
   */
  async getMunicipiosEditados(): Promise<MunicipioEditado[]> {
    const response = await this.client.get<MunicipioEditado[]>('/municipios-editados/');
    return response.data;
  }

  /**
   * Obtém dados editados de um município específico
   */
  async getMunicipioEditado(codigoIbge: string, competencia: string): Promise<MunicipioEditado> {
    const response = await this.client.get<MunicipioEditado>(
      `/municipios-editados/${codigoIbge}/${competencia}`
    );
    return response.data;
  }

  /**
   * Cria novos dados editados para um município
   */
  async criarMunicipioEditado(dados: MunicipioEditadoCreate): Promise<MunicipioEditado> {
    const response = await this.client.post<MunicipioEditado>('/municipios-editados/', dados);
    return response.data;
  }

  /**
   * Atualiza dados editados de um município
   */
  async atualizarMunicipioEditado(
    codigoIbge: string,
    competencia: string,
    dados: MunicipioEditadoUpdate
  ): Promise<MunicipioEditado> {
    const response = await this.client.put<MunicipioEditado>(
      `/municipios-editados/${codigoIbge}/${competencia}`,
      dados
    );
    return response.data;
  }

  /**
   * Remove dados editados de um município
   */
  async deletarMunicipioEditado(codigoIbge: string, competencia: string): Promise<{
    message: string;
    codigo_ibge: string;
    competencia: string;
  }> {
    const response = await this.client.delete(`/municipios-editados/${codigoIbge}/${competencia}`);
    return response.data;
  }

  /**
   * Cria ou atualiza dados editados (upsert)
   */
  async upsertMunicipioEditado(dados: MunicipioEditadoCreate): Promise<MunicipioEditado> {
    const response = await this.client.post<MunicipioEditado>('/municipios-editados/upsert', dados);
    return response.data;
  }

  // ================================
  // MÉTODOS AUXILIARES
  // ================================

  /**
   * Testa conectividade geral da API
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Obtém informações gerais da API
   */
  async getApiInfo(): Promise<{
    message: string;
    version: string;
    docs: string;
  }> {
    const response = await this.client.get('/');
    return response.data;
  }
}

// Instância singleton do cliente API
export const apiClient = new ApiClient();

// Exportar classe para uso em testes ou instâncias customizadas
export { ApiClient };

// ================================
// HOOKS PARA REACT QUERY
// ================================

/**
 * Chaves para React Query cache
 */
export const queryKeys = {
  ufs: ['ufs'] as const,
  municipios: (uf: string) => ['municipios', uf] as const,
  municipio: (codigo: string) => ['municipio', codigo] as const,
  financiamento: (codigo: string, competencia: string) => ['financiamento', codigo, competencia] as const,
  competencia: ['competencia', 'latest'] as const,
  editados: ['municipios-editados'] as const,
  editado: (codigo: string, competencia: string) => ['municipio-editado', codigo, competencia] as const,
} as const;