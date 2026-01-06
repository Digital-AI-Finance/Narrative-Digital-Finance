# Document Summaries

Generated from `output/` folder.

**Total documents:** 8

---

## NLP-Pricing_preprint.pdf

| Property | Value |
|----------|-------|
| File | `NLP-Pricing_preprint.pdf` |
| Pages | 4 |
| Author |  |
| Keywords | financial(45), data(38), text(34), analysis(32), nlp(17), market(17), multimodal(13), models(13) |

**Table of Contents:**
  - Introduction
  - Optimal utilization of NLP methods in finance
  - Integrating diverse methodologies in NLP for advanced financial data analysis
  - Using real-time data for analysis
  - Categorizing the input from different sources
  - Advancing Financial Analysis with Multimodal Theory and Automated Multi-Modal Text Analysis
  - Most effective techniques of NLP and text analysis methods

**Introduction (first 500 words):**

> Hypothesizing Multimodal Influence: Assessing the Impact of Textual and Non-Textual Data on Financial Instrument Pricing Using NLP and Generative AI Karolina Bolesta Warsaw School of Economics Warsaw, Poland kboles@sgh.waw.pl Gabin Taibi Bern University of Applied Sciences Bern, Switzerland gabin.taibi@bfh.ch Codruta Mare Babes-Bolyai University Cluj Napoca, Romania codruta.mare@econ.ubbcluj.ro Branka Hadji Misheva Bern University of Applied Sciences Bern, Switzerland branka.hadjimisheva@bfh.ch Christian Hopp Bern University of Applied Sciences Bern, Switzerland christian.hopp@bfh.ch Joerg Osterrieder Bern University of Applied Sciences Bern, Switzerland joerg.osterrieder@bfh.ch Abstract This paper presents an advanced conceptual framework for the analysis of textual data in the context of financial securities, hypothesizing that a comprehensive evaluation of events within the broader economic en- vironment, particularly through their descriptions, significantly influences the pricing of financial instruments. This research extends beyond the traditional scope of Natural Language Processing by proposing the inclu- sion of non-textual data forms such as images, videos, and audio in the analysis. Further, it acknowledges the recent developments in Generative Artificial Intelligence, suggesting its application to expand the breadth of textual analysis through the generation of varied textual datasets. The hypothesis posits that the systematic analysis of these diverse multimodal textual inputs, surpassing the conventional verbal text, could enhance the decision-making process in financial asset management. This study aims to elucidate the potential effects of this methodological advancement on financial market fluctuations and outlines the most pertinent NLP methodologies for the empirical investigation of the hypothesis in future scholarly work. Keywords: Financial Markets, Natural Language Processing (NLP), Generative Artificial Intelligence, Multimodal Data Analysis, Economic Context Analysis, Textual Data in Finance, Non-Textual Data Integration, Sentiment Analysis, Market Dynamics, Automated Decision-Making JEL Classification: G00, G10, G20 1 Electronic copy available at: https://ssrn.com/abstract=4698153 Multimodal Text Analysis 1 Introduction The exponential increase in data volume in the digital era represents a significant paradigm shift, particularly in the do- main of financial market analysis. The advent of the Internet and social media platforms has catalyzed an unprecedented growth in global data volumes. From a relatively modest scale of a few dozen exabytes in 2003 Cambria and White (2014), the year marking the emergence of social media, this figure is projected to soar to approximately 180 zettabytes by 2025 Statista (2023). This rapid expansion of data presents both formidable challenges and unique opportunities for contem- porary financial analysis methodologies. Within this context, Natural Language Processing (NLP), a core facet of Artificial Intelligence, has emerged as an instru- mental technology in understanding the vast and complex datasets prevalent in today’s digital landscape. Recognized for its efficacy in processing extensive textual information, NLP’s applications have gained considerable traction across multiple sectors, notably within the financial industry. How- ever, the hypothesis posed in this paper extends the analyti- cal reach beyond the consideration of traditional text-centric data. It argues for an integrative framework that combines the analysis of textual data with non-textual elements such as images, videos, and audio. This multimodal approach is essential to have a more holistic and nuanced understanding of financial market dynamics. Furthermore, the advent and...

---


## Poster_Macro_narratives.pdf

| Property | Value |
|----------|-------|
| File | `Poster_Macro_narratives.pdf` |
| Pages | 1 |
| Author |  |
| Keywords | macroeconomic(11), economic(9), index(9), narrative(7), analysis(7), null(7), central(6), drift(6) |

