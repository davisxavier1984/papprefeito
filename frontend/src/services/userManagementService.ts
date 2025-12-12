/**
 * Serviço de gestão de usuários (apenas para superusuários)
 */
import axios, { type AxiosInstance } from 'axios';
import { useAuthStore } from '../stores/authStore';
import type { User } from './authService';

// Tipos específicos para gestão de usuários
export interface UserListResponse {
  users: User[];
  total: number;
}

export interface CreateUserRequest {
  email: string;
  nome: string;
  password: string;
  is_superuser?: boolean;
}

export interface UpdateUserRequest {
  nome?: string;
  email?: string;
  is_active?: boolean;
  is_authorized?: boolean;
  is_superuser?: boolean;
}

export interface UserFilters {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  is_superuser?: boolean;
  search?: string;
}

// Configuração base da API
const DEFAULT_API_BASE_URL = 'http://localhost:8000/api';

const resolveApiBaseUrl = (): string => {
  const raw = import.meta.env.VITE_API_BASE_URL?.trim();
  if (!raw) {
    return DEFAULT_API_BASE_URL;
  }

  const sanitized = raw.replace(/\/+$/, '');
  return /\/api($|\/)/.test(sanitized) ? sanitized : `${sanitized}/api`;
};

const API_BASE_URL = resolveApiBaseUrl();

class UserManagementService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/users`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Interceptor para adicionar token nas requisições
    this.client.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor para tratar erros
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expirado, redirecionar para login
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Lista todos os usuários (apenas superusuário)
   */
  async listUsers(filters?: UserFilters): Promise<UserListResponse> {
    const params = new URLSearchParams();

    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters?.is_superuser !== undefined) params.append('is_superuser', filters.is_superuser.toString());
    if (filters?.search) params.append('search', filters.search);

    const response = await this.client.get<UserListResponse>('/', { params });

    return response.data;
  }

  /**
   * Obtém detalhes de um usuário específico
   */
  async getUser(userId: string): Promise<User> {
    const response = await this.client.get<User>(`/${userId}`);
    return response.data;
  }

  /**
   * Cria um novo usuário (apenas superusuário)
   */
  async createUser(data: CreateUserRequest): Promise<User> {
    const response = await this.client.post<User>('/', data);
    return response.data;
  }

  /**
   * Atualiza um usuário existente (apenas superusuário)
   */
  async updateUser(userId: string, data: UpdateUserRequest): Promise<User> {
    const response = await this.client.put<User>(`/${userId}`, data);
    return response.data;
  }

  /**
   * Desativa um usuário (soft delete)
   */
  async deactivateUser(userId: string): Promise<User> {
    const response = await this.client.put<User>(`/${userId}`, { is_active: false });
    return response.data;
  }

  /**
   * Ativa um usuário
   */
  async activateUser(userId: string): Promise<User> {
    const response = await this.client.put<User>(`/${userId}`, { is_active: true });
    return response.data;
  }

  /**
   * Deleta permanentemente um usuário (apenas superusuário)
   */
  async deleteUser(userId: string): Promise<void> {
    await this.client.delete(`/${userId}`);
  }
}

// Instância singleton
export const userManagementService = new UserManagementService();
