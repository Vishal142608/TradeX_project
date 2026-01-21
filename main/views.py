from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Stock, Portfolio, Transaction, Watchlist, Profile
from .utils import get_stock_data, get_multiple_stocks
from .forms import TradeXRegistrationForm, TradeXLoginForm, BuyStockForm, SellStockForm, SIPForm
from decimal import Decimal
import json

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = TradeXRegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            user = User.objects.create_user(
                username=phone,
                password=password
            )
            
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.phone_number = phone
            profile.save()

            messages.success(
                request,
                "Account created successfully. Please login to continue."
            )
            return redirect('login') 
    else:
        form = TradeXRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = TradeXLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid phone number or password")
    else:
        form = TradeXLoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    holdings = Portfolio.objects.filter(user=request.user)
    
    # Fetch live data for current holdings
    symbols = [h.stock.symbol for h in holdings]
    live_data = get_multiple_stocks(symbols)
    
    total_invested = sum(h.quantity * h.avg_price for h in holdings)
    current_value = Decimal('0.00')
    
    for h in holdings:
        price = live_data.get(h.stock.symbol, {}).get('price', h.avg_price)
        current_value += h.quantity * price
        
    profit_loss = current_value - total_invested
    pnl_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    # Market overview (Top stocks)
    market_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'AAPL', 'TSLA', 'MSFT']
    market_data = get_multiple_stocks(market_symbols)
    
    # Create Stock objects if they don't exist for the UI loops
    top_stocks = []
    for sym, data in market_data.items():
        stock_obj, _ = Stock.objects.get_or_create(symbol=sym, defaults={'name': data['name']})
        data['id'] = stock_obj.id
        top_stocks.append(data)

    # Simulated performance data
    chart_labels = ['1w', '6d', '5d', '4d', '3d', '2d', 'Today']
    chart_data = [
        float(total_invested - 5000), float(total_invested - 3000), 
        float(total_invested + 2000), float(total_invested - 1000), 
        float(total_invested + 4000), float(total_invested + 1000), 
        float(current_value)
    ]

    context = {
        'profile': profile,
        'total_invested': total_invested,
        'current_value': current_value,
        'profit_loss': profit_loss,
        'pnl_percent': pnl_percent,
        'top_stocks': top_stocks,
        'recent_transactions': Transaction.objects.filter(user=request.user).order_by('-timestamp')[:5],
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'main/dashboard.html', context)

@login_required
def portfolio_view(request):
    holdings = Portfolio.objects.filter(user=request.user, quantity__gt=0)
    symbols = [h.stock.symbol for h in holdings]
    live_data = get_multiple_stocks(symbols)
    
    for h in holdings:
        data = live_data.get(h.stock.symbol, {})
        h.current_price = data.get('price', Decimal('0.00'))
        h.pnl = (h.current_price - h.avg_price) * h.quantity
        h.pnl_percent = ((h.current_price - h.avg_price) / h.avg_price * 100) if h.avg_price > 0 else 0

    return render(request, 'main/portfolio.html', {'holdings': holdings})

