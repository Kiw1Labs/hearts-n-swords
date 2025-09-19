# game/views_pages.py
from django.views.generic import TemplateView, ListView
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
    """Lista as pontuações (Score) em ordem decrescente."""
    model = Score
    template_name = "ranking.html"
    context_object_name = "scores"
    paginate_by = 50
