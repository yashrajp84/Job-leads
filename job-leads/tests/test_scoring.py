from job_agent.scoring import score_record


def test_score_record_basic():
    rec = {"title": "Product Designer", "description": "Figma, WCAG required", "company": "Acme", "tags": "design,ux"}
    rules = {"plus": [["wcag", 3], ["figma", 2]], "minus": [["senior", 4]]}
    assert score_record(rec, rules) == 5

    rec2 = {"title": "Senior UX", "description": "", "company": "", "tags": ""}
    assert score_record(rec2, rules) == -4

