/**
 * Modal para o admin redefinir a senha de um usuário
 */
import React, { useState } from 'react';
import { Modal, Form, Input, Button, Alert, App, Typography } from 'antd';
import { LockOutlined, ThunderboltOutlined } from '@ant-design/icons';
import type { User } from '../../services/authService';
import { gerarSenha, validarSenha, REGRAS_SENHA } from '../../utils/senha';

const { Text } = Typography;

interface ResetPasswordModalProps {
  open: boolean;
  user: User | null;
  onClose: () => void;
  onSubmit: (userId: string, password: string) => Promise<void>;
}

export const ResetPasswordModal: React.FC<ResetPasswordModalProps> = ({
  open,
  user,
  onClose,
  onSubmit
}) => {
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [senhaGerada, setSenhaGerada] = useState<string | null>(null);

  const fechar = () => {
    form.resetFields();
    setSenhaGerada(null);
    onClose();
  };

  const handleGerar = () => {
    const senha = gerarSenha();
    form.setFieldsValue({ password: senha, confirm: senha });
    form.validateFields(['password', 'confirm']);
    setSenhaGerada(senha);
  };

  const handleSubmit = async () => {
    if (!user) return;
    try {
      const { password } = await form.validateFields();
      setLoading(true);
      await onSubmit(user.id, password);
      message.success(`Senha de ${user.nome} redefinida com sucesso!`);
      fechar();
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Erro ao redefinir senha: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="Redefinir Senha"
      open={open}
      onOk={handleSubmit}
      onCancel={fechar}
      confirmLoading={loading}
      okText="Redefinir"
      cancelText="Cancelar"
      width="min(520px, 92vw)"
    >
      {user && (
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          Nova senha para <Text strong>{user.nome}</Text> ({user.email})
        </Text>
      )}

      <Form
        form={form}
        layout="vertical"
        onValuesChange={(changed) => {
          if ('password' in changed) setSenhaGerada(null);
        }}
      >
        <Form.Item
          name="password"
          label="Nova senha"
          rules={[{ validator: validarSenha }]}
          help={REGRAS_SENHA}
        >
          <Input.Password prefix={<LockOutlined />} placeholder="Nova senha" size="large" />
        </Form.Item>

        <Form.Item
          name="confirm"
          label="Confirmar senha"
          dependencies={['password']}
          rules={[
            { required: true, message: 'Por favor, confirme a senha' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                return !value || getFieldValue('password') === value
                  ? Promise.resolve()
                  : Promise.reject(new Error('As senhas não conferem'));
              }
            })
          ]}
        >
          <Input.Password prefix={<LockOutlined />} placeholder="Repita a nova senha" size="large" />
        </Form.Item>

        <Button icon={<ThunderboltOutlined />} onClick={handleGerar} style={{ marginBottom: 16 }}>
          Gerar senha
        </Button>

        {senhaGerada && (
          <Alert
            type="warning"
            showIcon
            message="Anote ou copie a senha gerada antes de confirmar"
            description={
              <Text copyable={{ text: senhaGerada }} code style={{ fontSize: 16 }}>
                {senhaGerada}
              </Text>
            }
          />
        )}
      </Form>
    </Modal>
  );
};
