import pytest

from application import db


class FakeClient:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeCollection:
    def __init__(self):
        self.distinct_arguments = None

    def distinct(self, key, query):
        self.distinct_arguments = (key, query)
        return ["Elden Ring"]


def test_list_games_by_snippet(monkeypatch):
    client = FakeClient()
    collection = FakeCollection()

    monkeypatch.setattr(
        db,
        "get_deals_collection",
        lambda: (client, collection),
    )

    titles = db.list_games_by_snippet("ring")

    assert titles == ["Elden Ring"]
    assert collection.distinct_arguments == (
        "title",
        {"title": {"$regex": "ring", "$options": "i"}},
    )
    assert client.closed is True


@pytest.mark.parametrize(
    "invalid_snippet",
    [None, "", "   ", "a" * 51],
)
def test_list_games_by_snippet_rejects_invalid_input(
    monkeypatch,
    invalid_snippet,
):
    monkeypatch.setattr(
        db,
        "get_deals_collection",
        lambda: pytest.fail("Database should not be accessed"),
    )

    with pytest.raises(ValueError):
        db.list_games_by_snippet(invalid_snippet)
