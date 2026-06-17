"""Tests for practice problem generator."""

from investormate.education.practice import generate


class TestPractice:
    def test_generate_tvm_reproducible(self):
        p1 = generate("tvm", "easy", seed=42)
        p2 = generate("tvm", "easy", seed=42)
        assert p1["answer"] == p2["answer"]
        assert "question" in p1
        assert "solution_steps" in p1

    def test_generate_bonds(self):
        p = generate("bonds", "medium", seed=1)
        assert p["topic"] == "bonds"
        assert p["answer"] > 0

    def test_generate_options(self):
        p = generate("options", "medium", seed=1)
        assert p["topic"] == "options"
        assert p["answer"] >= 0
