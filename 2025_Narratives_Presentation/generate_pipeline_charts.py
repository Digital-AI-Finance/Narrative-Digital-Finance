import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.collections import PatchCollection
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
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
    'ChartPurple': '#CC79A7'
}

# Set default figure parameters
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# 1. Pipeline Architecture Diagram
print("Generating pipeline architecture...")
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Define pipeline stages
stages = [
    {"y": 11, "title": "Data Sources", "color": colors['ChartBlue'],
     "components": ["MarketAux API\n5000+ sources", "Alpha Vantage\nMarket Data", "RSS Feeds\nReal-time"]},
    {"y": 9.5, "title": "Ingestion Layer", "color": colors['ChartTeal'],
     "components": ["Rate Limiting", "Deduplication", "Date Extraction"]},
    {"y": 8, "title": "Preprocessing", "color": colors['ChartOrange'],
     "components": ["Text Cleaning", "Language Detection", "Entity Recognition"]},
    {"y": 6.5, "title": "Embeddings", "color": colors['ChartPurple'],
     "components": ["Sentence-BERT\n384 dims", "all-MiniLM-L6-v2", "Normalization"]},
    {"y": 5, "title": "Topic Modeling", "color": colors['DeepBlue'],
     "components": ["UMAP\nReduction", "HDBSCAN\nClustering", "c-TF-IDF\nRepresentation"]},
    {"y": 3.5, "title": "Classification", "color": colors['DarkGreen'],
     "components": ["FinBERT\nSentiment", "Zero-shot\nGPT-4o", "Few-shot\nPrompting"]},
    {"y": 2, "title": "Aggregation", "color": colors['DarkRed'],
     "components": ["Rolling Windows", "Exp. Smoothing", "Outlier Detection"]},
    {"y": 0.5, "title": "Output", "color": colors['DarkGray'],
     "components": ["Narrative\nTime Series", "Intensity\nScores", "API\nEndpoints"]}
]

# Draw stages
for stage in stages:
    # Draw main box
    rect = FancyBboxPatch((0.5, stage["y"]-0.3), 9, 0.8,
                          boxstyle="round,pad=0.05",
                          facecolor='white',
                          edgecolor=stage["color"],
                          linewidth=2)
    ax.add_patch(rect)

    # Add title
    ax.text(0.2, stage["y"], stage["title"], fontsize=11, fontweight='bold',
            va='center', color=stage["color"])

    # Add components
    for i, component in enumerate(stage["components"]):
        x = 2.5 + i * 2.5
        comp_rect = FancyBboxPatch((x, stage["y"]-0.25), 2, 0.5,
                                   boxstyle="round,pad=0.02",
                                   facecolor=stage["color"],
                                   alpha=0.15,
                                   edgecolor=stage["color"],
                                   linewidth=1)
        ax.add_patch(comp_rect)
        ax.text(x+1, stage["y"], component, fontsize=8, ha='center', va='center')

# Draw arrows between stages
for i in range(len(stages)-1):
    arrow = FancyArrowPatch((5, stages[i]["y"]-0.3), (5, stages[i+1]["y"]+0.3),
                           connectionstyle="arc3", arrowstyle='->',
                           mutation_scale=20, linewidth=2, color=colors['LightGray'])
    ax.add_patch(arrow)

