/**
 * Modal para edição de usuário existente
 */
import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Switch, App } from 'antd';
import { UserOutlined, MailOutlined, SafetyOutlined } from '@ant-design/icons';
import type { User } from '../../services/authService';
import type { UpdateUserRequest } from '../../services/userManagementService';

interface EditUserModalProps {
  open: boolean;
  user: User | null;
  onClose: () => void;
  onSubmit: (userId: string, data: UpdateUserRequest) => Promise<void>;
}

export const EditUserModal: React.FC<EditUserModalProps> = ({
  open,
  user,
  onClose,
  onSubmit
}) => {
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // Preencher o formulário quando o usuário for selecionado
  useEffect(() => {
    if (user && open) {
      form.setFieldsValue({
        nome: user.nome,
        email: user.email,
        is_active: user.is_active,
        is_authorized: user.is_authorized,
        is_superuser: user.is_superuser
      });
    }
  }, [user, open, form]);

  const handleSubmit = async () => {
    if (!user) return;

    try {
      const values = await form.validateFields();
      setLoading(true);

      await onSubmit(user.id, values);

      message.success('Usuário atualizado com sucesso!');
      onClose();
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Erro ao atualizar usuário: ${error.message}`);
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
      title={`Editar Usuário: ${user?.nome || ''}`}
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      confirmLoading={loading}
      okText="Salvar"
      cancelText="Cancelar"
      width={600}
    >
      <Form form={form} layout="vertical">
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
          name="is_authorized"
          label="Usuário autorizado"
          valuePropName="checked"
          tooltip="Novo usuários precisam ser autorizados pelo administrador para acessar o sistema"
        >
          <Switch checkedChildren="Autorizado" unCheckedChildren="Pendente" />
        </Form.Item>

        <Form.Item name="is_active" label="Usuário ativo" valuePropName="checked">
          <Switch checkedChildren="Ativo" unCheckedChildren="Inativo" />
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
