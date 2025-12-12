/**
 * Componente de tabela de listagem de usuários
 */
import React from 'react';
import { Table, Tag, Button, Space, Tooltip, Popconfirm } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CrownOutlined,
  UserOutlined
} from '@ant-design/icons';
import type { User } from '../../services/authService';
import dayjs from 'dayjs';

interface UserTableProps {
  users: User[];
  loading: boolean;
  onEdit: (user: User) => void;
  onDelete: (userId: string) => void;
  onToggleActive: (userId: string, isActive: boolean) => void;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  loading,
  onEdit,
  onDelete,
  onToggleActive
}) => {
  const columns: ColumnsType<User> = [
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      sorter: (a, b) => a.nome.localeCompare(b.nome),
      render: (nome: string, record: User) => (
        <Space>
          {record.is_superuser ? (
            <CrownOutlined style={{ color: '#f59e0b' }} />
          ) : (
            <UserOutlined style={{ color: '#64748b' }} />
          )}
          <span style={{ fontWeight: 500 }}>{nome}</span>
        </Space>
      )
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      sorter: (a, b) => a.email.localeCompare(b.email)
    },
    {
      title: 'Tipo',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      filters: [
        { text: 'Superusuário', value: true },
        { text: 'Usuário comum', value: false }
      ],
      onFilter: (value, record) => record.is_superuser === value,
      render: (isSuperuser: boolean) =>
        isSuperuser ? (
          <Tag color="gold" icon={<CrownOutlined />}>
            Superusuário
          </Tag>
        ) : (
          <Tag color="blue" icon={<UserOutlined />}>
            Usuário
          </Tag>
        )
    },
    {
      title: 'Autorização',
      dataIndex: 'is_authorized',
      key: 'is_authorized',
      filters: [
        { text: 'Autorizado', value: true },
        { text: 'Pendente', value: false }
      ],
      onFilter: (value, record) => record.is_authorized === value,
      render: (isAuthorized: boolean) =>
        isAuthorized ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>
            Autorizado
          </Tag>
        ) : (
          <Tag color="warning" icon={<CloseCircleOutlined />}>
            Pendente
          </Tag>
        )
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      filters: [
        { text: 'Ativo', value: true },
        { text: 'Inativo', value: false }
      ],
      onFilter: (value, record) => record.is_active === value,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>
            Ativo
          </Tag>
        ) : (
          <Tag color="error" icon={<CloseCircleOutlined />}>
            Inativo
          </Tag>
        )
    },
    {
      title: 'Criado em',
      dataIndex: 'created_at',
      key: 'created_at',
      sorter: (a, b) => dayjs(a.created_at).unix() - dayjs(b.created_at).unix(),
      render: (date: string) => dayjs(date).format('DD/MM/YYYY HH:mm')
    },
    {
      title: 'Ações',
      key: 'actions',
      fixed: 'right' as const,
      width: 200,
      render: (_: unknown, record: User) => (
        <Space size="small">
          <Tooltip title="Editar usuário">
            <Button
              type="primary"
              icon={<EditOutlined />}
              size="small"
              onClick={() => onEdit(record)}
            />
          </Tooltip>

          <Tooltip title={record.is_active ? 'Desativar usuário' : 'Ativar usuário'}>
            <Popconfirm
              title={`Tem certeza que deseja ${record.is_active ? 'desativar' : 'ativar'} este usuário?`}
              onConfirm={() => onToggleActive(record.id, !record.is_active)}
              okText="Sim"
              cancelText="Não"
            >
              <Button
                type={record.is_active ? 'default' : 'primary'}
                icon={record.is_active ? <CloseCircleOutlined /> : <CheckCircleOutlined />}
                size="small"
                danger={record.is_active}
              />
            </Popconfirm>
          </Tooltip>

          <Tooltip title="Desativar usuário">
            <Popconfirm
              title="Tem certeza que deseja desativar este usuário?"
              description="O usuário será marcado como inativo e não poderá mais acessar o sistema. Você poderá reativá-lo depois."
              onConfirm={() => onDelete(record.id)}
              okText="Sim, desativar"
              cancelText="Cancelar"
              okButtonProps={{ danger: true }}
            >
              <Button type="primary" danger icon={<DeleteOutlined />} size="small" />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <Table
      columns={columns}
      dataSource={users}
      loading={loading}
      rowKey="id"
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showTotal: (total) => `Total: ${total} usuário(s)`,
        pageSizeOptions: ['10', '20', '50', '100']
      }}
      scroll={{ x: 1000 }}
      bordered
      style={{ background: '#fff' }}
    />
  );
};
