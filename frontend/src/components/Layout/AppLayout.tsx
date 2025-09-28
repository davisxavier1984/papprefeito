/**
 * Layout principal da aplicação
 */

import React from 'react';
import { Layout } from 'antd';
import Header from './Header';
import Sidebar from './Sidebar';

const { Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header />
      <Layout>
        <Sidebar />
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              background: '#fff',
              padding: '24px',
              margin: 0,
              minHeight: 280,
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
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