from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "repo-visuals" / "scripts"


class RepoVisualsScriptsTest(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_end_to_end_dimensions_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "sample-project"
            repo.mkdir()
            (repo / "README.md").write_text(
                "# Prism Forge\n\nGenerate exact launch visuals without asking an image model to spell.\n",
                encoding="utf-8",
            )
            (repo / "package.json").write_text(
                json.dumps(
                    {
                        "name": "prism-forge",
                        "version": "1.2.3",
                        "description": "Generate exact launch visuals for open-source projects.",
                    }
                ),
                encoding="utf-8",
            )
            (repo / "index.ts").write_text("export const ready = true;\n", encoding="utf-8")

            output = temp / "output"
            manifest_path = output / "manifest.json"
            self.run_script(
                "inspect_repo.py",
                str(repo),
                "--out",
                str(manifest_path),
                "--repository-url",
                "https://github.com/example/prism-forge",
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["project"]["name"], "prism-forge")
            self.assertEqual(manifest["project"]["release"], "1.2.3")
            self.assertIn("TypeScript", manifest["project"]["tech_stack"])
            self.assertIn("No text", manifest["image_prompt"]["constraints"])

            background = temp / "background.png"
            Image.new("RGB", (1536, 1024), "#312E81").save(background)
            self.run_script(
                "compose_visual.py",
                "--manifest",
                str(manifest_path),
                "--background",
                str(background),
                "--out-dir",
                str(output),
            )

            expected = {
                "readme-hero.png": (1600, 900),
                "github-social.jpg": (1280, 640),
                "release-card.png": (1200, 675),
            }
            for filename, size in expected.items():
                path = output / filename
                self.assertTrue(path.exists())
                with Image.open(path) as image:
                    self.assertEqual(image.size, size)
            self.assertLess((output / "github-social.jpg").stat().st_size, 1_000_000)

            contact_sheet = output / "contact-sheet.png"
            self.run_script(
                "build_contact_sheet.py",
                "--input-dir",
                str(output),
                "--out",
                str(contact_sheet),
            )
            with Image.open(contact_sheet) as image:
                self.assertEqual(image.size, (1600, 1086))


if __name__ == "__main__":
    unittest.main()
