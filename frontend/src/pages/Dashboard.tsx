/**
 * Página principal do dashboard
 */

import React from 'react';
import { Typography, Space, Divider, Empty } from 'antd';
import FinancialTable from '../components/DataTable/FinancialTable';
import MetricsCards from '../components/Metrics/MetricsCards';
import { useHasDados } from '../stores/municipioStore';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const hasDados = useHasDados();

  if (!hasDados) {
    return (
      <div className="fade-in-up">
        <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }} size="large">
          <div style={{
            background: 'linear-gradient(135deg, var(--primary-blue), var(--secondary-blue))',
            borderRadius: '16px',
            padding: '32px 24px',
            color: '#fff',
            marginBottom: '24px'
          }}>
            <Title level={2} style={{ color: '#fff', margin: '0 0 8px 0' }}>
              🏛️ Sistema MaisPAP
            </Title>
            <Text style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '16px', fontWeight: 500 }}>
              Consulta e Edição de Dados de Financiamento APS
            </Text>
            <div style={{ marginTop: '12px' }}>
              <Text style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
                Desenvolvido pela MAIS GESTOR - Saúde e Inovações Tecnológicas
              </Text>
            </div>
          </div>

          <Empty
            image="https://gw.alipayobjects.com/zos/antfincdn/ZHrcdLPrvN/empty.svg"
            styles={{
              image: {
                height: 120,
                marginBottom: '16px'
              }
            }}
            description={
              <Space direction="vertical" size="small">
                <Text style={{ fontSize: '16px', color: 'var(--text-primary)', fontWeight: 500 }}>
                  Nenhum dado carregado ainda
                </Text>
                <Text type="secondary" style={{ fontSize: '14px' }}>
                  Configure os filtros para começar a consultar os dados
                </Text>
              </Space>
            }
          />

          <div style={{
            maxWidth: 680,
            margin: '0 auto',
            background: '#f8fafc',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #e2e8f0'
          }}>
            <Title level={4} style={{ color: 'var(--primary-blue)', marginBottom: '16px' }}>
              📋 Como utilizar o sistema:
            </Title>

            <div style={{ textAlign: 'left' }}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {[
                  { step: '1', title: 'Selecione a UF', desc: 'Escolha o estado desejado no painel lateral' },
                  { step: '2', title: 'Selecione o município', desc: 'Escolha o município após selecionar a UF' },
                  { step: '3', title: 'Informe a competência', desc: 'Digite no formato AAAAMM (ex: 202401)' },
                  { step: '4', title: 'Consulte os dados', desc: 'Clique em "Consultar Dados" para buscar as informações' },
                  { step: '5', title: 'Edite valores', desc: 'Modifique os valores de "Perca Recurso Mensal"' },
                  { step: '6', title: 'Acompanhe os cálculos', desc: 'Visualize as métricas atualizadas automaticamente' }
                ].map((item) => (
                  <div key={item.step} style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    padding: '12px',
                    backgroundColor: '#fff',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <div style={{
                      backgroundColor: 'var(--primary-blue)',
                      color: '#fff',
                      borderRadius: '50%',
                      width: '24px',
                      height: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      fontWeight: 600,
                      flexShrink: 0
                    }}>
                      {item.step}
                    </div>
                    <div>
                      <Text strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>
                        {item.title}
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '13px' }}>
                        {item.desc}
                      </Text>
                    </div>
                  </div>
                ))}
              </Space>
            </div>
          </div>

          <Divider style={{ margin: '32px 0 16px 0' }} />

          <Text type="secondary" style={{ fontSize: '12px', lineHeight: 1.4 }}>
            Dados obtidos do Ministério da Saúde via API oficial<br />
            Sistema para análise de financiamento da Atenção Primária à Saúde
          </Text>
        </Space>
      </div>
    );
  }

  return (
    <div className="fade-in-up">
      <Space direction="vertical" style={{ width: '100%' }} size="large">

        <MetricsCards />

        <div style={{
          background: '#fff',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid #e2e8f0',
          boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)'
        }}>
          <Title level={4} style={{ color: 'var(--text-primary)', marginBottom: '16px' }}>
            💰 Detalhamento por Recurso
          </Title>
          <FinancialTable />
        </div>
      </Space>
    </div>
  );
};

export default Dashboard;
