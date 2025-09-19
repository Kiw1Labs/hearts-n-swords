// static/js/api.js
import { getCookie } from './utils.js';

// Define a base da API a partir de window.API_BASE (setado no config.js do Pages).
// Se não houver, usa caminho relativo (funciona no Django local).
let API_BASE = (window.API_BASE || "").replace(/\/$/, "");

export function setApiBase(base) {
  API_BASE = (base || "").replace(/\/$/, "");
}

async function request(path, method = "GET", body = null) {
  const url = `${API_BASE}${path}`;
  const headers = { "Content-Type": "application/json" };

  // Envia CSRF apenas em same-origin (quando estamos usando os templates do Django).
  const csrf = getCookie("csrftoken");
  if (csrf && !API_BASE) headers["X-CSRFToken"] = csrf;

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (!res.ok) {
    let msg;
    try { const j = await res.json(); msg = j.detail || j.message || JSON.stringify(j); }
    catch { msg = await res.text(); }
    throw new Error(msg || `${res.status} ${res.statusText}`);
  }
  return await res.json();
}

export const API = {
  start: (seed, max_hp) => request("/api/start", "POST", { seed, max_hp }),
  getRun: (id) => request(`/api/run/${id}`),
  equip: (id, idx) => request(`/api/run/${id}/equip/${idx}`, "POST"),
  discard: (id, idx) => request(`/api/run/${id}/discard/${idx}`, "POST"),
  useHeal: (id, idx) => request(`/api/run/${id}/use_heal/${idx}`, "POST"),
  fight: (id, idx) => request(`/api/run/${id}/fight/${idx}`, "POST"),
  payLife: (id, idx) => request(`/api/run/${id}/pay_life/${idx}`, "POST"),
  endTurn: (id) => request(`/api/run/${id}/end_turn`, "POST"),
  submitScore: (id, player_name) => request(`/api/run/${id}/score`, "POST", { player_name }),
};
