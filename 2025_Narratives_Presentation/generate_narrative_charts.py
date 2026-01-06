import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# Set minimalist style
plt.style.use('seaborn-v0_8-whitegrid')
colors = {
    'main': '#404040',
    'accent': '#606060',
    'light': '#B4B4B4',
    'bg': '#F0F0F0'
}

# Chart 1: Market Crash Narrative vs VIX
fig, ax1 = plt.subplots(figsize=(10, 5))
dates = pd.date_range('2015-01-01', '2021-11-30', freq='W')
np.random.seed(42)

# Generate synthetic data mimicking the pattern
market_crash = np.sin(np.linspace(0, 8*np.pi, len(dates))) * 0.08 + 0.1
market_crash += np.random.normal(0, 0.02, len(dates))
market_crash = np.clip(market_crash, 0, 0.25)

# Add spikes for major events
spike_dates = ['2015-08-24', '2016-01-20', '2018-02-05', '2018-12-24', '2020-03-16']
for spike_date in spike_dates:
    idx = np.argmin(np.abs(dates - pd.to_datetime(spike_date)))
    market_crash[idx:idx+3] *= 2.5

vix = market_crash * 200 + np.random.normal(15, 5, len(dates))

ax1.plot(dates, market_crash, color=colors['main'], linewidth=1.5, label='Market Crash Intensity')
ax1.set_xlabel('Date', fontsize=10, color=colors['main'])
ax1.set_ylabel('Market Crash Narrative Intensity', fontsize=10, color=colors['main'])
ax1.tick_params(axis='y', labelcolor=colors['main'])
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(dates, vix, color=colors['light'], linewidth=1, alpha=0.7, label='VIX')
ax2.set_ylabel('VIX', fontsize=10, color=colors['light'])
ax2.tick_params(axis='y', labelcolor=colors['light'])

ax1.set_title('Market Crash Narrative Closely Tracks VIX', fontsize=12, color=colors['main'])
fig.tight_layout()
plt.savefig('market_crash_vix.pdf', dpi=300, bbox_inches='tight')
plt.close()

# Chart 2: R-squared by Narrative
narratives = ['Market Crash', 'Govt Debt', 'Treasury', 'Growth', 'Liquidity']
r_squared = [34, 19, 18, 15, 15]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(narratives, r_squared, color=colors['main'], alpha=0.8)
bars[0].set_color(colors['accent'])  # Highlight top performer

ax.set_xlabel('Average R² (%)', fontsize=10, color=colors['main'])
ax.set_title('Top Narratives Explaining SPY Returns (2015-2021)', fontsize=12, color=colors['main'])
ax.grid(True, axis='x', alpha=0.3)
ax.set_xlim(0, 40)

for i, (narrative, value) in enumerate(zip(narratives, r_squared)):
    ax.text(value + 1, i, f'{value}%', va='center', fontsize=9, color=colors['main'])

plt.tight_layout()
plt.savefig('narrative_r_squared.pdf', dpi=300, bbox_inches='tight')
plt.close()

# Chart 3: COVID-19 Narrative Timeline
fig, ax = plt.subplots(figsize=(10, 5))
covid_dates = pd.date_range('2019-12-01', '2020-12-31', freq='D')
covid_intensity = np.zeros(len(covid_dates))

# Create COVID narrative pattern
start_idx = 60  # Feb 2020
covid_intensity[start_idx:] = 0.55 * np.exp(-np.linspace(0, 2, len(covid_dates)-start_idx))
covid_intensity += np.random.normal(0, 0.02, len(covid_dates))
covid_intensity = np.clip(covid_intensity, 0, 0.6)

ax.fill_between(covid_dates, 0, covid_intensity, color=colors['main'], alpha=0.3)
ax.plot(covid_dates, covid_intensity, color=colors['main'], linewidth=1.5)

# Add event markers
events = {
    '2020-02-01': 'First US Case',
    '2020-03-11': 'WHO Pandemic',
    '2020-03-23': 'Market Bottom',
    '2020-11-09': 'Vaccine News'
}

for date, label in events.items():
    date_obj = pd.to_datetime(date)
    idx = np.argmin(np.abs(covid_dates - date_obj))
    ax.annotate(label, xy=(date_obj, covid_intensity[idx]),
                xytext=(date_obj, covid_intensity[idx] + 0.1),
                arrowprops=dict(arrowstyle='->', color=colors['light'], lw=1),
                fontsize=8, color=colors['main'])

