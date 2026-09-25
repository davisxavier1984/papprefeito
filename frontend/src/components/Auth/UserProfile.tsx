/**
 * Componente de perfil do usuário
 */
import { useState } from 'react';
import { Card, Form, Input, Button, App, Tabs, Typography, Space, Divider } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import { mensagemDeErro } from '../../utils/mensagemDeErro';
import { useAuthStore } from '../../stores/authStore';
import { authService, type UserUpdate, type PasswordChange } from '../../services/authService';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

export const UserProfile = () => {
  const { message } = App.useApp();
  const { user, updateUser } = useAuthStore();
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingPassword, setLoadingPassword] = useState(false);
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();

  // Atualizar perfil
  const handleUpdateProfile = async (values: UserUpdate) => {
    try {
      setLoadingProfile(true);
      const updatedUser = await authService.updateProfile(values);
      updateUser(updatedUser);
      message.success('Perfil atualizado com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error);
      message.error(mensagemDeErro(error, 'Erro ao atualizar perfil'));
    } finally {
      setLoadingProfile(false);
    }
  };

  // Alterar senha
  const handleChangePassword = async (values: PasswordChange) => {
    try {
      setLoadingPassword(true);
      await authService.changePassword(values);
      message.success('Senha alterada com sucesso!');
      passwordForm.resetFields();
    } catch (error) {
      console.error('Erro ao alterar senha:', error);
      message.error(mensagemDeErro(error, 'Erro ao alterar senha'));
    } finally {
      setLoadingPassword(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '24px' }}>
      <Title level={2}>Meu Perfil</Title>

      <Card>
        <Tabs defaultActiveKey="profile">
          <TabPane tab="Informações" key="profile">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Text type="secondary">Informações da Conta</Text>
                <Divider />
                <div style={{ marginBottom: '16px' }}>
                  <Text strong>ID: </Text>
                  <Text>{user.id}</Text>
                </div>
                <div style={{ marginBottom: '16px' }}>
                  <Text strong>Data de Criação: </Text>
                  <Text>{new Date(user.created_at).toLocaleDateString('pt-BR')}</Text>
                </div>
                {user.is_superuser && (
                  <div style={{ marginBottom: '16px' }}>
                    <Text strong>Tipo: </Text>
                    <Text type="warning">Administrador</Text>
                  </div>
                )}
              </div>

              <Form
                form={profileForm}
                layout="vertical"
                onFinish={handleUpdateProfile}
                initialValues={{
                  nome: user.nome,
                  email: user.email
                }}
              >
                <Form.Item
                  name="nome"
                  label="Nome Completo"
                  rules={[
                    { required: true, message: 'Por favor, insira seu nome' },
                    { min: 3, message: 'Nome deve ter no mínimo 3 caracteres' }
                  ]}
                >
                  <Input
                    prefix={<UserOutlined />}
                    placeholder="Seu nome completo"
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
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loadingProfile}
                  >
                    Salvar Alterações
                  </Button>
                </Form.Item>
              </Form>
            </Space>
          </TabPane>

          <TabPane tab="Segurança" key="security">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Title level={4}>Alterar Senha</Title>
                <Text type="secondary">
                  Sua senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números.
                </Text>
              </div>

              <Form
                form={passwordForm}
                layout="vertical"
                onFinish={handleChangePassword}
              >
                <Form.Item
                  name="current_password"
                  label="Senha Atual"
                  rules={[
                    { required: true, message: 'Por favor, insira sua senha atual' }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Senha atual"
                  />
                </Form.Item>

                <Form.Item
                  name="new_password"
                  label="Nova Senha"
                  rules={[
                    { required: true, message: 'Por favor, insira uma nova senha' },
                    { min: 8, message: 'Senha deve ter no mínimo 8 caracteres' },
                    {
                      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                      message: 'Senha deve conter maiúsculas, minúsculas e números'
                    }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Nova senha"
                  />
                </Form.Item>

                <Form.Item
                  name="confirm_password"
                  label="Confirmar Nova Senha"
                  dependencies={['new_password']}
                  rules={[
                    { required: true, message: 'Por favor, confirme sua nova senha' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('new_password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('As senhas não coincidem'));
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Confirme a nova senha"
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loadingPassword}
                  >
                    Alterar Senha
                  </Button>
                </Form.Item>
              </Form>
            </Space>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};
