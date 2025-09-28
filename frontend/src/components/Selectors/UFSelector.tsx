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

  const options = ufs?.map((uf: UF) => ({
    value: uf.sigla,
    label: `${uf.sigla} - ${uf.nome}`
  })) || [];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="small">
      <Text strong>
        <EnvironmentOutlined /> UF (Unidade Federativa):
      </Text>

      <Select
        placeholder="Selecione a UF"
        value={selectedUF || undefined}
        onChange={handleChange}
        style={{ width: '100%' }}
        showSearch
        optionFilterProp="label"
        loading={isLoading}
        notFoundContent={isLoading ? <Spin size="small" /> : 'Nenhuma UF encontrada'}
        status={error ? 'error' : undefined}
      >
        {options.map(option => (
          <Select.Option key={option.value} value={option.value}>
            {option.label}
          </Select.Option>
        ))}
      </Select>

      {error && (
        <Text type="danger" style={{ fontSize: '12px' }}>
          Erro ao carregar UFs. Tente novamente.
        </Text>
      )}
    </Space>
  );
};

export default UFSelector;