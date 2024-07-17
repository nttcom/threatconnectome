from app.slack import (
    TAG_URL,
    THREAT_IMPACT_LABEL,
    create_slack_pteam_alert_blocks_for_new_topic,
)


def test_create_blocks_for_pteam():
    notification_data = {
        "pteam_id": " 70de29d6-2b33-4990-8d2a-657554335064",
        "pteam_name": "team1",
        "tag_name": "tag1",
        "tag_id": "dd313aab-68aa-4dc4-8362-cec093d5d49b",
        "topic_id": "b1f74d1f-9360-4a8d-86ac-3cf5dd20c75c",
        "title": "test_title1",
        "threat_impact": 1,
        "services": ["test1_service", "test2_service"],
    }

    blocks = create_slack_pteam_alert_blocks_for_new_topic(**notification_data)
    assert notification_data["pteam_name"] in blocks[0]["text"]["text"]
    tag_page_url = f"{TAG_URL}{notification_data['tag_id']}?pteamId={notification_data['pteam_id']}"
    assert tag_page_url in blocks[2]["text"]["text"]
    assert notification_data["title"] in blocks[2]["text"]["text"]
    assert THREAT_IMPACT_LABEL[notification_data["threat_impact"]] in blocks[2]["text"]["text"]
    assert notification_data["services"][0] in blocks[2]["text"]["text"]
