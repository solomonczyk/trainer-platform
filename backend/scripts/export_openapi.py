#!/usr/bin/env python3
"""Export OpenAPI schema to JSON file."""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


def main():
    output_path = Path(__file__).resolve().parent.parent / "docs" / "openapi_schema.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    schema = app.openapi()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    paths_count = len(schema.get("paths", {}))
    print(f"[OK] OpenAPI schema exported to: {output_path}")
    print(f"     Paths: {paths_count}")


if __name__ == "__main__":
    main()
