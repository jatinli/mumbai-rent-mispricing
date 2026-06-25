"""Tests for the map legend's data-source caption.

The legend used to hardcode "ALL DATA SYNTHETIC" regardless of what data
actually built the map — a real-data map would have falsely claimed to be
synthetic. The caption must be derived from the `source` column instead.
"""

from __future__ import annotations

import pandas as pd

from rentlens.viz.map import _data_source_caption


def test_synthetic_source_caption():
    df = pd.DataFrame({"source": ["SYNTHETIC_GENERATED"] * 3})
    assert "SYNTHETIC" in _data_source_caption(df)
    assert "v0.1" in _data_source_caption(df)


def test_real_source_caption_names_the_source():
    df = pd.DataFrame({"source": ["MAGICBRICKS"] * 3})
    caption = _data_source_caption(df)
    assert "REAL DATA" in caption
    assert "MAGICBRICKS" in caption
    assert "SYNTHETIC" not in caption


def test_mixed_real_sources_lists_all():
    df = pd.DataFrame({"source": ["MAGICBRICKS", "NOBROKER"]})
    caption = _data_source_caption(df)
    assert "MAGICBRICKS" in caption
    assert "NOBROKER" in caption