**Table of Contents:**
  - References

**Introduction (first 500 words):**

> Strategic Narratives during Economic Turning Points: An AI Framework for Monitoring U.S. Central Bank Communications Gabin Taibi, Bern University of Applied Sciences, University of Twente Background Examining how the Federal Reserve System communicates during times of macroeconomic change is key to understanding policy strategy. While prior work has studied macro indicators [3, 2] or central bank speeches [1, 4] in isolation for this purpose, little is known about the key strategic communication patterns occurring in times of structural economic changes. This project bridges quantitative macroeconomic trends and qualitative commu- nication patterns to uncover patterns in U.S. central bankers narratives during changing economic conditions. Research Objectives ▶Construct a transparent and data-driven composite index that condenses multifaceted U.S. macroeconomic indicators. ▶Detect structural breaks in the macroeconomic environment through unsupervised change point detection. ▶Quantify how the thematic focus, sentiment orientation, and rhetorical structure of Federal Reserve communication evolves around these macroeconomic transitions. ▶Demonstrate that combining macroeconomic signal detection with narrative analysis offers a practical tool for interpreting monetary policy shifts, with direct applications in market monitoring and economic storytelling. Methodology Macroeconomic Index Construction A static Principal Component Analysis (PCA) [5] is applied to six standard- ized (12-month rolling window Z-score) monthly U.S. macroeconomic indicators (FED Funds Rate, CPI, PPI, GDP, Unemployment, Nonfarm Payrolls from St. Louis FED FRED datasets) from 1996 to 2025. The first principal component (explaining the largest share of variance, see fig. 1) is interpreted as the US Macro Strength Index, capturing joint dynamics in growth, inflation, and labor conditions. Change points are then identified using the PELT algorithm from the ruptures. Python library, with a radial basis function cost and penalty = 5 (see fig. 2). Narrative Shift Analysis As a case study, we focus on the 2008 financial crisis. Federal Reserve bankers speech transcripts (BIS Gigando datasets) from 2004-01-01 to 2010-04-01 are split at the detected breakpoint (2007-05-01). BERTopic is fit on the pre-break period and updated (partial fit) on the post-break period. For each topic, we compute: Mean polarity shift (FinBERT sentiment [6]), semantic topic centroid drift, cosine similarity between topic centroids, and Jaccard similarity of Maximal Marginal Relevance (MMR) keyword sets. We also generate word clouds aggre- gating MMR keywords from all topics before and after the breakpoint, visualizing the thematic drift across narrative regimes (fig 3 and 4). Null Hypothesis Testing To test statistical significance, we simulate 1000 null scenarios by randomly shuf- fling speech dates while preserving content and structure. Each metric is re- computed for the randomized assignments, allowing comparison of observed drift values to their null distributions (see fig. 5, 6, 7, and 8). Figure 1: PCA Loadings and Explained Variance Figure 2: Principal Component 1 and Change Points Preliminary Results Figure 3: MMR Wordcloud for 2004.01.01-2007.05.01 period Figure 4: MMR Wordcloud for 2004.01.01-2010.04.01 period Figure 5: Polarity Drift Null Hypothesis Distribution and Observed Value Figure 6: Centroid Drift Null Hypothesis Distribution and Observed Value Figure 7: Cosine Similarity Null Hypothesis Distribution and Observed Value Figure 8: Jaccard Similarity Null Hypothesis Distribution...

---


## topol.pdf

| Property | Value |
|----------|-------|
| File | `topol.pdf` |
| Pages | 7 |
| Author |  |
| Keywords | polarity(93), semantic(56), topol(49), sentiment(45), vector(34), topic(33), hotl(31), field(26) |

**Table of Contents:**
  - Introduction
  - Preliminary
  - Methodology
  - Defining Contextual Boundaries
  - Reconstructing Semantic Polarity Fields
  - Revealing TOPol Dimensions
  - Experiments
  - Experimental Setup
  - Semi-supervised Reconstruction of Narrative Polarity Vector Field and Shifts
  - Evaluation via Methodological Perturbations
  - ... (2 more sections)

**Introduction (first 500 words):**

