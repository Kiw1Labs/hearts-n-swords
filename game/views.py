from rest_framework import status, views, generics
from rest_framework.response import Response
from django.db import transaction

from .models import Run, EventLog, Score
from .serializers import RunSerializer
from .utils import new_deck, classify_card, rank_power, enemy_power

BOSS_BONUS = 6
MAX_TURNS_SPEED = 26
BOARD_SLOTS = 4
ENEMY_HOLD_LIMIT = 2  # inimigo pode ficar no máximo 2 turnos mantido

# ---------------- helpers ----------------

def _ensure_board(run: Run):
    if not isinstance(run.board, list) or len(run.board) != BOARD_SLOTS:
        run.board = [None]*BOARD_SLOTS

def _refill_board(run: Run):
    """Completa slots vazios com cartas do topo da deck."""
    _ensure_board(run)
    changed = False
    for i in range(BOARD_SLOTS):
        if run.board[i] is None and run.deck:
            c = run.deck.pop()
            slot = {"card": c, "type": classify_card(c), "held": 0}
            run.board[i] = slot
            EventLog.objects.create(run=run, text=f"Slot {i+1}: virou {slot['type']} {c['suit']}-{c['rank']}.")
            changed = True
    return changed

def _require_slot(run: Run, idx: int):
    _ensure_board(run)
    if idx < 0 or idx >= BOARD_SLOTS: 
        return None, Response({"detail":"slot inválido (0..3)"}, status=400)
    slot = run.board[idx]
    if slot is None:
        return None, Response({"detail":"slot vazio"}, status=400)
    return slot, None

def _finish_run_if_deck_ends(run: Run):
    if run.status == "ongoing" and not run.deck:
        # aplica bônus final só uma vez
        if not run.final_scored:
            victory_bonus = 30
            speed_bonus = max(0, 2 * (MAX_TURNS_SPEED - run.turn))
            run.score_total += victory_bonus + run.hp + speed_bonus
            run.final_scored = True
            EventLog.objects.create(run=run, text=f"Vitória! +30 +HP({run.hp}) +Speed({speed_bonus}). Score={run.score_total}.")
        run.status = "won"

def _score_kill(run: Run, val: int):
    base = val + (BOSS_BONUS if val == 14 else 0)
    run.combo_len += 1
    mult = 1 + 0.20 * (run.combo_len - 1)
    pts = round(base * mult)
    run.score_total += pts
    run.session_points += pts
    EventLog.objects.create(run=run, text=f"Kill {val}: +{pts} (combo {run.combo_len} ×{mult:.1f}). Score={run.score_total}.")
    if val == 2 and not run.descida_ate2:
        run.score_total += run.session_points  # dobra retroativo
        run.descida_ate2 = True
        EventLog.objects.create(run=run, text=f"BÔNUS descida até 2: +{run.session_points}.")

# ---------------- API ----------------

class StartRunView(views.APIView):
    """POST /api/start  body: {seed:str?, max_hp:int?}"""
    @transaction.atomic
    def post(self, request):
        seed = request.data.get("seed") or "default-seed"
        max_hp = int(request.data.get("max_hp", 20))
        deck = new_deck(seed)
        run = Run.objects.create(
            seed=seed, max_hp=max_hp, hp=max_hp, deck=deck, discard=[],
            board=[None]*BOARD_SLOTS, turn=1, emptied_this_turn=0,
            power=0, score_total=0, equip_session=0, combo_len=0,
            session_points=0, descida_ate2=False, final_scored=False
        )
        _refill_board(run)
        EventLog.objects.create(run=run, text=f"Run iniciada. Seed={seed}.")
        run.save()
        return Response(RunSerializer(run).data, status=201)

class RunDetailView(generics.RetrieveAPIView):
    queryset = Run.objects.all()
    serializer_class = RunSerializer

