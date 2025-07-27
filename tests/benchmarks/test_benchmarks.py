import subprocess
import sys
from pathlib import Path


def test_benchmark_scripts(tmp_path):
    scripts = [
        "benchmark_large_pst.py",
        "benchmark_index_growth.py",
    ]
    try:
        import pypff  # type: ignore
        scripts.append("profile_run.py")
    except Exception:
        pass
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[2])}
    for script in scripts:
        out = tmp_path / f"{script}.out"
        cmd = [sys.executable, str(Path(__file__).with_name(script)), "--out", str(out)]
        if script == "profile_run.py":
            dummy_pst = tmp_path / "dummy.pst"
            dummy_pst.write_text("dummy")
            cmd = [sys.executable, str(Path(__file__).with_name(script)), str(dummy_pst), "--output", str(out)]
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        assert res.returncode == 0
        assert out.exists()
