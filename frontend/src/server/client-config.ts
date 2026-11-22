import type { Hono } from 'hono'
import type { AppContext } from '../../worker.js'

type ClientConfigEnv = {
  VITE_API_URL?: string
  VITE_AUTH0_DOMAIN?: string
  VITE_AUTH0_CLIENT_ID?: string
  VITE_AUTH0_AUDIENCE?: string
}

function httpsUrl(value: string | undefined): string | null {
  if (!value) return null
  try {
    const url = new URL(value)
    return ['http:', 'https:'].includes(url.protocol) ? url.origin : null
  } catch { return null }
}

/** Public SPA configuration only. No provider secret is eligible for this route. */
export function clientConfigResponse(env: ClientConfigEnv): Response {
  const apiUrl = httpsUrl(env.VITE_API_URL)
  const auth0Domain = env.VITE_AUTH0_DOMAIN?.trim()
  const auth0ClientId = env.VITE_AUTH0_CLIENT_ID?.trim()
  const auth0Audience = env.VITE_AUTH0_AUDIENCE?.trim() || undefined
  const headers = { 'Cache-Control': 'no-store' }

  if (!apiUrl || !auth0Domain || !auth0ClientId) {
    return Response.json({ error: 'Public app configuration unavailable' }, { status: 503, headers })
  }
  return Response.json({ apiUrl, auth0Domain, auth0ClientId, auth0Audience }, { headers })
}

export function registerClientConfigRoute(app: Hono<AppContext>): void {
  app.get('/api/client-config', (c) => clientConfigResponse(c.env))
}