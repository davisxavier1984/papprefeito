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
  vlIntegral?: number;
  vlAjuste?: number;
  vlDesconto?: number;
  vlEfetivoRepasse: number;
  vlImplantacao?: number;
  vlAjusteImplantacao?: number;
  vlDescontoImplantacao?: number;
  vlTotalImplantacao?: number;
  dsFaixaIndiceEquidadeEsfEap?: string;
  qtPopulacao?: number;
}

export interface DadosPagamento {
  // Informações gerais
  coUfIbge: string;
  sgUf: string;
  noMunicipio: string;
  coMunicipioIbge: string;
  nuCompCnes: string;
  nuParcela: string;

  // eSF - Equipes de Saúde da Família
  dsFaixaIndiceEquidadeEsfEap?: string;
  dsClassificacaoVinculoEsfEap?: string;
  dsClassificacaoQualidadeEsfEap?: string;
  qtEsfCredenciado?: number;
  qtEsfHomologado?: number;
  qtEsfTotalPgto?: number;
  qtEsf100pcPgto?: number;
  qtEsf75pcPgto?: number;
  qtEsf50pcPgto?: number;
  qtEsf25pcPgto?: number;
  vlFixoEsf?: number;
  vlVinculoEsf?: number;
  vlQualidadeEsf?: number;
  vlTotalEsf?: number;
  vlPagamentoImplantacaoEsf?: number;
  qtTetoEsf?: number;

  // eAP - Equipes de Atenção Primária
  qtEapCredenciadas?: number;
  qtEapHomologado?: number;
  qtEapTotalPgto?: number;
  qtEap20hCompletas?: number;
  qtEap20hIncompletas?: number;
  qtEap30hCompletas?: number;
  qtEap30hIncompletas?: number;
  vlFixoEap?: number;
  vlVinculoEap?: number;
  vlQualidadeEap?: number;
  vlTotalEap?: number;
  vlPagamentoImplantacaoEap?: number;
  qtTetoEap?: number;

  // eMulti - Equipes Multiprofissionais
  dsClassificacaoQualidadeEmulti?: string;
  qtEmultiCredenciadas?: number;
  qtEmultiHomologado?: number;
  qtEmultiPagas?: number;
  qtEmultiPagamentoAmpliada?: number;
  qtEmultiPagamentoIntermunicipal?: number;
  qtEmultiPagamentoComplementar?: number;
  qtEmultiPagamentoEstrategica?: number;
  qtEmultiPagasAtendRemoto?: number;
  vlPagamentoEmultiAtendimentoRemoto?: number;
  vlPagamentoEmultiCusteio?: number;
  vlPagamentoEmultiQualidade?: number;
  vlTotalEmulti?: number;
  vlPagamentoEmultiImplantacao?: number;
  qtTetoEmultiAmpliadaIntermunicipal?: number;
  qtTetoEmultiAmpliada?: number;
  qtTetoEmultiComplementar?: number;
  qtTetoEmultiEstrategica?: number;

  // Saúde Bucal
  qtSb40hCredenciada?: number;
  qtSb40hDifCredenciada?: number;
  qtSb40hHomologado?: number;
  qtSbChDifHomologado?: number;
  qtSbPagamentoModalidadeI?: number;
  qtSbPagamentoModalidadeII?: number;
  qtSbPagamentoDifModalidade20Horas?: number;
  qtSbPagamentoDifModalidade30Horas?: number;
  qtSbEquipeImplantacao?: number;
  qtSbEqpQuilombAssentModalI?: number;
  qtSbEqpQuilombAssentModalII?: number;
  vlPagamentoEsb40h?: number;
  vlPagamentoImplantacaoEsb40h?: number;
  vlPagamentoEsbChDiferenciada?: number;
  vlPagamentoEsb40hQualidade?: number;
  vlPagamentoCeoMunicipal?: number;
  vlPagamentoCeoEstadual?: number;
  vlPagamentoLrpdMunicipal?: number;
  vlPagamentoLrpdEstadual?: number;
  qtTetoSb40h?: number;
  qtTetoSbChDif?: number;

  // ACS - Agentes Comunitários de Saúde
  qtTetoAcs?: number;
  qtAcsDiretoCredenciado?: number;
  qtAcsDiretoPgto?: number;
  vlPagamentoAcsDireto?: number;
  vlPagamentoParcelaExtraAcsDireto?: number;
  vlTotalAcsDireto?: number;
  qtAcsIndiretoCredenciado?: number;
  qtAcsIndiretoPgto?: number;
  vlPagamentoAcsIndireto?: number;
  vlPagamentoParcelaExtraAcsIndireto?: number;
  vlTotalAcsIndireto?: number;

