import { getCookie } from './utils.js';

async function request(url, method='GET', body=null){
  const headers = { 'Content-Type':'application/json' };
  const csrf = getCookie('csrftoken');
  if (csrf) headers['X-CSRFToken'] = csrf;
  const res = await fetch(url, { method, headers, body: body?JSON.stringify(body):null });
  if(!res.ok){
    let t = await res.text();
    try { t = JSON.parse(t).detail || t; } catch {}
    throw new Error(t || (res.status+' '+res.statusText));
  }
  return await res.json();
}

export const API = {
  start: (seed,max_hp) => request('/api/start','POST',{seed,max_hp}),
  getRun: (id) => request(`/api/run/${id}`),
  equip: (id, idx) => request(`/api/run/${id}/equip/${idx}`,'POST'),
  discard: (id, idx) => request(`/api/run/${id}/discard/${idx}`,'POST'),
  useHeal: (id, idx) => request(`/api/run/${id}/use_heal/${idx}`,'POST'),
  fight: (id, idx) => request(`/api/run/${id}/fight/${idx}`,'POST'),
  payLife: (id, idx) => request(`/api/run/${id}/pay_life/${idx}`,'POST'),
  endTurn: (id) => request(`/api/run/${id}/end_turn`,'POST'),
  submitScore: (id, player_name) => request(`/api/run/${id}/score`,'POST',{player_name}),
};
