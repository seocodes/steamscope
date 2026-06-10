from application.gemini_advisor import parse_gemini_response


# Ideal input
def test_parse_gemini_response_accepts_plain_json():
    response_text = """
          {
            "verdict": "good",
            "summary": "Worth considering.",
            "confidence": 80,
            "key_insights": ["Below average price"]
          }
          """
    
    parsed = parse_gemini_response(response_text)
    
    assert parsed["verdict"] == "good"
    assert parsed["confidence"] == 80
    assert parsed["key_insights"] == ["Below average price"]

# Realistic input
def test_parse_gemini_response_accepts_json_markdown_block():
    response_text = """
          ```json
          {
            "verdict": "good",
            "summary": "Worth considering.",
            "confidence": 80,
            "key_insights": ["Below average price"]
          }
          ```
          """

    parsed = parse_gemini_response(response_text)

    assert parsed["verdict"] == "good"
    assert parsed["confidence"] == 80
    assert parsed["key_insights"] == ["Below average price"]

# Error case
def test_parse_gemini_response_fallback_for_invalid_json():
    response_text = "Not JSON"

    parsed = parse_gemini_response(response_text)

    assert parsed["verdict"] == "unknown"
    assert parsed["summary"] == response_text
    assert parsed["confidence"] == 0
    assert parsed["key_insights"] == []
