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
    assert "new AbortController()" in source
    assert "aria-label=\"Close product search\"" in source
    assert "aria-label=\"Search products\"" in source
    assert "aria-hidden" in source
    assert "aria-expanded" in source
    assert "this.fabEl.focus()" in source
    assert "keepalive: true" in source
