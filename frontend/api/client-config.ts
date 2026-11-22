import { clientConfigResponse } from '../src/server/client-config.js'

export default {
  fetch(request: Request): Response {
    if (request.method !== 'GET') {
      return new Response(null, { status: 405, headers: { Allow: 'GET' } })
    }
    const { VITE_API_URL, VITE_AUTH0_DOMAIN, VITE_AUTH0_CLIENT_ID, VITE_AUTH0_AUDIENCE } = process.env
    return clientConfigResponse({ VITE_API_URL, VITE_AUTH0_DOMAIN, VITE_AUTH0_CLIENT_ID, VITE_AUTH0_AUDIENCE })
  },
}