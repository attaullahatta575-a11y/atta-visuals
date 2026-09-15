import os
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# APP SETTINGS
# =========================================================

APP_NAME = "Atta Visuals"

DEFAULT_SIZE = "2000x2000"

SUPPORTED_SIZES = {
    "2000x2000": (2000, 2000),
    "1500x1500": (1500, 1500),
    "1100x1100": (1100, 1100),
    "1080x1080": (1080, 1080),
}


# =========================================================
# GROQ SETTINGS
# =========================================================

def get_secret(name: str, default: str = "") -> str:
    """
    Read a secret from Streamlit Cloud Secrets first,
    then from environment variables.
    """

    # Streamlit Cloud
    try:
        import streamlit as st

        if name in st.secrets:
            value = st.secrets[name]

            if value is not None:
                return str(value).strip()

    except Exception:
        pass

    # Local .env / environment variable
    return os.getenv(name, default).strip()


GROQ_API_KEY = get_secret("GROQ_API_KEY")


# Preferred vision models.
# The first available model will be used.
VISION_MODELS = [
    "qwen/qwen3.6-27b",
    "qwen/qwen3.8-27b",
]


# Optional manual model from Streamlit Secrets/.env
GROQ_MODEL = get_secret("GROQ_MODEL")


# =========================================================
# AI LIMITS
# =========================================================

MAX_IMAGE_MB = 20

MAX_COMPLETION_TOKENS = 1200

TEMPERATURE = 0.2
