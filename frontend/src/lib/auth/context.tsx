"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { AuthMeResponse } from "@/lib/api/types";
import { login as apiLogin, getMe } from "@/lib/api/endpoints";

interface AuthContextValue {
  user: AuthMeResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (telegramUsername: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthMeResponse | null>(null);
  const [token, setToken] = useState<string | null>(null);
  // Lazy initializer: only show loading spinner when a saved token exists.
  // This avoids calling setState synchronously inside the effect.
  const [isLoading, setIsLoading] = useState(
    () => typeof window !== "undefined" && !!localStorage.getItem("auth_token"),
  );

  // On mount: check localStorage for existing token, validate with /auth/me
  useEffect(() => {
    const savedToken = localStorage.getItem("auth_token");
    if (!savedToken) return;
    getMe()
      .then((me) => {
        setToken(savedToken);
        setUser(me);
      })
      .catch(() => {
        localStorage.removeItem("auth_token");
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (telegramUsername: string) => {
    const response = await apiLogin({ telegram_username: telegramUsername });
    localStorage.setItem("auth_token", response.access_token);
    setToken(response.access_token);
    // Fetch full user info
    const me = await getMe();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("auth_token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated: !!user, isLoading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
