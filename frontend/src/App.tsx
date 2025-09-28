/**
 * Componente principal da aplicação
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import AppLayout from './components/Layout/AppLayout';
import Dashboard from './pages/Dashboard';
import './App.css';

// Configurar React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Não fazer retry para erros 4xx (client errors)
        if (error?.error_code && error.error_code.startsWith('4')) {
          return false;
        }
        return failureCount < 3;
      },
      staleTime: 1000 * 60 * 5, // 5 minutos por padrão
      gcTime: 1000 * 60 * 30, // 30 minutos para garbage collection
    },
    mutations: {
      retry: 1,
    },
  },
});

// Configuração do tema Ant Design
const antdTheme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    fontSize: 14,
  },
  components: {
    Layout: {
      headerBg: '#001529',
      siderBg: '#f5f5f5',
    },
    Button: {
      borderRadius: 6,
    },
    Input: {
      borderRadius: 6,
    },
    Select: {
      borderRadius: 6,
    },
    Table: {
      borderRadius: 6,
    },
  },
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={ptBR}
        theme={antdTheme}
      >
        <AppLayout>
          <Dashboard />
        </AppLayout>
        {/* DevTools apenas em desenvolvimento */}
        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;
