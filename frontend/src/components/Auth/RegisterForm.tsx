/**
 * Componente de formulário de Registro
 */
import { useState } from 'react';
import { Form, Input, Button, Card, Alert, Typography, Progress } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { authService, type RegisterRequest } from '../../services/authService';
import logo from '../../assets/logo.png';
import timbrado from '../../assets/timbrado.png';

const { Title, Text } = Typography;

// Função para calcular a força da senha
const calculatePasswordStrength = (password: string): number => {
  let strength = 0;
  if (password.length >= 8) strength += 25;
  if (password.length >= 12) strength += 15;
  if (/[a-z]/.test(password)) strength += 15;
  if (/[A-Z]/.test(password)) strength += 15;
  if (/[0-9]/.test(password)) strength += 15;
  if (/[^a-zA-Z0-9]/.test(password)) strength += 15;
  return Math.min(strength, 100);
};

export const RegisterForm = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [form] = Form.useForm();

  const handleSubmit = async (values: RegisterRequest) => {
    try {
      setError(null);
      setLoading(true);

      await authService.register(values);

      setSuccess(true);

      // Redireciona para o login após 2 segundos
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      console.error('Erro ao registrar:', err);
      const errorMessage = err.response?.data?.detail;

      if (typeof errorMessage === 'string') {
        setError(errorMessage);
      } else if (Array.isArray(errorMessage)) {
        setError(errorMessage[0]?.msg || 'Erro ao criar conta');
      } else {
        setError('Erro ao criar conta. Tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value;
    setPasswordStrength(calculatePasswordStrength(password));
  };

  const getPasswordStrengthColor = (strength: number): string => {
    if (strength < 40) return '#ff4d4f';
    if (strength < 70) return '#faad14';
    return '#52c41a';
  };

  const getPasswordStrengthText = (strength: number): string => {
    if (strength < 40) return 'Fraca';
    if (strength < 70) return 'Média';
    return 'Forte';
  };

  if (success) {
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

        <Card style={{
          width: '100%',
          maxWidth: '420px',
          textAlign: 'center',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          borderRadius: '16px',
          zIndex: 2,
          position: 'relative',
          border: 'none'
        }}>
          <img
            src={logo}
            alt="Mais Gestor"
            style={{
              height: '80px',
              marginBottom: '24px',
              filter: 'drop-shadow(0 2px 8px rgba(14, 165, 233, 0.3))'
            }}
          />
          <Alert
            message="Conta criada com sucesso!"
            description="Você será redirecionado para o login em instantes..."
            type="success"
            showIcon
          />
        </Card>
      </div>
    );
  }

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
          maxWidth: '460px',
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
            Criar Conta
          </Title>
          <Text type="secondary" style={{ fontSize: '15px' }}>
            Preencha os dados para criar sua conta
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
          name="register"
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="nome"
            label="Nome Completo"
            rules={[
              { required: true, message: 'Por favor, insira seu nome completo' },
              { min: 3, message: 'Nome deve ter no mínimo 3 caracteres' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Seu nome completo"
              autoComplete="name"
            />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Por favor, insira seu email' },
              { type: 'email', message: 'Email inválido' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="seu@email.com"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Senha"
            rules={[
              { required: true, message: 'Por favor, insira uma senha' },
              { min: 8, message: 'Senha deve ter no mínimo 8 caracteres' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                message: 'Senha deve conter maiúsculas, minúsculas e números'
              }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Mínimo 8 caracteres"
              autoComplete="new-password"
              onChange={handlePasswordChange}
            />
          </Form.Item>

          {passwordStrength > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <Progress
                percent={passwordStrength}
                strokeColor={getPasswordStrengthColor(passwordStrength)}
                showInfo={false}
                size="small"
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Força da senha: {getPasswordStrengthText(passwordStrength)}
              </Text>
            </div>
          )}

          <Form.Item
            name="confirmPassword"
            label="Confirmar Senha"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Por favor, confirme sua senha' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('As senhas não coincidem'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirme sua senha"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
              style={{
                height: '44px',
                fontSize: '16px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
                border: 'none',
                boxShadow: '0 4px 12px rgba(14, 165, 233, 0.4)'
              }}
            >
              Criar Conta
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: '14px' }}>
              Já tem uma conta?{' '}
              <Link to="/login" style={{ color: '#0ea5e9', fontWeight: '600' }}>
                Faça login
              </Link>
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  );
};
