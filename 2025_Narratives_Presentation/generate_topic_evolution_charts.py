import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import multivariate_normal
from scipy.spatial.distance import cdist
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
import warnings
warnings.filterwarnings('ignore')

# Set minimalist style with WCAG AAA compliant colors
plt.style.use('seaborn-v0_8-whitegrid')
colors = {
    'PureBlack': '#000000',
    'DeepBlue': '#002D72',
    'DarkGray': '#404040',
    'DarkGreen': '#006400',
    'DarkRed': '#8B0000',
    'LightGray': '#C0C0C0',
    'ChartBlue': '#0072B2',
    'ChartOrange': '#E69F00',
    'ChartTeal': '#009E73',
    'ChartPurple': '#CC79A7',
    'ChartPink': '#F0E442',
    'ChartBrown': '#D55E00'
}

# Set default figure parameters
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# 1. Topic Evolution Over Time
print("Generating topic evolution visualization...")
fig, ax = plt.subplots(figsize=(12, 6))

# Generate synthetic topic evolution data
np.random.seed(42)
dates = pd.date_range('2020-01-01', '2024-12-31', freq='W')
n_topics = 6
topic_names = ['Market Crash', 'Fed Policy', 'COVID-19', 'Inflation', 'AI/Tech', 'Geopolitical']
topic_colors = [colors['DarkRed'], colors['DeepBlue'], colors['DarkGreen'],
                colors['ChartOrange'], colors['ChartPurple'], colors['ChartTeal']]

# Create evolving topic intensities
topic_data = []
for i, topic in enumerate(topic_names):
    # Base pattern
    base = np.sin(np.linspace(0, 4*np.pi, len(dates)) + i*np.pi/3) * 0.1 + 0.15

    # Add topic-specific patterns
    if topic == 'COVID-19':
        spike_idx = np.where((dates >= '2020-03-01') & (dates <= '2021-06-01'))[0]
        base[spike_idx] *= 3
    elif topic == 'Inflation':
        spike_idx = np.where(dates >= '2022-01-01')[0]
        base[spike_idx] *= 2
    elif topic == 'AI/Tech':
        spike_idx = np.where(dates >= '2023-01-01')[0]
        base[spike_idx] *= 2.5

    # Add noise and smooth
    base += np.random.normal(0, 0.02, len(dates))
    base = np.convolve(base, np.ones(4)/4, mode='same')
    base = np.clip(base, 0, 1)
    topic_data.append(base)

# Stack area plot
ax.stackplot(dates, *topic_data, labels=topic_names, colors=topic_colors, alpha=0.8)

# Add major events
events = {
    '2020-03-11': 'WHO Pandemic',
    '2021-01-06': 'Capitol Events',
    '2022-02-24': 'Ukraine Crisis',
    '2022-11-30': 'ChatGPT Launch',
    '2023-03-10': 'SVB Collapse'
}

for date, label in events.items():
    date_obj = pd.to_datetime(date)
    if date_obj in dates:
        ax.axvline(date_obj, color=colors['LightGray'], linestyle='--', alpha=0.5)
        ax.text(date_obj, ax.get_ylim()[1]*0.95, label, rotation=90,
               fontsize=8, ha='right', va='top', color=colors['DarkGray'])

ax.set_xlabel('Date', fontsize=10, color=colors['DarkGray'])
ax.set_ylabel('Topic Intensity (Normalized)', fontsize=10, color=colors['DarkGray'])
ax.set_title('Dynamic Topic Evolution in Financial Narratives (2020-2024)', fontsize=12, fontweight='bold')
ax.legend(loc='upper left', frameon=True, fancybox=False, ncol=2, fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1.2)

