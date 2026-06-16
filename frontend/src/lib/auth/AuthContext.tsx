"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import {
  isAuthenticated,
  getCurrentUser,
  clearToken,
  ApiClientError,
  type UserResponse,
} from "@/lib/api/client";

interface AuthState {
  /** The currently authenticated user, or null if not logged in. */
  user: UserResponse | null;
  /** True while the initial /me request is in flight. */
  loading: boolean;
  /** Re-fetch the current user from /api/v1/me. */
  refresh: () => Promise<void>;
  /** Clear the session (token + user state). Does NOT redirect. */
  clearSession: () => void;
}

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  refresh: async () => {},
  clearSession: () => {},
});

/**
 * Canonical auth provider.
 *
 * Every component that needs the current user MUST read from this context.
 * Components MUST NOT hold their own UserResponse state or call
 * getCurrentUser() directly — they use useAuth() instead.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!isAuthenticated()) {
      setUser(null);
      return;
    }
    try {
      const u = await getCurrentUser();
      setUser(u);
    } catch (err) {
      setUser(null);
      // Zombie token guard: if /me returns 401 (expired/invalid token),
      // clear the stale token from localStorage so isAuthenticated()
      // returns false on subsequent checks.
      if (err instanceof ApiClientError && (err.status === 401 || err.code === 'UNAUTHORIZED')) {
        clearToken();
      }
    }
  }, []);

  const clearSession = useCallback(() => {
    clearToken();
    setUser(null);
    window.dispatchEvent(new CustomEvent("auth-changed"));
  }, []);

  // Initial fetch
  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  // Listen for auth-changed events (dispatched after login/register/verify/logout)
  useEffect(() => {
    const handler = () => {
      refresh();
    };
    window.addEventListener("auth-changed", handler);
    return () => window.removeEventListener("auth-changed", handler);
  }, [refresh]);

  return (
    <AuthContext.Provider value={{ user, loading, refresh, clearSession }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access the canonical auth state.
 *
 * Usage:
 *   const { user, loading, refresh, clearSession } = useAuth();
 *
 * - `user` is the single source of truth for the current user identity.
 * - Never call getCurrentUser() directly in components.
 */
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  // If used outside provider, fall back to empty state (defensive).
  if (!ctx) {
    return { user: null, loading: false, refresh: async () => {}, clearSession: () => {} };
  }
  return ctx;
}
