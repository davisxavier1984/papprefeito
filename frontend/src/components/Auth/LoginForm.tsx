/**
 * Componente de formulário de Login
 */
import { useState } from 'react';
import { Form, Input, Button, Card, Alert, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { authService, type LoginRequest } from '../../services/authService';
import { useAuthStore } from '../../stores/authStore';
import logo from '../../assets/logo.png';
import timbrado from '../../assets/timbrado.png';

const { Title, Text } = Typography;

export const LoginForm = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const setLoading = useAuthStore((state) => state.setLoading);
  const [error, setError] = useState<string | null>(null);
  const [form] = Form.useForm();

  const handleSubmit = async (values: LoginRequest) => {
    try {
      setError(null);
      setLoading(true);

      const { user, tokens } = await authService.login(values);

      // Atualiza a store com os dados do usuário e tokens
      login(user, tokens.access_token, tokens.refresh_token);

      // Redireciona para o dashboard
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Erro ao fazer login:', err);
      setError(err.response?.data?.detail || 'Erro ao fazer login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundImage: `url(${timbrado})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      position: 'relative',
      padding: '20px'
    }}>
      {/* Overlay para melhorar legibilidade */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.85) 0%, rgba(6, 182, 212, 0.9) 100%)',
        zIndex: 1
      }} />

      <Card
        style={{
          width: '100%',
          maxWidth: '420px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          borderRadius: '16px',
          zIndex: 2,
          position: 'relative',
          border: 'none'
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <img
            src={logo}
            alt="Mais Gestor"
            style={{
              height: '80px',
              marginBottom: '24px',
              filter: 'drop-shadow(0 2px 8px rgba(14, 165, 233, 0.3))'
            }}
          />
          <Title level={2} style={{ marginBottom: '8px', color: '#0ea5e9' }}>
            Bem-vindo
          </Title>
          <Text type="secondary" style={{ fontSize: '15px' }}>
            Entre com suas credenciais para acessar o sistema
          </Text>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: '24px' }}
          />
        )}

        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Por favor, insira seu email' },
              { type: 'email', message: 'Email inválido' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="seu@email.com"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Senha"
            rules={[
              { required: true, message: 'Por favor, insira sua senha' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Sua senha"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={useAuthStore((state) => state.isLoading)}
              style={{
                height: '44px',
                fontSize: '16px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
                border: 'none',
                boxShadow: '0 4px 12px rgba(14, 165, 233, 0.4)'
              }}
            >
              Entrar
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: '14px' }}>
              Não tem uma conta?{' '}
              <Link to="/register" style={{ color: '#0ea5e9', fontWeight: '600' }}>
                Registre-se aqui
              </Link>
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  );
};
