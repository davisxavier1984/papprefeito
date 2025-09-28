/**
 * Componente para input de competência
 */

import React, { useEffect } from 'react';
import { Input, Typography, Space, Button, Tooltip } from 'antd';
import { CalendarOutlined, SyncOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../../services/api';
import { useCanConsult, useMunicipioStore } from '../../stores/municipioStore';
import useConsultarDados from '../../hooks/useConsultarDados';

const { Text } = Typography;

const CompetenciaInput: React.FC = () => {
  const { selectedCompetencia, setSelectedCompetencia } = useMunicipioStore();
  const canConsult = useCanConsult();
  const { consultar } = useConsultarDados();

  // Query para buscar última competência disponível
  const {
    data: ultimaCompetencia,
    isLoading
  } = useQuery({
    queryKey: queryKeys.competencia,
    queryFn: () => apiClient.getUltimaCompetencia(),
    staleTime: 1000 * 60 * 10, // 10 minutos
    retry: 2
  });

  // Auto-fill com última competência se não houver seleção
  useEffect(() => {
    if (ultimaCompetencia?.competencia && !selectedCompetencia) {
      setSelectedCompetencia(ultimaCompetencia.competencia);
    }
  }, [ultimaCompetencia, selectedCompetencia, setSelectedCompetencia]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, ''); // Apenas números
    if (value.length <= 6) {
      setSelectedCompetencia(value);
    }
  };

  const handleUseLatest = () => {
    if (ultimaCompetencia?.competencia) {
      setSelectedCompetencia(ultimaCompetencia.competencia);
    }
  };

  const isValidCompetencia = (competencia: string): boolean => {
    if (competencia.length !== 6) return false;

    const ano = parseInt(competencia.substring(0, 4));
    const mes = parseInt(competencia.substring(4, 6));

    return ano >= 2020 && ano <= 2030 && mes >= 1 && mes <= 12;
  };

  const formatCompetencia = (competencia: string): string => {
    if (competencia.length >= 4) {
      const ano = competencia.substring(0, 4);
      const mes = competencia.substring(4);
      return `${ano}/${mes}`;
    }
    return competencia;
  };

  const formatCompetenciaDisplay = (competencia: string): string => {
    if (competencia.length === 6) {
      const ano = competencia.substring(0, 4);
      const mes = competencia.substring(4, 6);
      const mesNome = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
      ][parseInt(mes) - 1];
      return `${mesNome}/${ano}`;
    }
    return '';
  };

  const isValid = isValidCompetencia(selectedCompetencia);
  const status = selectedCompetencia && !isValid ? 'error' : undefined;

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="small">
      <Text strong>
        <CalendarOutlined /> Competência (AAAAMM):
      </Text>

      <Space.Compact style={{ width: '100%' }}>
        <Input
          id="competencia-input"
          name="competencia"
          placeholder="202401"
          value={selectedCompetencia}
          onChange={handleChange}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && isValidCompetencia(selectedCompetencia) && canConsult) {
              consultar();
            }
          }}
          style={{ flex: 1 }}
          status={status}
          maxLength={6}
          inputMode="numeric"
          allowClear
          suffix={
            selectedCompetencia && (
              <Text type="secondary" style={{ fontSize: '11px' }}>
                {formatCompetencia(selectedCompetencia)}
              </Text>
            )
          }
        />
        <Tooltip title="Usar última competência disponível">
          <Button
            icon={<SyncOutlined />}
            onClick={handleUseLatest}
            loading={isLoading}
            disabled={!ultimaCompetencia}
          />
        </Tooltip>
      </Space.Compact>

      {selectedCompetencia && isValid && (
        <Text type="secondary" style={{ fontSize: '12px' }}>
          📅 {formatCompetenciaDisplay(selectedCompetencia)}
        </Text>
      )}

      {selectedCompetencia && !isValid && (
        <Text type="danger" style={{ fontSize: '12px' }}>
          ❌ Competência inválida. Use o formato AAAAMM (ex: 202401)
        </Text>
      )}

    </Space>
  );
};

export default CompetenciaInput;
