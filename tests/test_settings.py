import os
from pathlib import Path
import subprocess
import sys
from unittest import TestCase


class SecretConfigurationTests(TestCase):
    def test_startup_rejects_missing_secret_key(self):
        environment = os.environ.copy()
        environment.pop("DJANGO_SECRET_KEY", None)
        result = subprocess.run(
            [sys.executable, "manage.py", "check"],
            cwd=Path(__file__).resolve().parents[1],
            env=environment, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)
