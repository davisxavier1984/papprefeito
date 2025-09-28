/**
 * Sidebar com seleções de parâmetros
 */

import React, { useState, useCallback } from 'react';
import { Layout, Typography, Space, Button, Alert, Drawer } from 'antd';
import { SearchOutlined, ReloadOutlined, FilterOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import UFSelector from '../Selectors/UFSelector';
import MunicipioSelector from '../Selectors/MunicipioSelector';
import CompetenciaInput from '../Selectors/CompetenciaInput';
import { useCanConsult, useMunicipioStore } from '../../stores/municipioStore';
import useConsultarDados from '../../hooks/useConsultarDados';

const { Sider } = Layout;
const { Title } = Typography;

interface SidebarProps {
  isMobile?: boolean;
  isDrawerOpen?: boolean;
  onDrawerClose?: () => void;
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  width?: number;
  onWidthChange?: (width: number) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isMobile = false,
  isDrawerOpen = false,
  onDrawerClose,
  collapsed = false,
  onCollapse,
  width = 350,
  onWidthChange
}) => {
  const canConsult = useCanConsult();
  const { isLoading, error, resetState } = useMunicipioStore();
  const { consultar } = useConsultarDados();
  const [isResizing, setIsResizing] = useState(false);

  const handleConsultar = () => {
    consultar();
  };

  const handleReset = () => {
    resetState();
  };

  const handleToggleCollapse = () => {
    onCollapse?.(!collapsed);
  };

  // Funcionalidade de redimensionamento
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);

    // Deixamos de usar uma classe global no <body> para evitar efeitos
    // colaterais (como fechar dropdowns do Ant Design). O estado isResizing
    // agora controla o estilo no wrapper local.

    const startX = e.clientX;
    const startWidth = width;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = Math.max(280, Math.min(500, startWidth + (e.clientX - startX)));
      onWidthChange?.(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [width, onWidthChange]);

  const sidebarContent = (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <div style={{ display: collapsed ? 'none' : 'block' }}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <UFSelector />
          <MunicipioSelector />
          <CompetenciaInput />
        </Space>
      </div>

      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={handleConsultar}
          disabled={!canConsult || isLoading}
          loading={isLoading}
          block={!collapsed}
          size={collapsed ? 'middle' : 'large'}
          style={{
            background: 'linear-gradient(135deg, var(--primary-blue), var(--secondary-blue))',
            border: 'none',
            fontWeight: 600
          }}
          title={collapsed ? 'Consultar Dados' : undefined}
        >
          {collapsed ? null : (isLoading ? 'Consultando...' : 'Consultar Dados')}
        </Button>

        {!collapsed && (
          <Button
            icon={<ReloadOutlined />}
            onClick={handleReset}
            disabled={isLoading}
            block
            style={{
              borderColor: 'var(--primary-blue)',
              color: 'var(--primary-blue)'
            }}
          >
            Limpar Seleções
          </Button>
        )}
      </Space>

      {!collapsed && error && (
        <Alert
          message="Erro na Consulta"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => useMunicipioStore.getState().setError(null)}
          style={{ borderRadius: 8 }}
        />
      )}

      {!collapsed && (
        <div style={{
          fontSize: '12px',
          color: 'var(--text-secondary)',
          lineHeight: 1.5,
          padding: '12px',
          backgroundColor: '#f1f5f9',
          borderRadius: '8px',
          border: '1px solid #e2e8f0'
        }}>
          <strong style={{ color: 'var(--text-primary)' }}>Como usar:</strong><br />
          1. Selecione a UF<br />
          2. Selecione o município<br />
          3. Informe a competência (AAAAMM)<br />
          4. Clique em "Consultar Dados"<br />
          5. Edite os valores na tabela
        </div>
      )}
    </Space>
  );

  return (
    <>
      {isMobile ? (
        <Drawer
          title={
            <Space>
              <FilterOutlined style={{ color: 'var(--primary-blue)' }} />
              <span>Filtros e Parâmetros</span>
            </Space>
          }
          placement="left"
          onClose={onDrawerClose}
          open={isDrawerOpen}
          width={340}
          styles={{
            body: {
              padding: '16px',
              backgroundColor: '#fafbfc'
            },
            header: {
              borderBottom: '1px solid #e2e8f0',
              backgroundColor: '#fff'
            }
          }}
        >
          {sidebarContent}
        </Drawer>
      ) : (
        <div
          style={{
            position: 'relative',
            userSelect: isResizing ? 'none' as const : undefined,
            cursor: isResizing ? 'col-resize' : undefined,
          }}
        >
          <Sider
            width={width}
            collapsed={collapsed}
            collapsedWidth={64}
            style={{
              background: '#fafbfc',
              padding: collapsed ? '24px 8px' : '24px 16px',
              borderRight: '1px solid #e2e8f0',
              boxShadow: '2px 0 8px rgba(0, 0, 0, 0.04)',
              transition: 'width 0.2s ease, padding 0.2s ease',
              overflow: 'visible'
            }}
            trigger={null}
          >
            <div style={{
              display: 'flex',
              justifyContent: collapsed ? 'center' : 'space-between',
              alignItems: 'center',
              marginBottom: collapsed ? '24px' : '16px'
            }}>
              {!collapsed && (
                <Title level={4} style={{ margin: 0, color: 'var(--primary-blue)' }}>
                  <FilterOutlined /> Filtros
                </Title>
              )}
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={handleToggleCollapse}
                style={{
                  color: 'var(--primary-blue)',
                  padding: collapsed ? '4px' : '4px 8px'
                }}
                title={collapsed ? 'Expandir sidebar' : 'Recolher sidebar'}
              />
            </div>
            {sidebarContent}
          </Sider>

          {/* Borda de redimensionamento */}
          {!collapsed && (
            <div
              className="sidebar-resize-handle"
              style={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: '4px',
                height: '100%',
                backgroundColor: isResizing ? 'var(--primary-blue)' : 'transparent',
                transition: 'background-color 0.2s',
                zIndex: 1,
                pointerEvents: 'auto',
                cursor: 'col-resize'
              }}
              onMouseDown={handleMouseDown}
              title="Arraste para redimensionar"
            />
          )}
        </div>
      )}
    </>
  );
};

export default Sidebar;
