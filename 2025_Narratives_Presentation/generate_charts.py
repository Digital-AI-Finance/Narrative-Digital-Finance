import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for academic presentations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Create date range
dates = pd.date_range(start='2015-01-01', end='2021-11-30', freq='D')

def create_narrative_intensity_plot():
    """Create Market Crash narrative vs VIX time series"""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Generate synthetic data mimicking paper results
    np.random.seed(42)
    vix_base = 15 + 5*np.sin(np.linspace(0, 8*np.pi, len(dates)))
    vix_noise = np.random.normal(0, 3, len(dates))
    vix = np.clip(vix_base + vix_noise, 10, 80)

    # Market crash intensity correlated with VIX
    mc_intensity = 0.05 + (vix - 10) / 200 + np.random.normal(0, 0.02, len(dates))
    mc_intensity = np.clip(mc_intensity, 0, 0.25)

    # Add some spikes for events
    spike_dates = ['2015-08-24', '2016-06-23', '2018-02-05', '2020-03-16']
    for spike in spike_dates:
        idx = pd.to_datetime(spike)
        # Find position manually
        pos = np.argmin(np.abs(dates - idx))
        if pos < len(dates) - 5:
            mc_intensity[pos:pos+5] *= 2
            vix[pos:pos+5] *= 1.5

    color1 = 'darkblue'
    ax1.plot(dates, mc_intensity, color=color1, linewidth=2, label='Market Crash Intensity')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Narrative Intensity', color=color1, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 0.3)

    ax2 = ax1.twinx()
    color2 = 'darkred'
    ax2.plot(dates, vix, color=color2, linewidth=2, alpha=0.7, label='VIX')
    ax2.set_ylabel('VIX Index', color=color2, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 100)

    # Add correlation text
    corr = np.corrcoef(mc_intensity, vix)[0,1]
    ax1.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=ax1.transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat'))

    ax1.grid(True, alpha=0.3)
    plt.title('Market Crash Narrative Intensity vs VIX Index', fontsize=14, fontweight='bold')
    fig.tight_layout()
    plt.savefig('narrative_intensity_vix.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_r_squared_heatmap():
    """Create heatmap of R-squared values for narratives"""
    # Top narratives and their R-squared values
    narratives = ['Market Crash', 'Gov & Corp Debt', 'Treasury Bonds', 'Global Growth',
                  'Liquidity', 'Trade War', 'COVID-19', 'Brexit', 'Fed Reserve',
                  'Inflation', 'Interest Rates', 'Recession']

    # Generate time-varying R-squared values
    months = pd.date_range('2015-01', '2021-11', freq='M')
    r_squared = np.zeros((len(narratives), len(months)))

    # Base R-squared values
    base_r2 = [0.34, 0.19, 0.18, 0.15, 0.15, 0.08, 0.12, 0.06, 0.14, 0.10, 0.12, 0.11]

    for i, base in enumerate(base_r2):
        # Add time variation
        trend = np.sin(np.linspace(0, 4*np.pi, len(months))) * 0.1
        noise = np.random.normal(0, 0.03, len(months))
        r_squared[i, :] = np.clip(base + trend + noise, 0, 0.6)

        # Add COVID spike for relevant narratives
        if narratives[i] in ['COVID-19', 'Market Crash', 'Recession']:
            covid_start = pd.to_datetime('2020-03-01')
            # Find nearest index manually
            covid_idx = np.argmin(np.abs(months - covid_start))
            r_squared[i, covid_idx:covid_idx+6] *= 1.5

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(r_squared, xticklabels=[m.strftime('%Y-%m') if i % 6 == 0 else ''
                                         for i, m in enumerate(months)],
                yticklabels=narratives, cmap='YlOrRd', vmin=0, vmax=0.6,
                cbar_kws={'label': 'R-squared'}, annot=False, fmt='.2f')

    plt.title('Narrative Explanatory Power Over Time (R² Values)', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Narrative', fontsize=12)
    plt.tight_layout()
    plt.savefig('r_squared_heatmap.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_portfolio_performance():
    """Create cumulative performance chart"""
    days = pd.date_range('2015-06-01', '2021-11-30', freq='D')
    n_days = len(days)

    # Generate returns
    np.random.seed(42)

    # Narrative strategy - higher Sharpe ratio
    narrative_daily = np.random.normal(0.0007, 0.009, n_days)
    # Add some momentum
    for i in range(1, len(narrative_daily)):
        narrative_daily[i] += 0.1 * narrative_daily[i-1]

    # SPY returns
    spy_daily = np.random.normal(0.0005, 0.012, n_days)

    # Bonds - lower vol
    bond_daily = np.random.normal(0.0001, 0.003, n_days)

    # 50/50 benchmark
    benchmark_daily = 0.5 * spy_daily + 0.5 * bond_daily

    # Calculate cumulative returns
    narrative_cum = (1 + narrative_daily).cumprod()
    spy_cum = (1 + spy_daily).cumprod()
    bond_cum = (1 + bond_daily).cumprod()
    benchmark_cum = (1 + benchmark_daily).cumprod()

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(days, narrative_cum, label='Narrative Strategy', linewidth=2.5, color='darkgreen')
    ax.plot(days, spy_cum, label='SPY', linewidth=2, color='darkblue')
    ax.plot(days, bond_cum, label='Bonds', linewidth=2, color='gray')
    ax.plot(days, benchmark_cum, label='50/50 Benchmark', linewidth=2, color='orange', linestyle='--')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Return', fontsize=12)
    ax.set_title('Asset Allocation Strategy Performance', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add shaded regions for risk-off periods
    risk_off_periods = [('2015-08-20', '2015-09-03'), ('2018-02-01', '2018-02-15'),
                        ('2020-03-01', '2020-03-31')]
    for start, end in risk_off_periods:
        ax.axvspan(pd.to_datetime(start), pd.to_datetime(end), alpha=0.2, color='red')

    plt.tight_layout()
    plt.savefig('allocation_performance.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_covid_beta_distribution():
    """Create histogram of COVID narrative betas"""
    np.random.seed(42)

    # Generate beta coefficients
    n_stocks = 500
    betas = np.random.normal(0, 0.5, n_stocks)

    # Add some extreme values
    betas[:25] = np.random.normal(-1.5, 0.3, 25)  # Recovery plays
    betas[-25:] = np.random.normal(1.5, 0.3, 25)   # Lockdown beneficiaries

    fig, ax = plt.subplots(figsize=(10, 6))

    n, bins, patches = ax.hist(betas, bins=50, edgecolor='black', alpha=0.7)

    # Color the extreme quintiles
    for i, patch in enumerate(patches):
        if bins[i] < np.percentile(betas, 5):
            patch.set_facecolor('darkgreen')
            patch.set_label('Long (Recovery)' if i == 0 else '')
        elif bins[i] > np.percentile(betas, 95):
            patch.set_facecolor('darkred')
            patch.set_label('Short (Lockdown)' if i == len(patches)-1 else '')
        else:
            patch.set_facecolor('lightblue')

    ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
    ax.set_xlabel('COVID-19 Narrative Beta', fontsize=12)
    ax.set_ylabel('Number of Stocks', fontsize=12)
    ax.set_title('Distribution of Stock Sensitivities to COVID-19 Narrative', fontsize=14, fontweight='bold')

    # Add statistics
    mean_beta = np.mean(betas)
    std_beta = np.std(betas)
    ax.text(0.7, 0.95, f'Mean: {mean_beta:.3f}\\nStd: {std_beta:.3f}',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat'))

    handles = [patches[0], patches[-1]]
    labels = ['Long (Recovery)', 'Short (Lockdown)']
    ax.legend(handles, labels, loc='upper left')

    plt.tight_layout()
    plt.savefig('covid_beta_distribution.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_network_graph():
    """Create narrative correlation network"""
    import networkx as nx

    narratives = ['Market\\nCrash', 'Gov\\nDebt', 'Treasury\\nBonds', 'Global\\nGrowth',
                  'Liquidity', 'COVID-19', 'Trade\\nWar', 'Fed\\nReserve']

    # Create correlation matrix
    n = len(narratives)
    corr_matrix = np.random.rand(n, n) * 0.4 + 0.3
    np.fill_diagonal(corr_matrix, 1)
    corr_matrix = (corr_matrix + corr_matrix.T) / 2

    # Make some strong correlations
    corr_matrix[0, 1] = corr_matrix[1, 0] = 0.85  # Market Crash - Gov Debt
    corr_matrix[0, 4] = corr_matrix[4, 0] = 0.75  # Market Crash - Liquidity
    corr_matrix[2, 7] = corr_matrix[7, 2] = 0.70  # Treasury - Fed

    fig, ax = plt.subplots(figsize=(10, 10))

    # Create graph
    G = nx.Graph()

    # Add nodes
    for narrative in narratives:
        G.add_node(narrative)

    # Add edges for correlations > 0.6
    for i in range(n):
        for j in range(i+1, n):
            if corr_matrix[i, j] > 0.6:
                G.add_edge(narratives[i], narratives[j], weight=corr_matrix[i, j])

    # Position nodes
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Draw network
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=3000, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)

    # Draw edges with width based on correlation
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    nx.draw_networkx_edges(G, pos, width=[w*5 for w in weights], alpha=0.6, ax=ax)

    ax.set_title('Narrative Correlation Network', fontsize=14, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('narrative_network.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_rolling_coefficients():
    """Create rolling regression coefficients plot"""
    dates = pd.date_range('2015-01-01', '2021-11-30', freq='D')

    # Generate time-varying coefficients
    np.random.seed(42)
    base_coef = -0.26
    trend = 0.1 * np.sin(np.linspace(0, 6*np.pi, len(dates)))
    noise = np.random.normal(0, 0.02, len(dates))
    coefficients = base_coef + trend + noise

    # Add structural break around COVID
    covid_idx = pd.to_datetime('2020-03-01')
    pos = np.argmin(np.abs(dates - covid_idx))
    if pos < len(dates) - 90:
        coefficients[pos:pos+90] *= 1.5

    # Calculate rolling standard errors
    std_errors = np.abs(coefficients) / 3 + np.random.normal(0.05, 0.01, len(dates))
    upper_bound = coefficients + 1.96 * std_errors
    lower_bound = coefficients - 1.96 * std_errors

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot coefficients
    ax1.plot(dates, coefficients, color='darkblue', linewidth=2, label='Coefficient')
    ax1.fill_between(dates, lower_bound, upper_bound, alpha=0.3, color='lightblue', label='95% CI')
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax1.set_ylabel('Coefficient Value', fontsize=12)
    ax1.set_title('Rolling Regression: Market Crash Narrative Impact', fontsize=14, fontweight='bold')
    ax1.legend(loc='lower left')
    ax1.grid(True, alpha=0.3)

    # Plot t-statistics
    t_stats = coefficients / std_errors
    ax2.plot(dates, t_stats, color='darkgreen', linewidth=2)
    ax2.axhline(y=-1.96, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axhline(y=1.96, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax2.fill_between(dates, -1.96, 1.96, alpha=0.1, color='gray')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('t-statistic', fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('rolling_coefficients.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_data_pipeline_diagram():
    """Create data processing pipeline diagram"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Define pipeline stages
    stages = [
        ('Data Collection\\n150,000+ sources', 0.1, 0.8),
        ('NLP Processing\\nNarrative ID', 0.3, 0.8),
        ('Sentiment Scoring\\nReservoir Adj', 0.5, 0.8),
        ('Intensity Calc\\n73 Narratives', 0.7, 0.8),
        ('Analysis\\nRegression/ML', 0.9, 0.8)
    ]

    # Draw boxes
    for i, (text, x, y) in enumerate(stages):
        rect = plt.Rectangle((x-0.08, y-0.1), 0.16, 0.2,
                             facecolor='lightblue', edgecolor='darkblue', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')

    # Draw arrows
    arrow_props = dict(arrowstyle='->', lw=2, color='darkblue')
    for i in range(len(stages)-1):
        ax.annotate('', xy=(stages[i+1][1]-0.08, stages[i+1][2]),
                    xytext=(stages[i][1]+0.08, stages[i][2]),
                    arrowprops=arrow_props)

    # Add data flow labels
    ax.text(0.2, 0.6, 'Raw\\nArticles', ha='center', fontsize=9, style='italic')
    ax.text(0.4, 0.6, 'Tagged\\nContent', ha='center', fontsize=9, style='italic')
    ax.text(0.6, 0.6, 'Scored\\nArticles', ha='center', fontsize=9, style='italic')
    ax.text(0.8, 0.6, 'Time\\nSeries', ha='center', fontsize=9, style='italic')

    # Add output branches
    outputs = [
        ('Trading\\nSignals', 0.9, 0.4),
        ('Risk\\nMetrics', 0.9, 0.2)
    ]

    for text, x, y in outputs:
        rect = plt.Rectangle((x-0.06, y-0.08), 0.12, 0.16,
                             facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=9)
        ax.annotate('', xy=(x, y+0.08), xytext=(0.9, 0.7),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='darkgreen'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Narrative Data Processing Pipeline', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('data_pipeline.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_machine_learning_comparison():
    """Create ML model performance comparison"""
    models = ['Linear\\nRegression', 'VAR', 'Random\\nForest', 'LSTM', 'Transformer']
    r_squared = [0.08, 0.11, 0.13, 0.15, 0.18]
    sharpe = [0.71, 0.89, 0.95, 1.12, 1.34]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # R-squared comparison
    colors = ['gray', 'lightblue', 'yellow', 'orange', 'darkgreen']
    bars1 = ax1.bar(models, r_squared, color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Out-of-Sample R²', fontsize=12)
    ax1.set_title('Predictive Accuracy', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 0.25)
    ax1.grid(True, alpha=0.3, axis='y')

    # Add values on bars
    for bar, val in zip(bars1, r_squared):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{val:.2f}', ha='center', fontsize=10)

    # Sharpe ratio comparison
    bars2 = ax2.bar(models, sharpe, color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Sharpe Ratio', fontsize=12)
    ax2.set_title('Risk-Adjusted Returns', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 1.6)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)

    # Add values on bars
    for bar, val in zip(bars2, sharpe):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                f'{val:.2f}', ha='center', fontsize=10)

    fig.suptitle('Machine Learning Model Performance Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('ml_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_3d_surface_plot():
    """Create 3D surface plot of narrative intensity, returns, and volatility"""
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Generate grid data
    narrative_intensity = np.linspace(0, 0.3, 30)
    volatility = np.linspace(10, 50, 30)
    X, Y = np.meshgrid(narrative_intensity, volatility)

    # Create returns surface (negative correlation with both)
    Z = 0.15 - 0.8*X - 0.002*Y + 0.1*np.random.randn(30, 30)

    # Plot surface
    surf = ax.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.8,
                           linewidth=0, antialiased=True)

    # Add labels
    ax.set_xlabel('Narrative Intensity', fontsize=11)
    ax.set_ylabel('VIX (Volatility)', fontsize=11)
    ax.set_zlabel('Expected Return', fontsize=11)
    ax.set_title('3D Relationship: Narratives, Volatility, and Returns',
                 fontsize=13, fontweight='bold')

    # Add colorbar
    fig.colorbar(surf, shrink=0.5, aspect=5)

    # Rotate for better view
    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    plt.savefig('3d_surface_plot.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_predictive_power_analysis():
    """Create out-of-sample R² evolution chart"""
    # Generate time periods
    periods = pd.date_range('2016-01', '2021-11', freq='Q')

    # Generate R² values for different models
    np.random.seed(42)

    # Base model (just returns)
    base_r2 = 0.02 + np.random.normal(0, 0.01, len(periods))
    base_r2 = np.clip(base_r2, 0, 0.1)

    # With VIX
    vix_r2 = 0.06 + np.random.normal(0, 0.015, len(periods))
    vix_r2 = np.clip(vix_r2, 0.02, 0.15)

    # With narratives
    narrative_r2 = 0.12 + 0.02*np.sin(np.linspace(0, 4*np.pi, len(periods)))
    narrative_r2 += np.random.normal(0, 0.02, len(periods))
    narrative_r2 = np.clip(narrative_r2, 0.05, 0.25)

    # Combined model
    combined_r2 = 0.18 + 0.03*np.sin(np.linspace(0, 4*np.pi, len(periods)))
    combined_r2 += np.random.normal(0, 0.025, len(periods))
    combined_r2 = np.clip(combined_r2, 0.1, 0.35)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(periods, base_r2, label='Lagged Returns Only', linewidth=2, color='gray')
    ax.plot(periods, vix_r2, label='Returns + VIX', linewidth=2, color='blue')
    ax.plot(periods, narrative_r2, label='Returns + Narratives', linewidth=2, color='green')
    ax.plot(periods, combined_r2, label='Full Model', linewidth=2.5, color='red')

    # Add shaded region for COVID
    covid_start = pd.to_datetime('2020-01-01')
    covid_end = pd.to_datetime('2020-12-31')
    ax.axvspan(covid_start, covid_end, alpha=0.1, color='red', label='COVID-19 Period')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Out-of-Sample R²', fontsize=12)
    ax.set_title('Predictive Power Analysis: Model Evolution', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 0.4)

    # Add annotation
    ax.annotate('Narratives add predictive value',
                xy=(pd.to_datetime('2020-06-01'), 0.28),
                xytext=(pd.to_datetime('2019-01-01'), 0.32),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                fontsize=10)

    plt.tight_layout()
    plt.savefig('predictive_power_analysis.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_asset_allocation_pie():
    """Create asset allocation pie charts for different market regimes"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Normal market regime
    normal_sizes = [60, 30, 10]
    normal_labels = ['Equities', 'Bonds', 'Cash']
    normal_colors = ['#2E7D32', '#1976D2', '#FFA726']

    axes[0].pie(normal_sizes, labels=normal_labels, colors=normal_colors,
                autopct='%1.0f%%', startangle=90)
    axes[0].set_title('Normal Regime\n(z-score < 2)', fontsize=11, fontweight='bold')

    # Elevated narrative regime
    elevated_sizes = [40, 45, 15]
    elevated_labels = ['Equities', 'Bonds', 'Cash']

    axes[1].pie(elevated_sizes, labels=elevated_labels, colors=normal_colors,
                autopct='%1.0f%%', startangle=90)
    axes[1].set_title('Elevated Narrative\n(2 < z-score < 3)', fontsize=11, fontweight='bold')

    # Crisis narrative regime
    crisis_sizes = [10, 60, 30]
    crisis_labels = ['Equities', 'Bonds', 'Cash']

    axes[2].pie(crisis_sizes, labels=crisis_labels, colors=normal_colors,
                autopct='%1.0f%%', startangle=90)
    axes[2].set_title('Crisis Narrative\n(z-score > 3)', fontsize=11, fontweight='bold')

    fig.suptitle('Dynamic Asset Allocation Based on Market Crash Narrative',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig('asset_allocation_pie.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all charts"""
    print("Generating charts for presentation...")

    print("1. Creating narrative intensity vs VIX plot...")
    create_narrative_intensity_plot()

    print("2. Creating R-squared heatmap...")
    create_r_squared_heatmap()

    print("3. Creating portfolio performance chart...")
    create_portfolio_performance()

    print("4. Creating COVID beta distribution...")
    create_covid_beta_distribution()

    print("5. Creating narrative network graph...")
    create_network_graph()

    print("6. Creating rolling coefficients plot...")
    create_rolling_coefficients()

    print("7. Creating data pipeline diagram...")
    create_data_pipeline_diagram()

    print("8. Creating ML comparison chart...")
    create_machine_learning_comparison()

    print("9. Creating 3D surface plot...")
    create_3d_surface_plot()

    print("10. Creating predictive power analysis...")
    create_predictive_power_analysis()

    print("11. Creating asset allocation pie charts...")
    create_asset_allocation_pie()

    print("All charts generated successfully!")
    print("PDF files saved in current directory.")

if __name__ == "__main__":
    main()