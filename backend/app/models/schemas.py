"""
Modelos Pydantic para validação de dados
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from pydantic import AliasChoices, ConfigDict
from datetime import datetime

class UF(BaseModel):
    """Modelo para Unidade Federativa"""
    codigo: str
    nome: str
    sigla: str

class Municipio(BaseModel):
    """Modelo para Município"""
    codigo_ibge: str = Field(..., description="Código IBGE do município (6 dígitos)")
    nome: str = Field(..., description="Nome do município")
    uf: str = Field(..., description="Sigla da UF")
    populacao: Optional[int] = Field(None, description="População do município")

class FinanciamentoParams(BaseModel):
    """Parâmetros para consulta de financiamento"""
    codigo_ibge: str = Field(..., min_length=6, max_length=7, description="Código IBGE do município")
    competencia: str = Field(..., min_length=6, max_length=6, description="Competência no formato AAAAMM")

    @validator('competencia')
    def validate_competencia(cls, v):
        if not v.isdigit():
            raise ValueError('Competência deve conter apenas dígitos')

        year = int(v[:4])
        month = int(v[4:])

        if year < 2020 or year > 2030:
            raise ValueError('Ano deve estar entre 2020 e 2030')

        if month < 1 or month > 12:
            raise ValueError('Mês deve estar entre 01 e 12')

        return v

class ResumoPlanoOrcamentario(BaseModel):
    """Modelo para resumo de plano orçamentário"""
    dsPlanoOrcamentario: str = Field(..., description="Descrição do plano orçamentário")
    vlEfetivoRepasse: float = Field(..., description="Valor efetivo do repasse")
    dsFaixaIndiceEquidadeEsfEap: Optional[str] = Field(None, description="Estrato de equidade")
    qtPopulacao: Optional[int] = Field(None, description="Quantidade da população")
    # Ignorar campos extras vindos da API externa
    model_config = ConfigDict(extra='ignore', populate_by_name=True)

class Pagamento(BaseModel):
    """Modelo para dados de pagamento"""
    # Aceita tanto campos locais quanto variações da API externa
    coUf: str = Field(
        ...,
        description="Código da UF",
        validation_alias=AliasChoices("coUf", "coUfIbge")
    )
    coMunicipio: str = Field(
        ...,
        description="Código do município",
        validation_alias=AliasChoices("coMunicipio", "coMunicipioIbge")
    )
    nuCompetencia: str = Field(
        ...,
        description="Competência",
        validation_alias=AliasChoices("nuCompetencia", "nuParcela")
    )
    dsPlanoOrcamentario: Optional[str] = Field(None, description="Descrição do plano orçamentário")
    vlEfetivoRepasse: Optional[float] = Field(None, description="Valor efetivo do repasse")
    dsFaixaIndiceEquidadeEsfEap: Optional[str] = Field(None, description="Estrato de equidade")
    qtPopulacao: Optional[int] = Field(None, description="Quantidade da população")
    # Ignorar demais campos do payload externo
    model_config = ConfigDict(extra='ignore', populate_by_name=True)

class DadosFinanciamento(BaseModel):
    """Modelo para dados completos de financiamento"""
    resumosPlanosOrcamentarios: List[ResumoPlanoOrcamentario] = Field(default_factory=list)
    pagamentos: List[Pagamento] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    model_config = ConfigDict(extra='ignore', populate_by_name=True)

class MunicipioEditado(BaseModel):
    """Modelo para dados editados de município"""
    codigo_ibge: str = Field(..., description="Código IBGE do município")
    competencia: str = Field(..., description="Competência")
    perca_recurso_mensal: List[float] = Field(default_factory=list, description="Lista de perdas mensais por recurso")
    data_edicao: datetime = Field(default_factory=datetime.now, description="Data da última edição")

class MunicipioEditadoCreate(BaseModel):
    """Modelo para criação de dados editados"""
    codigo_ibge: str
    competencia: str
    perca_recurso_mensal: List[float]

class MunicipioEditadoUpdate(BaseModel):
    """Modelo para atualização de dados editados"""
    perca_recurso_mensal: List[float]

class DadosProcessados(BaseModel):
    """Modelo para dados processados com cálculos"""
    recurso: str
    recurso_real: float
    perca_recurso_mensal: float
    recurso_potencial: float
    recurso_real_anual: float
    recurso_potencial_anual: float
    diferenca: float

class ResumoFinanceiro(BaseModel):
    """Modelo para resumo financeiro"""
    total_perca_mensal: float
    total_diferenca_anual: float
    percentual_perda_anual: float
    total_recebido: float


class DetalhamentoPrograma(BaseModel):
    """Modelo para detalhamento de um programa/plano orçamentário"""
    nome: str = Field(..., description="Nome do programa")
    nome_curto: str = Field(..., description="Nome abreviado do programa")
    valor_integral: float = Field(..., description="Valor integral do programa")
    valor_ajuste: float = Field(default=0.0, description="Valor de ajuste")
    valor_desconto: float = Field(default=0.0, description="Valor de desconto (negativo)")
    valor_efetivo: float = Field(..., description="Valor efetivamente recebido")
    percentual_efetivacao: float = Field(..., description="Percentual do valor integral que foi efetivado")
    tem_desconto: bool = Field(default=False, description="Indica se há desconto aplicado")
    ativo: bool = Field(default=True, description="Indica se o programa está ativo (valor > 0)")
    icone: str = Field(default="⚙️", description="Ícone do programa")
    cor_tema: str = Field(default="success", description="Cor temática: success, warning, danger, muted")


class ESBModalidade40h(BaseModel):
    """Detalhamento de ESB Modalidade 40h"""
    credenciadas: int = Field(default=0)
    homologadas: int = Field(default=0)
    modalidade_i: int = Field(default=0, alias="modalidadeI")
    modalidade_ii: int = Field(default=0, alias="modalidadeII")
    model_config = ConfigDict(populate_by_name=True)


class ESBCHDiferenciada(BaseModel):
    """Detalhamento de ESB Carga Horária Diferenciada"""
    credenciadas: int = Field(default=0)
    homologadas: int = Field(default=0)
    modalidade_20h: int = Field(default=0, alias="modalidade20h")
    modalidade_30h: int = Field(default=0, alias="modalidade30h")
    model_config = ConfigDict(populate_by_name=True)


class ESBQuilombolasAssentamentos(BaseModel):
    """Equipes ESB em Quilombolas e Assentamentos"""
    modalidade_i: int = Field(default=0, alias="modalidadeI")
    modalidade_ii: int = Field(default=0, alias="modalidadeII")
    model_config = ConfigDict(populate_by_name=True)


class ESBValores(BaseModel):
    """Valores financeiros das ESB"""
    pagamento: float = Field(default=0.0)
    qualidade: float = Field(default=0.0)
    ch_diferenciada: float = Field(default=0.0, alias="chDiferenciada")
    implantacao: float = Field(default=0.0)
    model_config = ConfigDict(populate_by_name=True)


class ESBDetalhamento(BaseModel):
    """Detalhamento completo de ESB"""
    modalidade40h: ESBModalidade40h = Field(default_factory=ESBModalidade40h)
    ch_diferenciada: ESBCHDiferenciada = Field(default_factory=ESBCHDiferenciada, alias="chDiferenciada")
    quilombolas_assentamentos: ESBQuilombolasAssentamentos = Field(
        default_factory=ESBQuilombolasAssentamentos,
        alias="quilombolasAssentamentos"
    )
    implantacao: int = Field(default=0)
    valores: ESBValores = Field(default_factory=ESBValores)
    model_config = ConfigDict(populate_by_name=True)


class UOMValores(BaseModel):
    """Valores financeiros de UOM"""
    pagamento: float = Field(default=0.0)
    implantacao: float = Field(default=0.0)


class UOMDetalhamento(BaseModel):
    """Detalhamento de Unidade Odontológica Móvel"""
    credenciadas: int = Field(default=0)
    homologadas: int = Field(default=0)
    pagas: int = Field(default=0)
    valores: UOMValores = Field(default_factory=UOMValores)


class CEODetalhamento(BaseModel):
    """Detalhamento de CEO (Centro Especialidades Odontológicas)"""
    municipal: float = Field(default=0.0)
    estadual: float = Field(default=0.0)


class LRPDDetalhamento(BaseModel):
    """Detalhamento de LRPD (Laboratório Regional Prótese Dentária)"""
    municipal: float = Field(default=0.0)
    estadual: float = Field(default=0.0)


class TotaisSaudeBucal(BaseModel):
    """Totais consolidados de Saúde Bucal"""
    vl_total: float = Field(default=0.0, alias="vlTotal")
    qt_total_equipes: int = Field(default=0, alias="qtTotalEquipes")
    model_config = ConfigDict(populate_by_name=True)


class DetalhamentoSaudeBucal(BaseModel):
    """Detalhamento expandido de Saúde Bucal"""
    esb: ESBDetalhamento = Field(default_factory=ESBDetalhamento)
    uom: UOMDetalhamento = Field(default_factory=UOMDetalhamento)
    ceo: CEODetalhamento = Field(default_factory=CEODetalhamento)
    lrpd: LRPDDetalhamento = Field(default_factory=LRPDDetalhamento)
    totais: TotaisSaudeBucal = Field(default_factory=TotaisSaudeBucal)
    model_config = ConfigDict(populate_by_name=True)


class ResumoDetalhado(ResumoFinanceiro):
    """Modelo para resumo financeiro com detalhamento de programas"""
    programas: List[DetalhamentoPrograma] = Field(default_factory=list, description="Detalhamento por programa")
    total_valor_integral: float = Field(default=0.0, description="Soma de todos os valores integrais")
    total_desconto: float = Field(default=0.0, description="Soma de todos os descontos")


class RelatorioPDFRequest(BaseModel):
    """Payload para geração do relatório financeiro em PDF"""
    codigo_ibge: str = Field(..., description="Código IBGE do município")
    competencia: str = Field(..., min_length=6, max_length=6, description="Competência no formato AAAAMM")
    municipio_nome: Optional[str] = Field(None, description="Nome do município para exibição")
    uf: Optional[str] = Field(None, description="Sigla da UF para exibição")

    @validator('codigo_ibge')
    def validate_codigo_ibge(cls, v: str) -> str:
        if not v or not v.isdigit() or len(v) < 6:
            raise ValueError('Código IBGE deve conter ao menos 6 dígitos numéricos')
        return v

    @validator('competencia')
    def validate_competencia(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Competência deve conter apenas dígitos')

        ano = int(v[:4])
        mes = int(v[4:])

        if ano < 2020 or ano > 2030:
            raise ValueError('Ano deve estar entre 2020 e 2030')

        if mes < 1 or mes > 12:
            raise ValueError('Mês deve estar entre 01 e 12')

        return v

class ResponseBase(BaseModel):
    """Modelo base para respostas da API"""
    success: bool = True
    message: str = "Operação realizada com sucesso"
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Modelo para respostas de erro"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
