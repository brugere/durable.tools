#!/usr/bin/env python3
"""
Setup database: Create DuckDB file and load washing machine data.
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data():
    logger.info("Loading washing machine data into DuckDB...")
    try:
        from ingest.load_washing_machines_to_db import main as load_main
        load_main()
        return True
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return False


def main():
    if not load_data():
        raise SystemExit(1)
    logger.info("DuckDB setup completed successfully!")


if __name__ == "__main__":
    main() 