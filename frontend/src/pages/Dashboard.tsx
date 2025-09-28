/**
 * Página principal do dashboard
 */

import React from 'react';
import { Typography, Space, Divider, Empty } from 'antd';
import { useHasDados, useMunicipioInfo } from '../stores/municipioStore';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const hasDados = useHasDados();
  const municipioInfo = useMunicipioInfo();

  if (!hasDados) {
    return (
      <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }} size="large">
        <Title level={2}>
          🏛️ Bem-vindo ao Sistema papprefeito
        </Title>

        <Text type="secondary" style={{ fontSize: '16px' }}>
          Sistema para consulta e edição de dados de financiamento APS do Ministério da Saúde
        </Text>

        <Divider />

        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <span>
              Selecione UF, município e competência no painel lateral<br />
              para começar a consultar os dados
            </span>
          }
        />

        <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'left' }}>
          <Title level={4}>📋 Como usar:</Title>
          <ol style={{ fontSize: '14px', lineHeight: 1.6 }}>
            <li><strong>Selecione a UF</strong> no painel lateral</li>
            <li><strong>Selecione o município</strong> desejado</li>
            <li><strong>Informe a competência</strong> no formato AAAAMM (ex: 202401)</li>
            <li><strong>Clique em "Consultar"</strong> para buscar os dados</li>
            <li><strong>Edite os valores</strong> de "Perca Recurso Mensal" na tabela</li>
            <li><strong>Visualize os cálculos</strong> atualizados automaticamente</li>
          </ol>
        </div>

        <Divider />

        <Text type="secondary" style={{ fontSize: '12px' }}>
          Dados obtidos do Ministério da Saúde via API oficial<br />
          Sistema desenvolvido para análise de financiamento da Atenção Primária à Saúde
        </Text>
      </Space>
    );
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Title level={2}>
        📊 Dados de Financiamento APS
      </Title>

      {municipioInfo && (
        <div>
          <Text strong style={{ fontSize: '16px' }}>
            {municipioInfo.nome}/{municipioInfo.uf} - Competência: {municipioInfo.competencia}
          </Text>
        </div>
      )}

      <Divider />

      {/* Aqui será implementada a tabela financeira e cards de métricas */}
      <div style={{ padding: '40px', textAlign: 'center', background: '#f5f5f5', borderRadius: '8px' }}>
        <Text type="secondary">
          🚧 Tabela financeira e métricas serão implementadas na próxima etapa
        </Text>
      </div>
    </Space>
  );
};

export default Dashboard;