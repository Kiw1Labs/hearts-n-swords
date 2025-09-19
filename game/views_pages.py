# game/views_pages.py
from django.views.generic import TemplateView, ListView
from django.db.models import Max
from .models import Score

class HomeView(TemplateView):
    """Página inicial com resumo das regras e CTA para jogar."""
    template_name = "home.html"

class GamePageView(TemplateView):
    """Página onde o jogo acontece (consome a API via JS)."""
    template_name = "game.html"

class ContactView(TemplateView):
    """Página de informações e contato."""
    template_name = "contact.html"

class RankingView(ListView):
    template_name = "ranking.html"
    context_object_name = "scores"
    paginate_by = 50

    def get_queryset(self):
        mode = self.request.GET.get("mode", "runs")
        if mode == "best":
            # melhor score por jogador
            return (Score.objects.values("player_name")
                    .annotate(points=Max("points"), last_at=Max("created_at"))
                    .order_by("-points", "-last_at"))
        # top runs (cada envio aparece)
        return Score.objects.select_related("run").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = self.request.GET.get("mode", "runs")
        return ctx
