from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('buy/<int:stock_id>/', views.buy_stock, name='buy_stock'),
    path('buy/search/', views.buy_stock, name='buy_stock_search'),
    path('sell/<int:stock_id>/', views.sell_stock, name='sell_stock'),
    path('transactions/', views.transactions_view, name='transactions'),
    
    path('watchlist/add/<str:symbol>/', views.add_to_watchlist, name='add_watchlist'),
    path('watchlist/remove/<int:stock_id>/', views.remove_from_watchlist, name='remove_watchlist'),
    
    path('sip/', views.sip_view, name='sip'),
    path('fo/', views.fo_view, name='fo'),
    path('profile/', views.profile_view, name='profile'),
    path('investment/', views.investment_summary, name='investment_summary'),
]