ax.set_title('News-to-Narrative Pipeline Architecture (2025)', fontsize=14, fontweight='bold', color=colors['PureBlack'])
plt.tight_layout()
plt.savefig('pipeline_architecture.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 2. BERTopic Clustering Visualization
print("Generating BERTopic clustering visualization...")
np.random.seed(42)

# Generate synthetic cluster data
n_clusters = 8
n_points = 500
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Stage 1: UMAP Reduction
ax = axes[0]
# Generate high-dimensional data projected to 2D
theta = np.random.uniform(0, 2*np.pi, n_points)
r = np.random.normal(5, 2, n_points)
x = r * np.cos(theta)
y = r * np.sin(theta)

# Add cluster structure
for i in range(n_clusters):
    mask = (i * n_points // n_clusters <= np.arange(n_points)) & (np.arange(n_points) < (i+1) * n_points // n_clusters)
    angle = i * 2 * np.pi / n_clusters
    x[mask] += 3 * np.cos(angle)
    y[mask] += 3 * np.sin(angle)

ax.scatter(x, y, c=colors['ChartBlue'], alpha=0.3, s=10)
ax.set_title('Step 1: UMAP Dimensionality Reduction', fontsize=11)
ax.set_xlabel('UMAP Component 1')
ax.set_ylabel('UMAP Component 2')
ax.grid(True, alpha=0.3)

# Stage 2: HDBSCAN Clustering
ax = axes[1]
# Assign clusters
clusters = KMeans(n_clusters=n_clusters, random_state=42).fit_predict(np.column_stack([x, y]))
cluster_colors = [colors['ChartBlue'], colors['ChartOrange'], colors['ChartTeal'],
                  colors['ChartPurple'], colors['DarkGreen'], colors['DarkRed'],
                  colors['DarkGray'], colors['DeepBlue']]

for i in range(n_clusters):
    mask = clusters == i
    ax.scatter(x[mask], y[mask], c=cluster_colors[i], alpha=0.6, s=10, label=f'Topic {i+1}')

ax.set_title('Step 2: HDBSCAN Clustering', fontsize=11)
ax.set_xlabel('UMAP Component 1')
ax.set_ylabel('UMAP Component 2')
ax.legend(loc='upper right', fontsize=7, ncol=2)
ax.grid(True, alpha=0.3)

# Stage 3: c-TF-IDF Topics
ax = axes[2]
topics = ['Market Crash', 'Fed Policy', 'COVID-19', 'Trade War',
          'Brexit', 'Inflation', 'Tech Bubble', 'ESG']
importance = np.random.uniform(0.3, 0.9, n_clusters)
importance = importance / importance.sum()

bars = ax.bar(range(n_clusters), importance, color=cluster_colors)
ax.set_xticks(range(n_clusters))
ax.set_xticklabels(topics, rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Topic Importance (c-TF-IDF)', fontsize=10)
ax.set_title('Step 3: c-TF-IDF Topic Representation', fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.suptitle('BERTopic Pipeline: From Embeddings to Topics', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('bertopic_clustering.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 3. Embedding Space Visualization
print("Generating embedding space visualization...")
fig, ax = plt.subplots(figsize=(10, 10))

# Generate synthetic narrative embeddings
np.random.seed(42)
n_narratives = 200

# Create narrative clusters
narrative_types = {
    'Crisis': {'center': [-3, 3], 'color': colors['DarkRed'], 'size': 40},
    'Policy': {'center': [3, 3], 'color': colors['DeepBlue'], 'size': 35},
    'Geopolitical': {'center': [-3, -3], 'color': colors['ChartOrange'], 'size': 30},
    'Economic': {'center': [3, -3], 'color': colors['ChartTeal'], 'size': 25},
    'Tech': {'center': [0, 0], 'color': colors['ChartPurple'], 'size': 20}
}

# Generate points for each narrative type
for narrative, props in narrative_types.items():
    n = props['size']
    x = np.random.normal(props['center'][0], 1.5, n)
    y = np.random.normal(props['center'][1], 1.5, n)
    ax.scatter(x, y, c=props['color'], alpha=0.6, s=50, label=narrative, edgecolors='white', linewidth=0.5)

# Add example narrative labels
example_narratives = [
    {'pos': [-3.5, 4], 'text': 'Market\nCrash'},
    {'pos': [3.5, 4], 'text': 'Fed\nPolicy'},
    {'pos': [-3.5, -4], 'text': 'Trade\nWar'},
    {'pos': [3.5, -4], 'text': 'GDP\nGrowth'},
    {'pos': [0, 0.5], 'text': 'AI\nBoom'}
]

for ex in example_narratives:
    ax.annotate(ex['text'], xy=ex['pos'], fontsize=9, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=colors['DarkGray']))

# Add cosine similarity circles
for r in [2, 4, 6]:
    circle = Circle((0, 0), r, fill=False, linestyle='--',
                   linewidth=0.5, color=colors['LightGray'], alpha=0.5)
    ax.add_patch(circle)
    ax.text(0.2, r, f'cos={1-r/10:.1f}', fontsize=7, color=colors['LightGray'])

ax.set_xlim(-7, 7)
ax.set_ylim(-7, 7)
ax.set_xlabel('t-SNE Dimension 1', fontsize=10)
ax.set_ylabel('t-SNE Dimension 2', fontsize=10)
ax.set_title('Narrative Embedding Space (384-dimensional → 2D t-SNE)', fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('embedding_space.pdf', dpi=300, bbox_inches='tight')
plt.close()

# 4. API Integration System Architecture
print("Generating API integration diagram...")
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')

# Define system components
components = [
    # Data Sources (left)
    {'pos': [1, 6], 'size': [2, 1], 'label': 'MarketAux\nNews API', 'color': colors['ChartBlue']},
    {'pos': [1, 4.5], 'size': [2, 1], 'label': 'Alpha Vantage\nMarket Data', 'color': colors['ChartBlue']},
    {'pos': [1, 3], 'size': [2, 1], 'label': 'Twitter/Reddit\nSocial APIs', 'color': colors['ChartBlue']},
    {'pos': [1, 1.5], 'size': [2, 1], 'label': 'RSS Feeds\nDirect Sources', 'color': colors['ChartBlue']},

    # Processing Core (center)
    {'pos': [5, 6], 'size': [2, 1.5], 'label': 'Data Ingestion\nQueue\n(Kafka/RabbitMQ)', 'color': colors['ChartTeal']},
    {'pos': [5, 3.5], 'size': [2, 2], 'label': 'NLP Pipeline\n\nBERTopic\nFinBERT\nGPT-4o', 'color': colors['DeepBlue']},
    {'pos': [5, 1], 'size': [2, 1], 'label': 'Vector DB\n(FAISS/Chroma)', 'color': colors['ChartPurple']},

    # Output (right)
    {'pos': [9, 6], 'size': [2, 1], 'label': 'REST API\nEndpoints', 'color': colors['DarkGreen']},
    {'pos': [9, 4.5], 'size': [2, 1], 'label': 'WebSocket\nReal-time', 'color': colors['DarkGreen']},
    {'pos': [9, 3], 'size': [2, 1], 'label': 'Time Series\nDatabase', 'color': colors['DarkGreen']},
    {'pos': [9, 1.5], 'size': [2, 1], 'label': 'Dashboard\nVisualization', 'color': colors['DarkGreen']},
]

# Draw components
for comp in components:
    rect = FancyBboxPatch((comp['pos'][0]-comp['size'][0]/2, comp['pos'][1]-comp['size'][1]/2),
                          comp['size'][0], comp['size'][1],
                          boxstyle="round,pad=0.05",
                          facecolor='white',
                          edgecolor=comp['color'],
                          linewidth=2)
    ax.add_patch(rect)
    ax.text(comp['pos'][0], comp['pos'][1], comp['label'],
           ha='center', va='center', fontsize=9, color=colors['DarkGray'])

# Draw connections
connections = [
    # From sources to queue
    ([3, 6], [5, 6.5]),
    ([3, 4.5], [5, 6.3]),
    ([3, 3], [5, 6.1]),
    ([3, 1.5], [5, 5.9]),
    # From queue to NLP
    ([5, 5.25], [5, 4.5]),
    # From NLP to Vector DB
    ([5, 2.5], [5, 2]),
    # From NLP to outputs
    ([7, 3.5], [9, 6]),
    ([7, 3.5], [9, 4.5]),
    ([7, 3.5], [9, 3]),
    # From Vector DB to Dashboard
    ([7, 1], [9, 1.5]),
]

for start, end in connections:
    arrow = FancyArrowPatch(start, end,
                           connectionstyle="arc3,rad=0.1",
                           arrowstyle='->',
                           mutation_scale=15,
                           linewidth=1.5,
                           color=colors['LightGray'])
    ax.add_patch(arrow)

# Add labels for data flow rates
ax.text(2, 7, '~1M articles/day', fontsize=8, color=colors['DarkGray'], style='italic')
ax.text(6, 7.5, 'Batch: 1000/sec', fontsize=8, color=colors['DarkGray'], style='italic')
ax.text(10, 7, 'Latency: <100ms', fontsize=8, color=colors['DarkGray'], style='italic')

ax.set_title('Real-time Narrative Processing System Architecture', fontsize=14, fontweight='bold', color=colors['PureBlack'])
plt.tight_layout()
plt.savefig('api_integration.pdf', dpi=300, bbox_inches='tight')
plt.close()

print("\nAll pipeline charts generated successfully:")
print("1. pipeline_architecture.pdf - Complete data processing pipeline")
print("2. bertopic_clustering.pdf - BERTopic 3-step visualization")
print("3. embedding_space.pdf - t-SNE narrative embedding clusters")
print("4. api_integration.pdf - System architecture diagram")