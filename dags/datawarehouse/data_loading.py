import json
from datetime import date
import logging

#logger object
logger=logging.getLogger(__name__)

def load_path():

    # determine path relative to this module's parent directories so it works in the
    # Airflow container regardless of the current working directory
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent
    file_path = repo_root / "data" / f"YT_data_{date.today()}.json"

    try:
        logger.info(f"Processing file: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as raw_data:
            data = json.load(raw_data)

        # normalize keys coming from the JSON so downstream code can rely on
        # consistent camelCase names
        for row in data:
            # view count sometimes appears as snake_case or camelCase
            if "view_count" in row and "viewCount" not in row:
                row["viewCount"] = row.pop("view_count")
            # if any of the count fields are None/empty, make them 0 so that
            # SQL doesn't break when expecting an integer
            for count_key in ("viewCount", "likeCount", "commentCount"):
                if row.get(count_key) in (None, ""):
                    row[count_key] = 0

        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        raise