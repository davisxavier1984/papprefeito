"""
Modelos Pydantic para validação de dados
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
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

class Pagamento(BaseModel):
    """Modelo para dados de pagamento"""
    coUf: str = Field(..., description="Código da UF")
    coMunicipio: str = Field(..., description="Código do município")
    nuCompetencia: str = Field(..., description="Competência")
    dsPlanoOrcamentario: str = Field(..., description="Descrição do plano orçamentário")
    vlEfetivoRepasse: float = Field(..., description="Valor efetivo do repasse")
    dsFaixaIndiceEquidadeEsfEap: Optional[str] = Field(None, description="Estrato de equidade")
    qtPopulacao: Optional[int] = Field(None, description="Quantidade da população")

class DadosFinanciamento(BaseModel):
    """Modelo para dados completos de financiamento"""
    resumosPlanosOrcamentarios: List[ResumoPlanoOrcamentario] = Field(default_factory=list)
    pagamentos: List[Pagamento] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

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