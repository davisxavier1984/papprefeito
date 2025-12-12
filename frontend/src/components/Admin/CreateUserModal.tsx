/**
 * Modal para criação de novo usuário
 */
import React, { useState } from 'react';
import { Modal, Form, Input, Switch, Select, App } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons';
import type { CreateUserRequest } from '../../services/userManagementService';

interface CreateUserModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreateUserRequest) => Promise<void>;
}

export const CreateUserModal: React.FC<CreateUserModalProps> = ({ open, onClose, onSubmit }) => {
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      await onSubmit(values);

      message.success('Usuário criado com sucesso!');
      form.resetFields();
      onClose();
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Erro ao criar usuário: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  // Validação de força de senha
  const validatePassword = (_: unknown, value: string) => {
    if (!value) {
      return Promise.reject(new Error('Por favor, insira uma senha'));
    }
    if (value.length < 8) {
      return Promise.reject(new Error('A senha deve ter no mínimo 8 caracteres'));
    }
    if (!/[A-Z]/.test(value)) {
      return Promise.reject(new Error('A senha deve conter pelo menos uma letra maiúscula'));
    }
    if (!/[a-z]/.test(value)) {
      return Promise.reject(new Error('A senha deve conter pelo menos uma letra minúscula'));
    }
    if (!/[0-9]/.test(value)) {
      return Promise.reject(new Error('A senha deve conter pelo menos um número'));
    }
    return Promise.resolve();
  };

  return (
    <Modal
      title="Criar Novo Usuário"
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      confirmLoading={loading}
      okText="Criar"
      cancelText="Cancelar"
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          is_superuser: false,
          authorization: 'municipal'
        }}
      >
        <Form.Item
          name="nome"
          label="Nome completo"
          rules={[
            { required: true, message: 'Por favor, insira o nome do usuário' },
            { min: 3, message: 'O nome deve ter no mínimo 3 caracteres' }
          ]}
        >
          <Input prefix={<UserOutlined />} placeholder="Nome completo do usuário" size="large" />
        </Form.Item>

        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Por favor, insira o email' },
            { type: 'email', message: 'Por favor, insira um email válido' }
          ]}
        >
          <Input prefix={<MailOutlined />} placeholder="email@exemplo.com" size="large" />
        </Form.Item>

        <Form.Item
          name="password"
          label="Senha"
          rules={[{ validator: validatePassword }]}
          help="Mínimo 8 caracteres, com letras maiúsculas, minúsculas e números"
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Senha do usuário"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="authorization"
          label="Nível de autorização"
          rules={[{ required: true, message: 'Por favor, selecione o nível de autorização' }]}
        >
          <Select size="large" placeholder="Selecione o nível">
            <Select.Option value="municipal">Municipal</Select.Option>
            <Select.Option value="estadual">Estadual</Select.Option>
            <Select.Option value="federal">Federal</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="is_superuser"
          label="Superusuário"
          valuePropName="checked"
          tooltip="Superusuários têm acesso total ao sistema, incluindo gestão de outros usuários"
        >
          <Switch
            checkedChildren={<SafetyOutlined />}
            unCheckedChildren={<UserOutlined />}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};
