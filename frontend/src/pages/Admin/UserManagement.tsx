/**
 * Página de administração de usuários
 */
import React, { useState, useEffect, useMemo, useCallback } from 'react';
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
import { ResetPasswordModal } from '../../components/Admin/ResetPasswordModal';
import { userManagementService, isAtivo } from '../../services/userManagementService';
import { mensagemDeErro } from '../../utils/mensagemDeErro';
import type { User } from '../../services/authService';
import type { CreateUserRequest, UpdateUserRequest } from '../../services/userManagementService';

const { Title } = Typography;

export const UserManagement: React.FC = () => {
  const { message } = App.useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [filterSituacao, setFilterSituacao] = useState<'ativos' | 'inativos' | undefined>(undefined);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [senhaUser, setSenhaUser] = useState<User | null>(null);

  // Carrega todos os usuários; filtros e contagens são feitos na tela
  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await userManagementService.listUsers({ limit: 1000 });
      setUsers(response.users);
    } catch (error) {
      message.error(mensagemDeErro(error, 'Erro ao carregar usuários'));
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const filteredUsers = useMemo(() => {
    const termo = searchText.trim().toLowerCase();
    return users.filter((u) => {
      if (filterSituacao === 'ativos' && !isAtivo(u)) return false;
      if (filterSituacao === 'inativos' && isAtivo(u)) return false;
      if (termo && !u.nome.toLowerCase().includes(termo) && !u.email.toLowerCase().includes(termo)) {
        return false;
      }
      return true;
    });
  }, [users, filterSituacao, searchText]);

  // Criar usuário
  const handleCreateUser = async (data: CreateUserRequest) => {
    try {
      await userManagementService.createUser(data);
      await loadUsers();
      setCreateModalOpen(false);
    } catch (error) {
      throw new Error(mensagemDeErro(error, 'Verifique os dados e tente novamente.'));
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
      throw new Error(mensagemDeErro(error, 'Verifique os dados e tente novamente.'));
    }
  };

  // Redefinir senha
  const handleResetPassword = async (userId: string, password: string) => {
    try {
      await userManagementService.resetPassword(userId, password);
    } catch (error) {
      throw new Error(mensagemDeErro(error, 'Verifique a senha e tente novamente.'));
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
      message.error(mensagemDeErro(error, 'Erro ao alterar a situação do usuário'));
      console.error('Erro ao alternar status:', error);
    }
  };

  // Estatísticas
  const totalUsers = users.length;
  const activeUsers = users.filter(isAtivo).length;
  const inactiveUsers = totalUsers - activeUsers;
  const superusers = users.filter((u) => u.is_superuser).length;

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <TeamOutlined /> Gestão de Usuários
      </Title>

      {/* Estatísticas */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Total de Usuários"
              value={totalUsers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#0ea5e9' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Usuários Ativos"
              value={activeUsers}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#22c55e' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Usuários Inativos"
              value={inactiveUsers}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ef4444' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Administradores"
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
              style={{ width: 'min(300px, 100%)' }}
              allowClear
            />

            <Select
              placeholder="Situação"
              style={{ width: 150 }}
              value={filterSituacao}
              onChange={setFilterSituacao}
              allowClear
            >
              <Select.Option value="ativos">Ativos</Select.Option>
              <Select.Option value="inativos">Inativos</Select.Option>
            </Select>
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
            users={filteredUsers}
            loading={loading}
            onEdit={handleEditUser}
            onResetPassword={setSenhaUser}
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

      <ResetPasswordModal
        open={senhaUser !== null}
        user={senhaUser}
        onClose={() => setSenhaUser(null)}
        onSubmit={handleResetPassword}
      />
    </div>
  );
};
