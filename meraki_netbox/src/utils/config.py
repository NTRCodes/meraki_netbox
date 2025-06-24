"""Configuration utilities for the application."""
import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from .env file."""
    load_dotenv()

# Load config when module is imported
load_dotenv()