> TOPol: Capturing and Explaining Multidimensional Semantic Polarity Fields and Vectors Gabin Taibi 1, 3, Lucia Gomez 2, 3, 1University of Twente 2Bern University of Applied Sciences 3University of Geneva gabin.taibi@utwente.nl lucia.gomezteijeiro@bfh.ch Abstract Semantic polarity in computational linguistics has tradition- ally been framed as sentiment along a unidimensional scale. We here challenge and advance this framing, as it oversim- plifies the inherently multidimensional nature of language. We introduce TOPol (Topic-Orientation Polarity), a semi- unsupervised framework for reconstructing and interpreting multidimensional narrative polarity fields given human-on- the-loop (HoTL) defined contextual boundaries (CBs). TOPol begins by embedding documents using a general-purpose transformer-based large language model (tLLM), followed by a neighbor-tuned UMAP projection and topic-based segmen- tation via Leiden partitioning. Given a CB between regimes A and B, the framework computes directional vectors between corresponding topic-boundary centroids, producing a polar- ity field that captures fine-grained semantic displacement for each discourse regime change. TOPol polarity field reveals CB quality as this vectorial representation enables quantifi- cation of the magnitude, direction, and semantic meaning of polarity shifts, acting as a polarity change detection tool di- recting HoTL CB tuning. To interpret TOPol identified po- larity shifts, we use the tLLM to compare the extreme points of each polarity vector and generate contrastive labels with estimated coverage. Robustness tests confirm that only the definition of CBs, the primary HoTL-tunable parameter, sig- nificantly modulates TOPol outputs, indicating methodolog- ical stability. We evaluate TOPol on two corpora: US Cen- tral Bank speeches upon a macroeconomic breakpoint as CB, where semantic shifts are non-affective, and Amazon product reviews upon rating strata as CB, where sentiment dominates and therefore TOPol interpretation strongly aligns with NRC valence. Results show that TOPol reliably captures both af- fective and non-affective polarity transitions, those naturally emerging from the data, offering a scalable, generalizable, context-sensitive and interpretable approach to HoTL-guided multidimensional discourse analysis. Code and Data — https://osf.io/nr94j/?view only= a787f6e842b64bd4a0bc0344872e1eec Introduction Sentiment Polarity scoring has long occupied a central po- sition in Natural Language Processing (NLP), treated as a synonym of Semantic Polarity since its inception, addressed within the scope of Sentiment Analysis, conceptualized as a scalar indicating the extent to which a text encodes a posi- tive or negative perspective about an object (M¨antyl¨a, Grazi- otin, and Kuutila 2018). Recent works dealing with Polarity Classification, still framed in the lens of sentiment, however seek to move beyond affective components for capturing di- mensions such as sarcasm (Prasanna, Shaila, and Vadivel 2023). While this sentiment-centric framing of polarity has proven powerful, it overlooks the multidimensional nature of semantic orientation. In response, recent academic efforts are challenging this unidimensional view by developing multi-label and fine- grained affective models (Demszky et al. 2020), and pro- gressively extending polarity modeling beyond sentiment- centric paradigms (Hofmann et al. 2021). These efforts demonstrate that semantic analysis cannot be reduced to sin- gle evaluative scales, as such reductions introduce bias by overlooking the multidimensional context and perspectival complexity in which meaning is embedded. Topic Modeling (TM), the second most used NLP analy-...

---


## FIN-manuscript-v2.pdf

| Property | Value |
|----------|-------|
| File | `PhD Twente\FIN-manuscript-v2.pdf` |
| Pages | 23 |
| Author |  |
| Keywords | financial(117), narrative(114), narratives(113), research(57), analysis(49), modeling(44), literature(43), market(40) |

**Table of Contents:**
  - Introduction
  - Methodology
  - Initial Research Sourcing
  - Algorithmic Selection Framework
  - Textual Analysis: Research Properties Statements
  - Data Preparation
  - Clustering Research Selection
  - Final Validation and Data Extraction
  - Results
  - Selection Phase Results
  - ... (9 more sections)

**Introduction (first 500 words):**

