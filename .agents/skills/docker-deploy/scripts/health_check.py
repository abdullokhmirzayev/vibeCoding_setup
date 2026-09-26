#!/usr/bin/env python3
"""
Docker compose configuration validator script
"""
import sys
from pathlib import Path
import yaml

def main():
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
    compose_file = root / "docker-compose.yml"

    print("[DOCKER-CHECK] Checking docker-compose.yml existence and syntax...")
    if not compose_file.exists():
        print("❌ [ERROR] docker-compose.yml not found!")
        sys.exit(1)

    try:
        data = yaml.safe_load(compose_file.read_text(encoding="utf-8"))
        services = list(data.get("services", {}).keys())
        print(f"✅ [SUCCESS] docker-compose.yml valid. Configured services: {services}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ [SYNTAX ERROR] Failed to parse docker-compose.yml: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
