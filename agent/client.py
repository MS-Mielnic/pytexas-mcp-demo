from servers.untrusted_demo_server.server import lookup_customer_strategy
from agent.models import ExternalStrategyRaw


def fetch_untrusted_customer_strategy(customer_id: str) -> ExternalStrategyRaw | None:
    result = lookup_customer_strategy(customer_id)

    if not result.found or result.record is None:
        return None

    return ExternalStrategyRaw(**result.record.model_dump())


import requests
from agent.prompts import SYSTEM_PROMPT


def call_ollama(prompt: str, model: str = "llama3") -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": f"{SYSTEM_PROMPT}\n\nUser input:\n{prompt}",
            "stream": False,
        },
    )

    response.raise_for_status()
    return response.json()["response"]
