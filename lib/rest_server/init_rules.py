"""Initialize rules configuration in Redis."""
import json
from pathlib import Path

import yaml

from lib.core.redis_connector import Redis


def init_rules() -> None:
    """Initialize rules configuration in Redis."""
    # Get rules file path
    config_dir = Path(__file__).parent.parent.parent / "config"
    rules_file = config_dir / "rules.yaml"

    if not rules_file.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_file}")

    # Load rules from YAML
    with open(rules_file, encoding="utf-8") as file:
        rules = yaml.safe_load(file)

    # Store rules in Redis
    redis = Redis(namespace="rest_server")
    redis.set_key("rules_config", json.dumps(rules))
