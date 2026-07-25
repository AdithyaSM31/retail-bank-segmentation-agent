# Customer Segmentation & Personalization Agent for Retail Banking

An AI-powered agentic system that ingests retail banking customer data, performs automated EDA, segments customers using ML/rule-based methods, generates interpretable personas, and delivers personalized product recommendations — all driven by natural language chat queries.

## Problem Statement

A retail bank provides a range of financial products (savings accounts, credit cards, personal loans, investment services) but currently applies broad, one-size-fits-all marketing strategies. This agent leverages customer transaction data to understand behavioural patterns, segment customers into meaningful groups, and deliver personalized product recommendations to improve customer experience and increase cross-selling opportunities.

## Solution Approach

### Architecture

The system follows an **agentic AI architecture** using a **LangGraph ReAct (Reason + Act) agent** that autonomously decides which tools to invoke based on the user's natural language query.

```
┌──────────────────┐     ┌─────────────────────────────┐     ┌───────────────┐
│  Streamlit UI    │────▶│  LangGraph ReAct Agent       │────▶│  Gemini 2.5   │
│  (Chat + Charts) │◀────│  (Orchestrator)              │◀────│  Flash LLM    │
└──────────────────┘     │                               │     └───────────────┘
                          │  ┌──────────────────────────┐│
                          │  │     25 Specialized Tools  ││
                          │  │  ┌─────┐ ┌──────────┐    ││
                          │  │  │ EDA │ │ Feature   │    ││
                          │  │  │Tool │ │Engineering│    ││
                          │  │  └─────┘ └──────────┘    ││
                          │  │  ┌─────────┐ ┌────────┐  ││
                          │  │  │Segmentat│ │Explain │  ││
                          │  │  │ion Tool │ │ability │  ││
                          │  │  └─────────┘ └────────┘  ││
                          │  │  ┌──────────┐ ┌───────┐  ││
                          │  │  │Recommend │ │Visual- │  ││
                          │  │  │ation     │ │ization│  ││
                          │  │  └──────────┘ └───────┘  ││
                          │  │  ┌───────┐               ││
                          │  │  │Export  │               ││
                          │  │  │Tool   │               ││
                          │  │  └───────┘               ││
                          │  └──────────────────────────┘│
                          └──────────────────────────────┘
                                        │
                          ┌─────────────────────────────┐
                          │  Data Layer (Pandas)         │
                          │  1M+ Transactions → ~800K    │
                          │  Customer-Level Features     │
                          └─────────────────────────────┘
```

### How the Agent Works

1. **User sends a natural language query** via the Streamlit chat interface
2. **LLM (Gemini 2.5 Flash) interprets the query** and decides which tools to call and in what order
3. **Agent executes a multi-step pipeline** automatically — e.g., for "Segment customers into priority, regular and dormant":
   - Step 1: Call `engineer_customer_features()` to aggregate transaction data
   - Step 2: Call `segment_customers_rule_based()` with appropriate rules
   - Step 3: Call `plot_segment_distribution()` to visualize results
   - Step 4: Call `export_segments_to_csv()` to save results
4. **Agent returns a structured response** with insights, tables, and interactive charts
5. **User can ask follow-up questions** with full conversation context maintained

### What Makes This Agentic

- ✅ **Multi-step automatic execution** — Single query triggers a pipeline of 3-5 tool calls
- ✅ **Dynamic tool selection** — Agent chooses tools based on query semantics
- ✅ **Query-driven orchestration** — Different queries invoke different tool sequences
- ✅ **Human-in-the-loop** — Agent asks clarifying questions when queries are ambiguous
- ✅ **Conversation memory** — Follow-up questions reference previous context

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (chat UI + Plotly chart rendering) |
| **Agent Framework** | LangGraph + LangChain (ReAct agent with tool calling) |
| **LLM** | Google Gemini 2.5 Flash (free API via Google AI Studio) |
| **Data Processing** | Pandas, NumPy |
| **ML / Clustering** | scikit-learn (KMeans, StandardScaler, silhouette analysis) |
| **Visualization** | Plotly (interactive charts with dark theme) |
| **Backend API** | FastAPI (optional REST endpoint) |
| **Language** | Python 3.10+ |

## Dataset Information

