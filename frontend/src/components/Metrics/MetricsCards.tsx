/**
 * Componente: MetricsCards
 * - Exibe métricas agregadas derivadas da tabela
 */

import React from 'react';
import { Card, Col, Row, Statistic, Tag } from 'antd';
import { ArrowDownOutlined, ArrowUpOutlined, DollarOutlined, PieChartOutlined } from '@ant-design/icons';
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
    total_perca_mensal,
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
      <Col xs={24} md={12} lg={6}>
        <Card>
          <Statistic
            title="💸 Total Perca Mensal"
            value={Number(total_perca_mensal) || 0}
            formatter={(v) => <span>{currencyFormatter.format(Number(v))}</span>}
            prefix={<ArrowDownOutlined style={{ color: '#cf1322' }} />}
          />
        </Card>
      </Col>
      <Col xs={24} md={12} lg={6}>
        <Card>
          <Statistic
            title="📊 Diferença Anual Total"
            value={Number(total_diferenca_anual) || 0}
            formatter={(v) => <span>{currencyFormatter.format(Number(v))}</span>}
            prefix={isPerda ? <ArrowDownOutlined style={{ color: '#cf1322' }} /> : undefined}
            suffix={lossTag}
          />
        </Card>
      </Col>
      <Col xs={24} md={12} lg={6}>
        <Card>
          <Statistic
            title="📈 % Perda Anual"
            value={(Number(percentual_perda_anual) || 0) / 100}
            formatter={(v) => <span>{percentFormatter.format(Number(v))}</span>}
            prefix={<PieChartOutlined style={{ color: '#722ed1' }} />}
          />
        </Card>
      </Col>
      <Col xs={24} md={12} lg={6}>
        <Card>
          <Statistic
            title="💰 Valor Total Recebido (Mensal)"
            value={Number(total_recebido) || 0}
            formatter={(v) => <span>{currencyFormatter.format(Number(v))}</span>}
            prefix={<DollarOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
      </Col>
    </Row>
  );
};

export default MetricsCards;
