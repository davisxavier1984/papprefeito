/**
 * Componente para seleção de UF
 */

import React from 'react';
import { Select, Typography, Space, Spin } from 'antd';
import { EnvironmentOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../../services/api';
import { useMunicipioStore } from '../../stores/municipioStore';
import type { UF } from '../../types';

const { Text } = Typography;

// Mapa de nomes oficiais das UFs para garantir label correto
const UF_NOMES: Record<string, string> = {
  AC: 'Acre',
  AL: 'Alagoas',
  AP: 'Amapá',
  AM: 'Amazonas',
  BA: 'Bahia',
  CE: 'Ceará',
  DF: 'Distrito Federal',
  ES: 'Espírito Santo',
  GO: 'Goiás',
  MA: 'Maranhão',
  MT: 'Mato Grosso',
  MS: 'Mato Grosso do Sul',
  MG: 'Minas Gerais',
  PA: 'Pará',
  PB: 'Paraíba',
  PR: 'Paraná',
  PE: 'Pernambuco',
  PI: 'Piauí',
  RJ: 'Rio de Janeiro',
  RN: 'Rio Grande do Norte',
  RS: 'Rio Grande do Sul',
  RO: 'Rondônia',
  RR: 'Roraima',
  SC: 'Santa Catarina',
  SP: 'São Paulo',
  SE: 'Sergipe',
  TO: 'Tocantins',
};

const UFSelector: React.FC = () => {
  const { selectedUF, setSelectedUF } = useMunicipioStore();

  // Query para buscar UFs
  const {
    data: ufs,
    isLoading,
    error
  } = useQuery({
    queryKey: queryKeys.ufs,
    queryFn: () => apiClient.getUFs(),
    staleTime: 1000 * 60 * 60, // 1 hora - UFs não mudam frequentemente
    retry: 2
  });

  const handleChange = (value: string) => {
    setSelectedUF(value);
  };

  const options = ufs?.map((uf: UF) => {
    const sigla = (uf.sigla || '').toUpperCase();
    const nome = UF_NOMES[sigla] || uf.nome || sigla;
    return {
      value: sigla,
      label: `${sigla} - ${nome}`,
    };
  }) || [];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="small">
      <Text strong>
        <EnvironmentOutlined /> UF (Unidade Federativa):
      </Text>

      <Select
        id="uf-selector"
        placeholder="Selecione a UF"
        value={selectedUF || undefined}
        onChange={handleChange}
        style={{ width: '100%' }}
        showSearch
        allowClear
        optionFilterProp="label"
        options={options}
        loading={isLoading}
        notFoundContent={isLoading ? <Spin size="small" /> : 'Nenhuma UF encontrada'}
        status={error ? 'error' : undefined}
        getPopupContainer={() => document.body}
      />

      {error && (
        <Text type="danger" style={{ fontSize: '12px' }}>
          Erro ao carregar UFs. Tente novamente.
        </Text>
      )}
    </Space>
  );
};

export default UFSelector;
