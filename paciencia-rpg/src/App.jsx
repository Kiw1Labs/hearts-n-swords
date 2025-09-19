import React, { useMemo, useState } from "react";

// ==========================
// Paciência RPG (protótipo web)
// ==========================
// Regras implementadas (ajustáveis na UI):
// - Naipes: ♣️/♠️ = Inimigos | ♥️ = Cura | ♦️ = Armas
// - Ás de ♣️ ou ♠️ é inimigo maior (força 18 por padrão)
// - Força inimiga base: 2–10 = valor | J=11, Q=12, K=13, A=18
// - Armas (♦️): bônus por carta: 2–6:+1 | 7–10:+2 | J/Q/K:+3 | A:+5
// - Curas (♥️): cura por carta: 2–6: +2 | 7–10:+4 | J/Q/K:+6 | A:+10 (uma vez por turno)
// - A cada compra de carta, ressolve imediatamente (inimigo/arma/cura)
// - Encontro: escolha "Atacar (D20)" ou "Fugir" (fuga custa 2 HP)
// - Ataque: se D20 + bônus_arma >= força, vence; senão, toma dano (força - bônus/2 arredondado, mínimo 1)
// - Vitória: sobreviver até esvaziar o baralho. Derrota: HP <= 0.

// Utilitário: ranks e naipes
const SUITS = ["♣", "♠", "♥", "♦"]; // clubs, spades, hearts, diamonds
const RANKS = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]; // ordem alta→baixa apenas para exibição

function rankNumeric(rank) {
  if (rank === "A") return 14; // uso interno (não é força direta)
  if (rank === "K") return 13;
  if (rank === "Q") return 12;
  if (rank === "J") return 11;
  return parseInt(rank, 10);
}

// Força inimiga conforme regra
function enemyStrength(rank) {
  const n = rankNumeric(rank);
  if (rank === "A") return 18; // boss
  if (n >= 2 && n <= 10) return n;
  if (rank === "J") return 11;
  if (rank === "Q") return 12;
  if (rank === "K") return 13;
  return 10;
}

// Bônus de arma (♦)
function weaponBonus(rank) {
  const n = rankNumeric(rank);
  if (rank === "A") return 5;
  if (n >= 11) return 3; // J/Q/K
  if (n >= 7) return 2; // 7-10
  return 1; // 2-6
}

// Cura por carta (♥) — balanceável
function healAmount(rank) {
  const n = rankNumeric(rank);
  if (rank === "A") return 10;
  if (n >= 11) return 6; // J/Q/K
  if (n >= 7) return 4; // 7-10
  return 2; // 2-6
}

function makeDeck() {
  const deck = [];
  for (const s of SUITS) {
    for (const r of RANKS) {
      deck.push({ suit: s, rank: r, id: `${s}${r}${Math.random().toString(36).slice(2,7)}` });
    }
  }
  return deck;
}

