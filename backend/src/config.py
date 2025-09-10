import os

def load_google_api_key():
    secret_path = "/run/secrets/google_api_key"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    return os.getenv("GOOGLE_API_KEY")

def ensure_google_api_key():
    api_key = load_google_api_key()
    if not api_key:
        raise RuntimeError("Google API key not found in Docker secret or environment variable.")
    os.environ["GOOGLE_API_KEY"] = api_key
    return api_key
