# Datasets

The Narrative Digital Finance project has produced and utilized several novel datasets for research in financial markets and NLP.

---

## Project Datasets

### 1. Financial Narratives Corpus

**Type**: Textual data from multiple financial sources

| Attribute | Details |
|-----------|---------|
| Sources | Financial news, Social media, Earnings calls |
| Languages | English (primary) |
| Time Period | 2010-present |
| Format | Text + Metadata |

#### Data Sources

**Financial News**:
- Major wire services (Reuters, Bloomberg)
- Financial newspapers (WSJ, FT)
- Online financial media

**Social Media**:
- Twitter/X financial discussions
- Reddit (r/wallstreetbets, r/investing)
- StockTwits

**Corporate Communications**:
- Earnings call transcripts
- Press releases
- SEC filings (10-K, 10-Q, 8-K)

#### Annotations
- Sentiment labels (positive/negative/neutral)
- Topic tags
- Entity mentions (companies, people, products)
- Event types (earnings, M&A, policy)

#### Applications
- Sentiment analysis
- Narrative structure extraction
- Market impact prediction
- Bubble detection from narratives

---

### 2. High-Frequency Market Microstructure Dataset

**Collaboration with**: Deutsche Borse AG

| Attribute | Details |
|-----------|---------|
| Source | Deutsche Borse / Xetra |
| Frequency | Tick-level (milliseconds/microseconds) |
| Assets | European equities, ETFs |
| Time Period | Selected event windows |

#### Features

**Timestamp Data**:
- Order submission times
- Trade execution times
- Message latencies

**Order Book Data**:
- Bid/ask prices and quantities
- Order flow
- Depth of market

**Event Markers**:
- Macroeconomic announcements (PMI, NFP, FOMC)
- Corporate events
- Market stress periods

#### Applications
- HFT reaction time analysis
- Market microstructure research
- Information processing studies
- Latency analysis

#### Related Publications
- Osterrieder & Schlamp (2025) "Reaction Times to Economic News in High-Frequency Trading"

---

## External Datasets Used

### Financial Market Data

| Dataset | Provider | Use |
|---------|----------|-----|
| Stock prices | Bloomberg, Refinitiv | Price prediction, bubble detection |
| Macroeconomic indicators | FRED, ECB | Structural break analysis |
| Cryptocurrency data | CoinGecko | Digital asset analysis |
| NFT market data | OpenSea, Rarible | Metaverse research |

### Text & NLP Resources

| Resource | Description | Use |
|----------|-------------|-----|
| Loughran-McDonald Dictionary | Financial sentiment lexicon | Sentiment analysis |
| FinBERT | Pre-trained financial language model | NLP tasks |
| SEC-EDGAR | SEC filings database | Corporate text analysis |

---

## Data Access

### Availability

| Dataset | Access Level | Contact |
|---------|--------------|---------|
| Financial Narratives | Partial open access | Project team |
| HFT Microstructure | Restricted (collaboration) | Deutsche Borse |

### Data Sharing Policy

The project follows FAIR principles:
- **Findable**: Datasets documented with metadata
- **Accessible**: Clear access procedures
- **Interoperable**: Standard formats (CSV, JSON, Parquet)
- **Reusable**: Comprehensive documentation

### Ethical Considerations

- All data is anonymized where applicable
- Compliance with GDPR and data protection regulations
- No personally identifiable information (PII) in published datasets
- Proper attribution to data providers

---

## Dataset Statistics

| Dataset | Records | Features | Publications |
|---------|---------|----------|--------------|
| Financial Narratives | 1M+ documents | Text + metadata | 2 |
| HFT Microstructure | 100M+ ticks | Order book + timing | 2 |

---

## Future Data Collection

Ongoing and planned data collection efforts:

1. **Multimodal Financial Data**: Images, video, audio from financial sources
2. **Central Bank Communications**: Extended corpus of policy communications
3. **ESG Narratives**: Environmental, Social, Governance text data
4. **Cross-market Data**: Extended geographic coverage

---

[Back to Home](Home) | [View Methodology](Methodology) | [View Publications](Publications)
