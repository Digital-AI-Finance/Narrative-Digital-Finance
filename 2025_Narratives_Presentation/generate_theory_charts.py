import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import odeint
from scipy.stats import norm
import networkx as nx

# Set style for academic presentations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_sir_narrative_dynamics():
    """Create SIR model dynamics for narrative contagion"""
    # Parameters
    beta = 0.3  # transmission rate
    gamma = 0.05  # recovery rate
    delta = 0.01  # loss of immunity

    # Initial conditions
    S0, I0, R0 = 0.8, 0.2, 0.0
    N = 1.0

    # Time points
    t = np.linspace(0, 200, 1000)

    # SIR differential equations
    def deriv(y, t, beta, gamma, delta):
        S, I, R = y
        dS = -beta * S * I + delta * R
        dI = beta * S * I - gamma * I
        dR = gamma * I - delta * R
        return dS, dI, dR

    # Integrate the SIR equations
    y0 = S0, I0, R0
    sol = odeint(deriv, y0, t, args=(beta, gamma, delta))
    S, I, R = sol.T

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Time evolution
    ax1.plot(t, S, 'b-', alpha=0.7, linewidth=2, label='Susceptible')
    ax1.plot(t, I, 'r-', alpha=0.7, linewidth=2, label='Infected (Active Narrative)')
    ax1.plot(t, R, 'g-', alpha=0.7, linewidth=2, label='Recovered')
    ax1.set_xlabel('Time', fontsize=11)
    ax1.set_ylabel('Population Fraction', fontsize=11)
    ax1.set_title('Narrative Contagion Dynamics (SIR Model)', fontsize=12, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Phase portrait
    ax2.plot(S, I, 'k-', alpha=0.5)
    ax2.plot(S[0], I[0], 'go', markersize=8, label='Start')
    ax2.plot(S[-1], I[-1], 'ro', markersize=8, label='End')
    ax2.set_xlabel('Susceptible', fontsize=11)
    ax2.set_ylabel('Infected', fontsize=11)
    ax2.set_title('Phase Portrait', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Add R0 annotation
    ax1.text(0.7, 0.85, f'$R_0$ = {beta/gamma:.2f}', transform=ax1.transAxes,
             fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat'))

    plt.tight_layout()
    plt.savefig('sir_narrative_dynamics.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_information_theory_visualization():
    """Visualize entropy and mutual information concepts"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Shannon Entropy vs distribution
    ax = axes[0, 0]
    p_values = np.linspace(0.01, 0.99, 100)
    entropy_binary = -p_values * np.log2(p_values) - (1-p_values) * np.log2(1-p_values)
    ax.plot(p_values, entropy_binary, 'b-', linewidth=2)
    ax.set_xlabel('Probability p', fontsize=11)
    ax.set_ylabel('H(X) bits', fontsize=11)
    ax.set_title('Shannon Entropy for Binary Narrative', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axvline(x=0.5, color='r', linestyle='--', alpha=0.5)
    ax.text(0.5, 0.8, 'Maximum\nuncertainty', ha='center', fontsize=9)

    # 2. Mutual Information Venn Diagram
    ax = axes[0, 1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    circle1 = plt.Circle((3.5, 5), 2, color='blue', alpha=0.3, label='H(N)')
    circle2 = plt.Circle((6.5, 5), 2, color='red', alpha=0.3, label='H(R)')
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    ax.text(3, 5, 'H(N|R)', fontsize=10, ha='center')
    ax.text(5, 5, 'I(N;R)', fontsize=10, ha='center', fontweight='bold')
    ax.text(7, 5, 'H(R|N)', fontsize=10, ha='center')
    ax.set_title('Mutual Information Structure', fontsize=11, fontweight='bold')
    ax.axis('off')

    # 3. Transfer Entropy
    ax = axes[1, 0]
    lags = np.arange(0, 20)
    te_forward = np.exp(-lags/5) * (1 + 0.3*np.sin(lags))
    te_backward = np.exp(-lags/10) * 0.3
    ax.plot(lags, te_forward, 'b-', linewidth=2, label='TE(Narrative→Return)')
    ax.plot(lags, te_backward, 'r-', linewidth=2, label='TE(Return→Narrative)')
    ax.set_xlabel('Lag (days)', fontsize=11)
    ax.set_ylabel('Transfer Entropy (bits)', fontsize=11)
    ax.set_title('Directional Information Flow', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Joint Entropy Heatmap
    ax = axes[1, 1]
    n_bins = 20
    narrative = np.random.normal(0, 1, 1000)
    returns = 0.3 * narrative + np.random.normal(0, 0.8, 1000)
    H, xedges, yedges = np.histogram2d(narrative, returns, bins=n_bins)
    H = H.T
    im = ax.imshow(H, interpolation='nearest', origin='lower',
                   extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
                   aspect='auto', cmap='YlOrRd')
    ax.set_xlabel('Narrative Intensity', fontsize=11)
    ax.set_ylabel('Returns', fontsize=11)
    ax.set_title('Joint Distribution', fontsize=11, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Frequency')

    plt.tight_layout()
    plt.savefig('information_theory.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_stochastic_process_paths():
    """Simulate jump-diffusion process for narrative intensity"""
    np.random.seed(42)

    # Parameters
    T = 2.0  # time horizon
    dt = 0.01
    n_steps = int(T / dt)
    t = np.linspace(0, T, n_steps)

    # Mean-reverting jump-diffusion parameters
    kappa = 2.0  # mean reversion
    theta = 0.1  # long-run mean
    sigma = 0.15  # diffusion volatility
    lambda_jump = 3.0  # jump intensity
    mu_jump = 0.05  # jump mean
    sigma_jump = 0.02  # jump std

    # Simulate multiple paths
    n_paths = 5
    paths = []

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    for i in range(n_paths):
        N = np.zeros(n_steps)
        N[0] = 0.1

        for j in range(1, n_steps):
            # Diffusion part
            dW = np.random.normal(0, np.sqrt(dt))
            drift = kappa * (theta - N[j-1]) * dt
            diffusion = sigma * np.sqrt(max(N[j-1], 0)) * dW

            # Jump part
            dJ = np.random.poisson(lambda_jump * dt)
            if dJ > 0:
                jump_size = np.random.normal(mu_jump, sigma_jump)
                jump = jump_size * dJ
            else:
                jump = 0

            N[j] = N[j-1] + drift + diffusion + jump
            N[j] = max(N[j], 0)  # ensure non-negative

        paths.append(N)
        ax1.plot(t, N, alpha=0.7, linewidth=1.5)

    ax1.axhline(y=theta, color='r', linestyle='--', label=f'θ = {theta}')
    ax1.set_xlabel('Time', fontsize=11)
    ax1.set_ylabel('Narrative Intensity', fontsize=11)
    ax1.set_title('Jump-Diffusion Sample Paths', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Distribution at terminal time
    terminal_values = [path[-1] for path in paths]
    ax2.hist(terminal_values, bins=30, density=True, alpha=0.7, color='blue')
    x = np.linspace(0, 0.3, 100)
    ax2.set_xlabel('Narrative Intensity', fontsize=11)
    ax2.set_ylabel('Density', fontsize=11)
    ax2.set_title('Terminal Distribution', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('stochastic_processes.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_portfolio_frontier():
    """Create efficient frontier with narrative constraints"""
    np.random.seed(42)

    # Generate sample returns and narrative betas
    n_assets = 100
    mu = np.random.normal(0.08, 0.03, n_assets)
    sigma = np.random.uniform(0.15, 0.35, n_assets)
    narrative_beta = np.random.normal(0, 0.5, n_assets)

    # Correlation matrix
    rho = 0.3
    corr = np.full((n_assets, n_assets), rho)
    np.fill_diagonal(corr, 1.0)

    # Covariance matrix
    D = np.diag(sigma)
    cov_matrix = D @ corr @ D

    # Efficient frontier without constraints
    target_returns = np.linspace(mu.min(), mu.max(), 50)
    frontier_vol = []
    frontier_weights = []

    for target in target_returns:
        # Simplified mean-variance (equal weight for demonstration)
        w = np.ones(n_assets) / n_assets
        portfolio_vol = np.sqrt(w.T @ cov_matrix @ w)
        frontier_vol.append(portfolio_vol)
        frontier_weights.append(w)

    # Efficient frontier with narrative constraint
    max_narrative_exposure = 0.3
    constrained_vol = []

    for target in target_returns:
        w = np.ones(n_assets) / n_assets
        # Adjust weights to satisfy narrative constraint
        narrative_exposure = np.abs(w @ narrative_beta)
        if narrative_exposure > max_narrative_exposure:
            w = w * (max_narrative_exposure / narrative_exposure)
            w = w / w.sum()
        portfolio_vol = np.sqrt(w.T @ cov_matrix @ w)
        constrained_vol.append(portfolio_vol)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Efficient frontier plot
    ax1.plot(frontier_vol, target_returns, 'b-', linewidth=2, label='Unconstrained')
    ax1.plot(constrained_vol, target_returns, 'r--', linewidth=2, label='Narrative Constrained')
    ax1.scatter(sigma[:20], mu[:20], alpha=0.5, s=30, c='gray', label='Individual Assets')
    ax1.set_xlabel('Volatility', fontsize=11)
    ax1.set_ylabel('Expected Return', fontsize=11)
    ax1.set_title('Efficient Frontier with Narrative Constraints', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Narrative exposure vs return
    narrative_exposures = [np.abs(w @ narrative_beta) for w in frontier_weights]
    ax2.plot(target_returns, narrative_exposures, 'b-', linewidth=2)
    ax2.axhline(y=max_narrative_exposure, color='r', linestyle='--', label='Constraint')
    ax2.set_xlabel('Expected Return', fontsize=11)
    ax2.set_ylabel('Narrative Exposure', fontsize=11)
    ax2.set_title('Narrative Exposure along Frontier', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('portfolio_frontier.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_network_eigenvalues():
    """Visualize network eigenvalue spectrum and centrality"""
    # Create a narrative network
    n_nodes = 50
    G = nx.barabasi_albert_graph(n_nodes, 3, seed=42)

    # Get adjacency matrix and compute eigenvalues
    A = nx.adjacency_matrix(G).todense()
    eigenvalues = np.linalg.eigvals(A)
    eigenvalues = np.sort(eigenvalues)[::-1]

    # Compute centrality measures
    degree_cent = nx.degree_centrality(G)
    eigenvector_cent = nx.eigenvector_centrality(G)
    pagerank = nx.pagerank(G)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Network visualization
    ax = axes[0, 0]
    pos = nx.spring_layout(G, seed=42)
    node_colors = [pagerank[i]*1000 for i in G.nodes()]
    nx.draw(G, pos, ax=ax, node_color=node_colors, node_size=300,
            cmap='YlOrRd', with_labels=False, edge_color='gray', alpha=0.6)
    ax.set_title('Narrative Network Structure', fontsize=12, fontweight='bold')

    # 2. Eigenvalue spectrum
    ax = axes[0, 1]
    ax.plot(np.real(eigenvalues), 'b-', linewidth=2)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax.set_xlabel('Index', fontsize=11)
    ax.set_ylabel('Eigenvalue', fontsize=11)
    ax.set_title('Adjacency Matrix Spectrum', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.text(0.6, 0.9, f'λ_max = {np.real(eigenvalues[0]):.2f}',
            transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat'))

    # 3. Centrality comparison
    ax = axes[1, 0]
    nodes = list(G.nodes())[:20]
    x = np.arange(len(nodes))
    width = 0.25
    ax.bar(x - width, [degree_cent[n] for n in nodes], width, label='Degree')
    ax.bar(x, [eigenvector_cent[n] for n in nodes], width, label='Eigenvector')
    ax.bar(x + width, [pagerank[n] for n in nodes], width, label='PageRank')
    ax.set_xlabel('Node', fontsize=11)
    ax.set_ylabel('Centrality Score', fontsize=11)
    ax.set_title('Centrality Measures Comparison', fontsize=12, fontweight='bold')
    ax.legend()

    # 4. Laplacian spectrum (for diffusion)
    ax = axes[1, 1]
    L = nx.laplacian_matrix(G).todense()
    laplacian_eigenvalues = np.linalg.eigvals(L)
    laplacian_eigenvalues = np.sort(np.real(laplacian_eigenvalues))
    ax.plot(laplacian_eigenvalues, 'g-', linewidth=2)
    ax.set_xlabel('Index', fontsize=11)
    ax.set_ylabel('Eigenvalue', fontsize=11)
    ax.set_title('Laplacian Spectrum (Diffusion)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.text(0.6, 0.9, f'λ_2 = {laplacian_eigenvalues[1]:.3f}',
            transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat'))

    plt.tight_layout()
    plt.savefig('network_analysis.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_optimization_surface():
    """3D surface for portfolio optimization with narrative constraints"""
    fig = plt.figure(figsize=(14, 6))

    # Create grid
    lambda_risk = np.linspace(0, 5, 50)
    gamma_narrative = np.linspace(0, 2, 50)
    X, Y = np.meshgrid(lambda_risk, gamma_narrative)

    # Objective function (simplified)
    expected_return = 0.08
    variance = 0.04
    narrative_penalty = 0.02
    Z = expected_return - X * variance - Y * narrative_penalty

    # First subplot: 3D surface
    ax1 = fig.add_subplot(121, projection='3d')
    surf = ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    ax1.set_xlabel('Risk Aversion (λ)', fontsize=10)
    ax1.set_ylabel('Narrative Penalty (γ)', fontsize=10)
    ax1.set_zlabel('Utility', fontsize=10)
    ax1.set_title('Optimization Landscape', fontsize=12, fontweight='bold')
    fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5)

    # Second subplot: Contour plot
    ax2 = fig.add_subplot(122)
    contour = ax2.contour(X, Y, Z, levels=20)
    ax2.clabel(contour, inline=True, fontsize=8)
    ax2.set_xlabel('Risk Aversion (λ)', fontsize=11)
    ax2.set_ylabel('Narrative Penalty (γ)', fontsize=11)
    ax2.set_title('Utility Contours', fontsize=12, fontweight='bold')

    # Mark optimal point
    opt_lambda = 2.5
    opt_gamma = 0.8
    ax2.plot(opt_lambda, opt_gamma, 'r*', markersize=15, label='Optimal')
    ax2.legend()

    plt.tight_layout()
    plt.savefig('optimization_surface.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all theory-focused charts"""
    print("Generating theory-focused visualizations...")

    print("1. Creating SIR narrative dynamics...")
    create_sir_narrative_dynamics()

    print("2. Creating information theory visualization...")
    create_information_theory_visualization()

    print("3. Creating stochastic process paths...")
    create_stochastic_process_paths()

    print("4. Creating portfolio frontier...")
    create_portfolio_frontier()

    print("5. Creating network analysis...")
    create_network_eigenvalues()

    print("6. Creating optimization surface...")
    create_optimization_surface()

    print("All theory-focused charts generated successfully!")
    print("PDF files saved in current directory.")

if __name__ == "__main__":
    main()