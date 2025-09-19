import { valFromRank, suitIcon, typeLabel } from './utils.js';
import { state } from './state.js';

export function render(run){
  state.run = run;
  const r = run;

  // KPIs
  setText('runId', r.id || '—');
  setText('hp', `${r.hp}/${r.max_hp}`);
  setText('turn', r.turn);
  setText('status', r.status);
  setText('power', r.power ?? 0);
  setText('score', r.score_total ?? 0);
  setText('emptied', r.emptied_this_turn ?? 0);

  // banner
  const banner = document.getElementById('banner');
  banner.innerHTML = r.status==='lost'
    ? `<div class="card" style="border-color:#5a2b2b;background:#221416">Você caiu em batalha. 😵</div>`
    : r.status==='won'
      ? `<div class="card" style="border-color:#2b5a3a;background:#142219">Vitória! 🏆</div>`
      : '';

  // board
  const boardEl = document.getElementById('board');
  boardEl.innerHTML = '';
  (r.board || []).forEach((slot, i) => {
    const el = document.createElement('div'); el.className='slot';
    if(!slot){
      el.innerHTML = `<div class="top"><div class="badge">Vazio</div><div class="muted mono">#${i+1}</div></div><div class="muted">—</div>`;
      return boardEl.appendChild(el);
    }
    const c = slot.card, t = slot.type, held = slot.held||0;
    const val = valFromRank(c.rank);
    const canFight = t==='enemy' && (r.power ?? 0) >= val && r.status==='ongoing';

    let badge = 'badge';
    if(t==='enemy') badge+=' enemy'; if(t==='weapon') badge+=' weapon'; if(t==='heal') badge+=' heal';

    el.innerHTML = `
      <div class="top">
        <div class="${badge}">${typeLabel(t)}</div>
        <div class="muted mono">slot #${i+1}</div>
      </div>
      <div>
        <h3 class="title">${suitIcon(c.suit)} <span class="mono">${c.rank}</span> <span class="muted">(${val})</span></h3>
        ${t==='enemy'?`<div class="held">Mantido: ${held}/2 turnos</div>`:''}
        <div class="actions">
          ${t==='weapon'?`
            <button class="btn ok" data-action="equip" data-idx="${i}">Equipar ♦️${val}</button>
            <button class="btn secondary" data-action="discard" data-idx="${i}">Descartar</button>
          `:''}
          ${t==='heal'?`
            <button class="btn ok" data-action="use_heal" data-idx="${i}">Usar ♥️${val}</button>
            <button class="btn secondary" data-action="discard" data-idx="${i}">Descartar</button>
          `:''}
          ${t==='enemy'?`
            <button class="btn ${canFight?'ok':'secondary'}" data-action="fight" data-idx="${i}" ${canFight?'':'disabled'}>Lutar (${val})</button>
            <button class="btn danger" data-action="pay_life" data-idx="${i}">Pagar Vida ${val}</button>
          `:''}
        </div>
      </div>`;
    boardEl.appendChild(el);
  });

  document.getElementById('endTurn').disabled = !canEndTurn(r);
}

export function log(msg){
  const el = document.getElementById('log');
  const time = new Date().toLocaleTimeString();
  el.innerHTML = `<div>• [${time}] ${msg}</div>` + el.innerHTML;
}

function setText(id, txt){ const el=document.getElementById(id); if(el) el.textContent = txt; }
function canEndTurn(r){
  if ((r.emptied_this_turn||0) < 2) return false;
  if ((r.board||[]).some(s=>s && s.type==='weapon')) return false;
  return true;
}
