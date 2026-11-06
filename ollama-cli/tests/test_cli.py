"""Tests for the CLI and client. No Ollama server needed: HTTP is mocked."""

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "src"))

import client as client_mod  # noqa: E402
import ollama_vs_code as cli  # noqa: E402


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


class FakePipe(io.StringIO):
    def isatty(self):
        return False


class TestNormalizeUrl(unittest.TestCase):
    def test_forms(self):
        n = client_mod.normalize_url
        self.assertEqual(n(None), "http://localhost:11434")
        self.assertEqual(n("localhost"), "http://localhost:11434")
        self.assertEqual(n("gpu-box:1234"), "http://gpu-box:1234")
        self.assertEqual(n("0.0.0.0:11434"), "http://localhost:11434")   # Ollama's bind-address format
        self.assertEqual(n("https://ollama.example.com/"), "https://ollama.example.com:11434")
        self.assertEqual(n("http://10.0.0.5:11434"), "http://10.0.0.5:11434")


class TestReadInput(unittest.TestCase):
    def args(self, *argv):
        return cli.build_parser().parse_args(list(argv))

    def test_piped_code_is_used_even_though_examples_prompt_exists(self):
        # Regression: examples/prompt used to silently replace piped input.
        self.assertTrue((ROOT.parent / "examples" / "prompt").exists())
        code = cli.read_input(self.args("--explain"), stdin=FakePipe("print('mine')"))
        self.assertEqual(code, "print('mine')")

    def test_positional_prompt_wins_over_stdin(self):
        self.assertEqual(cli.read_input(self.args("hello"), stdin=FakePipe("ignored")), "hello")

    def test_prompt_file_wins(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("from file")
        try:
            got = cli.read_input(self.args("-f", f.name, "positional"), stdin=FakePipe("x"))
            self.assertEqual(got, "from file")
        finally:
            os.unlink(f.name)

    def test_nothing_on_a_terminal(self):
        self.assertIsNone(cli.read_input(self.args("--explain"), stdin=FakeTTY()))


class TestSplitAnswerAndScript(unittest.TestCase):
    def test_json(self):
        out = json.dumps({"answer": "Here you go", "script": "#!/bin/bash\necho hi"})
        self.assertEqual(cli.split_answer_and_script(out), ("Here you go", "#!/bin/bash\necho hi"))

    def test_json_in_fence(self):
        out = "```json\n" + json.dumps({"answer": "a", "script": "echo 1"}) + "\n```"
        self.assertEqual(cli.split_answer_and_script(out), ("a", "echo 1"))

    def test_marker(self):
        self.assertEqual(cli.split_answer_and_script("Explanation\n===SCRIPT===\necho 2"),
                         ("Explanation", "echo 2"))

    def test_code_fence(self):
        answer, script = cli.split_answer_and_script("Try this:\n```bash\necho 3\n```\nDone.")
        self.assertEqual(script, "echo 3")
        self.assertIn("Try this:", answer)

    def test_plain_text_is_the_script(self):
        self.assertEqual(cli.split_answer_and_script("echo 4"), (None, "echo 4"))


def fake_response(status=200, payload=None, lines=None):
    r = mock.Mock()
    r.status_code = status
    r.json.return_value = payload or {}
    r.text = json.dumps(payload or {})
    r.iter_lines.return_value = [json.dumps(x).encode() for x in (lines or [])]
    return r


class TestClient(unittest.TestCase):
    def test_streaming_collects_all_chunks(self):
        lines = [{"response": "Hel"}, {"response": "lo"}, {"response": "", "done": True}]
        with mock.patch("requests.request", return_value=fake_response(lines=lines)), \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(client_mod.OllamaClient().generate("x", stream=True), "Hello")

    def test_unknown_model_raises_a_clear_error(self):
        resp = fake_response(404, {"error": "model 'nope' not found"})
        with mock.patch("requests.request", return_value=resp):
            with self.assertRaisesRegex(client_mod.OllamaError, "not found"):
                client_mod.OllamaClient().generate("x", model="nope")

    def test_requests_have_timeouts(self):
        with mock.patch("requests.request", return_value=fake_response(payload={"response": "ok"})) as req:
            client_mod.OllamaClient().generate("x")
        self.assertIn("timeout", req.call_args.kwargs)


class TestMain(unittest.TestCase):
    def run_main(self, argv, stdin=""):
        stub = mock.Mock()
        stub.check_connection.return_value = True
        stub.base_url = "http://localhost:11434"
        stub.generate.return_value = "```bash\n#!/bin/bash\necho generated\n```"
        with mock.patch.object(cli, "OllamaClient", return_value=stub), \
                mock.patch("sys.stdin", FakePipe(stdin)), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            code = cli.main(argv)
        return code, stub, out.getvalue()

    def test_fix_and_tests_respect_model(self):
        # Regression: --fix and --tests used to ignore --model.
        _, stub, _ = self.run_main(["--fix", "--model", "llama3", "--error", "boom"], stdin="x=1")
        stub.fix_code.assert_called_once_with("x=1", "boom", model="llama3")
        _, stub, _ = self.run_main(["--tests", "--model", "llama3"], stdin="x=1")
        stub.write_tests.assert_called_once_with("x=1", model="llama3")

    def test_explain_uses_piped_code(self):
        _, stub, _ = self.run_main(["--explain"], stdin="def f(): pass")
        stub.explain_code.assert_called_once_with("def f(): pass", model=cli.DEFAULT_MODEL)

    def test_write_file_with_positional_prompt_writes_the_file(self):
        # Regression: this used to fall into chat mode and never write anything.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out" / "gen.sh"
            code, stub, out = self.run_main(["--write-file", str(target), "make a script"])
            self.assertEqual(code, 0)
            stub.generate.assert_called_once()
            self.assertEqual(stub.generate.call_args.args[0], "make a script")
            self.assertEqual(target.read_text(encoding="utf-8"), "#!/bin/bash\necho generated")
            stub.chat.assert_not_called()

    def test_no_connection_exits_nonzero(self):
        stub = mock.Mock()
        stub.check_connection.return_value = False
        stub.base_url = "http://localhost:11434"
        with mock.patch.object(cli, "OllamaClient", return_value=stub), \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(["--list"]), 1)


if __name__ == "__main__":
    unittest.main()
