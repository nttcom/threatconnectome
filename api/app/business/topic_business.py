import json
from hashlib import md5
from typing import Sequence

from app import models


def get_sorted_topics(topics: Sequence[models.Topic]) -> Sequence[models.Topic]:
    """
    Sort topics with standard sort rules -- (cvss_v3_score DESC, updated_at DESC)
    """
    return sorted(
        topics,
        key=lambda topic: (
            topic.cvss_v3_score if topic.cvss_v3_score is not None else -1,
            dt.timestamp() if (dt := topic.updated_at) else 0,
        ),
        reverse=True,
    )


def calculate_topic_content_fingerprint(
    title: str,
    abstract: str,
    cvss_v3_score: float | None,
    tag_names: Sequence[str],
) -> str:
    data = {
        "title": title,
        "abstract": abstract,
        "cvss_v3_score": cvss_v3_score,
        "tag_names": sorted(set(tag_names)),
    }
    return md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
