/**
 * Componente para proteger rotas que requerem autenticação
 */
import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuthStore } from '../../stores/authStore';

interface ProtectedRouteProps {
  children: ReactNode;
  requireSuperuser?: boolean;
}

export const ProtectedRoute = ({ children, requireSuperuser = false }: ProtectedRouteProps) => {
  const location = useLocation();
  const { isAuthenticated, isLoading, user } = useAuthStore();

  // Se ainda está carregando, mostra um spinner
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh'
      }}>
        <Spin size="large" />
      </div>
    );
  }

  // Se não está autenticado, redireciona para login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Se requer superuser e o usuário não é superuser, mostra acesso negado
  if (requireSuperuser && !user?.is_superuser) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <h1>Acesso Negado</h1>
        <p>Você não tem permissão para acessar esta página.</p>
      </div>
    );
  }

  return <>{children}</>;
};
