/**
 * Modal para criação de novo usuário
 */
import React, { useState } from 'react';
import { Modal, Form, Input, Radio, Alert, App } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import type { CreateUserRequest } from '../../services/userManagementService';
import { validarSenha, REGRAS_SENHA } from '../../utils/senha';

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

  return (
    <Modal
      title="Criar Novo Usuário"
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      confirmLoading={loading}
      okText="Criar"
      cancelText="Cancelar"
      width="min(600px, 92vw)"
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          is_superuser: false
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
          rules={[{ validator: validarSenha }]}
          help={REGRAS_SENHA}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Senha do usuário"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="is_superuser"
          label="Perfil"
          tooltip="Administradores também gerenciam os usuários do sistema"
        >
          <Radio.Group optionType="button" buttonStyle="solid">
            <Radio value={false}>Usuário</Radio>
            <Radio value={true}>Administrador</Radio>
          </Radio.Group>
        </Form.Item>

        <Alert type="info" showIcon message="O usuário já poderá entrar com este email e senha." />
      </Form>
    </Modal>
  );
};
