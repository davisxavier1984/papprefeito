/**
 * Componente principal da aplicação
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import AppLayout from './components/Layout/AppLayout';
import Dashboard from './pages/Dashboard';
import { LoginForm } from './components/Auth/LoginForm';
import { RegisterForm } from './components/Auth/RegisterForm';
import { ProtectedRoute } from './components/Auth/ProtectedRoute';
import { UserProfile } from './components/Auth/UserProfile';
import './App.css';

// Configurar React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: unknown) => {
        // Não fazer retry para erros 4xx (client errors)
        if (error && typeof error === 'object' && 'error_code' in error &&
            typeof (error as Record<string, unknown>).error_code === 'string' &&
            (error as Record<string, string>).error_code.startsWith('4')) {
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

// Configuração do tema Ant Design baseado na marca MAIS GESTOR
const antdTheme = {
  token: {
    colorPrimary: '#0ea5e9', // Azul primário do logo
    colorSuccess: '#22c55e', // Verde para valores positivos
    colorError: '#ef4444', // Vermelho para perdas
    colorWarning: '#f59e0b', // Laranja para alertas
    borderRadius: 8,
    fontSize: 14,
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    boxShadow: '0 4px 12px rgba(14, 165, 233, 0.1)',
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f8fafc',
  },
  components: {
    Layout: {
      headerBg: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
      siderBg: '#f8fafc',
      bodyBg: '#f8fafc',
    },
    Button: {
      borderRadius: 8,
      fontWeight: 500,
      primaryShadow: '0 4px 12px rgba(14, 165, 233, 0.3)',
    },
    Input: {
      borderRadius: 8,
      activeBorderColor: '#0ea5e9',
      hoverBorderColor: '#38bdf8',
    },
    Select: {
      borderRadius: 8,
      activeBorderColor: '#0ea5e9',
      hoverBorderColor: '#38bdf8',
    },
    Table: {
      borderRadius: 8,
      headerBg: '#f1f5f9',
      headerColor: '#334155',
      borderColor: '#e2e8f0',
    },
    Card: {
      borderRadius: 12,
      boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
    },
    Tag: {
      borderRadius: 6,
    },
    Statistic: {
      titleFontSize: 14,
      contentFontSize: 24,
      fontFamily: 'inherit',
    },
  },
};

const App: React.FC = () => {
  // Sanitizar possíveis classes residuais em HMR/atualizações
  useEffect(() => {
    document.body.classList.remove('resizing');
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={ptBR}
        theme={antdTheme}
      >
        <BrowserRouter>
          <Routes>
            {/* Rotas públicas de autenticação */}
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<RegisterForm />} />

            {/* Rotas protegidas */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Dashboard />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <UserProfile />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Redirecionar raiz para login */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Rota 404 - redireciona para login */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>

        {/* DevTools apenas em desenvolvimento */}
        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;