> Abstract This paper presents a systematic literature review on financial narratives and the methods used to model them. To support this review, we develop an algorithmic framework that improves the efficiency, reproducibility, and consistency of study selection. The framework uses Natural Language Processing (NLP) techniques, clustering algorithms, and interpretability tools to automate key steps of the screening and analysis process. We apply this approach to the study of financial narratives, a growing field in financial economics concerned with how structured interpretations of economic events shape market behaviour and asset prices. Drawing from the Scopus1 database of peer-reviewed literature, the review identifies research practices used to model financial narratives with a range of NLP methods. Results show that although technical progress has been significant, the conceptualization of financial narratives remains fragmented and is often simplified to sentiment-based measures. A large share of studies relies on media sources, which is understandable given their availability, but the short length of these texts introduces noise and reduces predictive reliability. Using longer and more diverse textual materials would help to address this limitation and provide a broader view of narratives circulating among economic agents. The findings also highlight the importance of more comprehensive forms of narrative modeling that go beyond sentiment alone, and they illustrate the practical usefulness of the proposed algorithmic SLR methodology. Keywords— Systematic Literature Review, Text Processing, NLP, Financial Narrative, Financial Market Dynamics 1 Introduction The influence of narratives on financial markets has recently become a prominent area of study in both economics and finance. The analysis of narratives includes understanding how stories evolve, spread, and impact financial markets over time. By examining the mechanisms through which they form and propagate, researchers aim to uncover their role in shaping expectations, driving investor behavior, and consequently impacting market cycles. In social science, narratives are structured accounts or interpretive frameworks through which people understand and act in the social world. The work of Somers (1994) advances that they are not simply representations but ontological structures: social life itself is storied. Narratives constitute social identities, guide actions, and embed individuals in relational settings over time and space. These narratives are constituted through emplotment (causal linking of events), selective appropriation, and their temporal and spatial connectivity. In economics, narratives have gained traction as a bridge between behavioral and informational theories of markets. Grossman (1980) shows that when information is costly, prices cannot be perfectly informationally efficient, as perfectly revealing markets would remove incentives to acquire information. This insight departs from the view of fully efficient markets and acknowledges the role of delayed or selective information diffusion. Thus, if information diffusion is neither instantaneous nor uniform, then the stories through which it is interpreted play an important role in how beliefs form and prices adjust. The work of Shiller (2017) highlights this point by demonstrating that contagious economic stories can drive fluctuations in aggregate activity. Additionally, Shiller (2019) goes further and argues that economic fluctuations cannot be fully understood through quantitative models alone, as narratives play a...

---


## Nanosecond Microstructure: High-Frequency Traders Participation Stylized Facts

| Property | Value |
|----------|-------|
| File | `Internships\Deutsche Börse\HFT-stylized-facts.pdf` |
| Pages | 34 |
| Author | Gabin Taibi; Joerg Osterrieder; Stefan Schlamp;  |
| Keywords | market(127), trading(78), price(74), high(68), their(54), our(53), latency(49), participants(45) |

**Table of Contents:**
  - Introduction
  - Context of the Study
  - Research Questions and Objectives
  - Main Contributions
  - Paper Structure
  - Literature Review
  - Ultra-Fast and High-Frequency Traders Activity Monitoring
  - Fair-Value Modeling and Price Discovery
  - Variance and Jump Modeling in High-Frequency Settings
  - Market Quality and HFT Impact
  - ... (35 more sections)

**Introduction (first 500 words):**

