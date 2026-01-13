# TradeX Technical Documentation

## 1. Frameworks and Libraries Used
TradeX is built using a modern full-stack architecture centered around the Django ecosystem.

- **Primary Framework**: [Django](https://www.djangoproject.com/) (Version 5.x)
- **API Development**: [Django REST Framework (DRF)](https://www.django-rest-framework.org/) - used for potential future API expansions and internal data handling.
- **Frontend Styling**: [Tailwind CSS](https://tailwindcss.com/) (Accessed via CDN for maximum performance and zero build overhead).
- **Data Visualizations**: [Chart.js](https://www.chartjs.org/) (Version 4.x) - used for portfolio growth and stock performance analysis.
- **Financial Data Integration**: [yfinance](https://github.com/ranaroussi/yfinance) - used to fetch real-time stock market data from Yahoo Finance.
- **Icons & Fonts**: [Font Awesome 6.0](https://fontawesome.com/) and [Google Fonts (Inter)](https://fonts.google.com/).
- **Database**: [MySQL](https://www.mysql.com/) (Database: `Dhan`) - Production-grade relational database management system.
- **Database Driver**: [PyMySQL](https://pymysql.readthedocs.io/) - Pure-Python MySQL client used for seamless Django integration on Windows.
- **Performance Optimization**: [Django Caching Framework](https://docs.djangoproject.com/en/stable/topics/cache/) - Uses `LocMemCache` to reduce external API overhead for stock data.

---

## 2. Formulas and Calculations
The project implements specific financial logic to simulate a real-world trading environment.

### 2.1 Portfolio Metrics
- **Total Invested Amount**:
  $$\sum (\text{Quantity} \times \text{Average Buy Price})$$
  *Logic*: This represents the actual capital deployed by the user to acquire their current holdings.

- **Current Market Value**:
  $$\sum (\text{Quantity} \times \text{Live Market Price})$$
  *Logic*: Calculated by fetching the latest price from `yfinance` for each symbol in the user's portfolio.

- **Profit / Loss (Absolute)**:
  $$\text{Current Market Value} - \text{Total Invested Amount}$$

- **P&L Percentage**:
  $$\left( \frac{\text{Profit/Loss}}{\text{Total Invested Amount}} \right) \times 100$$

### 2.2 SIP (Systematic Investment Plan)
- **Monthly Growth Simulation**:
  Calculated using the future value of an annuity formula for simulation projections.
- **Frequency Logic**: Supports 'WEEKLY' and 'MONTHLY' intervals, simulating how much wealth a user would accumulate over time given a fixed investment rate.

---

## 3. Main App Structure & Files
The core logic resides in the `main` app, following Django's MVT (Model-View-Template) pattern.

| File | Purpose | Key Functionality |
| :--- | :--- | :--- |
| `models.py` | **Data Layer** | Defines `Profile`, `Stock`, `Portfolio`, `Transaction`, and `Watchlist` models. |
| `views.py` | **Business Logic** | Processes requests, performs financial calculations, and renders templates. |
| `forms.py` | **Data Validation** | Custom forms for Phone-based Auth, Buy/Sell actions, and SIP configuration. |
| `utils.py` | **Integrations** | Contains wrapper functions for `yfinance` to fetch live stock prices. |
| `urls.py` | **Routing** | Maps clean URLs (e.g., `/investment/`, `/dashboard/`) to their respective views. |
| `templates/` | **Presentation Layer** | Responsive HTML files using Tailwind CSS for a Groww-style UI. |
| `auth_backends.py`| **Custom Auth** | Implementation of the `PhoneBackend` for login via phone number. |

---

## 4. Project Flow
1. **Authentication**: Users register/login using their **Phone Number**. The `PhoneBackend` sanitizes and authenticates credentials.
2. **Onboarding**: Upon registration, a `Profile` is automatically created with a default simulation balance of ₹1,00,000.
3. **Dashboard**: The main entry point displaying live market indices, top stocks, and a high-level portfolio summary.
4. **Trading**:
   - **Buy**: View fetches live price -> Form validates balance -> `Transaction` and `Portfolio` records are updated.
   - **Sell**: View validates ownership -> `Transaction` and `Portfolio` updated -> Sale proceeds added to balance.
5. **Investment Summary**: A dedicated page (`/investment/`) calculating deep performance metrics and growth charts.

---

## 5. APIs and Integrations
- **yfinance (Direct Import)**: Used extensively in `utils.py` to fetch `fast_info` (for speed) and `history` (for P&L calculations).
- **Intelligent Caching Layer**: Implemented in `utils.py` using Django's `cache` API.
    - **Mechanism**: Stores stock data tuples (price, change, name) in memory.
    - **TTL (Time-To-Live)**: 5 Minutes (300 seconds).
    - **Performance Gain**: Reduces page reload time from ~2s to <50ms after the first load.
- **Internal API**: Views like `dashboard` and `investment_summary` act as internal data providers, passing serialized JSON to frontend Chart.js components.
- **No External REST Endpoints**: All data fetching is currently handled server-side to prevent API key exposure and ensure data consistency.

---

## 6. Project Entry Point
The project execution starts at the root `urls.py` of the `config_pro` directory:
1. **Root URL**: `config_pro/urls.py` includes `main.urls`.
2. **Default Route**: The `''` (empty path) in `main/urls.py` points to the `home` view.
3. **MVT Cycle**:
   - **Request** hits URL -> **View** is triggered -> **View** queries **Model** -> **Model** returns data -> **View** passes data to **Template** -> **Template** renders HTML/CSS/JS.

---

## 7. Utility & Special Configurations
- **Custom Management Command**: `populate_stocks.py` allows developers to seed the database with initial stock data using `python manage.py populate_stocks`.
- **Glassmorphism UI**: Implemented via custom CSS classes in `base.html` and Tailwind utilities to achieve the premium "Groww" aesthetic.
- **Environment**: Configured for local development with `DEBUG=True` and `django-browser-reload` for a seamless development experience.
