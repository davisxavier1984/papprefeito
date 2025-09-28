/**
 * Cabeçalho da aplicação
 */

import React from 'react';
import { Layout, Typography, Space, Tag } from 'antd';
import { BankOutlined, BarChartOutlined } from '@ant-design/icons';
import { useMunicipioInfo } from '../../stores/municipioStore';

const { Header: AntHeader } = Layout;
const { Title, Text } = Typography;

const Header: React.FC = () => {
  const municipioInfo = useMunicipioInfo();

  return (
    <AntHeader
      style={{
        background: '#001529',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
      }}
    >
      <Space align="center">
        <BankOutlined style={{ color: '#fff', fontSize: '24px' }} />
        <div>
          <Title
            level={3}
            style={{
              color: '#fff',
              margin: 0,
              fontSize: '20px'
            }}
          >
            🏛️ Sistema papprefeito
          </Title>
          <Text
            style={{
              color: 'rgba(255, 255, 255, 0.65)',
              fontSize: '12px'
            }}
          >
            Consulta e Edição de Dados de Financiamento APS
          </Text>
        </div>
      </Space>

      {municipioInfo && (
        <Space>
          <Tag color="blue" icon={<BarChartOutlined />}>
            {municipioInfo.nome}/{municipioInfo.uf}
          </Tag>
          <Tag color="green">
            {municipioInfo.competencia}
          </Tag>
        </Space>
      )}
    </AntHeader>
  );
};

export default Header;