> Nanosecond Microstructure: High-Frequency Traders Participation Stylized Facts Gabin Taibia,b,, Joerg Osterriedera,, Stefan Schlampc, aFaculty of Behavioral Management and Social Sciences, University of Twente, Enschede, Netherlands bDepartment of Applied Data Science and Finance, Bern University of Applied Sciences, Bern, Switzerland cMarket Data and Services, Deutsche Börse, Eschborn, Germany Abstract This paper introduces a novel methodology for classifying market participants in electronic financial markets based on their reaction times and measuring their participation. As technological innovation reshapes trading, accurately distinguishing trader types is critical for understanding market dynamics and informing regulation. Using nanosecond-level timestamp data from Deutsche Börse, we analyze post-trade latencies to separate ultra-fast traders (UFTs) relying on field-programmable gate arrays (FPGAs), high-frequency traders (HFTs), and other conventional participants. Transparent latency thresholds enable this classification, after which we document their behavior in terms of (i) participation shares, (ii) price discovery via a 15-second mark-out signal- to-noise ratio, and (iii) average reaction latency. We pair these with market quality metrics including order-imbalance volatility, Amihud illiquidity, and high-frequency return diagnostics such as autocorrelation and variance-ratio tests. The methodology is applied to Euro STOXX 50 Index Futures (FESX), examining the most actively traded contract each day from January to Au- gust 2025. Keywords: Market Microstructures, High-Frequency Trading, Price Discovery, Market Efficiency, Liquidity Email addresses: gabin.taibi@utwente.nl (Gabin Taibi), joerg.osterrieder@utwente.nl (Joerg Osterrieder), stefan.schlamp@deutsche-boerse.com (Stefan Schlamp) 1. Introduction 1.1. Context of the Study The rapid advancement of electronic markets has reshaped the financial landscape, driven by technological innovations such as ultra-low-latency trad- ing systems, high-performance computing, and Field-Programmable Gate Array (FPGA) technology. These technological developments have enabled the rise of Ultra-Fast Traders (UFTs) and High-Frequency Traders (HFTs), who leverage ultra-fast reaction times to gain a competitive edge in financial markets. The emergence of these sophisticated market participants has fun- damentally altered price formation mechanisms, liquidity provision, and the competitive dynamics of modern trading venues. In modern financial markets, a variety of participants operate with differ- ent objectives and strategies, including market makers, speculators, hedgers, and institutional investors. Each group contributes to market liquidity and efficiency in distinct ways, yet the precise classification of these participants is critical to understanding their impact on price formation, market dynam- ics, and liquidity provision. Particularly, UFTs and HFTs, equipped with cutting-edge technological infrastructures, stand out due to their ability to react to market signals within microseconds, distinguishing them from con- ventional participants. The technological arms race in financial markets has intensified over the past decade, with firms investing massively in infrastructure to shave mi- croseconds off their reaction times. This competition has profound impli- cations for market quality, fairness, and stability. While proponents argue that HFT improves liquidity and price efficiency, critics raise concerns about market manipulation, flash crashes, and the creation of a two-tiered market system. 1.2. Research Questions and Objectives This paper addresses two fundamental research questions that guide our empirical investigation. First, we examine how to accurately classify market participants based on their technological capabilities, specifically their reac- tion times to market events. Then, we analyze how different...

---


## Poster_HFT_Impact_1.pdf

| Property | Value |
|----------|-------|
| File | `Internships\Deutsche Börse\Poster_HFT_Impact_1.pdf` |
| Pages | 1 |
| Author |  |
| Keywords | participation(15), market(10), uft(6), hft(6), data(6), traders(5), events(5), total(5) |


**Introduction (first 500 words):**

> FromSpeedtoStability: TheInfluenceofLowLatency TradingonMarketQuality Gabin Taibi, Bern University of Applied Sciences, University of Twente Background The rapid evolution of electronic financial markets, driven by technological ad- vancements such as ultra-low-latency trading systems, high-performance comput- ing, and Field-Programmable Gate Arrays (FPGA) technology, has transformed the landscape of trading. These innovations have enabled the rise of Ultra-Fast Traders (UFT) and High-Frequency Traders (HFT), also known as Low-Latency Traders (LLT), who can react to market events within a few microseconds. These ultra-fast reaction capabilities set them apart from conventional market partici- pants, making them a unique force in financial markets. Understanding the role and behavior of these traders is critical to analyzing modern market dynamics. UFTs and HFTs play a significant role in liquidity and price formation, but their impact on market stability and efficiency remains the subject of ongoing debate. Research Objectives ▶Contributing to the ongoing discussion about the role of ultra-fast trading in financial markets. ▶Proposing a novel market participants’ classification method. ▶Providing a detailed analysis of participation rates and trading behaviors of UFT and HFT. ▶Analyzing if and how these participants affect market microstructure, efficiency, and volatility. Data and Preprocessing The study is based on nanoseconds timestamp data from Deutsche B¨orse’s T7 platform, starting from January 2021 until September 2024. Specifically, we se- lected Euro STOXX 50 and DAX Futures, along with MSCI World and S&P500 iShares ETFs for their high liquidity on Eurex and Xetra, although only the Euro STOXX 50 results are presented on this poster. To classify a specific market event, we have based our approach on the latency between a prior triggering trade and the event. Events with a latency of less than 1µs are classified as UFT-triggered, latencies between 1µs and 10µs as HFT-triggered, while latencies exceeding 10µs are attributed to conventional traders. Additionally, negative latencies are attributed to noise. Methodology ▶The total participation is measured as the sum of the notional value (price × quantity) for all market events triggered by a given participant category. ▶Other participation types: aggressive, passive, canceled, and deep (beyond the first order book level). ▶Aggregated tick-to-trade data into 1-minute intervals to compute metrics: traded volume, average spread, effective spread, depth, order imbalance ratio (OIR), and mid/micro/trade price volatility. ▶Included a control variable similar to SNR. ▶Combined 1-minute data into monthly datasets and divided into 5 total participation quantiles. Conclusion ▶LLT (both UFT and HFT) produce, at most, roughly 20% of total participation, including aggressive and passive (Fig. 1). ▶All participants primarily generate passive order data, with UFTs contributing almost no passive orders (Fig. 1): market making strategies? ▶UFTs cancel around 80% of their orders, but this represents, at most, 20% of total canceled participation. (Fig. 2). ▶The deep order book participation (often considered noise) is insignificant, at most 0.06% (Fig. 3). ▶Clear correlation between high LLT participation and all eight metrics (Fig. 4), but the impact is positive on spread, effective spread, depth and OIR. ▶Interesting difference between UFT and HFT’s behaviour: UFTs’ SNR decreases with higher participation while HFTs’...

