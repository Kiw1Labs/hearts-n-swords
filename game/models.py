from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Run(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    # baralho / estado
    seed = models.CharField(max_length=64)
    deck = models.JSONField(default=list)       # cartas restantes (topo = último)
    discard = models.JSONField(default=list)    # histórico de cartas resolvidas
    board = models.JSONField(default=list)      # 4 slots: [None | {card,type,held:int}]

    # vida / turno
    max_hp = models.IntegerField(default=20)
    hp = models.IntegerField(default=20)
    turn = models.IntegerField(default=1)
    emptied_this_turn = models.IntegerField(default=0)  # slots esvaziados no turno

    status = models.CharField(
        max_length=10,
        choices=[("ongoing","ongoing"),("won","won"),("lost","lost")],
        default="ongoing"
    )

    # “pilha de equipamento” (poder atual)
    power = models.IntegerField(default=0)

    # pontuação v1
    score_total = models.IntegerField(default=0)
    equip_session = models.IntegerField(default=0)
    combo_len = models.IntegerField(default=0)
    session_points = models.IntegerField(default=0)
    descida_ate2 = models.BooleanField(default=False)
    final_scored = models.BooleanField(default=False)

    def __str__(self):
        return f"Run {self.id} | T{self.turn} | HP {self.hp}/{self.max_hp} | PWR {self.power} | SCORE {self.score_total}"

class EventLog(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="events")
    created_at = models.DateTimeField(default=timezone.now)
    text = models.TextField()

class Roll(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="rolls")
    d20 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    bonus = models.IntegerField(default=0)
    total = models.IntegerField()
    context = models.CharField(max_length=50, default="combat")
    created_at = models.DateTimeField(default=timezone.now)

class Score(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(Run, on_delete=models.SET_NULL, null=True, blank=True, related_name="scores")
    player_name = models.CharField(max_length=30)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-points", "created_at"]
