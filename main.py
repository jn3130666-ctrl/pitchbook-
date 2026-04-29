#!/usr/bin/env python3
"""VC/PE Weekly Pipeline — orchestrates the full flow."""

import os
import subprocess
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Ensure subprocesses use UTF-8 output (critical on Windows with Chinese text)
_base_env = os.environ.copy()
_base_env.setdefault("PYTHONIOENCODING", "utf-8")

STEPS = [
    ("fetch_emails",     "Fetching emails from IMAP..."),
    ("download_reports", "Downloading report attachments..."),
    ("analyze",          "Analyzing emails via DeepSeek API..."),
    ("generate_report",  "Generating weekly markdown report..."),
]


def run():
    total = len(STEPS)
    for i, (module, desc) in enumerate(STEPS, 1):
        print(f"\n{'='*60}")
        print(f"Step {i}/{total}: {desc}")
        print(f"{'='*60}")

        t0 = time.time()
        result = subprocess.run(
            [sys.executable, f"{module}.py"],
            env=_base_env,
            capture_output=False,
        )
        elapsed = time.time() - t0

        if result.returncode != 0:
            print(f"\n[ERROR] Step {i} failed (exit code {result.returncode}).")
            sys.exit(result.returncode)
        else:
            print(f"[OK] Step {i} completed in {elapsed:.1f}s")

    print(f"\n{'='*60}")
    print("Pipeline completed successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    run()
