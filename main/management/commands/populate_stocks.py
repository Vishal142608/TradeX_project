from django.core.management.base import BaseCommand
from main.models import Stock
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate initial stock data'

    def handle(self, *args, **kwargs):
        stocks = [
            {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries Ltd', 'price': 2540.35},
            {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services', 'price': 3420.10},
            {'symbol': 'HDFCBANK', 'company_name': 'HDFC Bank Ltd', 'price': 1650.00},
            {'symbol': 'INFY', 'company_name': 'Infosys Ltd', 'price': 1480.50},
            {'symbol': 'ICICIBANK', 'company_name': 'ICICI Bank Ltd', 'price': 940.25},
            {'symbol': 'AAPL', 'company_name': 'Apple Inc.', 'price': 15600.00},
            {'symbol': 'TSLA', 'company_name': 'Tesla Inc.', 'price': 21000.00},
            {'symbol': 'AMZN', 'company_name': 'Amazon.com Inc.', 'price': 12500.00},
        ]
        
        for s in stocks:
            Stock.objects.update_or_create(
                symbol=s['symbol'],
                defaults={
                    'name': s['company_name'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated stock data'))
