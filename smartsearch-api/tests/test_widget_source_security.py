from pathlib import Path


def test_widget_builds_match_and_escape_untrusted_values():
    repository_root = Path(__file__).resolve().parents[2]
    source = (repository_root / "widget" / "widget.js").read_text(encoding="utf-8")
    public = (repository_root / "dashboard" / "public" / "widget.js").read_text(
        encoding="utf-8"
    )

    assert source == public
    assert "this.escapeHtml(p.title)" in source
    assert "this.escapeHtml(p.description)" in source
    assert "this.safeUrl(p.product_url)" in source
    assert "X-Query-Event-Token" in source
    assert "query_log_id" not in source
