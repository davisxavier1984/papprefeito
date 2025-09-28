/**
 * Componente: FinancialTable
 * - Tabela editável de financiamento
 * - Coluna "Perca Recurso Mensal" editável
 * - Cálculos reativos
 * - Auto-save com debounce
 */

import React, { useMemo } from 'react';
import { Table, Typography, Space, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMunicipioStore, useUpdatePercaRecurso } from '../../stores/municipioStore';
import type { DadosProcessados } from '../../types';
import useAutoSave from '../../hooks/useAutoSave';
import CurrencyInput from '../inputs/CurrencyInput';

const { Text } = Typography;

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
});

const formatCurrency = (value: number) => currencyFormatter.format(value);

const FinancialTable: React.FC = () => {
  const { dadosProcessados, isLoading } = useMunicipioStore();
  const updatePerca = useUpdatePercaRecurso();
  const { triggerSave, status, isSaving, isSaved, isError } = useAutoSave(2000);

  const columns: ColumnsType<DadosProcessados & { key: number }> = useMemo(() => [
    {
      title: 'Recurso',
      dataIndex: 'recurso',
      key: 'recurso',
      width: 240,
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Recebido Mensal',
      dataIndex: 'recurso_real',
      key: 'recurso_real',
      align: 'right',
      width: 160,
      render: (value: number) => <Text>{formatCurrency(value)}</Text>,
    },
    {
      title: 'Perca Recurso Mensal',
      dataIndex: 'perca_recurso_mensal',
      key: 'perca_recurso_mensal',
      align: 'right',
      width: 240,
      render: (_value: number, _record, index) => (
        <CurrencyInput
          value={dadosProcessados[index]?.perca_recurso_mensal ?? 0}
          onCommit={(val) => {
            const sanitized = Number.isFinite(val) && val >= 0 ? val : 0;
            updatePerca(index, sanitized);
            triggerSave();
          }}
        />
      ),
    },
    {
      title: 'Potencial Mensal',
      dataIndex: 'recurso_potencial',
      key: 'recurso_potencial',
      align: 'right',
      width: 160,
      render: (value: number) => <Text>{formatCurrency(value)}</Text>,
    },
    {
      title: 'Recebido Anual',
      dataIndex: 'recurso_real_anual',
      key: 'recurso_real_anual',
      align: 'right',
      width: 160,
      render: (value: number) => <Text>{formatCurrency(value)}</Text>,
    },
    {
      title: 'Potencial Anual',
      dataIndex: 'recurso_potencial_anual',
      key: 'recurso_potencial_anual',
      align: 'right',
      width: 170,
      render: (value: number) => <Text>{formatCurrency(value)}</Text>,
    },
    {
      title: 'Diferença Anual',
      dataIndex: 'diferenca',
      key: 'diferenca',
      align: 'right',
      width: 160,
      render: (value: number) => (
        <Text type={value > 0 ? 'success' : value < 0 ? 'danger' : undefined}>
          {formatCurrency(value)}
        </Text>
      ),
    },
  ], [dadosProcessados, triggerSave, updatePerca]);

  const dataSource = useMemo(
    () => dadosProcessados.map((row, idx) => ({ key: idx, ...row })),
    [dadosProcessados]
  );

  return (
    <Space direction="vertical" size="small" style={{ width: '100%' }}>
      <Space size="small">
        <Text type="secondary">Status:</Text>
        {isSaving && <Tag color="processing">Salvando...</Tag>}
        {isSaved && status === 'saved' && <Tag color="success">Salvo</Tag>}
        {isError && <Tag color="error">Erro ao salvar</Tag>}
        {!isSaving && !isSaved && !isError && <Tag>Pronto</Tag>}
      </Space>

      <Table
        size="middle"
        bordered
        loading={isLoading}
        columns={columns}
        dataSource={dataSource}
        pagination={false}
        scroll={{ x: true }}
        rowKey="key"
      />
    </Space>
  );
};

export default FinancialTable;
