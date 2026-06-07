/**
 * Componente: MetricsCards
 * - Exibe métricas agregadas derivadas da tabela
 */

import React from 'react';
import { Card, Col, Row, Statistic, Tag, Space } from 'antd';
import { ArrowDownOutlined, PieChartOutlined, RiseOutlined, CreditCardOutlined } from '@ant-design/icons';
import { useMunicipioStore } from '../../stores/municipioStore';

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
});

const percentFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'percent',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const MetricsCards: React.FC = () => {
  const { resumoFinanceiro } = useMunicipioStore();

  if (!resumoFinanceiro) return null;

  const {
    total_perda_mensal,
    total_diferenca_anual,
    percentual_perda_anual,
    total_recebido,
  } = resumoFinanceiro;

  const isPerda = Number(total_diferenca_anual) > 0;
  const lossTag = isPerda ? (
    <Tag color="red" icon={<ArrowDownOutlined />}>Perda</Tag>
  ) : (
    <Tag>Estável</Tag>
  );

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} md={12} lg={6}>
        <Card
          className="shadow-brand"
          style={{
            background: 'var(--tint-danger-bg)',
            border: '1px solid var(--tint-danger-border)',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                backgroundColor: '#ef4444',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <ArrowDownOutlined style={{ color: '#fff', fontSize: '14px' }} />
              </div>
              <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--tint-danger-text)' }}>
                Perda Mensal Total
              </span>
            </div>
            <Statistic
              value={Number(total_perda_mensal) || 0}
              formatter={(v) => <span style={{ color: 'var(--tint-danger-strong)', fontWeight: 700 }}>{currencyFormatter.format(Number(v))}</span>}
              style={{ margin: 0 }}
            />
          </Space>
        </Card>
      </Col>

      <Col xs={24} sm={12} md={12} lg={6}>
        <Card
          className="shadow-brand"
          style={{
            background: isPerda ? 'var(--tint-danger-bg)' : 'var(--tint-success-bg)',
            border: `1px solid ${isPerda ? 'var(--tint-danger-border)' : 'var(--tint-success-border)'}`,
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  backgroundColor: isPerda ? '#ef4444' : '#22c55e',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <RiseOutlined style={{ color: '#fff', fontSize: '14px' }} />
                </div>
                <span style={{ fontSize: '14px', fontWeight: 500, color: isPerda ? 'var(--tint-danger-text)' : 'var(--tint-success-text)' }}>
                  Diferença Anual
                </span>
              </div>
              {lossTag}
            </div>
            <Statistic
              value={Number(total_diferenca_anual) || 0}
              formatter={(v) => <span style={{ color: isPerda ? 'var(--tint-danger-strong)' : 'var(--tint-success-strong)', fontWeight: 700 }}>{currencyFormatter.format(Number(v))}</span>}
              style={{ margin: 0 }}
            />
          </Space>
        </Card>
      </Col>

      <Col xs={24} sm={12} md={12} lg={6}>
        <Card
          className="shadow-brand"
          style={{
            background: 'var(--tint-info-bg)',
            border: '1px solid var(--tint-info-border)',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                backgroundColor: 'var(--primary-blue)',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <PieChartOutlined style={{ color: '#fff', fontSize: '14px' }} />
              </div>
              <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--tint-info-text)' }}>
                Percentual de Perda
              </span>
            </div>
            <Statistic
              value={(Number(percentual_perda_anual) || 0) / 100}
              formatter={(v) => <span style={{ color: 'var(--tint-info-strong)', fontWeight: 700 }}>{percentFormatter.format(Number(v))}</span>}
              style={{ margin: 0 }}
            />
          </Space>
        </Card>
      </Col>

      <Col xs={24} sm={12} md={12} lg={6}>
        <Card
          className="shadow-brand"
          style={{
            background: 'var(--tint-success-bg)',
            border: '1px solid var(--tint-success-border)',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                backgroundColor: '#22c55e',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <CreditCardOutlined style={{ color: '#fff', fontSize: '14px' }} />
              </div>
              <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--tint-success-text)' }}>
                Total Recebido
              </span>
            </div>
            <Statistic
              value={Number(total_recebido) || 0}
              formatter={(v) => <span style={{ color: 'var(--tint-success-strong)', fontWeight: 700 }}>{currencyFormatter.format(Number(v))}</span>}
              style={{ margin: 0 }}
            />
          </Space>
        </Card>
      </Col>
    </Row>
  );
};

export default MetricsCards;