class EquipFromSlotView(views.APIView):
    """POST /api/run/<uuid>/equip/<int:idx>  (idx = 0..3)"""
    @transaction.atomic
    def post(self, request, pk, idx: int):
        run = Run.objects.select_for_update().get(pk=pk)
        if run.status != "ongoing": return Response({"detail":"run finalizada"}, status=400)
        slot, err = _require_slot(run, idx)
        if err: return err
        if slot["type"] != "weapon":
            return Response({"detail":"slot não é arma"}, status=400)
        val = rank_power(slot["card"]["rank"])

        # iniciar nova sessão de equipamento
        run.equip_session += 1
        run.combo_len = 0
        run.session_points = 0
        run.descida_ate2 = False

        run.power = val
        run.discard.append(slot["card"])
        run.board[idx] = None
        run.emptied_this_turn += 1

        EventLog.objects.create(run=run, text=f"Equipou ♦️{val}. Sessão #{run.equip_session}. PWR={run.power}.")
        run.save()
        return Response(RunSerializer(run).data)

class DiscardFromSlotView(views.APIView):
    """POST /api/run/<uuid>/discard/<int:idx> — descarta arma/vida"""
    @transaction.atomic
    def post(self, request, pk, idx: int):
        run = Run.objects.select_for_update().get(pk=pk)
        if run.status != "ongoing": return Response({"detail":"run finalizada"}, status=400)
        slot, err = _require_slot(run, idx)
        if err: return err
        if slot["type"] not in ("weapon","heal"):
            return Response({"detail":"para inimigo, use pay_life ou fight"}, status=400)
        run.discard.append(slot["card"])
        run.board[idx] = None
        run.emptied_this_turn += 1
        EventLog.objects.create(run=run, text=f"Descartou {slot['type']} {slot['card']['suit']}-{slot['card']['rank']}.")
        run.save()
        return Response(RunSerializer(run).data)

class UseHealFromSlotView(views.APIView):
    """POST /api/run/<uuid>/use_heal/<int:idx> — usa cura do slot"""
    @transaction.atomic
    def post(self, request, pk, idx: int):
        run = Run.objects.select_for_update().get(pk=pk)
        if run.status != "ongoing": return Response({"detail":"run finalizada"}, status=400)
        slot, err = _require_slot(run, idx)
        if err: return err
        if slot["type"] != "heal":
            return Response({"detail":"slot não é cura"}, status=400)

        val = rank_power(slot["card"]["rank"])
        run.hp = min(run.max_hp, run.hp + val)
        run.discard.append(slot["card"])
        run.board[idx] = None
        run.emptied_this_turn += 1

        EventLog.objects.create(run=run, text=f"Usou ♥️{val}. HP={run.hp}.")
        run.save()
        return Response(RunSerializer(run).data)

class FightFromSlotView(views.APIView):
    """POST /api/run/<uuid>/fight/<int:idx> — luta (se puder vencer)"""
    @transaction.atomic
    def post(self, request, pk, idx: int):
        run = Run.objects.select_for_update().get(pk=pk)
        if run.status != "ongoing": return Response({"detail":"run finalizada"}, status=400)
        slot, err = _require_slot(run, idx)
        if err: return err
        if slot["type"] != "enemy":
            return Response({"detail":"slot não é inimigo"}, status=400)

        val = enemy_power(slot["card"])
        if run.power < val:
            return Response({"detail":"poder insuficiente; pague vida ou mantenha"}, status=400)

        # derrota: pontua + absorve valor
        _score_kill(run, val)
        run.power = val
        run.discard.append(slot["card"])
        run.board[idx] = None
        run.emptied_this_turn += 1

        run.save()
        return Response(RunSerializer(run).data)

