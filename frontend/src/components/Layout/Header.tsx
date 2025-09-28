/**
 * Cabeçalho da aplicação
 */

import React from 'react';
import { Layout, Typography, Space, Tag } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';
import { useMunicipioInfo } from '../../stores/municipioStore';
import logoMaisGestor from '../../assets/logo.png';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header: React.FC = () => {
  const municipioInfo = useMunicipioInfo();

  return (
    <AntHeader
      style={{
        background: '#fff',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        borderBottom: '1px solid #e2e8f0',
        height: '74px'
      }}
    >
      <Space align="center" size="middle">
        <img
          src={logoMaisGestor}
          alt="MAIS GESTOR"
          style={{
            height: '80px',
            width: 'auto'
          }}
        />
        <Title
          level={4}
          style={{
            color: 'var(--text-primary)',
            margin: 0,
            fontSize: '20px',
            fontWeight: 600,
            lineHeight: 1.2
          }}
        >
          Projeção de Financiamento PAP
        </Title>
      </Space>

      {municipioInfo && (
        <Space>
          <Tag
            icon={<BarChartOutlined />}
            style={{
              backgroundColor: 'var(--primary-blue)',
              borderColor: 'var(--primary-blue)',
              color: '#fff',
              fontWeight: 500,
              borderRadius: '6px'
            }}
          >
            {municipioInfo.nome}/{municipioInfo.uf}
          </Tag>
          <Tag
            style={{
              backgroundColor: 'var(--success-green)',
              borderColor: 'var(--success-green)',
              color: '#fff',
              fontWeight: 500,
              borderRadius: '6px'
            }}
          >
            {municipioInfo.competencia}
          </Tag>
        </Space>
      )}
    </AntHeader>
  );
};

export default Header;