/**
 * Componente: SiapsClassificacaoCard
 * - Exibe o detalhe da classificação SIAPS (CVAT + Qualidade) por equipe
 * - Mostra as duas lacunas lado a lado: "já vigente" e "potencial total"
 */
import React from 'react';
import { Card, Table, Typography, Space, Tag, Tooltip, Row, Col, Divider } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMunicipioStore } from '../../stores/municipioStore';
import { useIsMobile } from '../../hooks/useIsMobile';
import type { SiapsGapDetalhe } from '../../types';
import { formatCurrencyBRL as formatCurrency } from '../../utils/formatCurrency';

const { Text } = Typography;

const COMPONENTE_LABEL: Record<string, string> = {
  CVAT: 'Vínculo e Acompanhamento',
  QUALIDADE: 'Qualidade',
};

const SiapsClassificacaoCard: React.FC = () => {
  const { siapsGap } = useMunicipioStore();
  const isMobile = useIsMobile();

  if (!siapsGap || siapsGap.detalhe.length === 0) {
    return null;
  }

  const columns: ColumnsType<SiapsGapDetalhe & { key: string }> = [
    {
      title: 'Equipe',
      dataIndex: 'sgEquipe',
      key: 'sgEquipe',
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: 'Componente',
      dataIndex: 'componente',
      key: 'componente',
      render: (v: string) => COMPONENTE_LABEL[v] ?? v,
    },
    {
      title: 'Ótimo',
      key: 'otimo',
      align: 'center',
      render: (_v, r) => r.contagens?.Otimo ?? 0,
    },
    {
      title: 'Bom',
      key: 'bom',
      align: 'center',
      render: (_v, r) => r.contagens?.Bom ?? 0,
    },
    {
      title: 'Suficiente',
      key: 'suf',
      align: 'center',
      render: (_v, r) => r.contagens?.Suficiente ?? 0,
    },
    {
      title: 'Regular',
      key: 'reg',
      align: 'center',
      render: (_v, r) => r.contagens?.Regular ?? 0,
    },
    {
      title: <Tooltip title="Ganho capturável agora, sob a fase atual do cronograma (na transição = R$ 0)">Já vigente</Tooltip>,
      dataIndex: 'gap_vigente',
      key: 'gap_vigente',
      align: 'right',
      render: (v: number) => <Text>{formatCurrency(v)}</Text>,
    },
    {
      title: <Tooltip title="Ganho mensal se todas as equipes chegarem a Ótimo, comparado ao que é pago hoje (na transição, todas como Bom)">Potencial total</Tooltip>,
      dataIndex: 'gap_potencial',
      key: 'gap_potencial',
      align: 'right',
      render: (v: number) => <Text type="success">{formatCurrency(v)}</Text>,
    },
  ];

  const dataSource = siapsGap.detalhe.map((d, i) => ({ key: `${d.sgEquipe}-${d.componente}-${i}`, ...d }));

  // Visualização mobile em cards (substitui a tabela de 8 colunas em telas pequenas)
  const MobileCardView = () => (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {siapsGap.detalhe.map((d, i) => (
        <Card
          key={`${d.sgEquipe}-${d.componente}-${i}`}
          size="small"
          style={{ borderRadius: 8, border: '1px solid var(--border-color)' }}
        >
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <Space wrap>
              <Text strong>{d.sgEquipe}</Text>
              <Tag color="blue">{COMPONENTE_LABEL[d.componente] ?? d.componente}</Tag>
            </Space>
            <Space size="small" wrap style={{ fontSize: 12 }}>
              <Tag>Ótimo: {d.contagens?.Otimo ?? 0}</Tag>
              <Tag>Bom: {d.contagens?.Bom ?? 0}</Tag>
              <Tag>Suficiente: {d.contagens?.Suficiente ?? 0}</Tag>
              <Tag>Regular: {d.contagens?.Regular ?? 0}</Tag>
            </Space>
            <Divider style={{ margin: '8px 0' }} />
            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Já vigente</Text>
                <Text>{formatCurrency(d.gap_vigente)}</Text>
              </Col>
              <Col span={12} style={{ textAlign: 'right' }}>
                <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Potencial total</Text>
                <Text type="success">{formatCurrency(d.gap_potencial)}</Text>
              </Col>
            </Row>
          </Space>
        </Card>
      ))}
      <Card size="small" style={{ borderRadius: 8, border: '1px solid var(--border-color)', background: 'var(--bg-elevated)' }}>
        <Row gutter={[8, 8]}>
          <Col span={12}>
            <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Total já vigente</Text>
            <Text strong>{formatCurrency(siapsGap.total_vigente)}</Text>
          </Col>
          <Col span={12} style={{ textAlign: 'right' }}>
            <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Total potencial</Text>
            <Text strong type="success">{formatCurrency(siapsGap.total_potencial)}</Text>
          </Col>
        </Row>
      </Card>
    </Space>
  );

  return (
    <Card
      title={
        <Space size="small" wrap>
          <span>📊 Classificação das equipes (SIAPS)</span>
          <Tag color="blue">Quadrimestre {siapsGap.quadrimestre_aplicado}</Tag>
          <Tag>Estrato {siapsGap.estrato}</Tag>
          {!siapsGap.valores_validados && (
            <Tooltip title="Valores de referência por classificação/estrato ainda em validação.">
              <Tag color="warning">valores provisórios</Tag>
            </Tooltip>
          )}
        </Space>
      }
      style={{ borderRadius: 12, border: '1px solid var(--border-color)' }}
    >
      {isMobile ? (
        <MobileCardView />
      ) : (
        <Table
          size="small"
          bordered
          pagination={false}
          columns={columns}
          dataSource={dataSource}
          scroll={{ x: 720 }}
          summary={() => (
            <Table.Summary.Row>
              <Table.Summary.Cell index={0} colSpan={6}>
                <Text strong>Total</Text>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={6} align="right">
                <Text strong>{formatCurrency(siapsGap.total_vigente)}</Text>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={7} align="right">
                <Text strong type="success">{formatCurrency(siapsGap.total_potencial)}</Text>
              </Table.Summary.Cell>
            </Table.Summary.Row>
          )}
        />
      )}
    </Card>
  );
};

export default SiapsClassificacaoCard;
