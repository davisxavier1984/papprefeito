/**
 * Página de administração de usuários
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Input,
  Select,
  App,
  Typography,
  Statistic,
  Row,
  Col,
  Spin
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CrownOutlined
} from '@ant-design/icons';
import { UserTable } from '../../components/Admin/UserTable';
import { CreateUserModal } from '../../components/Admin/CreateUserModal';
import { EditUserModal } from '../../components/Admin/EditUserModal';
import { userManagementService } from '../../services/userManagementService';
import type { User } from '../../services/authService';
import type { CreateUserRequest, UpdateUserRequest } from '../../services/userManagementService';

const { Title } = Typography;

export const UserManagement: React.FC = () => {
  const { message } = App.useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | undefined>(true);
  const [filterSuperuser, setFilterSuperuser] = useState<boolean | undefined>(undefined);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Carregar usuários
  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await userManagementService.listUsers({
        is_active: filterActive,
        is_superuser: filterSuperuser,
        search: searchText || undefined
      });
      setUsers(response.users);
    } catch (error) {
      message.error('Erro ao carregar usuários');
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  // Carregar usuários ao montar o componente ou quando os filtros mudarem
  useEffect(() => {
    loadUsers();
  }, [filterActive, filterSuperuser]);

  // Criar usuário
  const handleCreateUser = async (data: CreateUserRequest) => {
    try {
      await userManagementService.createUser(data);
      await loadUsers();
      setCreateModalOpen(false);
    } catch (error) {
      throw new Error('Falha ao criar usuário. Verifique os dados e tente novamente.');
    }
  };

  // Editar usuário
  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setEditModalOpen(true);
  };

  const handleUpdateUser = async (userId: string, data: UpdateUserRequest) => {
    try {
      await userManagementService.updateUser(userId, data);
      await loadUsers();
      setEditModalOpen(false);
      setSelectedUser(null);
    } catch (error) {
      throw new Error('Falha ao atualizar usuário. Verifique os dados e tente novamente.');
    }
  };

  // Alternar status ativo
  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      if (isActive) {
        await userManagementService.activateUser(userId);
        message.success('Usuário ativado com sucesso');
      } else {
        await userManagementService.deactivateUser(userId);
        message.success('Usuário desativado com sucesso');
      }
      await loadUsers();
    } catch (error) {
      message.error('Erro ao alterar status do usuário');
      console.error('Erro ao alternar status:', error);
    }
  };

  // Desativar usuário
  const handleDeleteUser = async (userId: string) => {
    try {
      await userManagementService.deleteUser(userId);
      message.success('Usuário desativado com sucesso');
      await loadUsers();
    } catch (error) {
      message.error('Erro ao desativar usuário');
      console.error('Erro ao desativar usuário:', error);
    }
  };

  // Estatísticas
  const totalUsers = users.length;
  const activeUsers = users.filter((u) => u.is_active).length;
  const inactiveUsers = users.filter((u) => !u.is_active).length;
  const superusers = users.filter((u) => u.is_superuser).length;

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <TeamOutlined /> Gestão de Usuários
      </Title>

      {/* Estatísticas */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total de Usuários"
              value={totalUsers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#0ea5e9' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Usuários Ativos"
              value={activeUsers}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#22c55e' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Usuários Inativos"
              value={inactiveUsers}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ef4444' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Superusuários"
              value={superusers}
              prefix={<CrownOutlined />}
              valueStyle={{ color: '#f59e0b' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filtros e ações */}
      <Card style={{ marginBottom: 24 }}>
        <Space
          direction="vertical"
          size="middle"
          style={{ width: '100%' }}
        >
          <Space wrap>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalOpen(true)}
              size="large"
            >
              Novo Usuário
            </Button>
          </Space>

          <Space wrap style={{ width: '100%' }}>
            <Input
              placeholder="Buscar por nome ou email"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={loadUsers}
              style={{ width: 300 }}
              allowClear
            />

            <Select
              placeholder="Status"
              style={{ width: 150 }}
              value={filterActive}
              onChange={setFilterActive}
              allowClear
            >
              <Select.Option value={true}>Ativos</Select.Option>
              <Select.Option value={false}>Inativos</Select.Option>
            </Select>

            <Select
              placeholder="Tipo"
              style={{ width: 150 }}
              value={filterSuperuser}
              onChange={setFilterSuperuser}
              allowClear
            >
              <Select.Option value={true}>Superusuários</Select.Option>
              <Select.Option value={false}>Usuários comuns</Select.Option>
            </Select>

            <Button icon={<SearchOutlined />} onClick={loadUsers}>
              Buscar
            </Button>
          </Space>
        </Space>
      </Card>

      {/* Tabela de usuários */}
      <Card>
        {loading && !users.length ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
          </div>
        ) : (
          <UserTable
            users={users}
            loading={loading}
            onEdit={handleEditUser}
            onDelete={handleDeleteUser}
            onToggleActive={handleToggleActive}
          />
        )}
      </Card>

      {/* Modais */}
      <CreateUserModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreateUser}
      />

      <EditUserModal
        open={editModalOpen}
        user={selectedUser}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedUser(null);
        }}
        onSubmit={handleUpdateUser}
      />
    </div>
  );
};
