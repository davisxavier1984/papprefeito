/**
 * Acerto do preenchimento automático em relação ao consultor.
 * Recalcula a regra atual sobre as perdas informadas à mão e mostra, por plano, quanto se aproxima.
 */

import React, { useState } from 'react';
import { Alert, Button, Card, Input, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import { competenciaValida } from '../../utils/municipiosLote';
import type { MetricasPlano } from '../../types';

const { Title, Text } = Typography;

const pct = (v?: number | null) => (v == null ? '—' : `${Math.round(v * 100)}%`);
const razao = (v?: number | null) => (v == null ? '—' : v.toLocaleString('pt-BR', { maximumFractionDigits: 2 }));

const colunas: ColumnsType<MetricasPlano> = [
  { title: 'Plano', dataIndex: 'plano' },
  { title: 'Registros', dataIndex: 'registros', align: 'right' },
  { title: 'Exatos', key: 'exatos', align: 'right', render: (_, m) => `${m.exatos} de ${m.registros}` },
  { title: 'Erro mediano', dataIndex: 'erro_mediano', align: 'right', render: pct },
  { title: 'Dentro de ±25%', dataIndex: 'dentro_25', align: 'right' },
  { title: 'Zero certo', key: 'zero', align: 'right', render: (_, m) => `${m.zero_certo} de ${m.registros}` },
  { title: 'Sugerido ÷ informado', dataIndex: 'razao_soma', align: 'right', render: razao },
  {
    title: 'Situação',
    key: 'alerta',
    render: (_, m) => (m.alerta ? <Tag color="orange">Afastado do consultor</Tag> : <Tag color="green">Ok</Tag>),
  },
];

const AcertoAutomatico: React.FC = () => {
  const [desde, setDesde] = useState('202512');
  const [consultado, setConsultado] = useState('202512');

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['acerto-automatico', consultado],
    queryFn: () => apiClient.getAcerto(consultado),
  });

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={2} style={{ marginBottom: 0 }}>Acerto do automático</Title>
        <Text type="secondary">
          Compara o preenchimento automático com o que o consultor informou à mão. Só valores digitados pelo consultor
          entram; o que veio da própria regra não conta.
        </Text>
      </div>

      <Card>
        <Space wrap>
          <Input
            addonBefore="Desde a competência"
            value={desde}
            maxLength={6}
            status={desde && !competenciaValida(desde) ? 'error' : undefined}
            onChange={(e) => setDesde(e.target.value.replace(/\D/g, ''))}
            style={{ width: 280 }}
          />
          <Button type="primary" disabled={!competenciaValida(desde)} onClick={() => setConsultado(desde)}>
            Atualizar
          </Button>
        </Space>
      </Card>

      {isError && (
        <Alert
          type="error"
          showIcon
          message="Não foi possível calcular o acerto."
          action={<Button size="small" onClick={() => refetch()}>Tentar novamente</Button>}
        />
      )}

      {data && data.sem_resposta > 0 && (
        <Alert
          type="info"
          showIcon
          message={`${data.sem_resposta} registro(s) ficaram de fora por não ter a resposta do Ministério guardada.`}
        />
      )}

      <Card title="Planos com regra">
        <Table size="small" rowKey="tipo" loading={isLoading} columns={colunas} dataSource={data?.planos ?? []}
               pagination={false} scroll={{ x: 800 }} />
      </Card>

      <Card title="Planos preenchidos só pelo consultor">
        <Space direction="vertical">
          {(data?.manuais ?? []).map((m) => (
            <Text key={m.plano}>
              {m.plano}: preenchido em {m.preenchidos} de {m.registros} registros
            </Text>
          ))}
        </Space>
      </Card>
    </Space>
  );
};

export default AcertoAutomatico;
