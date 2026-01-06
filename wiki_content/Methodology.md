# Methodology

This page details the methodological approaches employed in the Narrative Digital Finance project, spanning data collection, analysis techniques, and model development.

---

## Data Collection & Processing

### Financial Data Sources

| Data Type | Sources | Frequency |
|-----------|---------|-----------|
| Stock Prices | Bloomberg, Refinitiv, Yahoo Finance | Daily/Intraday |
| Macroeconomic Indicators | FRED, ECB, BIS | Monthly/Quarterly |
| High-Frequency Data | Deutsche Borse, Xetra | Tick-level |
| Cryptocurrency | CoinGecko, Binance | Real-time |

### Textual Data Sources

| Source | Type | Volume |
|--------|------|--------|
| Financial News | Reuters, Bloomberg, WSJ | Millions of articles |
| Social Media | Twitter/X, Reddit, StockTwits | Real-time feeds |
| Earnings Calls | Transcripts, Audio | Quarterly |
| Central Bank Communications | FOMC minutes, ECB statements | Policy meetings |
| Web Content | Financial blogs, Forums | Continuous |

### Alternative Data

- Satellite imagery (economic activity indicators)
- Web traffic data
- App usage statistics
- Credit card transaction aggregates

---

## Natural Language Processing (NLP)

### Text Preprocessing

1. **Tokenization**: Word and subword tokenization
2. **Normalization**: Lowercasing, stemming, lemmatization
3. **Cleaning**: Remove noise, special characters, HTML tags
4. **Entity Recognition**: Identify companies, people, locations

### Sentiment Analysis

| Method | Application | Tools |
|--------|-------------|-------|
| Lexicon-based | Financial sentiment dictionaries | Loughran-McDonald, VADER |
| Machine Learning | Supervised classification | SVM, Naive Bayes |
| Deep Learning | Contextual understanding | BERT, FinBERT, RoBERTa |
| Aspect-based | Topic-specific sentiment | Custom models |

### Topic Modeling & Narrative Extraction

- **LDA (Latent Dirichlet Allocation)**: Identify latent topics in document collections
- **BERTopic**: Neural topic modeling for better coherence
- **Narrative Structure Analysis**: Extract story arcs and causal chains
- **Named Entity Recognition**: Track entities across time

### Embedding & Representation

- Word2Vec / GloVe for word embeddings
- BERT / FinBERT for contextual embeddings
- Document embeddings for similarity analysis
- Time-aware embeddings for temporal analysis

---

## Machine Learning Methods

### Classical Machine Learning

| Algorithm | Application | Strengths |
|-----------|-------------|-----------|
| Elastic Net | Credit risk, Feature selection | Regularization, Interpretability |
| Random Forest | Classification, Feature importance | Robustness, Non-linearity |
| XGBoost | Prediction, Ranking | Performance, Speed |
| SVM | Classification | High-dimensional data |

### Deep Learning

| Architecture | Application | Use Case |
|--------------|-------------|----------|
| MLP (Multi-Layer Perceptron) | Tabular data prediction | Credit scoring |
| LSTM / GRU | Time series, Sequences | Price prediction |
| Transformer | NLP, Time series | Narrative analysis |
| CNN | Pattern recognition | Technical analysis |

### Ensemble Methods

- Stacking: Combine predictions from multiple models
- Bagging: Reduce variance (Random Forest)
- Boosting: Reduce bias (XGBoost, LightGBM)
- Voting: Democratic model combination

---

## Network Analysis

### Graph Construction

- **Nodes**: Borrowers, companies, investors
- **Edges**: Transactions, co-investment, similarity

### Centrality Metrics

| Metric | Meaning | Application |
|--------|---------|-------------|
| Degree Centrality | Number of connections | Borrower activity |
| Betweenness Centrality | Bridge position | Information flow |
| Closeness Centrality | Average distance | Market access |
| PageRank | Recursive importance | Influence measurement |

### Network Machine Learning

- Graph Neural Networks (GNN)
- Node2Vec for graph embeddings
- Community detection algorithms
- Temporal network analysis

---

## Econometric Methods

### Time Series Analysis

- ARIMA / GARCH for volatility modeling
- VAR (Vector Autoregression) for multivariate analysis
- Cointegration tests for long-run relationships
- State-space models for latent variable estimation

### Structural Break Detection

| Method | Description |
|--------|-------------|
| Chow Test | Known break point testing |
| CUSUM | Cumulative sum control chart |
| Bai-Perron | Multiple structural break detection |
| GSADF | Generalized sup ADF for bubble detection |

### Bubble Detection

- **LPPLS Model**: Log-Periodic Power Law Singularity
- **PSY Tests**: Phillips, Shi, Yu recursive tests
- **Real-time monitoring**: Rolling window detection

---

## Experimental Design

### Validation Approaches

1. **Train-Test Split**: Temporal split for time series
2. **Cross-Validation**: K-fold for robustness
3. **Walk-Forward Validation**: Rolling window prediction
4. **Out-of-Sample Testing**: Hold-out periods

### Robustness Checks

- Shuffled feature tests (network centrality validation)
- Alternative model specifications
- Sensitivity analysis
- Bootstrap confidence intervals

### Comparison Benchmarks

- Baseline models (random, naive)
- State-of-the-art alternatives
- Industry standard approaches

---

## Generative AI Applications

### Text Generation

- Synthetic data augmentation
- Scenario generation for stress testing
- Counterfactual narrative creation

### Multimodal Analysis

- Vision-language models for image+text
- Audio transcription and analysis
- Video content summarization

### LLM Applications

- Zero-shot classification
- Few-shot learning for financial tasks
- Prompt engineering for domain adaptation

---

## Software & Tools

### Programming Languages

| Language | Use Case |
|----------|----------|
| Python | Primary development, ML/NLP |
| R | Statistical analysis, Econometrics |
| SQL | Data management |

### Key Libraries

**Python**:
- `scikit-learn`: Classical ML
- `PyTorch` / `TensorFlow`: Deep learning
- `transformers`: NLP models (HuggingFace)
- `networkx`: Graph analysis
- `statsmodels`: Econometrics
- `pandas` / `numpy`: Data manipulation

**R**:
- `tseries`: Time series analysis
- `rugarch`: GARCH modeling
- `igraph`: Network analysis

### Infrastructure

- High-Performance Computing clusters
- GPU computing for deep learning
- Cloud resources (AWS, Google Cloud)

---

## Reproducibility

All research follows best practices for reproducibility:

- Version-controlled code (Git)
- Documented preprocessing pipelines
- Fixed random seeds
- Published datasets where possible
- Detailed methodology in publications

---

[Back to Home](Home) | [View Research Focus](Research-Focus) | [View Datasets](Datasets)
