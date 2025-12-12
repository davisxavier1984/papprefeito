/**
 * Componente: FinancialTable
 * - Tabela editável de financiamento
 * - Coluna "Perda Recurso Mensal" editável
 * - Cálculos reativos
 * - Auto-save com debounce
 */

import React, { useMemo, useState, useEffect } from 'react';
import { Table, Typography, Space, Tag, Card, Row, Col, Statistic, Divider } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMunicipioStore, useUpdatePerdaRecurso } from '../../stores/municipioStore';
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
  const updatePerca = useUpdatePerdaRecurso();
  const { triggerSave, status, isSaving, isSaved, isError } = useAutoSave(2000);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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
      title: 'Perda Recurso Mensal',
      dataIndex: 'perda_recurso_mensal',
      key: 'perda_recurso_mensal',
      align: 'right',
      width: 240,
      render: (_value: number, _record, index) => (
        <CurrencyInput
          id={`perda-recurso-${index}`}
          name={`perda_recurso_mensal_${index}`}
          value={dadosProcessados[index]?.perda_recurso_mensal ?? 0}
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

  // Componente para visualização mobile em cards
  const MobileCardView = () => (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {dadosProcessados.map((item, index) => (
        <Card
          key={index}
          className="shadow-brand"
          style={{
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text strong style={{ fontSize: '16px', color: 'var(--text-primary)' }}>
                {item.recurso}
              </Text>
            </div>

            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic
                  title="Recebido Mensal"
                  value={item.recurso_real}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '14px', color: 'var(--primary-blue)' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Potencial Mensal"
                  value={item.recurso_potencial}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '14px', color: 'var(--success-green)' }}
                />
              </Col>
            </Row>

            <Divider style={{ margin: '8px 0' }} />

            <div>
              <Text type="secondary" style={{ fontSize: '13px', fontWeight: 500 }}>
                Perda Recurso Mensal:
              </Text>
              <div style={{ marginTop: '4px' }}>
                <CurrencyInput
                  id={`perda-recurso-mobile-${index}`}
                  name={`perda_recurso_mensal_mobile_${index}`}
                  value={item.perda_recurso_mensal ?? 0}
                  onCommit={(val) => {
                    const sanitized = Number.isFinite(val) && val >= 0 ? val : 0;
                    updatePerca(index, sanitized);
                    triggerSave();
                  }}
                />
              </div>
            </div>

            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic
                  title="Recebido Anual"
                  value={item.recurso_real_anual}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '13px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Potencial Anual"
                  value={item.recurso_potencial_anual}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '13px' }}
                />
              </Col>
            </Row>

            <div style={{ textAlign: 'center', marginTop: '8px' }}>
              <Tag
                color={item.diferenca > 0 ? 'success' : item.diferenca < 0 ? 'error' : 'default'}
                style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  padding: '4px 12px',
                  borderRadius: '6px'
                }}
              >
                Diferença: {formatCurrency(item.diferenca)}
              </Tag>
            </div>
          </Space>
        </Card>
      ))}
    </Space>
  );

  return (
    <Space direction="vertical" size="small" style={{ width: '100%' }}>
      <Space size="small" style={{ justifyContent: 'space-between', width: '100%' }}>
        <Space size="small">
          <Text type="secondary" style={{ fontSize: '13px' }}>Status:</Text>
          {isSaving && <Tag color="processing">Salvando...</Tag>}
          {isSaved && status === 'saved' && <Tag color="success">Salvo</Tag>}
          {isError && <Tag color="error">Erro ao salvar</Tag>}
          {!isSaving && !isSaved && !isError && <Tag>Pronto</Tag>}
        </Space>
        {!isMobile && (
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {dadosProcessados.length} registros
          </Text>
        )}
      </Space>

      {isMobile ? (
        <MobileCardView />
      ) : (
        <Table
          size="middle"
          bordered
          loading={isLoading}
          columns={columns}
          dataSource={dataSource}
          pagination={false}
          scroll={{ x: 1200 }}
          rowKey="key"
          style={{
            backgroundColor: '#fff',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        />
      )}
    </Space>
  );
};

export default FinancialTable;
