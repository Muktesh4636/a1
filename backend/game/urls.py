from django.urls import path
from . import views

urlpatterns = [
    path('round/', views.current_round, name='current_round'),
    path('bet/', views.place_bet, name='place_bet'),
    path('bet/<int:number>/', views.remove_bet, name='remove_bet'),
    path('bets/', views.my_bets, name='my_bets'),
    path('betting-history/', views.betting_history, name='betting_history'),
    path('set-dice/', views.set_dice_result, name='set_dice_result'),
    path('dice-mode/', views.dice_mode, name='dice_mode'),
    path('stats/', views.game_stats, name='game_stats'),
]

