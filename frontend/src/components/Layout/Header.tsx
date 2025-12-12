/**
 * Cabeçalho da aplicação
 */

import React from 'react';
import { Layout, Typography, Space, Tag, Dropdown, Avatar, Button } from 'antd';
import {
  BarChartOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  TeamOutlined,
  DashboardOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useMunicipioInfo } from '../../stores/municipioStore';
import { useAuthStore } from '../../stores/authStore';
import { authService } from '../../services/authService';
import logoMaisGestor from '../../assets/logo.png';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header: React.FC = () => {
  const municipioInfo = useMunicipioInfo();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      onClick: () => navigate('/dashboard')
    },
    {
      key: 'profile',
      icon: <SettingOutlined />,
      label: 'Meu Perfil',
      onClick: () => navigate('/profile')
    },
    ...(user?.is_superuser
      ? [
          {
            type: 'divider' as const
          },
          {
            key: 'admin',
            icon: <TeamOutlined />,
            label: 'Gestão de Usuários',
            onClick: () => navigate('/admin/users')
          }
        ]
      : []),
    {
      type: 'divider' as const
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sair',
      danger: true,
      onClick: handleLogout
    }
  ];

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

      <Space style={{ position: 'relative', zIndex: 1 }}>
        {municipioInfo && (
          <>
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
              {municipioInfo.nome}
            </Tag>
            <Tag
              style={{
                backgroundColor: municipioInfo.uf === 'BA' ? '#1e40af' : municipioInfo.uf === 'GO' ? '#16a34a' : '#64748b',
                borderColor: municipioInfo.uf === 'BA' ? '#1e40af' : municipioInfo.uf === 'GO' ? '#16a34a' : '#64748b',
                color: '#fff',
                fontWeight: 600,
                borderRadius: '6px',
                fontSize: '13px'
              }}
            >
              {municipioInfo.uf}
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
          </>
        )}

        {user && (
          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
            trigger={['click']}
          >
            <Button
              type="text"
              style={{
                height: '48px',
                padding: '0 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Avatar
                icon={<UserOutlined />}
                style={{
                  backgroundColor: user.is_superuser ? '#f59e0b' : '#0ea5e9'
                }}
              />
              <Space direction="vertical" size={0} style={{ alignItems: 'flex-start' }}>
                <span style={{ fontWeight: 500, fontSize: '14px' }}>{user.nome}</span>
                {user.is_superuser && (
                  <Tag
                    color="gold"
                    style={{ margin: 0, fontSize: '10px', padding: '0 4px' }}
                  >
                    Admin
                  </Tag>
                )}
              </Space>
            </Button>
          </Dropdown>
        )}
      </Space>
    </AntHeader>
  );
};

export default Header;
