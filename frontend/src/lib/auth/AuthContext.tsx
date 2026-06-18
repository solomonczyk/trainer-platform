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

export type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthState {
  /** The currently authenticated user, or null if not logged in. */
  user: UserResponse | null;
  /** Explicit auth lifecycle status — never conflates "not loaded" with "not authenticated". */
  status: AuthStatus;
  /** True while the initial /me request is in flight. */
  loading: boolean;
  /** Re-fetch the current user from /api/v1/me. */
  refresh: () => Promise<void>;
  /** Clear the session (token + user state). Does NOT redirect. */
  clearSession: () => void;
}

const AuthContext = createContext<AuthState>({
  user: null,
  status: "loading",
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
 *
 * Bootstrap logic:
 * - initial status = "loading"
 * - no token → user=null, status="unauthenticated", loading=false
 * - /me 200 → user=response, status="authenticated", loading=false
 * - /me 401 → clearToken(), user=null, status="unauthenticated", loading=false
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<AuthStatus>("loading");

  const refresh = useCallback(async () => {
    if (!isAuthenticated()) {
      setUser(null);
      setStatus("unauthenticated");
      return;
    }
    try {
      const u = await getCurrentUser();
      setUser(u);
      setStatus("authenticated");
    } catch (err) {
      setUser(null);
      setStatus("unauthenticated");
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
    setStatus("unauthenticated");
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
    <AuthContext.Provider value={{ user, status, loading, refresh, clearSession }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access the canonical auth state.
 *
 * Usage:
 *   const { user, status, loading, refresh, clearSession } = useAuth();
 *
 * - `user` is the single source of truth for the current user identity.
 * - `status` is "loading" | "authenticated" | "unauthenticated".
 * - Never call getCurrentUser() directly in components.
 */
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  // If used outside provider, fall back to empty state (defensive).
  if (!ctx) {
    return {
      user: null,
      status: "unauthenticated",
      loading: false,
      refresh: async () => {},
      clearSession: () => {},
    };
  }
  return ctx;
}