  // Outros programas
  qtUomCredenciada?: number;
  qtUomHomologado?: number;
  qtUomPgto?: number;
  vlPagamentoUom?: number;
  vlPagamentoUomImplantacao?: number;

  qtIafCredenciado?: number;
  qtIafHomologado?: number;
  qtIafPgto?: number;
  vlPagamentoIaf?: number;

  qtAcademiaSaudeCredenciado?: number;
  qtAcademiaSaudeHomologado?: number;
  qtAcademiaSaudePgto?: number;
  qtAcademiaSaudeDescredenciamento?: number;
  vlPagamentoAcademia?: number;

  // SESB - Serviço de Especialidades em Saúde Bucal
  vlPagamentoSesb?: number;
  vlPagamentoDesempenhoSesb?: number;
  vlTotalPagamentoSesb?: number;

  // População e per capita
  qtPopulacao?: number;
  nuAnoRefPopulacaoIbge?: number;
  vlPagamentoIncentivoPopulacional?: number;
  vlPagamentoManutencaoPgto?: number;
  vlPagamentoIncentivoTransicao?: number;

  // Outros campos
  [key: string]: any;
}

export interface Pagamento extends DadosPagamento {
  // Mantendo compatibilidade com interface antiga
  coUf?: string;
  coMunicipio?: string;
  nuCompetencia?: string;
  dsPlanoOrcamentario?: string;
  vlEfetivoRepasse?: number;
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

// Tipos para detalhamento de programas
export type StatusPrograma = 'ok' | 'desconto' | 'alerta' | 'inativo' | 'oportunidade';

export interface ComponenteValor {
  nome: string;
  valor: number;
}

export interface QuantidadesPrograma {
  credenciados?: number;
  homologados?: number;
  pagos?: number;
  teto?: number;
  percentual?: number;
  detalhes?: string;
}

export interface DetalhamentoPrograma {
  codigo: string; // Identificador único (esf, sb, emulti, acs, demais, percapita)
  nome: string;
  icone: string;
  cor: string;

  // Quantidades
  quantidades?: QuantidadesPrograma;
  quantidadesSecundarias?: QuantidadesPrograma; // Para eAP, CH diferenciada, etc

  // Valores financeiros
  vlIntegral?: number;
  vlDesconto?: number;
  percentualDesconto?: number;
  vlEfetivoRepasse: number;
  componentesValor?: ComponenteValor[];

  // Status e mensagens
  status: StatusPrograma;
  badge: string;
  alertas?: string[];
  oportunidades?: string[];

  // Metadados
  populacao?: number;
  anoReferencia?: number;
  perCapitaMensal?: number;

  // Detalhamento específico (para Saúde Bucal expandida)
  detalhamentoSaudeBucal?: DetalhamentoSaudeBucal;
}

// Detalhamento expandido para Saúde Bucal
export interface DetalhamentoSaudeBucal {
  esb: {
    modalidade40h: {
      credenciadas: number;
      homologadas: number;
      modalidadeI: number;
      modalidadeII: number;
    };
    chDiferenciada: {
      credenciadas: number;
      homologadas: number;
      modalidade20h: number;
      modalidade30h: number;
    };
    quilombolasAssentamentos: {
      modalidadeI: number;
      modalidadeII: number;
    };
    implantacao: number;
    valores: {
      pagamento: number;
      qualidade: number;
      chDiferenciada: number;
      implantacao: number;
    };
  };
  uom: {
    credenciadas: number;
    homologadas: number;
    pagas: number;
    valores: {
      pagamento: number;
      implantacao: number;
    };
  };
  ceo: {
    municipal: number;
    estadual: number;
  };
  lrpd: {
    municipal: number;
    estadual: number;
  };
  totais: {
    vlTotal: number;
    qtTotalEquipes: number;
  };
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

  // Dados processados para cards de programas
  dadosProgramas: DetalhamentoPrograma[];
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
  updateDadosProgramas: (programas: DetalhamentoPrograma[]) => void;
  resetState: () => void;
  processarDados: () => void;
  calcularResumoFinanceiro: () => void;
  processarProgramas: () => void;
}

// Type para o store completo
export type AppStore = AppState & AppActions;

// Tipos utilitários
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
