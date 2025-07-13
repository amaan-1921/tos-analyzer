import httpx
from typing import List, Dict, Any
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ToSModel:
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", api_key: str = "lm-studio"):
        self.client = httpx.Client(
            base_url="http://127.0.0.1:1234/v1",
            headers={"Authorization": "Bearer lm-studio"},
            timeout=httpx.Timeout(180.0)
        )
        self.label_map = ["Risky", "Unfair", "Benign"]

    def predict(self, clauses: List[str]) -> List[Dict[str, Any]]:
        if not clauses:
            logger.error("No clauses provided")
            return []

        clauses_text = '\n'.join(f'{i}. {clause}' for i, clause in enumerate(clauses, 1))
        prompt = (
            "You are a legal analysis assistant. Classify each Terms of Service clause as 'Risky', 'Unfair', or 'Benign':\n"
            "- 'Risky': Harms the user significantly (e.g., privacy violations, financial traps).\n"
            "- 'Unfair': Limits user rights or favors the company (e.g., arbitration clauses).\n"
            "- 'Benign': No significant risk (e.g., age restrictions).\n\n"
            f"Clauses:\n{clauses_text}\n\n"
            "Return a JSON array of objects, each with 'label' (one of 'Risky', 'Unfair', 'Benign') and 'explanation' (max 30 words). "
            "Example: [{\"label\": \"Risky\", \"explanation\": \"Privacy violation.\"}, ...]."
        )

        request_body = {
            "model": "mistral-7b-instruct-v0.2",   # ← Use the exact model ID from API Usage
            "prompt": prompt,
            "temperature": 0.1,
            "max_tokens": 1000
        }

        try:
            logger.debug(f"Sending request to LM Studio: {json.dumps(request_body, indent=2)}")
            res = self.client.post("/completions", json=request_body)
            try:
                res.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"LM Studio error response: {res.text}")
                raise
            content = res.json()["choices"][0]["text"]
            logger.debug(f"LM Studio response: {content}")

            result = json.loads(content)
            if not isinstance(result, list) or len(result) != len(clauses):
                raise ValueError(f"Mismatch between number of clauses ({len(clauses)}) and responses ({len(result)}).")
            if any(not isinstance(r, dict) or "label" not in r or r["label"] not in self.label_map or "explanation" not in r for r in result):
                raise ValueError(f"Invalid response format: {result}")

            return [
                {
                    "clause_number": i + 1,
                    "text": clauses[i],
                    "label": r["label"],
                    "explanation": r["explanation"]
                } for i, r in enumerate(result)
            ]

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return [
                {
                    "clause_number": i + 1,
                    "text": clause,
                    "label": "Benign",
                    "explanation": f"Error analyzing clause: {str(e)}."
                }
                for i, clause in enumerate(clauses)
            ]