---


## 20251108_Gabin-Taibi_Progress-Report.pdf

| Property | Value |
|----------|-------|
| File | `PhD Twente\Qualifier\20251108_Gabin-Taibi_Progress-Report.pdf` |
| Pages | 2 |
| Author |  |
| Keywords | volatility(23), narratives(14), narrative(13), financial(10), realized(9), chapter(9), detection(8), based(8) |


**Introduction (first 500 words):**

> PhD Progress Report Gabin Taibi Behavioural, Management and Social sciences (BMS), University of Twente Promotor(s): prof. dr. Joerg Osterrieder Co-Promotor(s): dr. Xiaohong Huang Supervisors: dr. Stefan Schlamp, dr. Axel Gross-Klussmann November 8, 2025 Thesis Title: Modeling Narrative Dynamics for Volatility Regime Detection in Financial Markets PhD Period: December 2023 – November 2027 1. Introduction My PhD investigates how financial narratives influence volatility and market regime changes. I study how information contained in unstructured text (news headlines, articles, speech transcripts, corpo- rate communication or filings) can be quantified and linked to volatility patterns. The objective is to integrate natural language processing, econometrics, and machine learning to model narrative for- mation, diffusion, and their relationship with market uncertainty. Ultimately, the goal is to quantify the informational role of narratives in shaping risk perception and to assess their predictive power for structural breaks and volatility regimes in financial markets. The project combines theoreti- cal and empirical approaches, aiming to provide a framework that bridges narrative economics and quantitative finance. 2. Research Progress and Planning I have completed the first stage of my PhD, which focused on data collection and the systematic literature review. I implemented custom libraries to collect and structure datasets from RavenPack (news headlines), LSEG (earnings call transcripts), BIS (worldwide central bank speeches), SEC EDGAR (10-K and 10-Q filings), and Deutsche B¨orse (nanosecond-level Xetra and Eurex trading data). I developed Python pipelines for data ingestion, preprocessing, and version control. The first paper, an AI-enhanced systematic literature review on financial narratives, is currently under revision at Financial Innovation. The second stage, which is ongoing, focuses on the detection and quantification of financial narratives. I am developing both supervised and unsupervised NLP frameworks using embedding similarity, Large Language Models (LLM), and graph-based clustering algorithms. This part of the research will lead to two papers, one presenting the narrative detection framework and another introducing TOPol, a tool used for semantic polarity shift detection. The third stage, starting in 2026, will consist in computing and benchmarking realized volatility estimators using Deutsche B¨orse data. The realized-library I created provides efficient Python and C++ implementations for realized volatility estimators and jump detection. I will also compute historical implied volatility, and realized and implied roughness and vol-of-vol. This work will produce two papers: one on the impact of high-frequency traders on market quality and another on volatility estimation methods (eventually a third one on Hurst exponent computation). The fourth stage will integrate narratives into volatility modeling. I will apply structural break detection methods such as Bai–Perron, CUSUM, and Bayesian frameworks to realized and implied volatility measures. The goal is to link potential regime shifts with narrative dynamics changes and to test for causal relationships. The final stage of the PhD will synthesize these results and present a comprehensive understanding of narrative-driven volatility dynamics. Envisioned Chapters: • Chapter 1 – Systematic Literature Review: This chapter defines and contextualizes the concept of financial narratives. It traces how narrative ideas have evolved within economics and finance, highlighting the shift from qualitative,...

