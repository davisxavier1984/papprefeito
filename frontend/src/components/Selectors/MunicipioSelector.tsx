/**
 * Componente para seleção de município
 */

import React from 'react';
import { Select, Typography, Space, Spin } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../../services/api';
import { useMunicipioStore } from '../../stores/municipioStore';
import type { Municipio } from '../../types';

const { Text } = Typography;

const MunicipioSelector: React.FC = () => {
  const { selectedUF, selectedMunicipio, setSelectedMunicipio } = useMunicipioStore();

  // Query para buscar municípios da UF selecionada
  const {
    data: municipios,
    isLoading,
    error
  } = useQuery({
    queryKey: queryKeys.municipios(selectedUF),
    queryFn: () => apiClient.getMunicipiosPorUF(selectedUF),
    enabled: !!selectedUF, // Só executa se UF estiver selecionada
    staleTime: 1000 * 60 * 30, // 30 minutos
    retry: 2
  });

  const handleChange = (value: string) => {
    const municipio = municipios?.find(m => m.codigo_ibge === value);
    setSelectedMunicipio(municipio || null);
  };

  const options = municipios?.map((municipio: Municipio) => ({
    value: municipio.codigo_ibge,
    label: municipio.populacao
      ? `${municipio.nome} (Pop: ${municipio.populacao.toLocaleString('pt-BR')})`
      : `${municipio.nome}`,
  })) || [];

  const isDisabled = !selectedUF;

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="small">
      <Text strong>
        <HomeOutlined /> Município:
      </Text>

      <Select
        placeholder={isDisabled ? "Selecione primeiro a UF" : "Selecione o município"}
        value={selectedMunicipio?.codigo_ibge || undefined}
        onChange={handleChange}
        style={{ width: '100%' }}
        showSearch
        allowClear
        optionFilterProp="label"
        options={options}
        loading={isLoading}
        disabled={isDisabled}
        notFoundContent={
          isLoading ? (
            <Spin size="small" />
          ) : isDisabled ? (
            'Selecione primeiro a UF'
          ) : (
            'Nenhum município encontrado'
          )
        }
        status={error ? 'error' : undefined}
      />

      {error && (
        <Text type="danger" style={{ fontSize: '12px' }}>
          Erro ao carregar municípios. Tente novamente.
        </Text>
      )}

      {selectedMunicipio && (
        <Space style={{ marginTop: 4 }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Código IBGE: {selectedMunicipio.codigo_ibge}
          </Text>
          {selectedMunicipio.populacao && (
            <Text type="secondary" style={{ fontSize: '12px' }}>
              | Pop: {selectedMunicipio.populacao.toLocaleString()}
            </Text>
          )}
        </Space>
      )}
    </Space>
  );
};

export default MunicipioSelector;