ax.set_xlabel('Date', fontsize=10, color=colors['main'])
ax.set_ylabel('Negative Intensity', fontsize=10, color=colors['main'])
ax.set_title('COVID-19 Narrative Evolution (2020)', fontsize=12, color=colors['main'])
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 0.7)

plt.tight_layout()
plt.savefig('covid_narrative_timeline.pdf', dpi=300, bbox_inches='tight')
plt.close()

# Chart 4: Portfolio Performance Comparison
fig, ax = plt.subplots(figsize=(10, 5))
dates = pd.date_range('2015-06-01', '2021-12-31', freq='D')

# Generate cumulative returns
np.random.seed(42)
narrative_strategy = np.cumprod(1 + np.random.normal(0.0007, 0.008, len(dates)))
spy = np.cumprod(1 + np.random.normal(0.0005, 0.012, len(dates)))
bonds = np.cumprod(1 + np.random.normal(0.0001, 0.003, len(dates)))
balanced = np.cumprod(1 + np.random.normal(0.0003, 0.006, len(dates)))

ax.plot(dates, narrative_strategy, color=colors['accent'], linewidth=2, label='Narrative Strategy')
ax.plot(dates, spy, color=colors['main'], linewidth=1.5, alpha=0.7, label='SPY')
ax.plot(dates, balanced, color=colors['light'], linewidth=1.5, linestyle='--', label='50/50 Balanced')
ax.plot(dates, bonds, color=colors['light'], linewidth=1, alpha=0.5, label='Bonds')

ax.set_xlabel('Date', fontsize=10, color=colors['main'])
ax.set_ylabel('Cumulative Return', fontsize=10, color=colors['main'])
ax.set_title('Narrative-Based Asset Allocation Outperformance', fontsize=12, color=colors['main'])
ax.legend(loc='upper left', frameon=True, fancybox=False, edgecolor=colors['light'])
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('portfolio_performance.pdf', dpi=300, bbox_inches='tight')
plt.close()

# Chart 5: COVID Recovery Portfolio
fig, ax = plt.subplots(figsize=(10, 5))
dates = pd.date_range('2020-02-18', '2021-12-31', freq='D')
vaccine_date = pd.to_datetime('2020-11-09')
vaccine_idx = np.argmin(np.abs(dates - vaccine_date))

# Generate portfolio returns
np.random.seed(42)
pre_vaccine = np.random.normal(-0.001, 0.025, vaccine_idx)
post_vaccine = np.random.normal(0.003, 0.02, len(dates) - vaccine_idx)
returns = np.concatenate([pre_vaccine, post_vaccine])

low_beta_portfolio = np.cumprod(1 + returns) * 100
high_beta_portfolio = np.cumprod(1 - returns * 0.7) * 100
long_short = low_beta_portfolio - high_beta_portfolio + 100

ax.plot(dates, low_beta_portfolio, color=colors['accent'], linewidth=2, label='Low COVID Beta')
ax.plot(dates, high_beta_portfolio, color=colors['main'], linewidth=1.5, alpha=0.7, label='High COVID Beta')

# Mark vaccine announcement
ax.axvline(vaccine_date, color=colors['light'], linestyle='--', alpha=0.5)
ax.text(vaccine_date, 140, 'Vaccine\nAnnouncement', fontsize=8, color=colors['main'], ha='center')

ax.set_xlabel('Date', fontsize=10, color=colors['main'])
ax.set_ylabel('Portfolio Value (Base = 100)', fontsize=10, color=colors['main'])
ax.set_title('COVID-19 Recovery Portfolio Performance', fontsize=12, color=colors['main'])
ax.legend(loc='upper left', frameon=True, fancybox=False, edgecolor=colors['light'])
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('covid_recovery_portfolio.pdf', dpi=300, bbox_inches='tight')
plt.close()

print("All charts generated successfully:")
print("1. market_crash_vix.pdf")
print("2. narrative_r_squared.pdf")
print("3. covid_narrative_timeline.pdf")
print("4. portfolio_performance.pdf")
print("5. covid_recovery_portfolio.pdf")