from app.core.url_security import is_secure_redis_url


def test_secure_redis_url_accepts_tls_and_render_private_network():
    assert is_secure_redis_url("rediss://default:secret@cache.example.com:6379/0")
    assert is_secure_redis_url("redis://red-abc123:6379/0")
    assert is_secure_redis_url("redis://default:secret@red-abc123:6379/0")


def test_secure_redis_url_rejects_public_plaintext_and_local_defaults():
    assert not is_secure_redis_url("redis://cache.example.com:6379/0")
    assert not is_secure_redis_url("redis://localhost:6379/0")
    assert not is_secure_redis_url("redis://127.0.0.1:6379/0")
    assert not is_secure_redis_url("not-a-url")