---


## PhD Qualifier Report

| Property | Value |
|----------|-------|
| File | `PhD Twente\Qualifier\20251108_Gabin-Taibi_Qualifier-slides.pdf` |
| Pages | 47 |
| Author | Gabin Taibi |
| Keywords | volatility(140), narratives(122), narrative(76), doctoral(73), research(72), thesis(59), phd(57), structure(54) |

**Table of Contents:**
  - Doctoral Journey and Structure
  - Thesis Overview
  - Doctoral Education Programme
  - Other Academic Activities
  - Research Design and Methodology
  - Thesis
  - Dataset
  - Narratives
  - Volatility
  - Narratives–Volatility Dynamics
  - ... (1 more sections)

**Introduction (first 500 words):**

> PhD Qualifier Report Gabin Taibi Faculty, Department: Behavioural, Management and Social sciences (BMS), High-tech Business and Entrepreneurship (HBE) Promotor(s): prof. dr. Joerg Osterrieder Co-Promotor(s): dr. Xiaohong Huang Supervisors: dr. Stefan Schlamp, dr. Axel Gross-Klussmann Qualifier Committee Members: prof. dr. Wolfgang Haerdle, prof. dr. Ali Hirsa, prof. dr. Daniel Pele November 10, 2025 Doctoral Journey and Structure Research Design and Methodology Thesis Overview Doctoral Education Programme Other Academic Activities Table of Contents 1. Doctoral Journey and Structure Thesis Overview Doctoral Education Programme Other Academic Activities 2. Research Design and Methodology Thesis Dataset Narratives Volatility Narratives–Volatility Dynamics Conclusion Gabin Taibi PhD Qualifier Report Doctoral Journey and Structure Research Design and Methodology Thesis Overview Doctoral Education Programme Other Academic Activities Abstract Modeling Narrative Dynamics for Volatility Regime Detection in Financial Markets Research question: How do forms of narratives influence volatility and regime changes in markets? Research summary: Financial markets are increasingly driven by narratives, defined as collective interpretations that influence expectations, volatility, and market regimes. Yet, despite their central role, narratives remain largely unquantified in financial modeling. This research aims to bridge that gap by developing a computational framework linking the evolution of financial narratives to volatility dynamics and structural market shifts. The thesis integrates methods from natural language processing, high–frequency econometrics, and machine learning to (1) detect and quantify narratives across multiple textual sources, (2) measure volatility and its higher–order properties from high–frequency data, and (3) analyze the causal and predictive relationship between narrative shifts and volatility regimes. PhD expected period: Dec 1st, 2023 - Nov 30th, 2027 Gabin Taibi PhD Qualifier Report Doctoral Journey and Structure Research Design and Methodology Thesis Overview Doctoral Education Programme Other Academic Activities Research Motivation Rationale: Narrative information forms a latent context for market decisions (Shiller), yet quantitative models often overlook these textual dynamics. Recent advances in transformer-based NLP: Allow scalable narrative extraction, extending analysis beyond simple sentiment/polarity. As LLMs increase textual data, this research seeks to identify which narratives matter most. Access to high-quality, high-frequency (HFT) data allows for precise estimation of market dynamics, including volatility and its higher-order properties. Understanding how narrative shocks translate into volatility regime changes provides academic and practical insights for risk management and narrative-aware trading. Gabin Taibi PhD Qualifier Report Doctoral Journey and Structure Research Design and Methodology Thesis Overview Doctoral Education Programme Other Academic Activities Research Motivation Social perspectives: 1. Understanding Financial Narratives and Financial Markets Reactions; 2. Improving Financial Stability and Crisis Prediction; 3. Empowering Retail and Institutional Decision-Making; 4. Interdisciplinary Applications Beyond Finance. Gabin Taibi PhD Qualifier Report Doctoral Journey and Structure Research Design and Methodology Thesis Overview Doctoral Education Programme Other Academic Activities Research Motivation Scientific perspective: 1. Improving NLP methods for financial text; 2. Advancing the quantitative modeling of various forms of narratives within finance; 3. Highlight interconnexion between narratives or forms of narratives (e.g. how macro and micro information spread in news); 4. Linking narrative and volatility dynamics. Gabin Taibi PhD Qualifier Report Doctoral Journey and Structure Research Design and Methodology Thesis Overview Doctoral...

---
