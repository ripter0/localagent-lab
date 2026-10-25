import agent


def fake_gpu(monkeypatch, limit, model_max=262144):
    """Pretend the GPU fits any num_ctx up to `limit`; record every probe."""
    probes = []
    monkeypatch.setattr(agent, "model_max_ctx", lambda model: model_max)

    def fits(model, num_ctx):
        probes.append(num_ctx)
        return num_ctx <= limit

    monkeypatch.setattr(agent, "fits_on_gpu", fits)
    return probes


def test_finds_largest_step_that_fits(monkeypatch):
    probes = fake_gpu(monkeypatch, limit=100_000)
    assert agent.find_num_ctx("m") == 98304  # 12 * 8192
    assert len(probes) <= 7  # binary search, not 32 loads


def test_capped_at_model_max(monkeypatch):
    fake_gpu(monkeypatch, limit=10**9, model_max=32768)
    assert agent.find_num_ctx("m") == 32768


def test_nothing_fits_falls_back_to_one_step(monkeypatch):
    fake_gpu(monkeypatch, limit=0)
    assert agent.find_num_ctx("m") == agent.CTX_STEP


def test_cached_value_reused_if_it_still_fits(monkeypatch, tmp_path):
    cache = tmp_path / "num_ctx.json"
    cache.write_text('{"m": 65536}')
    monkeypatch.setattr(agent, "CTX_CACHE", cache)
    monkeypatch.delenv("AGENT_NUM_CTX", raising=False)
    probes = fake_gpu(monkeypatch, limit=100_000)
    assert agent.pick_num_ctx("m") == 65536
    assert probes == [65536]  # one check, no new search


def test_env_var_overrides(monkeypatch):
    monkeypatch.setenv("AGENT_NUM_CTX", "4096")
    assert agent.pick_num_ctx("m") == 4096


def test_clip_keeps_short_output(monkeypatch):
    monkeypatch.setattr(agent, "MAX_OUTPUT", 10)
    assert agent.clip("short") == "short"


def test_clip_marks_truncated_output(monkeypatch):
    monkeypatch.setattr(agent, "MAX_OUTPUT", 10)
    out = agent.clip("x" * 25)
    assert out.startswith("x" * 10)
    assert "[truncated: showed 10 of 25 characters]" in out
