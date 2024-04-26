from openai import OpenAI

class Config:

    NCFA = "your_ncfa_token"

    GCP_API_KEY = 'your_api_key'

    OPENAI_API_KEY = "your_api_key"

LLM = OpenAI(
    api_key=Config.OPENAI_API_KEY
)
