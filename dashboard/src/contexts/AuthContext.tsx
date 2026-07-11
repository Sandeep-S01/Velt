import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { AuthContext, type User } from './auth-context';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const userData = await api.get<User>('/auth/me');
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching current user:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const tokenResponse = await api.post<{ access_token: string; token_type: string }>(
      '/auth/token',
      formData
    );
    
    localStorage.setItem('token', tokenResponse.access_token);
    await fetchCurrentUser();
  };

  const register = async (email: string, fullName: string, password: string) => {
    await api.post<User>('/auth/register', {
      email,
      full_name: fullName,
      password,
    });
    // Auto-login after registration
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsLoading(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
