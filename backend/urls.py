from django.contrib import admin
from django.urls import path
from game.views_pages import HomeView, GamePageView, ContactView, RankingView
from game.views import (
    StartRunView, RunDetailView,
    EquipFromSlotView, DiscardFromSlotView, UseHealFromSlotView,
    FightFromSlotView, PayLifeDiscardView, EndTurnView,
    SubmitScoreView
)

urlpatterns = [
    # páginas
    path("", HomeView.as_view(), name="home"),
    path("play/", GamePageView.as_view(), name="play"),
    path("ranking/", RankingView.as_view(), name="ranking"),
    path("contact/", ContactView.as_view(), name="contact"),

    # admin
    path("admin/", admin.site.urls),

    # API nova
    path("api/start", StartRunView.as_view()),
    path("api/run/<uuid:pk>", RunDetailView.as_view()),
    path("api/run/<uuid:pk>/equip/<int:idx>", EquipFromSlotView.as_view()),
    path("api/run/<uuid:pk>/discard/<int:idx>", DiscardFromSlotView.as_view()),
    path("api/run/<uuid:pk>/use_heal/<int:idx>", UseHealFromSlotView.as_view()),
    path("api/run/<uuid:pk>/fight/<int:idx>", FightFromSlotView.as_view()),
    path("api/run/<uuid:pk>/pay_life/<int:idx>", PayLifeDiscardView.as_view()),
    path("api/run/<uuid:pk>/end_turn", EndTurnView.as_view()),
    path("api/run/<uuid:pk>/score", SubmitScoreView.as_view()),
]
