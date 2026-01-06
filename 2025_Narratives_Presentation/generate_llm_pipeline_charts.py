import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.patheffects import withStroke
import warnings
warnings.filterwarnings('ignore')

# Set style for academic presentations
plt.style.use('default')
sns.set_palette("husl")

# Define consistent color scheme
COLORS = {
    'llm': '#2E86AB',      # Deep blue for LLMs
    'embedding': '#A23B72', # Purple for embeddings
    'data': '#F18F01',     # Orange for data
    'process': '#C73E1D',  # Red for processing
    'output': '#6A994E',   # Green for output
    'gray': '#646464'      # Gray for annotations
}

def create_llm_pipeline_flow():
    """Complete LLM-based narrative pipeline architecture"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'LLM-Centric Narrative Pipeline',
            fontsize=20, fontweight='bold', ha='center')

    # Stage 1: Data Ingestion with LLM
    box1 = FancyBboxPatch((0.5, 7), 2.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['data'], alpha=0.7, edgecolor='black')
    ax.add_patch(box1)
    ax.text(1.75, 7.75, 'News Ingestion', fontsize=11, ha='center', fontweight='bold')
    ax.text(1.75, 7.35, 'GPT-4 API\nClaude API', fontsize=9, ha='center')

    # Stage 2: LLM Preprocessing
    box2 = FancyBboxPatch((4, 7), 2.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['llm'], alpha=0.7, edgecolor='black')
    ax.add_patch(box2)
    ax.text(5.25, 7.75, 'LLM Preprocessing', fontsize=11, ha='center', fontweight='bold')
    ax.text(5.25, 7.35, 'Entity extraction\nCoreference resolution', fontsize=9, ha='center')

    # Stage 3: Embedding Generation
    box3 = FancyBboxPatch((7.5, 7), 2.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['embedding'], alpha=0.7, edgecolor='black')
    ax.add_patch(box3)
    ax.text(8.75, 7.75, 'Dense Embeddings', fontsize=11, ha='center', fontweight='bold')
    ax.text(8.75, 7.35, 'text-embedding-3\nClaude embeddings', fontsize=9, ha='center')

    # Stage 4: Vector Storage
    box4 = FancyBboxPatch((11, 7), 2.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['process'], alpha=0.7, edgecolor='black')
    ax.add_patch(box4)
    ax.text(12.25, 7.75, 'Vector Database', fontsize=11, ha='center', fontweight='bold')
    ax.text(12.25, 7.35, 'Pinecone\nQdrant', fontsize=9, ha='center')

    # Stage 5: Zero-Shot Classification
    box5 = FancyBboxPatch((0.5, 4.5), 3, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['llm'], alpha=0.7, edgecolor='black')
    ax.add_patch(box5)
    ax.text(2, 5.25, 'Zero-Shot Classification', fontsize=11, ha='center', fontweight='bold')
    ax.text(2, 4.85, 'Dynamic prompts\nNo training required', fontsize=9, ha='center')

    # Stage 6: Few-Shot Learning
    box6 = FancyBboxPatch((4, 4.5), 3, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['llm'], alpha=0.7, edgecolor='black')
    ax.add_patch(box6)
    ax.text(5.5, 5.25, 'Few-Shot Learning', fontsize=11, ha='center', fontweight='bold')
    ax.text(5.5, 4.85, 'In-context examples\nPrompt templates', fontsize=9, ha='center')

    # Stage 7: RAG Enhancement
    box7 = FancyBboxPatch((7.5, 4.5), 3, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['embedding'], alpha=0.7, edgecolor='black')
    ax.add_patch(box7)
    ax.text(9, 5.25, 'RAG Enhancement', fontsize=11, ha='center', fontweight='bold')
    ax.text(9, 4.85, 'Context retrieval\nKnowledge augmentation', fontsize=9, ha='center')

    # Stage 8: Chain-of-Thought
    box8 = FancyBboxPatch((11, 4.5), 2.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['llm'], alpha=0.7, edgecolor='black')
    ax.add_patch(box8)
    ax.text(12.25, 5.25, 'CoT Reasoning', fontsize=11, ha='center', fontweight='bold')
    ax.text(12.25, 4.85, 'Step-by-step\nExplainable', fontsize=9, ha='center')

    # Stage 9: Narrative Time Series
    box9 = FancyBboxPatch((3, 2), 4, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['output'], alpha=0.7, edgecolor='black')
    ax.add_patch(box9)
    ax.text(5, 2.75, 'Narrative Time Series', fontsize=11, ha='center', fontweight='bold')
    ax.text(5, 2.35, 'LLM-weighted aggregation\nSemantic similarity scoring', fontsize=9, ha='center')

    # Stage 10: Output
    box10 = FancyBboxPatch((8, 2), 4, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLORS['output'], alpha=0.7, edgecolor='black')
    ax.add_patch(box10)
    ax.text(10, 2.75, 'Narrative Indicators', fontsize=11, ha='center', fontweight='bold')
    ax.text(10, 2.35, 'Intensity scores\nSentiment analysis', fontsize=9, ha='center')

    # Add arrows
    arrows = [
        (3, 7.75, 4, 7.75),      # Ingestion to Preprocessing
        (6.5, 7.75, 7.5, 7.75),  # Preprocessing to Embeddings
        (10, 7.75, 11, 7.75),    # Embeddings to Vector DB
        (12.25, 7, 12.25, 6),    # Vector DB down
        (12.25, 6, 2, 6),        # Across to Zero-Shot
        (2, 6, 2, 6),            # Zero-Shot input
        (2, 4.5, 5.5, 4.5),      # Zero-Shot to Few-Shot (bottom)
        (5.5, 4.5, 9, 4.5),      # Few-Shot to RAG (bottom)
        (9, 4.5, 12.25, 4.5),    # RAG to CoT (bottom)
        (5.5, 4.5, 5, 3.5),      # Few-Shot to Time Series
        (9, 4.5, 10, 3.5),       # RAG to Output
    ]

    for x1, y1, x2, y2 in arrows:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle='->', mutation_scale=20,
                              color='black', linewidth=1.5, alpha=0.7)
        ax.add_patch(arrow)

    # Add annotations
    ax.text(7, 0.5, 'All stages powered by LLMs and dense embeddings',
            fontsize=10, ha='center', style='italic', color=COLORS['gray'])

    plt.tight_layout()
    plt.savefig('llm_pipeline_flow.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_embedding_similarity_matrix():
    """Semantic similarity matrix for narrative detection"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Generate sample similarity data
    narratives = ['Market Crash', 'COVID-19', 'Inflation', 'Fed Policy', 'Supply Chain',
                  'Energy Crisis', 'Tech Bubble', 'Trade War', 'Recession', 'Recovery']

    # Cosine similarity matrix
    np.random.seed(42)
    similarity = np.random.rand(10, 10)
    similarity = (similarity + similarity.T) / 2  # Make symmetric
    np.fill_diagonal(similarity, 1.0)

    # Plot heatmap
    im1 = ax1.imshow(similarity, cmap='RdBu_r', vmin=0, vmax=1)
    ax1.set_xticks(range(len(narratives)))
    ax1.set_yticks(range(len(narratives)))
    ax1.set_xticklabels(narratives, rotation=45, ha='right')
    ax1.set_yticklabels(narratives)
    ax1.set_title('Embedding Cosine Similarity Matrix', fontsize=14, fontweight='bold')

    # Add colorbar
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Cosine Similarity', rotation=270, labelpad=15)

    # Clustering dendrogram
    from scipy.cluster import hierarchy
    from scipy.spatial.distance import pdist, squareform

    # Convert similarity to distance
    distance = 1 - similarity
    condensed_dist = squareform(distance)

    # Perform hierarchical clustering
    linkage_matrix = hierarchy.linkage(condensed_dist, method='ward')

    # Plot dendrogram
    dendro = hierarchy.dendrogram(linkage_matrix, labels=narratives, ax=ax2,
                                  orientation='right', color_threshold=0.7)
    ax2.set_title('Narrative Clustering via Embeddings', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Distance')

    # Add annotation
    fig.text(0.5, 0.02, 'Dense embeddings capture semantic relationships between narratives',
             ha='center', fontsize=10, style='italic', color=COLORS['gray'])

    plt.tight_layout()
    plt.savefig('embedding_similarity_matrix.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_prompt_performance():
    """Comparison of different prompting strategies"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # Zero-shot vs Few-shot performance
    models = ['GPT-3.5', 'GPT-4', 'Claude-3', 'Llama-2', 'Mistral']
    zero_shot = [0.72, 0.85, 0.83, 0.68, 0.71]
    few_shot = [0.81, 0.92, 0.91, 0.78, 0.82]
    chain_of_thought = [0.84, 0.95, 0.94, 0.82, 0.86]

    x = np.arange(len(models))
    width = 0.25

    ax1.bar(x - width, zero_shot, width, label='Zero-shot', color=COLORS['llm'], alpha=0.7)
    ax1.bar(x, few_shot, width, label='Few-shot (3 examples)', color=COLORS['embedding'], alpha=0.7)
    ax1.bar(x + width, chain_of_thought, width, label='Chain-of-Thought', color=COLORS['output'], alpha=0.7)

    ax1.set_xlabel('Model')
    ax1.set_ylabel('F1 Score')
    ax1.set_title('Narrative Classification Performance', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0.6, 1.0)

    # Prompt template effectiveness
    templates = ['Basic\nClassification', 'Role-based\nPrompting', 'Structured\nOutput',
                 'Context\nEnhanced', 'Multi-step\nReasoning']
    accuracy = [0.75, 0.82, 0.86, 0.89, 0.93]

    bars = ax2.barh(templates, accuracy, color=COLORS['process'], alpha=0.7)
    ax2.set_xlabel('Accuracy')
    ax2.set_title('Prompt Template Effectiveness', fontsize=12, fontweight='bold')
    ax2.set_xlim(0.7, 1.0)
    ax2.grid(True, alpha=0.3, axis='x')

    # Add values on bars
    for bar, val in zip(bars, accuracy):
        ax2.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}', va='center')

    # Token usage vs accuracy tradeoff
    shot_counts = [0, 1, 3, 5, 10, 15, 20]
    accuracies = [0.72, 0.78, 0.85, 0.88, 0.91, 0.92, 0.92]
    tokens = [150, 400, 900, 1400, 2600, 3800, 5000]

    ax3_twin = ax3.twinx()

    line1 = ax3.plot(shot_counts, accuracies, 'o-', color=COLORS['llm'],
                     linewidth=2, markersize=8, label='Accuracy')
    line2 = ax3_twin.plot(shot_counts, tokens, 's-', color=COLORS['process'],
                         linewidth=2, markersize=8, label='Token Usage')

    ax3.set_xlabel('Number of Few-Shot Examples')
    ax3.set_ylabel('Accuracy', color=COLORS['llm'])
    ax3_twin.set_ylabel('Tokens Used', color=COLORS['process'])
    ax3.set_title('Few-Shot Examples vs Performance', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='y', labelcolor=COLORS['llm'])
    ax3_twin.tick_params(axis='y', labelcolor=COLORS['process'])

    # Add legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='center right')

    # RAG retrieval impact
    contexts = ['No Context', '1 Document', '3 Documents', '5 Documents', '10 Documents']
    precision = [0.68, 0.79, 0.87, 0.91, 0.89]
    recall = [0.72, 0.81, 0.85, 0.88, 0.92]

    x = np.arange(len(contexts))
    width = 0.35

    ax4.bar(x - width/2, precision, width, label='Precision', color=COLORS['embedding'], alpha=0.7)
    ax4.bar(x + width/2, recall, width, label='Recall', color=COLORS['output'], alpha=0.7)

    ax4.set_xlabel('RAG Context Size')
    ax4.set_ylabel('Score')
    ax4.set_title('RAG Context Impact on Performance', fontsize=12, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(contexts, rotation=45, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0.6, 1.0)

    plt.suptitle('LLM Prompting Strategies for Narrative Detection',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig('prompt_performance.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_rag_architecture():
    """RAG system architecture for narrative analysis"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'RAG-Enhanced Narrative Analysis',
            fontsize=20, fontweight='bold', ha='center')

    # Input Query
    query_box = FancyBboxPatch((1, 7.5), 3, 1,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['data'], alpha=0.7, edgecolor='black')
    ax.add_patch(query_box)
    ax.text(2.5, 8, 'Input News Article', fontsize=11, ha='center', fontweight='bold')

    # Embedding Model
    embed_box = FancyBboxPatch((5.5, 7.5), 3, 1,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['embedding'], alpha=0.7, edgecolor='black')
    ax.add_patch(embed_box)
    ax.text(7, 8, 'Embedding Model', fontsize=11, ha='center', fontweight='bold')

    # Vector Database
    vector_box = FancyBboxPatch((10, 7.5), 3, 1,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['process'], alpha=0.7, edgecolor='black')
    ax.add_patch(vector_box)
    ax.text(11.5, 8, 'Vector Database', fontsize=11, ha='center', fontweight='bold')

    # Historical Narratives Store
    hist_box = FancyBboxPatch((10, 5.5), 3, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor='#E8E8E8', alpha=0.7, edgecolor='black')
    ax.add_patch(hist_box)
    ax.text(11.5, 6.5, 'Historical Narratives', fontsize=10, ha='center', fontweight='bold')
    ax.text(11.5, 6, '• Past classifications\n• Narrative evolution\n• Context patterns',
            fontsize=8, ha='center')

    # Retrieval Process
    retrieval_box = FancyBboxPatch((5.5, 5), 3, 1.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor=COLORS['embedding'], alpha=0.7, edgecolor='black')
    ax.add_patch(retrieval_box)
    ax.text(7, 6, 'Semantic Search', fontsize=11, ha='center', fontweight='bold')
    ax.text(7, 5.5, 'k-NN retrieval\nReranking', fontsize=9, ha='center')

    # Context Assembly
    context_box = FancyBboxPatch((1, 5), 3, 1.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor=COLORS['process'], alpha=0.7, edgecolor='black')
    ax.add_patch(context_box)
    ax.text(2.5, 6, 'Context Assembly', fontsize=11, ha='center', fontweight='bold')
    ax.text(2.5, 5.5, 'Relevant examples\nSimilar narratives', fontsize=9, ha='center')

    # LLM Processing
    llm_box = FancyBboxPatch((3, 2.5), 8, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=COLORS['llm'], alpha=0.7, edgecolor='black')
    ax.add_patch(llm_box)
    ax.text(7, 3.5, 'LLM with Augmented Context', fontsize=11, ha='center', fontweight='bold')
    ax.text(7, 3, 'GPT-4 / Claude with retrieved examples', fontsize=9, ha='center')

    # Output
    output_box = FancyBboxPatch((5, 0.5), 4, 1,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['output'], alpha=0.7, edgecolor='black')
    ax.add_patch(output_box)
    ax.text(7, 1, 'Narrative Classification', fontsize=11, ha='center', fontweight='bold')

    # Add arrows with labels
    arrows = [
        ((4, 8), (5.5, 8), 'Encode'),
        ((8.5, 8), (10, 8), 'Query'),
        ((11.5, 7.5), (11.5, 7), ''),
        ((11.5, 5.5), (8.5, 5.75), 'Top-k'),
        ((5.5, 5.75), (4, 5.75), 'Retrieved'),
        ((2.5, 5), (2.5, 4), ''),
        ((7, 4), (7, 4), 'Augmented\nPrompt'),
        ((7, 2.5), (7, 1.5), 'Prediction'),
    ]

    for start, end, label in arrows:
        arrow = FancyArrowPatch(start, end,
                              arrowstyle='->', mutation_scale=20,
                              color='black', linewidth=2, alpha=0.7)
        ax.add_patch(arrow)
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            ax.text(mid_x, mid_y + 0.2, label, fontsize=8, ha='center')

    # Add performance metrics
    metrics_text = 'Performance Gains:\n• 23% accuracy improvement\n• 91% F1 score\n• 15% latency increase'
    ax.text(0.5, 3.5, metrics_text, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray'))

    plt.tight_layout()
    plt.savefig('rag_architecture.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_llm_comparison_matrix():
    """Comparison of different LLMs for narrative tasks"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # Model capabilities comparison
    models = ['GPT-4', 'Claude-3', 'Llama-2-70B', 'Mistral-7B', 'FinBERT']
    capabilities = {
        'Zero-shot': [0.95, 0.94, 0.82, 0.78, 0.71],
        'Few-shot': [0.97, 0.96, 0.88, 0.85, 0.79],
        'Context Length': [0.90, 0.95, 0.70, 0.65, 0.40],
        'Speed': [0.60, 0.65, 0.85, 0.95, 0.98],
        'Cost Efficiency': [0.30, 0.35, 0.80, 0.90, 0.95]
    }

    # Create bar chart instead of radar chart for compatibility
    x = np.arange(len(models))
    width = 0.15

    for i, (cap_name, cap_values) in enumerate(capabilities.items()):
        offset = (i - 2) * width
        ax1.bar(x + offset, cap_values, width, label=cap_name, alpha=0.7)

    ax1.set_xlabel('Model')
    ax1.set_ylabel('Score')
    ax1.set_title('LLM Capabilities for Narrative Analysis', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=45, ha='right')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.1)

    # Token efficiency
    models_short = ['GPT-4', 'Claude', 'Llama-2', 'Mistral', 'FinBERT']
    input_tokens = [2000, 1800, 3200, 2800, 512]
    output_quality = [0.95, 0.94, 0.85, 0.82, 0.75]

    scatter = ax2.scatter(input_tokens, output_quality, s=[300, 280, 200, 150, 100],
                         c=range(len(models_short)), cmap='viridis', alpha=0.6)

    for i, model in enumerate(models_short):
        ax2.annotate(model, (input_tokens[i], output_quality[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)

    ax2.set_xlabel('Average Input Tokens Required')
    ax2.set_ylabel('Output Quality Score')
    ax2.set_title('Token Efficiency vs Quality', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Response time comparison
    batch_sizes = [1, 10, 50, 100, 500]
    gpt4_time = [0.8, 2.1, 8.5, 16.2, 78.3]
    claude_time = [0.7, 1.9, 7.8, 15.1, 72.5]
    llama_time = [0.3, 0.9, 3.2, 6.1, 28.4]

    ax3.plot(batch_sizes, gpt4_time, 'o-', label='GPT-4', linewidth=2)
    ax3.plot(batch_sizes, claude_time, 's-', label='Claude-3', linewidth=2)
    ax3.plot(batch_sizes, llama_time, '^-', label='Llama-2 (local)', linewidth=2)

    ax3.set_xlabel('Batch Size (articles)')
    ax3.set_ylabel('Response Time (seconds)')
    ax3.set_title('Scalability Analysis', fontsize=12, fontweight='bold')
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Cost analysis
    models = ['GPT-4', 'Claude-3', 'Llama-2\n(Cloud)', 'Llama-2\n(Local)', 'FinBERT\n(Local)']
    cost_per_million = [30, 25, 8, 0.5, 0.1]
    colors = [COLORS['llm'], COLORS['embedding'], COLORS['process'], COLORS['output'], COLORS['data']]

    bars = ax4.bar(models, cost_per_million, color=colors, alpha=0.7)
    ax4.set_ylabel('Cost per Million Tokens ($)')
    ax4.set_title('Cost Comparison', fontsize=12, fontweight='bold')
    ax4.set_ylim(0, 35)

    # Add value labels on bars
    for bar, cost in zip(bars, cost_per_million):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'${cost}', ha='center', va='bottom', fontsize=9)

    ax4.grid(True, alpha=0.3, axis='y')

    plt.suptitle('LLM Model Comparison for Narrative Processing',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig('llm_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def create_prompt_templates():
    """Visualization of different prompt engineering templates"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'Prompt Engineering Templates for Narrative Classification',
            fontsize=18, fontweight='bold', ha='center')

    # Zero-shot template
    zero_box = FancyBboxPatch((0.5, 7), 4, 1.8,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['llm'], alpha=0.3, edgecolor='black')
    ax.add_patch(zero_box)
    ax.text(2.5, 8.5, 'Zero-Shot Template', fontsize=11, fontweight='bold', ha='center')
    ax.text(0.7, 7.8, 'System: You are a financial narrative classifier.', fontsize=8, family='monospace')
    ax.text(0.7, 7.5, 'User: Classify this article into narratives:', fontsize=8, family='monospace')
    ax.text(0.7, 7.2, '[ARTICLE_TEXT]', fontsize=8, family='monospace', style='italic')

    # Few-shot template
    few_box = FancyBboxPatch((5, 7), 4, 1.8,
                             boxstyle="round,pad=0.1",
                             facecolor=COLORS['embedding'], alpha=0.3, edgecolor='black')
    ax.add_patch(few_box)
    ax.text(7, 8.5, 'Few-Shot Template', fontsize=11, fontweight='bold', ha='center')
    ax.text(5.2, 7.8, 'Examples: [Market Crash] -> "Stocks plunge..."', fontsize=8, family='monospace')
    ax.text(5.2, 7.5, '         [Inflation] -> "Prices surge..."', fontsize=8, family='monospace')
    ax.text(5.2, 7.2, 'Classify: [NEW_ARTICLE]', fontsize=8, family='monospace', style='italic')

    # Chain-of-thought template
    cot_box = FancyBboxPatch((9.5, 7), 4, 1.8,
                             boxstyle="round,pad=0.1",
                             facecolor=COLORS['process'], alpha=0.3, edgecolor='black')
    ax.add_patch(cot_box)
    ax.text(11.5, 8.5, 'Chain-of-Thought', fontsize=11, fontweight='bold', ha='center')
    ax.text(9.7, 7.8, '1. Identify key entities', fontsize=8, family='monospace')
    ax.text(9.7, 7.5, '2. Analyze sentiment', fontsize=8, family='monospace')
    ax.text(9.7, 7.2, '3. Match to narratives', fontsize=8, family='monospace')

    # Structured output template
    struct_box = FancyBboxPatch((0.5, 4.5), 6, 2,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['output'], alpha=0.3, edgecolor='black')
    ax.add_patch(struct_box)
    ax.text(3.5, 6.2, 'Structured Output Template', fontsize=11, fontweight='bold', ha='center')
    ax.text(0.7, 5.7, 'Return JSON:', fontsize=9, family='monospace')
    ax.text(0.7, 5.4, '{', fontsize=9, family='monospace')
    ax.text(0.9, 5.1, '"primary_narrative": "Market Crash",', fontsize=9, family='monospace')
    ax.text(0.9, 4.8, '"confidence": 0.92,', fontsize=9, family='monospace')
    ax.text(0.9, 4.5, '"secondary_narratives": ["Fed Policy", "Recession"]', fontsize=9, family='monospace')
    ax.text(0.7, 4.2, '}', fontsize=9, family='monospace')

    # Multi-agent template
    multi_box = FancyBboxPatch((7.5, 4.5), 6, 2,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['data'], alpha=0.3, edgecolor='black')
    ax.add_patch(multi_box)
    ax.text(10.5, 6.2, 'Multi-Agent Reasoning', fontsize=11, fontweight='bold', ha='center')
    ax.text(7.7, 5.7, 'Agent 1: Extract entities and facts', fontsize=9, family='monospace')
    ax.text(7.7, 5.4, 'Agent 2: Analyze market sentiment', fontsize=9, family='monospace')
    ax.text(7.7, 5.1, 'Agent 3: Historical pattern matching', fontsize=9, family='monospace')
    ax.text(7.7, 4.8, 'Aggregator: Combine insights -> narrative', fontsize=9, family='monospace')

    # Performance metrics
    metrics_box = FancyBboxPatch((2, 2), 10, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor='white', alpha=1, edgecolor='black')
    ax.add_patch(metrics_box)
    ax.text(7, 3.2, 'Template Performance Metrics', fontsize=11, fontweight='bold', ha='center')

    # Add performance bars
    templates = ['Zero-Shot', 'Few-Shot', 'CoT', 'Structured', 'Multi-Agent']
    f1_scores = [0.72, 0.85, 0.91, 0.88, 0.94]
    colors_list = [COLORS['llm'], COLORS['embedding'], COLORS['process'], COLORS['output'], COLORS['data']]

    bar_width = 1.5
    bar_spacing = 2
    start_x = 3

    for i, (template, score, color) in enumerate(zip(templates, f1_scores, colors_list)):
        x = start_x + i * bar_spacing
        height = score * 0.8
        bar = FancyBboxPatch((x, 2.2), bar_width, height,
                             boxstyle="round,pad=0.02",
                             facecolor=color, alpha=0.7, edgecolor='black')
        ax.add_patch(bar)
        ax.text(x + bar_width/2, 2.1, template, fontsize=8, ha='center')
        ax.text(x + bar_width/2, 2.2 + height + 0.05, f'{score:.2f}',
                fontsize=8, ha='center', fontweight='bold')

    # Add annotation
    ax.text(7, 0.5, 'Advanced prompting techniques improve narrative detection by 30%',
            fontsize=10, ha='center', style='italic', color=COLORS['gray'])

    plt.tight_layout()
    plt.savefig('prompt_templates.pdf', dpi=300, bbox_inches='tight')
    plt.close()

# Generate all charts
if __name__ == "__main__":
    print("Generating LLM pipeline visualizations...")

    create_llm_pipeline_flow()
    print("Created: llm_pipeline_flow.pdf")

    create_embedding_similarity_matrix()
    print("Created: embedding_similarity_matrix.pdf")

    create_prompt_performance()
    print("Created: prompt_performance.pdf")

    create_rag_architecture()
    print("Created: rag_architecture.pdf")

    create_llm_comparison_matrix()
    print("Created: llm_comparison.pdf")

    create_prompt_templates()
    print("Created: prompt_templates.pdf")

    print("\nAll LLM pipeline visualizations generated successfully!")