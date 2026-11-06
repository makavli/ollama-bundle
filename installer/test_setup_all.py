"""Tests for setup_all.py's configuration logic (no docker/systemd needed)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup_all  # noqa: E402


class TestOpenWebUICommand(unittest.TestCase):
    def test_uses_the_variable_openwebui_reads(self):
        cmd = setup_all.openwebui_command("open-webui", "3000", "http://host.docker.internal:11434", False)
        self.assertIn("OLLAMA_BASE_URL=http://host.docker.internal:11434", cmd)
        self.assertFalse(any(c.startswith("OLLAMA_BACKEND=") for c in cmd))

    def test_bridged_maps_the_port(self):
        cmd = setup_all.openwebui_command("open-webui", "3000", "x", False)
        self.assertIn("3000:8080", cmd)
        self.assertNotIn("host", cmd[cmd.index("--name") + 2:])  # no --network host

    def test_host_network_sets_port_env(self):
        cmd = setup_all.openwebui_command("open-webui", "3000", "http://127.0.0.1:11434", True)
        self.assertEqual(cmd[cmd.index("--network") + 1], "host")
        self.assertIn("PORT=3000", cmd)
        self.assertNotIn("-p", cmd)

    def test_data_volume_is_kept(self):
        cmd = setup_all.openwebui_command("open-webui", "3000", "x", False)
        self.assertIn("open-webui:/app/backend/data", cmd)


class TestArgs(unittest.TestCase):
    def test_override_is_kept_by_default(self):
        self.assertFalse(setup_all.parse_args([]).reset_ollama_override)

    def test_models_positional(self):
        self.assertEqual(setup_all.parse_args(["llama3:latest"]).models, ["llama3:latest"])


if __name__ == "__main__":
    unittest.main()
