import { fetchData, getApiUrl, postData } from "./base"
import { resetNotificationsCache } from "./notifications"

export type SessionUser = {
  username: string
  email: string
  name: string
  uuid: string
  is_superuser: boolean
  require_reset: boolean
  has_password: boolean
}

// Public settings for the login and signup pages; /api/instance-settings/ needs a login.
export type LoginConfig = {
  oidc: {
    enabled: boolean
    button_label: string
    auto_redirect: boolean
  }
  local_login_enabled: boolean
  allow_email_login: boolean
  allow_signup: boolean
}

export async function getLoginConfig() {
  return fetchData<LoginConfig>("/api/login-config/")
}

// A full page navigation, since the provider redirects back to the backend callback.
export function startOIDCLogin() {
  resetNotificationsCache()
  window.location.assign(getApiUrl("/api/oidc/authenticate/"))
}

export async function login(identifier: string, password: string) {
  const result = await postData<{ detail: string; user: SessionUser }>("/api/login/", {
    identifier,
    password,
  })
  resetNotificationsCache()
  return result
}

export async function signup(
  username: string,
  email: string,
  name: string,
  password: string,
) {
  const result = await postData<{ detail: string; user: SessionUser }>('/api/signup/', {
    username,
    email,
    name,
    password,
  })
  resetNotificationsCache()
  return result
}

export async function logout() {
  const result = await postData<{ detail: string }>("/api/logout/", {})
  resetNotificationsCache()
  return result
}

export async function getCurrentSession() {
  return fetchData<{ authenticated: boolean; user: SessionUser | null }>("/api/me/")
}

export async function resetCredentials(username: string, password: string) {
  return postData<{ detail: string; user: SessionUser }>('/api/credentials/reset/', {
    username,
    password,
  })
}

export async function updatePersonalAccount(
  username: string,
  name: string,
  password?: string,
) {
  return postData<{ detail: string; user: SessionUser }>('/api/credentials/reset/', {
    username,
    name,
    ...(password ? { password } : {}),
  })
}
