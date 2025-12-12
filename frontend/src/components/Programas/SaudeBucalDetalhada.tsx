import { Collapse, Divider, Row, Col, Typography, Tag, Space, Card } from 'antd';
import { CaretRightOutlined } from '@ant-design/icons';
import type { DetalhamentoSaudeBucal } from '../../types';

const { Text } = Typography;
const { Panel } = Collapse;

interface SaudeBucalDetalhadaProps {
  detalhamento: DetalhamentoSaudeBucal;
}

export const SaudeBucalDetalhada: React.FC<SaudeBucalDetalhadaProps> = ({ detalhamento }) => {
  const formatarValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(valor);
  };

  const renderInfoBox = (label: string, valor: number | string, cor?: string) => (
    <div
      style={{
        backgroundColor: cor ? `${cor}10` : '#f8fafc',
        padding: '8px 12px',
        borderRadius: '6px',
        border: `1px solid ${cor ? `${cor}40` : '#e2e8f0'}`,
      }}
    >
      <Text style={{ fontSize: '11px', color: '#64748b', display: 'block' }}>{label}</Text>
      <Text strong style={{ fontSize: '13px', color: cor || '#1e293b' }}>
        {typeof valor === 'number' && valor > 0 ? formatarValor(valor) : valor}
      </Text>
    </div>
  );

  const renderQuantidadeBox = (label: string, valor: number) => (
    <div style={{ textAlign: 'center', padding: '8px 0' }}>
      <Text style={{ fontSize: '11px', color: '#64748b', display: 'block', marginBottom: '4px' }}>
        {label}
      </Text>
      <Tag color="blue" style={{ fontSize: '12px', fontWeight: 600, margin: 0 }}>
        {valor}
      </Tag>
    </div>
  );

  return (
    <Collapse
      bordered={false}
      expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}
      style={{ backgroundColor: 'transparent', marginTop: '12px' }}
    >
      <Panel
        header={
          <Space>
            <Text strong style={{ color: '#0ea5e9' }}>
              📋 Ver Detalhamento Completo
            </Text>
            <Tag color="cyan">{detalhamento.totais.qtTotalEquipes} equipes</Tag>
          </Space>
        }
        key="1"
        style={{ backgroundColor: '#f0f9ff', borderRadius: '8px' }}
      >
        {/* ESB - Equipes de Saúde Bucal */}
        <Card
          title={<Text strong style={{ color: '#1e293b' }}>🦷 ESB - Equipes de Saúde Bucal</Text>}
          size="small"
          style={{ marginBottom: '12px' }}
        >
          {/* Modalidade 40h */}
          <div style={{ marginBottom: '12px' }}>
            <Text strong style={{ fontSize: '12px', color: '#475569' }}>
              Modalidade 40h
            </Text>
            <Row gutter={[8, 8]} style={{ marginTop: '8px' }}>
              <Col span={12}>{renderQuantidadeBox('Credenciadas', detalhamento.esb.modalidade40h.credenciadas)}</Col>
              <Col span={12}>{renderQuantidadeBox('Homologadas', detalhamento.esb.modalidade40h.homologadas)}</Col>
              <Col span={12}>{renderQuantidadeBox('Modalidade I', detalhamento.esb.modalidade40h.modalidadeI)}</Col>
              <Col span={12}>{renderQuantidadeBox('Modalidade II', detalhamento.esb.modalidade40h.modalidadeII)}</Col>
            </Row>
          </div>

          <Divider style={{ margin: '12px 0' }} />

          {/* CH Diferenciada */}
          <div style={{ marginBottom: '12px' }}>
            <Text strong style={{ fontSize: '12px', color: '#475569' }}>
              Carga Horária Diferenciada
            </Text>
            <Row gutter={[8, 8]} style={{ marginTop: '8px' }}>
              <Col span={12}>{renderQuantidadeBox('Credenciadas', detalhamento.esb.chDiferenciada.credenciadas)}</Col>
              <Col span={12}>{renderQuantidadeBox('Homologadas', detalhamento.esb.chDiferenciada.homologadas)}</Col>
              <Col span={12}>{renderQuantidadeBox('20 horas', detalhamento.esb.chDiferenciada.modalidade20h)}</Col>
              <Col span={12}>{renderQuantidadeBox('30 horas', detalhamento.esb.chDiferenciada.modalidade30h)}</Col>
            </Row>
          </div>

          <Divider style={{ margin: '12px 0' }} />

          {/* Quilombolas e Assentamentos */}
          {(detalhamento.esb.quilombolasAssentamentos.modalidadeI > 0 ||
            detalhamento.esb.quilombolasAssentamentos.modalidadeII > 0) && (
            <>
              <div style={{ marginBottom: '12px' }}>
                <Text strong style={{ fontSize: '12px', color: '#475569' }}>
                  Quilombolas e Assentamentos
                </Text>
                <Row gutter={[8, 8]} style={{ marginTop: '8px' }}>
                  <Col span={12}>
                    {renderQuantidadeBox('Modalidade I', detalhamento.esb.quilombolasAssentamentos.modalidadeI)}
                  </Col>
                  <Col span={12}>
                    {renderQuantidadeBox('Modalidade II', detalhamento.esb.quilombolasAssentamentos.modalidadeII)}
                  </Col>
                </Row>
              </div>
              <Divider style={{ margin: '12px 0' }} />
            </>
          )}

          {/* Valores ESB */}
          <div>
            <Text strong style={{ fontSize: '12px', color: '#475569', display: 'block', marginBottom: '8px' }}>
              Valores Financeiros ESB
            </Text>
            <Row gutter={[8, 8]}>
              <Col span={12}>{renderInfoBox('Pagamento', detalhamento.esb.valores.pagamento, '#0ea5e9')}</Col>
              <Col span={12}>{renderInfoBox('Qualidade', detalhamento.esb.valores.qualidade, '#10b981')}</Col>
              <Col span={12}>{renderInfoBox('CH Diferenciada', detalhamento.esb.valores.chDiferenciada, '#8b5cf6')}</Col>
              <Col span={12}>{renderInfoBox('Implantação', detalhamento.esb.valores.implantacao, '#f59e0b')}</Col>
            </Row>
          </div>
        </Card>

        {/* UOM - Unidade Odontológica Móvel */}
        {detalhamento.uom.credenciadas > 0 && (
          <Card
            title={<Text strong style={{ color: '#1e293b' }}>🚐 UOM - Unidade Odontológica Móvel</Text>}
            size="small"
            style={{ marginBottom: '12px' }}
          >
            <Row gutter={[8, 8]}>
              <Col span={8}>{renderQuantidadeBox('Credenciadas', detalhamento.uom.credenciadas)}</Col>
              <Col span={8}>{renderQuantidadeBox('Homologadas', detalhamento.uom.homologadas)}</Col>
              <Col span={8}>{renderQuantidadeBox('Pagas', detalhamento.uom.pagas)}</Col>
            </Row>
            <Divider style={{ margin: '12px 0' }} />
            <Row gutter={[8, 8]}>
              <Col span={12}>{renderInfoBox('Pagamento', detalhamento.uom.valores.pagamento, '#0ea5e9')}</Col>
              <Col span={12}>{renderInfoBox('Implantação', detalhamento.uom.valores.implantacao, '#f59e0b')}</Col>
            </Row>
          </Card>
        )}

        {/* CEO - Centro de Especialidades Odontológicas */}
        {(detalhamento.ceo.municipal > 0 || detalhamento.ceo.estadual > 0) && (
          <Card
            title={<Text strong style={{ color: '#1e293b' }}>🏥 CEO - Centro de Especialidades Odontológicas</Text>}
            size="small"
            style={{ marginBottom: '12px' }}
          >
            <Row gutter={[8, 8]}>
              <Col span={12}>{renderInfoBox('Municipal', detalhamento.ceo.municipal, '#3b82f6')}</Col>
              <Col span={12}>{renderInfoBox('Estadual', detalhamento.ceo.estadual, '#8b5cf6')}</Col>
            </Row>
          </Card>
        )}

        {/* LRPD - Laboratório Regional de Prótese Dentária */}
        {(detalhamento.lrpd.municipal > 0 || detalhamento.lrpd.estadual > 0) && (
          <Card
            title={
              <Text strong style={{ color: '#1e293b' }}>
                🔬 LRPD - Laboratório Regional de Prótese Dentária
              </Text>
            }
            size="small"
            style={{ marginBottom: '12px' }}
          >
            <Row gutter={[8, 8]}>
              <Col span={12}>{renderInfoBox('Municipal', detalhamento.lrpd.municipal, '#3b82f6')}</Col>
              <Col span={12}>{renderInfoBox('Estadual', detalhamento.lrpd.estadual, '#8b5cf6')}</Col>
            </Row>
          </Card>
        )}

        {/* Totais */}
        <Card
          style={{
            backgroundColor: '#f0f9ff',
            border: '2px solid #0ea5e9',
          }}
          size="small"
        >
          <Row gutter={[16, 8]} align="middle">
            <Col span={12} style={{ textAlign: 'center' }}>
              <Text style={{ fontSize: '11px', color: '#64748b', display: 'block' }}>Total de Equipes</Text>
              <Text strong style={{ fontSize: '20px', color: '#0ea5e9' }}>
                {detalhamento.totais.qtTotalEquipes}
              </Text>
            </Col>
            <Col span={12} style={{ textAlign: 'center' }}>
              <Text style={{ fontSize: '11px', color: '#64748b', display: 'block' }}>Valor Total</Text>
              <Text strong style={{ fontSize: '16px', color: '#10b981' }}>
                {formatarValor(detalhamento.totais.vlTotal)}
              </Text>
            </Col>
          </Row>
        </Card>
      </Panel>
    </Collapse>
  );
};