@login_required
def watchlist_view(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    symbols = [item.stock.symbol for item in watchlist_items]
    live_data = get_multiple_stocks(symbols)
    
    for item in watchlist_items:
        data = live_data.get(item.stock.symbol, {})
        item.price = data.get('price')
        item.change_percent = data.get('change_percent')

    # Popular stocks to add
    popular_symbols = ['INFY.NS', 'ICICIBANK.NS', 'AMZN', 'GOOGL', 'NVDA']
    popular_data = get_multiple_stocks(popular_symbols)
    
    return render(request, 'main/watchlist.html', {
        'watchlist': watchlist_items,
        'popular_stocks': popular_data.values()
    })

@login_required
def buy_stock(request, stock_id=None):
    stock = None
    if stock_id:
        stock = get_object_or_404(Stock, id=stock_id)
    elif request.GET.get('symbol'):
        symbol = request.GET.get('symbol').upper()
        data = get_stock_data(symbol)
        if data:
            stock, _ = Stock.objects.get_or_create(symbol=symbol, defaults={'name': data['name']})
    
    if not stock:
        messages.error(request, "Stock not found")
        return redirect('dashboard')

    live_data = get_stock_data(stock.symbol)
    price = live_data['price'] if live_data else Decimal('0.00')

    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = BuyStockForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            total_cost = price * quantity
            
            if profile.balance >= total_cost:
                profile.balance -= total_cost
                profile.save()
                
                holding, created = Portfolio.objects.get_or_create(
                    user=request.user, stock=stock, 
                    defaults={'quantity': 0, 'avg_price': 0}
                )
                
                new_total_qty = holding.quantity + quantity
                holding.avg_price = ((holding.avg_price * holding.quantity) + total_cost) / new_total_qty
                holding.quantity = new_total_qty
                holding.save()
                
                Transaction.objects.create(
                    user=request.user, stock=stock, quantity=quantity,
                    price=price, transaction_type='BUY'
                )
                messages.success(request, f"Successfully bought {quantity} shares of {stock.symbol}")
                return redirect('portfolio')
            else:
                messages.error(request, "Insufficient balance in your wallet.")
    else:
        form = BuyStockForm()

    return render(request, 'main/buy.html', {
        'stock': stock, 
        'price': price, 
        'balance': profile.balance,
        'form': form
    })

@login_required
def sell_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    holding = get_object_or_404(Portfolio, user=request.user, stock=stock)
    
    live_data = get_stock_data(stock.symbol)
    price = live_data['price'] if live_data else Decimal('0.00')
    
    if request.method == 'POST':
        form = SellStockForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity <= holding.quantity:
                total_revenue = price * quantity
                profile = Profile.objects.get(user=request.user)
                profile.balance += total_revenue
                profile.save()
                
                holding.quantity -= quantity
                if holding.quantity == 0:
                    holding.delete()
                else:
                    holding.save()
                    
                Transaction.objects.create(
                    user=request.user, stock=stock, quantity=quantity,
                    price=price, transaction_type='SELL'
                )
                messages.success(request, f"Successfully sold {quantity} shares of {stock.symbol}")
                return redirect('portfolio')
            else:
                messages.error(request, f"You only have {holding.quantity} shares available to sell.")
    else:
        form = SellStockForm(initial={'quantity': 1})

    return render(request, 'main/sell.html', {
        'stock': stock, 
        'holding': holding, 
        'price': price,
        'form': form
    })

@login_required
def transactions_view(request):
    txs = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'main/transactions.html', {'transactions': txs})

@login_required
def add_to_watchlist(request, symbol):
    data = get_stock_data(symbol)
    if data:
        stock, _ = Stock.objects.get_or_create(symbol=symbol, defaults={'name': data['name']})
        Watchlist.objects.get_or_create(user=request.user, stock=stock)
        messages.success(request, f"Added {symbol} to watchlist")
    return redirect('watchlist')

@login_required
def remove_from_watchlist(request, stock_id):
    item = get_object_or_404(Watchlist, user=request.user, stock_id=stock_id)
    item.delete()
    return redirect('watchlist')

@login_required
def sip_view(request):
    if request.method == 'POST':
        form = SIPForm(request.POST)
        if form.is_valid():
            messages.success(request, "SIP scheduled successfully! (Simulation)")
            return redirect('dashboard')
    else:
        form = SIPForm()
    return render(request, 'main/sip.html', {'form': form})

@login_required
def fo_view(request):
    # Skeleton for F&O
    return render(request, 'main/fo.html')

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'main/profile.html', {'profile': profile})

@login_required
def investment_summary(request):
    holdings = Portfolio.objects.filter(user=request.user)
    symbols = [h.stock.symbol for h in holdings]
    live_data = get_multiple_stocks(symbols)
    
    total_invested = sum(h.quantity * h.avg_price for h in holdings)
    current_value = Decimal('0.00')
    
    for h in holdings:
        price = live_data.get(h.stock.symbol, {}).get('price', h.avg_price)
        current_value += h.quantity * price
        
    profit_loss = current_value - total_invested
    pnl_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    # Calculate performance history for chart (Simulated for this demo)
    # In production, this would pull from historical price snapshots
    chart_labels = ['1W', '6D', '5D', '4D', '3D', '2D', 'Today']
    chart_data = [
        float(total_invested * Decimal('0.95')),
        float(total_invested * Decimal('0.98')),
        float(total_invested * Decimal('1.02')),
        float(total_invested * Decimal('0.99')),
        float(total_invested * Decimal('1.04')),
        float(total_invested * Decimal('1.03')),
        float(current_value)
    ]
    
    context = {
        'total_invested': total_invested,
        'current_value': current_value,
        'profit_loss': profit_loss,
        'pnl_percent': pnl_percent,
        'holdings': holdings,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'main/investment_summary.html', context)
