/**
 * Componente de tabela de listagem de usuários
 */
import React from 'react';
import { Table, Tag, Button, Space, Tooltip, Popconfirm, Card, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  EditOutlined,
  KeyOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CrownOutlined,
  UserOutlined
} from '@ant-design/icons';
import type { User } from '../../services/authService';
import { useAuthStore } from '../../stores/authStore';
import { isAtivo } from '../../services/userManagementService';
import { useIsMobile } from '../../hooks/useIsMobile';
import dayjs from 'dayjs';

const { Text } = Typography;

interface UserTableProps {
  users: User[];
  loading: boolean;
  onEdit: (user: User) => void;
  onResetPassword: (user: User) => void;
  onToggleActive: (userId: string, isActive: boolean) => void;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  loading,
  onEdit,
  onResetPassword,
  onToggleActive
}) => {
  const currentUserId = useAuthStore((state) => state.user?.id);
  const isMobile = useIsMobile();

  // Ações compartilhadas entre a tabela (desktop) e os cards (mobile)
  const renderActions = (record: User) => (
    <Space size="small">
      <Tooltip title="Editar usuário">
        <Button
          type="primary"
          icon={<EditOutlined />}
          size="small"
          onClick={() => onEdit(record)}
        />
      </Tooltip>

      <Tooltip title="Redefinir senha">
        <Button
          icon={<KeyOutlined />}
          size="small"
          onClick={() => onResetPassword(record)}
        />
      </Tooltip>

      {record.id !== currentUserId && (
        <Tooltip title={isAtivo(record) ? 'Desativar usuário' : 'Ativar usuário'}>
          <Popconfirm
            title={isAtivo(record) ? 'Desativar este usuário?' : 'Ativar este usuário?'}
            description={
              isAtivo(record)
                ? 'Ele deixará de conseguir entrar no sistema. Você poderá reativá-lo depois.'
                : 'Ele voltará a conseguir entrar no sistema.'
            }
            onConfirm={() => onToggleActive(record.id, !isAtivo(record))}
            okText={isAtivo(record) ? 'Sim, desativar' : 'Sim, ativar'}
            cancelText="Cancelar"
            okButtonProps={{ danger: isAtivo(record) }}
          >
            <Button
              type={isAtivo(record) ? 'default' : 'primary'}
              icon={isAtivo(record) ? <CloseCircleOutlined /> : <CheckCircleOutlined />}
              size="small"
              danger={isAtivo(record)}
            />
          </Popconfirm>
        </Tooltip>
      )}
    </Space>
  );

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
            <UserOutlined style={{ color: 'var(--text-secondary)' }} />
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
      title: 'Perfil',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      filters: [
        { text: 'Administrador', value: true },
        { text: 'Usuário', value: false }
      ],
      onFilter: (value, record) => record.is_superuser === value,
      render: (isSuperuser: boolean) =>
        isSuperuser ? (
          <Tag color="gold" icon={<CrownOutlined />}>
            Administrador
          </Tag>
        ) : (
          <Tag color="blue" icon={<UserOutlined />}>
            Usuário
          </Tag>
        )
    },
    {
      title: 'Situação',
      key: 'situacao',
      render: (_: unknown, record: User) =>
        isAtivo(record) ? (
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
      width: 150,
      render: (_: unknown, record: User) => renderActions(record)
    }
  ];

  if (isMobile) {
    return (
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {users.map((record) => (
          <Card
            key={record.id}
            size="small"
            loading={loading && !users.length}
            style={{ borderRadius: 8, border: '1px solid var(--border-color)' }}
          >
            <Space direction="vertical" size={8} style={{ width: '100%' }}>
              <Space>
                {record.is_superuser ? (
                  <CrownOutlined style={{ color: '#f59e0b' }} />
                ) : (
                  <UserOutlined style={{ color: 'var(--text-secondary)' }} />
                )}
                <Text strong>{record.nome}</Text>
              </Space>
              <Text type="secondary" style={{ fontSize: 13, wordBreak: 'break-all' }}>
                {record.email}
              </Text>
              <Space size={[4, 4]} wrap>
                {record.is_superuser ? (
                  <Tag color="gold" icon={<CrownOutlined />}>Administrador</Tag>
                ) : (
                  <Tag color="blue" icon={<UserOutlined />}>Usuário</Tag>
                )}
                {isAtivo(record) ? (
                  <Tag color="success" icon={<CheckCircleOutlined />}>Ativo</Tag>
                ) : (
                  <Tag color="error" icon={<CloseCircleOutlined />}>Inativo</Tag>
                )}
              </Space>
              <Text type="secondary" style={{ fontSize: 12 }}>
                Criado em {dayjs(record.created_at).format('DD/MM/YYYY HH:mm')}
              </Text>
              {renderActions(record)}
            </Space>
          </Card>
        ))}
      </Space>
    );
  }

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
      style={{ background: 'var(--bg-container)' }}
    />
  );
};
