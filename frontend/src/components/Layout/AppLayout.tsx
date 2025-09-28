/**
 * Layout principal da aplicação
 */

import React, { useState, useEffect } from 'react';
import { Layout, Button, Affix } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import Header from './Header';
import Sidebar from './Sidebar';

const { Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(350);

  useEffect(() => {
    const checkMobile = () => {
      const w = window.innerWidth;
      // Histerese para evitar flicker ao redor do breakpoint
      setIsMobile((prev) => (w < 760 ? true : w > 780 ? false : prev));
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleDrawerClose = () => {
    setIsDrawerOpen(false);
  };

  const handleDrawerOpen = () => {
    setIsDrawerOpen(true);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header />
      <Layout>
        <Sidebar
          isMobile={isMobile}
          isDrawerOpen={isDrawerOpen}
          onDrawerClose={handleDrawerClose}
          collapsed={sidebarCollapsed}
          onCollapse={setSidebarCollapsed}
          width={sidebarWidth}
          onWidthChange={setSidebarWidth}
        />

        <Layout style={{ padding: isMobile ? '16px' : '24px' }}>
          {isMobile && (
            <Affix offsetTop={16}>
              <Button
                type="primary"
                icon={<MenuOutlined />}
                onClick={handleDrawerOpen}
                style={{
                  background: 'linear-gradient(135deg, var(--primary-blue), var(--secondary-blue))',
                  border: 'none',
                  marginBottom: '16px',
                  borderRadius: '8px',
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(14, 165, 233, 0.3)'
                }}
                size="large"
              >
                Filtros
              </Button>
            </Affix>
          )}

          <Content
            className="fade-in-up"
            style={{
              background: '#fff',
              padding: isMobile ? '16px' : '24px',
              margin: 0,
              minHeight: 280,
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
              border: '1px solid #e2e8f0'
            }}
          >
            {children}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
