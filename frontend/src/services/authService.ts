/**
 * Serviço de autenticação
 */
import axios, { type AxiosInstance } from 'axios';
import { useAuthStore } from '../stores/authStore';

// Tipos
export interface User {
  id: string;
  email: string;
  nome: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  nome: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserUpdate {
  nome?: string;
  email?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
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

class AuthService {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/auth`,
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

    // Interceptor para refresh automático do token
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Se o erro for 401 e não for uma tentativa de retry
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Tenta renovar o token
            const newAccessToken = await this.refreshAccessToken();

            // Atualiza o header da requisição original
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

            // Refaz a requisição original
            return this.client(originalRequest);
          } catch (refreshError) {
            // Se falhar ao renovar, faz logout
            useAuthStore.getState().logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Registra um novo usuário
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await this.client.post<User>('/register', data);
    return response.data;
  }

  /**
   * Faz login do usuário
   */
  async login(credentials: LoginRequest): Promise<{ user: User; tokens: Token }> {
    // Primeiro, faz login para obter os tokens
    const tokenResponse = await this.client.post<Token>('/login', credentials);
    const tokens = tokenResponse.data;

    // Salva os tokens temporariamente
    useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token);

    // Busca os dados do usuário
    const user = await this.getCurrentUser();

    return { user, tokens };
  }

  /**
   * Renova o access token usando o refresh token
   */
  async refreshAccessToken(): Promise<string> {
    // Se já existe uma promessa de refresh em andamento, retorna ela
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
        const refreshToken = useAuthStore.getState().refreshToken;

        if (!refreshToken) {
          throw new Error('Refresh token não encontrado');
        }

        const response = await axios.post<Token>(
          `${API_BASE_URL}/auth/refresh`,
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`
            }
          }
        );

        const tokens = response.data;

        // Atualiza os tokens na store
        useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token);

        return tokens.access_token;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  /**
   * Obtém os dados do usuário atual
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/me');
    return response.data;
  }

  /**
   * Atualiza os dados do usuário atual
   */
  async updateProfile(data: UserUpdate): Promise<User> {
    const response = await this.client.put<User>('/me', data);
    return response.data;
  }

  /**
   * Altera a senha do usuário
   */
  async changePassword(data: PasswordChange): Promise<ApiResponse<null>> {
    const response = await this.client.post<ApiResponse<null>>('/me/change-password', data);
    return response.data;
  }

  /**
   * Faz logout do usuário
   */
  async logout(): Promise<void> {
    try {
      await this.client.post('/logout');
    } catch (error) {
      // Ignora erros de logout no servidor
      console.error('Erro ao fazer logout no servidor:', error);
    } finally {
      // Limpa os dados locais
      useAuthStore.getState().logout();
    }
  }

  /**
   * Desativa a conta do usuário
   */
  async deleteAccount(): Promise<ApiResponse<null>> {
    const response = await this.client.delete<ApiResponse<null>>('/me');
    return response.data;
  }

  /**
   * Verifica se o usuário está autenticado
   */
  isAuthenticated(): boolean {
    return useAuthStore.getState().isAuthenticated;
  }

  /**
   * Obtém o token de acesso atual
   */
  getAccessToken(): string | null {
    return useAuthStore.getState().accessToken;
  }
}

// Instância singleton
export const authService = new AuthService();
