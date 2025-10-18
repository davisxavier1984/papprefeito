import { Card, Alert, Space, Statistic, Row, Col, Typography, Divider } from 'antd';
import {
  WarningOutlined,
  BulbOutlined,
  DollarOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import type { DetalhamentoPrograma } from '../../types';

const { Text, Title } = Typography;

interface AnaliseBoxProps {
  programas: DetalhamentoPrograma[];
}

export const AnaliseBox: React.FC<AnaliseBoxProps> = ({ programas }) => {
  // Calcular totais
  const totalDescontos = programas.reduce((acc, p) => {
    return acc + Math.abs(p.vlDesconto || 0);
  }, 0);

  const totalRepasse = programas.reduce((acc, p) => {
    return acc + p.vlEfetivoRepasse;
  }, 0);

  // Coletar todas as oportunidades
  const todasOportunidades = programas.flatMap((p) => p.oportunidades || []);

  // Coletar todos os alertas
  const todosAlertas = programas.flatMap((p) => p.alertas || []);

  // Contar programas por status
  const programasAtivos = programas.filter((p) => p.status === 'ok').length;
  const programasComDesconto = programas.filter((p) => p.status === 'desconto').length;
  const programasComAlerta = programas.filter((p) => p.status === 'alerta').length;
  const programasInativos = programas.filter((p) => p.status === 'inativo').length;

  // Formatar valor em BRL
  const formatarValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(valor);
  };

  return (
    <div style={{ marginBottom: '24px' }}>
      <Card
        style={{
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        }}
        bodyStyle={{ padding: '24px' }}
      >
        <Title level={5} style={{ marginBottom: '16px' }}>
          📈 Análise Consolidada
        </Title>

        {/* Estatísticas */}
        <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
          <Col xs={12} sm={6}>
            <Statistic
              title="Total Repasse"
              value={totalRepasse}
              formatter={(value) => formatarValor(value as number)}
              prefix={<DollarOutlined />}
              valueStyle={{ fontSize: '18px', color: '#22c55e' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="Total Descontos"
              value={totalDescontos}
              formatter={(value) => formatarValor(value as number)}
              prefix={<WarningOutlined />}
              valueStyle={{ fontSize: '18px', color: '#ef4444' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="Programas Ativos"
              value={programasAtivos}
              suffix={`/ ${programas.length}`}
              prefix={<TeamOutlined />}
              valueStyle={{ fontSize: '18px', color: '#0ea5e9' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="Oportunidades"
              value={todasOportunidades.length}
              prefix={<BulbOutlined />}
              valueStyle={{ fontSize: '18px', color: '#f59e0b' }}
            />
          </Col>
        </Row>

        <Divider style={{ margin: '16px 0' }} />

        {/* Resumo de Status */}
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ fontSize: '13px', color: '#475569', display: 'block', marginBottom: '8px' }}>
            Status dos Programas:
          </Text>
          <Space size="small" wrap>
            {programasAtivos > 0 && (
              <Text style={{ fontSize: '12px' }}>
                ✓ {programasAtivos} ativo{programasAtivos > 1 ? 's' : ''}
              </Text>
            )}
            {programasComDesconto > 0 && (
              <Text style={{ fontSize: '12px', color: '#f59e0b' }}>
                ⚠️ {programasComDesconto} com desconto
              </Text>
            )}
            {programasComAlerta > 0 && (
              <Text style={{ fontSize: '12px', color: '#ef4444' }}>
                ⚠️ {programasComAlerta} com alerta
              </Text>
            )}
            {programasInativos > 0 && (
              <Text style={{ fontSize: '12px', color: '#64748b' }}>
                ❌ {programasInativos} inativo{programasInativos > 1 ? 's' : ''}
              </Text>
            )}
          </Space>
        </div>

        {/* Alertas */}
        {todosAlertas.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <Alert
              message="Pontos de Atenção"
              description={
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  {todosAlertas.map((alerta, index) => (
                    <li key={index} style={{ fontSize: '12px', marginBottom: '4px' }}>
                      {alerta}
                    </li>
                  ))}
                </ul>
              }
              type="warning"
              showIcon
              icon={<WarningOutlined />}
            />
          </div>
        )}

        {/* Oportunidades */}
        {todasOportunidades.length > 0 && (
          <div>
            <Alert
              message="Oportunidades de Expansão"
              description={
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  {todasOportunidades.slice(0, 5).map((oportunidade, index) => (
                    <li key={index} style={{ fontSize: '12px', marginBottom: '4px' }}>
                      {oportunidade}
                    </li>
                  ))}
                  {todasOportunidades.length > 5 && (
                    <li style={{ fontSize: '12px', color: '#64748b' }}>
                      ... e mais {todasOportunidades.length - 5} oportunidades
                    </li>
                  )}
                </ul>
              }
              type="info"
              showIcon
              icon={<BulbOutlined />}
            />
          </div>
        )}

        {/* Mensagem se tudo estiver ok */}
        {todosAlertas.length === 0 && todasOportunidades.length === 0 && totalDescontos === 0 && (
          <Alert
            message="Tudo em ordem!"
            description="Todos os programas estão funcionando adequadamente sem alertas ou descontos."
            type="success"
            showIcon
          />
        )}
      </Card>
    </div>
  );
};
