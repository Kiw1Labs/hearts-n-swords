export function getCookie(name){
  const m = document.cookie.match(new RegExp('(^| )'+name+'=([^;]+)'));
  return m ? decodeURIComponent(m[2]) : null;
}
export function valFromRank(rank){
  if (typeof rank === 'number') return rank;
  const map = { J:11, Q:12, K:13, A:14 };
  return map[rank] ?? 0;
}
export const suitIcon = s => ({clubs:'♣️',spades:'♠️',hearts:'♥️',diamonds:'♦️'})[s] || s;
export const typeLabel = t => t==='enemy'?'Inimigo':(t==='weapon'?'Arma':'Cura');
