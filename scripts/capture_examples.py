"""Capture actual backend responses for the README; requires the running API."""

import json
from pathlib import Path

import httpx


def main() -> None:
    directory = Path(__file__).resolve().parents[1] / "docs"
    with httpx.Client(base_url="http://localhost:8000/api/v1", timeout=180) as client:
        response = client.get("/profiles/demo")
        response.raise_for_status()
        profiles = response.json()
        for filename, endpoint, payload in [
            ("example-match.json", "/match/1-to-1", {"profile_a": profiles[3], "profile_b": profiles[7]}),
            (
                "example-ranking.json",
                "/match/1-to-n",
                {"source_profile": profiles[3], "limit": 3, "justify_top": 2},
            ),
        ]:
            response = client.post(endpoint, json=payload)
            response.raise_for_status()
            (directory / filename).write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
            print(f"Captured {filename}")


if __name__ == "__main__":
    main()