function shuffle(array) {
  const a = array.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function Card({ card, highlight=false }) {
  const isRed = card.suit === "♥" || card.suit === "♦";
  return (
    <div className={`rounded-2xl shadow p-3 w-20 h-28 flex flex-col items-center justify-center border text-center select-none ${highlight ? "ring-4 ring-yellow-300" : ""}`} style={{background:"white"}}>
      <div className="text-xs opacity-70">{card.suit}</div>
      <div className={`text-2xl font-semibold ${isRed ? "text-red-500" : "text-slate-800"}`}>{card.rank}</div>
      <div className="text-xs opacity-70">{card.suit}</div>
    </div>
  );
}

function Pill({ children }) {
  return <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">{children}</span>;
}

export default function PacienciaRPG() {
  const freshDeck = useMemo(() => shuffle(makeDeck()), []);
  const [deck, setDeck] = useState(freshDeck);
  const [discard, setDiscard] = useState([]);
  const [current, setCurrent] = useState(null);
  const [hp, setHp] = useState(30);
  const [maxHp, setMaxHp] = useState(30);
  const [weapon, setWeapon] = useState(null); // {card, bonus}
  const [hearts, setHearts] = useState([]); // cartas ♥ acumuladas
  const [log, setLog] = useState(["Jogo iniciado. Compre uma carta!"]);
  const [canHealThisTurn, setCanHealThisTurn] = useState(true);
  const [gameOver, setGameOver] = useState(false);
  const [win, setWin] = useState(false);

  function pushLog(msg) {
    setLog(l => [msg, ...l].slice(0, 50));
  }

  function resetGame() {
    const d = shuffle(makeDeck());
    setDeck(d);
    setDiscard([]);
    setCurrent(null);
    setHp(30);
    setMaxHp(30);
    setWeapon(null);
    setHearts([]);
    setLog(["Novo jogo embaralhado. Boa sorte!"]);
    setCanHealThisTurn(true);
    setGameOver(false);
    setWin(false);
  }

  function drawCard() {
    if (gameOver) return;
    if (deck.length === 0) {
      // fim do baralho → condição de vitória
      setWin(true);
      setGameOver(true);
      pushLog("Você vasculhou o baralho inteiro e sobreviveu! Vitória!");
      return;
    }
    const [next, ...rest] = deck;
    setDeck(rest);
    setCurrent(next);
    setCanHealThisTurn(true); // novo turno inicia ao comprar

    if (next.suit === "♦") {
      const bonus = weaponBonus(next.rank);
      setWeapon({ card: next, bonus });
      setDiscard(d => [next, ...d]);
      pushLog(`Você encontrou uma arma (♦ ${next.rank}). Bônus de +${bonus}.`);
      setCurrent(null);
    } else if (next.suit === "♥") {
      // estoca cura
      setHearts(h => [{ card: next, heal: healAmount(next.rank) }, ...h]);
      setDiscard(d => [next, ...d]);
      pushLog(`Você encontrou uma cura (♥ ${next.rank}). Armazene e use 1x por turno.`);
      setCurrent(null);
    } else {
      pushLog(`Inimigo apareceu: ${next.suit} ${next.rank} (força ${enemyStrength(next.rank)}).`);
    }
  }

  function healOnce() {
    if (gameOver) return;
    if (!canHealThisTurn) { pushLog("Você já se curou neste turno."); return; }
    if (hearts.length === 0) { pushLog("Sem cartas de cura no estoque."); return; }
    const [h, ...rest] = hearts;
    const healed = Math.min(h.heal, maxHp - hp);
    setHp(v => Math.min(maxHp, v + h.heal));
    setHearts(rest);
    setCanHealThisTurn(false);
    pushLog(`Curou +${healed} HP usando ♥ ${h.card.rank}.`);
  }

  function flee() {
    if (gameOver || !current) return;
    if (current.suit !== "♣" && current.suit !== "♠") return;
    setHp(h => h - 2);
    setDiscard(d => [current, ...d]);
    pushLog(`Você fugiu do ${current.suit} ${current.rank} e perdeu 2 HP.`);
    setCurrent(null);
    checkDefeat(hp - 2);
  }

  function attack() {
    if (gameOver || !current) return;
    if (current.suit !== "♣" && current.suit !== "♠") return;

    const str = enemyStrength(current.rank);
    const bonus = weapon?.bonus || 0;
    const roll = Math.floor(Math.random() * 20) + 1; // D20
    const total = roll + bonus;

    if (total >= str) {
      pushLog(`Ataque! d20=${roll} + bônus(${bonus}) = ${total} ≥ ${str}. Inimigo derrotado!`);
      setDiscard(d => [current, ...d]);
      setCurrent(null);
    } else {
      // dano recebido (balanceado)
      const dmg = Math.max(1, Math.ceil((str - bonus) / 2));
      const newHp = hp - dmg;
      setHp(newHp);
      pushLog(`Falha no ataque (d20=${roll} + ${bonus} = ${total} < ${str}). Você recebe ${dmg} de dano.`);
      setDiscard(d => [current, ...d]);
      setCurrent(null);
      checkDefeat(newHp);
    }
  }

  function checkDefeat(hpValue) {
    if (hpValue <= 0) {
      setGameOver(true);
      setWin(false);
      pushLog("Você caiu em batalha. Derrota.");
    }
  }

  // UI Helpers
  function Stat({ label, value }) {
    return (
      <div className="p-3 rounded-2xl bg-white shadow flex flex-col items-center">
        <div className="text-xs text-slate-500">{label}</div>
        <div className="text-xl font-semibold">{value}</div>
      </div>
    );
  }

  function WeaponView() {
    if (!weapon) return (
      <div className="p-3 rounded-2xl bg-slate-50 border text-slate-500">Sem arma</div>
    );
    return (
      <div className="flex items-center gap-2 p-3 rounded-2xl bg-white shadow">
        <Card card={weapon.card} />
        <div className="flex flex-col">
          <div className="text-sm">Bônus: <b>+{weapon.bonus}</b></div>
          <div className="text-xs opacity-70">Troque ao achar outra ♦️</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-slate-100 text-slate-800 p-6">
      <div className="max-w-5xl mx-auto grid gap-6">
        {/* Header */}
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🃏</div>
            <div>
              <h1 className="text-2xl font-bold">Paciência RPG</h1>
              <div className="text-sm text-slate-500">Protótipo jogável (D20)</div>
            </div>
          </div>
          <button onClick={resetGame} className="px-4 py-2 rounded-xl bg-slate-900 text-white hover:opacity-90">Reiniciar</button>
        </header>

        {/* Painel de Status */}
        <section className="grid md:grid-cols-4 gap-4">
          <Stat label="HP" value={`${hp}/${maxHp}`} />
          <Stat label="Baralho" value={`${deck.length} cartas`} />
          <Stat label="Descarte" value={`${discard.length}`} />
          <div className="p-3 rounded-2xl bg-white shadow">
            <div className="text-xs text-slate-500 mb-1">Arma</div>
            <WeaponView />
          </div>
        </section>

        {/* Ações */}
        <section className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-2xl bg-white shadow flex flex-col gap-3">
            <div className="text-sm font-semibold">Turno</div>
            <div className="flex flex-wrap gap-2">
              <button onClick={drawCard} disabled={gameOver} className="px-4 py-2 rounded-xl bg-emerald-600 text-white hover:opacity-90 disabled:opacity-50">Comprar carta</button>
              <button onClick={healOnce} disabled={gameOver} className="px-4 py-2 rounded-xl bg-rose-600 text-white hover:opacity-90 disabled:opacity-50">Curar (1x/turno)</button>
            </div>
            <div className="text-xs text-slate-500">Hearts disponíveis: {hearts.length}</div>
          </div>

          <div className="p-4 rounded-2xl bg-white shadow flex flex-col gap-3">
            <div className="text-sm font-semibold">Encontro</div>
            <div className="flex gap-3 items-center">
              {current ? <Card card={current} highlight /> : <div className="text-slate-500 text-sm">Sem encontro ativo</div>}
              {current && (current.suit === "♣" || current.suit === "♠") && (
                <div className="flex flex-col gap-2">
                  <button onClick={attack} className="px-4 py-2 rounded-xl bg-indigo-600 text-white hover:opacity-90">Atacar (d20)</button>
                  <button onClick={flee} className="px-4 py-2 rounded-xl bg-amber-600 text-white hover:opacity-90">Fugir (-2 HP)</button>
                  <div className="text-xs text-slate-500">Força: {enemyStrength(current.rank)} {current.rank === "A" && <Pill>Chefe</Pill>}</div>
                </div>
              )}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white shadow flex flex-col gap-3">
            <div className="text-sm font-semibold">Curas em estoque (♥)</div>
            <div className="flex flex-wrap gap-2">
              {hearts.length === 0 && <div className="text-sm text-slate-500">Nenhuma</div>}
              {hearts.map((h, idx) => (
                <div key={h.card.id+idx} className="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border">
                  <Card card={h.card} />
                  <div className="text-xs">cura <b>+{h.heal}</b></div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Log */}
        <section className="p-4 rounded-2xl bg-white shadow">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-semibold">Registro</div>
            <div className="flex gap-2">
              <Pill>♣/♠ Inimigos</Pill>
              <Pill>♦ Armas</Pill>
              <Pill>♥ Cura</Pill>
            </div>
          </div>
          <ul className="space-y-1 max-h-64 overflow-auto pr-2">
            {log.map((entry, i) => (
              <li key={i} className="text-sm">• {entry}</li>
            ))}
          </ul>
        </section>

        {/* Fim de jogo */}
        {gameOver && (
          <section className={`p-4 rounded-2xl shadow text-center ${win ? "bg-emerald-50" : "bg-rose-50"}`}>
            <div className="text-xl font-bold mb-1">{win ? "Vitória" : "Derrota"}</div>
            <div className="text-sm text-slate-600 mb-3">{win ? "Você sobreviveu ao baralho!" : "Seus pontos de vida chegaram a zero."}</div>
            <button onClick={resetGame} className="px-4 py-2 rounded-xl bg-slate-900 text-white hover:opacity-90">Jogar novamente</button>
          </section>
        )}

        {/* Créditos / ajuda */}
        <footer className="text-xs text-slate-500 text-center py-4">
          Paciência RPG — protótipo. Ajuste os números no código para balancear.
        </footer>
      </div>
    </div>
  );
}
