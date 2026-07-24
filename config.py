"""
Centralized configuration for the Customer Segmentation Agent.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUT_DIR / "charts"

# Ensure output directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Dataset ---
TRANSACTIONS_CSV = DATA_DIR / "bank_transactions.csv"
SYNTHETIC_PRODUCTS_CSV = DATA_DIR / "synthetic_products.csv"

# --- LLM ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
LLM_MODEL = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.1  # Low temperature for consistent analytical outputs

# --- Clustering Defaults ---
DEFAULT_N_CLUSTERS = 3
MAX_CLUSTERS_SEARCH = 10
RANDOM_STATE = 42

# --- App ---
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8000
STREAMLIT_PORT = 8501
