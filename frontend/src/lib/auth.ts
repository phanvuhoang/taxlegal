export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: "admin" | "user";
}

export function getUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAuth(token: string, user: AuthUser) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export function isAdmin(): boolean {
  return getUser()?.role === "admin";
}