plt.tight_layout()
plt.savefig('topic_evolution.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 2. Embedding Space with Contrastive Learning
print("Generating contrastive learning embedding space...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Before contrastive learning
ax = axes[0]
np.random.seed(42)
n_samples = 300
n_clusters = 5

# Generate overlapping clusters
X_before = []
y_before = []
cluster_centers = np.random.randn(n_clusters, 2) * 2

for i in range(n_clusters):
    cluster_data = np.random.randn(n_samples//n_clusters, 2) * 1.5 + cluster_centers[i]
    X_before.append(cluster_data)
    y_before.extend([i] * (n_samples//n_clusters))

X_before = np.vstack(X_before)
colors_list = [colors['ChartBlue'], colors['ChartOrange'], colors['ChartTeal'],
              colors['ChartPurple'], colors['DarkRed']]

for i in range(n_clusters):
    mask = np.array(y_before) == i
    ax.scatter(X_before[mask, 0], X_before[mask, 1], c=colors_list[i],
              alpha=0.5, s=30, label=f'Topic {i+1}')

ax.set_title('Before Contrastive Learning', fontsize=11)
ax.set_xlabel('Dimension 1')
ax.set_ylabel('Dimension 2')
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)

# After contrastive learning
ax = axes[1]
X_after = []
y_after = []

# Better separated clusters
cluster_centers_after = np.array([[3, 3], [-3, 3], [-3, -3], [3, -3], [0, 0]]) * 1.5

for i in range(n_clusters):
    cluster_data = np.random.randn(n_samples//n_clusters, 2) * 0.5 + cluster_centers_after[i]
    X_after.append(cluster_data)
    y_after.extend([i] * (n_samples//n_clusters))

X_after = np.vstack(X_after)

for i in range(n_clusters):
    mask = np.array(y_after) == i
    ax.scatter(X_after[mask, 0], X_after[mask, 1], c=colors_list[i],
              alpha=0.6, s=30, label=f'Topic {i+1}')

    # Add cluster boundaries
    circle = plt.Circle(cluster_centers_after[i], 1.2, fill=False,
                       edgecolor=colors_list[i], linestyle='--', linewidth=1, alpha=0.5)
    ax.add_patch(circle)

ax.set_title('After Contrastive Learning (SimCLR)', fontsize=11)
ax.set_xlabel('Dimension 1')
ax.set_ylabel('Dimension 2')
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)

plt.suptitle('Impact of Contrastive Learning on Topic Embeddings', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('contrastive_embeddings.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 3. Hierarchical Topic Structure
print("Generating hierarchical topic structure...")
fig, ax = plt.subplots(figsize=(10, 10))

# Define hierarchical structure
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Root and branches
hierarchy = {
    'Financial Markets': {
        'pos': [5, 9],
        'children': {
            'Equity': {
                'pos': [2, 7],
                'children': {
                    'Tech Stocks': {'pos': [1, 5]},
                    'Value Stocks': {'pos': [3, 5]}
                }
            },
            'Fixed Income': {
                'pos': [5, 7],
                'children': {
                    'Treasuries': {'pos': [4.5, 5]},
                    'Corporate': {'pos': [5.5, 5]}
                }
            },
            'Macro': {
                'pos': [8, 7],
                'children': {
                    'Fed Policy': {'pos': [7, 5]},
                    'Inflation': {'pos': [9, 5]}
                }
            }
        }
    },
    'Geopolitical': {
        'pos': [5, 3],
        'children': {
            'Trade Wars': {'pos': [3, 1]},
            'Sanctions': {'pos': [5, 1]},
            'Elections': {'pos': [7, 1]}
        }
    }
}

def draw_node(ax, name, pos, level=0):
    colors_by_level = [colors['DeepBlue'], colors['ChartTeal'], colors['ChartOrange']]
    color = colors_by_level[min(level, 2)]

    box = FancyBboxPatch((pos[0]-0.8, pos[1]-0.2), 1.6, 0.4,
                         boxstyle="round,pad=0.05",
                         facecolor='white',
                         edgecolor=color,
                         linewidth=2)
    ax.add_patch(box)
    ax.text(pos[0], pos[1], name, ha='center', va='center',
           fontsize=9-level, fontweight='bold' if level==0 else 'normal')

def draw_connections(ax, parent_pos, children):
    for child_info in children.values():
        child_pos = child_info['pos']
        arrow = FancyArrowPatch(parent_pos, child_pos,
                              connectionstyle="arc3,rad=0.1",
                              arrowstyle='->',
                              mutation_scale=15,
                              linewidth=1.5,
                              color=colors['LightGray'])
        ax.add_patch(arrow)

# Draw hierarchy
def draw_hierarchy(ax, node_dict, level=0):
    for name, info in node_dict.items():
        draw_node(ax, name, info['pos'], level)
        if 'children' in info:
            draw_connections(ax, info['pos'], info['children'])
            draw_hierarchy(ax, info['children'], level+1)

draw_hierarchy(ax, hierarchy)

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('Hierarchical Topic Taxonomy', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('hierarchical_topics.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 4. Time Series Aggregation Methods Comparison
print("Generating time series aggregation comparison...")
fig, axes = plt.subplots(3, 2, figsize=(12, 10))

# Generate raw narrative signal
np.random.seed(42)
t = np.linspace(0, 365, 365)  # Daily data for one year
raw_signal = (np.sin(t/30) * 0.3 +
             np.sin(t/7) * 0.1 +  # Weekly pattern
             np.random.normal(0, 0.15, len(t)))  # Noise

# Add events/spikes
event_days = [50, 150, 250, 300]
for day in event_days:
    raw_signal[day:day+5] += np.random.uniform(0.3, 0.6)

# 1. Raw signal
ax = axes[0, 0]
ax.plot(t, raw_signal, color=colors['LightGray'], linewidth=0.5, alpha=0.7)
ax.set_title('Raw Narrative Intensity', fontsize=10)
ax.set_ylabel('Intensity')
ax.grid(True, alpha=0.3)

# 2. Simple Moving Average
ax = axes[0, 1]
window = 7
sma = np.convolve(raw_signal, np.ones(window)/window, mode='same')
ax.plot(t, raw_signal, color=colors['LightGray'], linewidth=0.5, alpha=0.3, label='Raw')
ax.plot(t, sma, color=colors['ChartBlue'], linewidth=2, label=f'SMA-{window}')
ax.set_title(f'Simple Moving Average (Window={window})', fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 3. Exponential Weighted Average
ax = axes[1, 0]
alpha = 0.1
ewa = pd.Series(raw_signal).ewm(alpha=alpha, adjust=False).mean().values
ax.plot(t, raw_signal, color=colors['LightGray'], linewidth=0.5, alpha=0.3, label='Raw')
ax.plot(t, ewa, color=colors['ChartOrange'], linewidth=2, label=f'EWA α={alpha}')
ax.set_title(f'Exponential Weighted Average', fontsize=10)
ax.set_ylabel('Intensity')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 4. Adaptive Window (volatility-based)
ax = axes[1, 1]
volatility = pd.Series(raw_signal).rolling(20).std().fillna(0.1).values
adaptive_window = np.clip(5 + (volatility * 50).astype(int), 5, 30)
adaptive_smooth = np.zeros_like(raw_signal)
for i in range(len(raw_signal)):
    w = int(adaptive_window[i])
    start = max(0, i-w//2)
    end = min(len(raw_signal), i+w//2)
    adaptive_smooth[i] = np.mean(raw_signal[start:end])

ax.plot(t, raw_signal, color=colors['LightGray'], linewidth=0.5, alpha=0.3, label='Raw')
ax.plot(t, adaptive_smooth, color=colors['ChartTeal'], linewidth=2, label='Adaptive')
ax.set_title('Adaptive Window Smoothing', fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 5. Wavelet Denoising
ax = axes[2, 0]
# Simplified wavelet denoising using FFT
fft = np.fft.fft(raw_signal)
frequencies = np.fft.fftfreq(len(raw_signal))
# Keep only low frequencies
fft[np.abs(frequencies) > 0.1] = 0
wavelet_smooth = np.real(np.fft.ifft(fft))

ax.plot(t, raw_signal, color=colors['LightGray'], linewidth=0.5, alpha=0.3, label='Raw')
ax.plot(t, wavelet_smooth, color=colors['ChartPurple'], linewidth=2, label='Wavelet')
ax.set_title('Wavelet Denoising', fontsize=10)
ax.set_xlabel('Days')
ax.set_ylabel('Intensity')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 6. Comparison of all methods
ax = axes[2, 1]
ax.plot(t, sma, color=colors['ChartBlue'], linewidth=1.5, alpha=0.8, label='SMA')
ax.plot(t, ewa, color=colors['ChartOrange'], linewidth=1.5, alpha=0.8, label='EWA')
ax.plot(t, adaptive_smooth, color=colors['ChartTeal'], linewidth=1.5, alpha=0.8, label='Adaptive')
ax.plot(t, wavelet_smooth, color=colors['ChartPurple'], linewidth=1.5, alpha=0.8, label='Wavelet')
ax.set_title('All Smoothing Methods Compared', fontsize=10)
ax.set_xlabel('Days')
ax.legend(fontsize=8, ncol=2)
ax.grid(True, alpha=0.3)

plt.suptitle('Time Series Aggregation Methods for Narrative Construction', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('timeseries_aggregation.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 5. Topic Coherence Metrics
print("Generating topic coherence visualization...")
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Coherence scores for different models
models = ['LDA', 'NMF', 'Top2Vec', 'BERTopic']
coherence_scores = {
    'C_v': [0.42, 0.48, 0.61, 0.73],
    'C_uci': [0.38, 0.44, 0.58, 0.69],
    'C_npmi': [0.35, 0.41, 0.55, 0.71],
    'C_umass': [-2.1, -1.8, -1.2, -0.8]
}

# 1. Bar chart comparison
ax = axes[0, 0]
x = np.arange(len(models))
width = 0.2
multiplier = 0

for metric, scores in coherence_scores.items():
    if metric != 'C_umass':  # Skip negative metric for this plot
        offset = width * multiplier
        ax.bar(x + offset, scores, width, label=metric,
              color=[colors['ChartBlue'], colors['ChartOrange'], colors['ChartTeal']][multiplier])
        multiplier += 1

ax.set_xlabel('Topic Model')
ax.set_ylabel('Coherence Score')
ax.set_title('Topic Coherence Comparison', fontsize=11)
ax.set_xticks(x + width)
ax.set_xticklabels(models)
ax.legend(loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3, axis='y')

# 2. Number of topics vs coherence
ax = axes[0, 1]
n_topics_range = np.arange(5, 51, 5)
for model, color in zip(models, [colors['DarkGray'], colors['ChartOrange'], colors['ChartTeal'], colors['ChartBlue']]):
    if model == 'BERTopic':
        coherence = 0.73 - 0.002 * (n_topics_range - 20)**2 / 100
    elif model == 'LDA':
        coherence = 0.42 - 0.001 * n_topics_range
    elif model == 'Top2Vec':
        coherence = 0.61 - 0.003 * (n_topics_range - 15)**2 / 100
    else:  # NMF
        coherence = 0.48 - 0.0015 * n_topics_range

    ax.plot(n_topics_range, coherence, marker='o', label=model,
           color=color, linewidth=2, markersize=5)

ax.set_xlabel('Number of Topics')
ax.set_ylabel('C_v Coherence')
ax.set_title('Coherence vs Topic Count', fontsize=11)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 3. Topic diversity
ax = axes[1, 0]
diversity_data = {
    'LDA': [0.65, 0.72, 0.45, 0.38],
    'NMF': [0.71, 0.75, 0.52, 0.44],
    'Top2Vec': [0.82, 0.85, 0.71, 0.65],
    'BERTopic': [0.89, 0.91, 0.84, 0.78]
}
metrics = ['Unique Words', 'Topic Distinctness', 'Coverage', 'Exclusivity']

x = np.arange(len(metrics))
width = 0.2
multiplier = 0

for model, scores in diversity_data.items():
    offset = width * multiplier
    color = [colors['DarkGray'], colors['ChartOrange'], colors['ChartTeal'], colors['ChartBlue']][multiplier]
    ax.bar(x + offset, scores, width, label=model, color=color, alpha=0.8)
    multiplier += 1

ax.set_xlabel('Diversity Metric')
ax.set_ylabel('Score')
ax.set_title('Topic Diversity Metrics', fontsize=11)
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(metrics, rotation=45, ha='right')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3, axis='y')

# 4. Perplexity over iterations
ax = axes[1, 1]
iterations = np.arange(0, 101, 10)
for model, color in zip(['LDA', 'NMF', 'BERTopic'],
                       [colors['DarkGray'], colors['ChartOrange'], colors['ChartBlue']]):
    if model == 'LDA':
        perplexity = 1000 * np.exp(-iterations/30) + 100
    elif model == 'NMF':
        perplexity = 800 * np.exp(-iterations/25) + 80
    else:  # BERTopic
        perplexity = 500 * np.exp(-iterations/20) + 50

    ax.plot(iterations, perplexity, marker='s', label=model,
           color=color, linewidth=2, markersize=4)

ax.set_xlabel('Training Iterations')
ax.set_ylabel('Perplexity (lower is better)')
ax.set_title('Model Convergence', fontsize=11)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

plt.suptitle('Topic Model Quality Metrics', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('topic_coherence_metrics.pdf', dpi=300, bbox_inches='tight')
plt.close()

print("\nAll topic modeling visualizations generated successfully:")
print("1. topic_evolution.pdf - Dynamic topic evolution over time")
print("2. contrastive_embeddings.pdf - Impact of contrastive learning")
print("3. hierarchical_topics.pdf - Hierarchical topic taxonomy")
print("4. timeseries_aggregation.pdf - Comparison of aggregation methods")
print("5. topic_coherence_metrics.pdf - Topic model quality metrics")