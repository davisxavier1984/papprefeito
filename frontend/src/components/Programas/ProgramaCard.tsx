import { Card, Tag, Alert, Divider, Space, Typography, Row, Col } from 'antd';
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  BulbOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import type { DetalhamentoPrograma } from '../../types';
import { ProgressBar } from './ProgressBar';

const { Text, Title } = Typography;

interface ProgramaCardProps {
  programa: DetalhamentoPrograma;
}

export const ProgramaCard: React.FC<ProgramaCardProps> = ({ programa }) => {
  // Determinar ícone do badge baseado no status
  const getBadgeIcon = () => {
    switch (programa.status) {
      case 'ok':
        return <CheckCircleOutlined />;
      case 'desconto':
        return <WarningOutlined />;
      case 'alerta':
        return <ExclamationCircleOutlined />;
      case 'inativo':
        return <CloseCircleOutlined />;
      case 'oportunidade':
        return <BulbOutlined />;
      default:
        return <CheckCircleOutlined />;
    }
  };

  // Determinar cor do badge
  const getBadgeColor = () => {
    switch (programa.status) {
      case 'ok':
        return 'success';
      case 'desconto':
        return 'warning';
      case 'alerta':
        return 'error';
      case 'inativo':
        return 'default';
      case 'oportunidade':
        return 'processing';
      default:
        return 'success';
    }
  };

  // Formatar valor em BRL
  const formatarValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(valor);
  };

  return (
    <Card
      style={{
        height: '100%',
        borderRadius: '12px',
        borderLeft: `4px solid ${programa.cor}`,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      }}
      styles={{ body: { padding: '20px' } }}
    >
      {/* Header: Nome + Ícone + Badge */}
      <div style={{ marginBottom: '16px' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
            <Title
              level={5}
              style={{
                margin: 0,
                fontSize: '16px',
                fontWeight: 600,
                color: '#1e293b',
              }}
            >
              <span style={{ marginRight: '8px' }}>{programa.icone}</span>
              {programa.nome}
            </Title>
          </div>
          <Tag icon={getBadgeIcon()} color={getBadgeColor()}>
            {programa.badge}
          </Tag>
        </Space>
      </div>

      <Divider style={{ margin: '12px 0' }} />

      {/* Quantidades com barra de progresso */}
      {programa.quantidades && (
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ fontSize: '13px', color: '#475569' }}>
            Quantidades
          </Text>
          <div style={{ marginTop: '8px' }}>
            {programa.quantidades.teto !== undefined &&
              programa.quantidades.credenciados !== undefined && (
                <ProgressBar
                  atual={programa.quantidades.credenciados}
                  total={programa.quantidades.teto}
                  cor={programa.cor}
                />
              )}
            {programa.quantidades.detalhes && (
              <Text style={{ fontSize: '12px', color: '#64748b', display: 'block', marginTop: '4px' }}>
                {programa.quantidades.detalhes}
              </Text>
            )}
          </div>
        </div>
      )}

      {/* Quantidades Secundárias */}
      {programa.quantidadesSecundarias && programa.quantidadesSecundarias.detalhes && (
        <div style={{ marginBottom: '16px' }}>
          <Text style={{ fontSize: '12px', color: '#64748b' }}>
            {programa.quantidadesSecundarias.detalhes}
          </Text>
        </div>
      )}

      {/* Valores Financeiros */}
      <div style={{ marginBottom: '16px' }}>
        <Text strong style={{ fontSize: '13px', color: '#475569' }}>
          Valores
        </Text>
        <div style={{ marginTop: '8px' }}>
          <Row gutter={[8, 4]}>
            {/* Valor Integral */}
            {programa.vlIntegral !== undefined && programa.vlIntegral > 0 && (
              <Col span={24}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text style={{ fontSize: '12px', color: '#64748b' }}>Integral:</Text>
                  <Text strong style={{ fontSize: '12px' }}>
                    {formatarValor(programa.vlIntegral)}
                  </Text>
                </div>
              </Col>
            )}

            {/* Desconto */}
            {programa.vlDesconto !== undefined && programa.vlDesconto !== 0 && (
              <Col span={24}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text style={{ fontSize: '12px', color: '#ef4444' }}>
                    Desconto ({programa.percentualDesconto?.toFixed(1)}%):
                  </Text>
                  <Text strong style={{ fontSize: '12px', color: '#ef4444' }}>
                    {formatarValor(programa.vlDesconto)}
                  </Text>
                </div>
              </Col>
            )}

            {/* Efetivo Repasse */}
            <Col span={24}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  backgroundColor: '#f8fafc',
                  padding: '8px',
                  borderRadius: '6px',
                  marginTop: '4px',
                }}
              >
                <Text strong style={{ fontSize: '13px', color: '#1e293b' }}>
                  Efetivo:
                </Text>
                <Text
                  strong
                  style={{
                    fontSize: '14px',
                    color: programa.cor,
                  }}
                >
                  {formatarValor(programa.vlEfetivoRepasse)}
                </Text>
              </div>
            </Col>
          </Row>
        </div>
      </div>

      {/* Componentes de Valor */}
      {programa.componentesValor && programa.componentesValor.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ fontSize: '12px', color: '#64748b' }}>
            Componentes:
          </Text>
          <div style={{ marginTop: '4px' }}>
            {programa.componentesValor.map((componente, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '11px',
                  color: '#64748b',
                  marginTop: '2px',
                }}
              >
                <Text style={{ fontSize: '11px', color: '#64748b' }}>{componente.nome}:</Text>
                <Text style={{ fontSize: '11px', color: '#64748b' }}>
                  {formatarValor(componente.valor)}
                </Text>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Informações Per Capita */}
      {programa.populacao !== undefined && programa.perCapitaMensal !== undefined && (
        <div style={{ marginBottom: '16px' }}>
          <Row gutter={[8, 4]}>
            <Col span={24}>
              <Text style={{ fontSize: '12px', color: '#64748b' }}>
                População ({programa.anoReferencia}): {programa.populacao.toLocaleString('pt-BR')} hab
              </Text>
            </Col>
            <Col span={24}>
              <div
                style={{
                  backgroundColor: '#f0f9ff',
                  padding: '8px',
                  borderRadius: '6px',
                  textAlign: 'center',
                }}
              >
                <Text strong style={{ fontSize: '13px', color: '#0ea5e9' }}>
                  Per capita: {formatarValor(programa.perCapitaMensal)}/hab/mês
                </Text>
              </div>
            </Col>
          </Row>
        </div>
      )}

      {/* Alertas */}
      {programa.alertas && programa.alertas.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          {programa.alertas.map((alerta, index) => (
            <Alert
              key={index}
              message={alerta}
              type="warning"
              showIcon
              style={{ fontSize: '11px', marginBottom: '8px' }}
            />
          ))}
        </div>
      )}

      {/* Oportunidades */}
      {programa.oportunidades && programa.oportunidades.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          {programa.oportunidades.map((oportunidade, index) => (
            <Alert
              key={index}
              message={oportunidade}
              type="info"
              showIcon
              icon={<BulbOutlined />}
              style={{ fontSize: '11px', marginBottom: index < programa.oportunidades!.length - 1 ? '8px' : 0 }}
            />
          ))}
        </div>
      )}
    </Card>
  );
};
