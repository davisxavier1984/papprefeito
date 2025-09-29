/**
 * Tipos TypeScript baseados nos modelos Pydantic da API
 */

// Tipos básicos
export interface UF {
  codigo: string;
  nome: string;
  sigla: string;
}

export interface Municipio {
  codigo_ibge: string;
  nome: string;
  uf: string;
  populacao?: number;
}

// Tipos de financiamento
export interface FinanciamentoParams {
  codigo_ibge: string;
  competencia: string;
}

export interface RelatorioPDFRequest {
  codigo_ibge: string;
  competencia: string;
  municipio_nome?: string;
  uf?: string;
}

export interface ResumoPlanoOrcamentario {
  dsPlanoOrcamentario: string;
  vlEfetivoRepasse: number;
  dsFaixaIndiceEquidadeEsfEap?: string;
  qtPopulacao?: number;
}

export interface Pagamento {
  coUf: string;
  coMunicipio: string;
  nuCompetencia: string;
  dsPlanoOrcamentario: string;
  vlEfetivoRepasse: number;
  dsFaixaIndiceEquidadeEsfEap?: string;
  qtPopulacao?: number;
}

export interface DadosFinanciamento {
  resumosPlanosOrcamentarios: ResumoPlanoOrcamentario[];
  pagamentos: Pagamento[];
  metadata?: Record<string, any>;
}

// Tipos para dados editados
export interface MunicipioEditado {
  codigo_ibge: string;
  competencia: string;
  perca_recurso_mensal: number[];
  data_edicao: string;
}

export interface MunicipioEditadoCreate {
  codigo_ibge: string;
  competencia: string;
  perca_recurso_mensal: number[];
}

export interface MunicipioEditadoUpdate {
  perca_recurso_mensal: number[];
}

// Tipos para dados processados (frontend)
export interface DadosProcessados {
  recurso: string;
  recurso_real: number;
  perca_recurso_mensal: number;
  recurso_potencial: number;
  recurso_real_anual: number;
  recurso_potencial_anual: number;
  diferenca: number;
}

export interface ResumoFinanceiro {
  total_perca_mensal: number;
  total_diferenca_anual: number;
  percentual_perda_anual: number;
  total_recebido: number;
}

// Tipos para respostas da API
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ApiError {
  success: false;
  message: string;
  error_code?: string;
  details?: Record<string, any>;
}

// Tipos para estado da aplicação
export interface MunicipioInfo {
  uf: string;
  codigo: string;
  nome: string;
  competencia: string;
}

// Tipos para UI/UX
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface SelectOption {
  value: string;
  label: string;
}

// Tipos para competência
export interface CompetenciaInfo {
  competencia: string;
  ano: string;
  mes: string;
  timestamp: string;
}

// Tipos para validação
export interface ValidationError {
  field: string;
  message: string;
}

// Tipos para o store global
export interface AppState {
  // Seleções atuais
  selectedUF: string;
  selectedMunicipio: Municipio | null;
  selectedCompetencia: string;

  // Dados carregados
  dadosFinanciamento: DadosFinanciamento | null;
  dadosEditados: MunicipioEditado | null;

  // Estados de UI
  isLoading: boolean;
  error: string | null;

  // Dados processados para tabela
  dadosProcessados: DadosProcessados[];
  resumoFinanceiro: ResumoFinanceiro | null;
}

// Tipos para ações do store
export interface AppActions {
  setSelectedUF: (uf: string) => void;
  setSelectedMunicipio: (municipio: Municipio | null) => void;
  setSelectedCompetencia: (competencia: string) => void;
  setDadosFinanciamento: (dados: DadosFinanciamento | null) => void;
  setDadosEditados: (dados: MunicipioEditado | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateDadosProcessados: (dados: DadosProcessados[]) => void;
  updateResumoFinanceiro: (resumo: ResumoFinanceiro) => void;
  resetState: () => void;
  processarDados: () => void;
  calcularResumoFinanceiro: () => void;
}

// Type para o store completo
export type AppStore = AppState & AppActions;

// Tipos utilitários
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