### Primary Dataset
- **Source:** [Bank Customer Segmentation (1M+ Transactions)](https://www.kaggle.com/datasets/shivamb/bank-customer-segmentation) — Kaggle
- **Size:** 1,048,567 transactions, ~800K unique customers
- **Features:** TransactionID, CustomerID, CustomerDOB, CustGender, CustLocation, CustAccountBalance, TransactionDate, TransactionTime, TransactionAmount (INR)

### Synthetic Data
- **File:** `data/synthetic_products.csv`
- **Purpose:** Maps customers to product holdings (credit cards, personal loans, FDs, mutual funds, insurance, mobile banking)
- **Generation Logic:** Product ownership probabilities are correlated with account balance tiers (high/medium/low) to simulate realistic banking product penetration. See `generate_synthetic_data.py` for full logic.
- **Schema:**
  - `CustomerID` — Maps to primary dataset
  - `has_credit_card`, `has_personal_loan`, `has_fixed_deposit`, `has_mutual_funds`, `has_insurance`, `has_mobile_banking` — Binary (0/1)
  - `total_products` — Count of products held

## Agent Tools (25 Total)

| Category | Tools | Description |
|---|---|---|
| **EDA** | 5 tools | Full EDA, column distributions, correlations, aggregations, missing values |
| **Feature Engineering** | 3 tools | Customer-level feature creation, feature selection, scaling |
| **Segmentation** | 4 tools | Rule-based segmentation, KMeans ML clustering, optimal-k analysis, segment statistics |
| **Explainability** | 4 tools | Segment explanation, customer-level explanation, segment comparison, feature importance |
| **Recommendations** | 3 tools | Product recommendations, upgrade candidates, retention strategies |
| **Visualization** | 5 tools | Segment distribution, feature comparison, scatter plots, radar charts, heatmaps |
| **Data Export** | 3 tools | CSV export, report generation, segment queries |

## Setup & Usage

### Prerequisites
- Python 3.10+
- Google AI Studio API key ([Get one free](https://aistudio.google.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/AdithyaSM31/retail-bank-segmentation-agent.git
cd retail-bank-segmentation-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Dataset Setup
1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/shivamb/bank-customer-segmentation)
2. Place the CSV file at `data/bank_transactions.csv`
3. Generate synthetic product data:
```bash
python generate_synthetic_data.py
```

### Running the Application (New React + Glassmorphism UI)

1. **Start the FastAPI Backend**
   Open a new terminal, activate your virtual environment, and run:
   ```bash
   uvicorn app:app --reload
   ```
   (The API will run on `http://localhost:8000`)

2. **Start the React Frontend**
   Open a second terminal, navigate to the `frontend` directory, and run:
   ```bash
   cd frontend
   npm run dev
   ```
   (The UI will run on `http://localhost:5173`)

### Example Queries

| Query | What the Agent Does |
|---|---|
| "Run EDA on the dataset" | Comprehensive data analysis with statistics and distributions |
| "Segment customers into priority, regular and dormant based on balance and transaction frequency" | Feature engineering → Rule-based segmentation → Visualization → CSV export |
| "On what basis were priority customers selected?" | Returns rules/thresholds used for priority classification |
| "What is the average size of transactions for priority and regular customers?" | Aggregates and compares transaction metrics across segments |
| "Which regular customers can be converted to priority? What should be done?" | Identifies upgrade candidates near priority thresholds + conversion strategies |
| "Show me a radar chart of all segments" | Generates interactive radar chart comparing segment profiles |

## Project Structure

```
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variable template
├── config.py                           # Centralized configuration
├── data_loader.py                      # Data ingestion & preprocessing
├── app.py                              # FastAPI backend
├── generate_synthetic_data.py          # Synthetic product data generator
├── agent/
│   ├── orchestrator.py                 # LangGraph ReAct agent
│   ├── prompts.py                      # System prompts
│   └── state.py                        # Agent state definition
├── tools/
│   ├── eda_tool.py                     # Exploratory Data Analysis
│   ├── feature_engineering_tool.py     # Feature creation & scaling
│   ├── segmentation_tool.py            # KMeans + rule-based clustering
│   ├── explainability_tool.py          # Segment explanations
│   ├── recommendation_tool.py          # Product recommendations
│   ├── visualization_tool.py           # Plotly chart generation
│   └── data_export_tool.py             # CSV export & reports
├── ui/
│   └── streamlit_app.py               # Streamlit chat frontend
├── data/
│   ├── bank_transactions.csv           # Primary dataset (Kaggle)
│   └── synthetic_products.csv          # Generated product holdings
└── outputs/                            # Generated reports, CSVs, charts
    └── charts/
```

## Disclosures

### AI Tools Used
- **Google Gemini 2.5 Flash** — LLM for agent reasoning and tool selection (via Google AI Studio free API)
- **Agentic coding assistant** — Used during development

### External Libraries
All dependencies are listed in `requirements.txt`. Key libraries: LangChain, LangGraph, scikit-learn, Plotly, Streamlit, FastAPI, Pandas.
