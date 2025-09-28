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
        height: '74px',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Logo grande como background decorativo */}
      <img src={logoMaisGestor} alt="" aria-hidden="true" className="header-bg-logo" />

      <Space align="center" size="middle" style={{ height: '100%', position: 'relative', zIndex: 1 }}>
        <img
          src={logoMaisGestor}
          alt="MAIS GESTOR"
          className="header-logo"
          style={{
            width: 'auto',
            display: 'block'
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
        <Space style={{ position: 'relative', zIndex: 1 }}>
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
