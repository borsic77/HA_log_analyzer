# custom_components/log_summarizer/__init__.py
try:
    from .log_summarizer import setup
except ImportError:
    # Allow importing from Streamlit or CLI context where Home Assistant is not installed
    setup = None