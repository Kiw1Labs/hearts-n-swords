import { API } from './api.js';
import { state, setRun } from './state.js';
import { render, log } from './ui.js';

export function attachEvents(){
  // start form
  document.getElementById('startForm').addEventListener('submit', async (e)=>{
    e.preventDefault();
    const seed = document.getElementById('seed').value || 'demo';
    const max_hp = parseInt(document.getElementById('maxhp').value || '20',10);
    const run = await API.start(seed, max_hp);
    setRun(run); render(run); log(`Run iniciada (seed=${seed})`);
  });

  document.getElementById('refreshBtn').addEventListener('click', async ()=>{
    if(!state.id) return;
    const run = await API.getRun(state.id);
    setRun(run); render(run);
  });

  // board delegation
  document.getElementById('board').addEventListener('click', async (e)=>{
    const btn = e.target.closest('button[data-action]');
    if(!btn || !state.id) return;
    const action = btn.dataset.action;
    const idx = parseInt(btn.dataset.idx,10);
    try{
      let run;
      if(action==='equip') run = await API.equip(state.id, idx);
      else if(action==='discard') run = await API.discard(state.id, idx);
      else if(action==='use_heal') run = await API.useHeal(state.id, idx);
      else if(action==='fight') run = await API.fight(state.id, idx);
      else if(action==='pay_life'){
        if(!confirm('Confirmar: pagar vida para descartar este inimigo?')) return;
        run = await API.payLife(state.id, idx);
      }
      if(run){ setRun(run); render(run); log(`${action} no slot ${idx+1}`); }
    }catch(err){ alert(err.message); }
  });

  // end turn
  document.getElementById('endTurn').addEventListener('click', async ()=>{
    try{
      const run = await API.endTurn(state.id);
      setRun(run); render(run); log(`Fim do turno. Novo turno: ${run.turn}`);
    }catch(err){ alert(err.message); }
  });
}