class PayLifeDiscardView(views.APIView):
    """POST /api/run/<uuid>/pay_life/<int:idx> — paga vida = valor do inimigo e descarta"""
    @transaction.atomic
    def post(self, request, pk, idx: int):
        run = Run.objects.select_for_update().get(pk=pk)
        if run.status != "ongoing": return Response({"detail":"run finalizada"}, status=400)
        slot, err = _require_slot(run, idx)
        if err: return err
        if slot["type"] != "enemy":
            return Response({"detail":"slot não é inimigo"}, status=400)

        val = enemy_power(slot["card"])
        run.hp -= val
        run.discard.append(slot["card"])
        run.board[idx] = None
        run.emptied_this_turn += 1
        EventLog.objects.create(run=run, text=f"Pagou {val} de vida para descartar inimigo. HP={run.hp}.")

        if run.hp <= 0:
            run.status = "lost"
            EventLog.objects.create(run=run, text="Você caiu em batalha. Derrota.")
        run.save()
        return Response(RunSerializer(run).data)

class EndTurnView(views.APIView):
    """POST /api/run/<uuid>/end_turn — avança turno se >=2 slots esvaziados e regras de manter ok"""
    @transaction.atomic
    def post(self, request, pk):
        run = Run.objects.select_for_update().get(pk=pk)
        if run.status != "ongoing": return Response({"detail":"run finalizada"}, status=400)

        if run.emptied_this_turn < 2:
            return Response({"detail":"você precisa esvaziar pelo menos 2 slots para terminar o turno"}, status=400)

        # regras de manter: ♦️ não pode ficar; inimigos no máximo 2 turnos
        _ensure_board(run)
        for i, slot in enumerate(run.board):
            if slot is None: continue
            if slot["type"] == "weapon":
                return Response({"detail": f"arma no slot {i+1} não pode ser mantida; equipar ou descartar"}, status=400)

        # incrementar contadores de 'held' para inimigos; bloquear se exceder
        for i, slot in enumerate(run.board):
            if slot and slot["type"] == "enemy":
                slot["held"] = int(slot.get("held", 0)) + 1
                if slot["held"] > ENEMY_HOLD_LIMIT:
                    return Response({"detail": f"inimigo no slot {i+1} já foi mantido por {ENEMY_HOLD_LIMIT} turnos; resolva-o"}, status=400)

        run.turn += 1
        run.emptied_this_turn = 0

        # reabastece mesa
        _refill_board(run)
        _finish_run_if_deck_ends(run)

        EventLog.objects.create(run=run, text=f"Início do turno {run.turn}.")
        run.save()
        return Response(RunSerializer(run).data)

class SubmitScoreView(views.APIView):
    """POST /api/run/<uuid>/score  body: {player_name?:str}"""
    def post(self, request, pk):
        run = Run.objects.filter(pk=pk).first()
        if not run:
            return Response({"detail":"run não encontrada"}, status=404)

        allow_ongoing = False  # mude para True se quiser permitir envio antes do fim
        if not allow_ongoing and run.status == "ongoing":
            return Response({"detail":"termine a run antes de enviar ao ranking"}, status=400)

        player_name = (request.data.get("player_name") or "Jogador").strip()[:30]
        obj, created = Score.objects.get_or_create(
            run=run, player_name=player_name,
            defaults={"points": run.score_total}
        )
        if not created:
            obj.points = max(obj.points, run.score_total)  # mantém o melhor daquela run+player
            obj.save(update_fields=["points"])

        EventLog.objects.create(run=run, text=f"Score enviado ao ranking: {player_name} — {obj.points}.")
        return Response({"ok": True, "player_name": player_name, "points": obj.points})

# views.py
from django.db.models import Max
from rest_framework import views
from rest_framework.response import Response
from .models import Score

class RankingApiView(views.APIView):
    def get(self, request):
        mode = request.GET.get("mode","runs")
        if mode == "best":
            qs = (Score.objects.values("player_name")
                  .annotate(points=Max("points"), last_at=Max("created_at"))
                  .order_by("-points","-last_at"))[:500]
            return Response(list(qs))
        qs = (Score.objects
              .order_by("-points","-created_at")
              .values("player_name","points","created_at","run_id")[:500])
        return Response(list(qs))
