import unittest
from pathlib import Path


class Export(unittest.TestCase):


    def test_export_py(self):
        export_file = Path(__file__).parent / "exported_code.py"
        root_dir = Path(__file__).parent.parent/"packages"
        files = list(root_dir.glob("**/*.py"))

        # Attach to export file
        for file in files:
            if file.name == "exported_code.py":
                continue
            with open(file, "r") as f:
                content = f.read()
            with open(export_file, "a") as ef:
                ef.write(f"# From {file}\n")
                ef.write(content)
                ef.write("\n\n")


    def test_export_tom(self):
        export_file = Path(__file__).parent / "exported_toml.toml"
        root_dir = Path(__file__).parent.parent/"packages"
        files = list(root_dir.glob("**/*.toml"))

        # Attach to export file
        for file in files:
            if file.name == "exported_toml.toml":
                continue
            with open(file, "r") as f:
                content = f.read()
            with open(export_file, "a") as ef:
                ef.write(f"# From {file}\n")
                ef.write(content)
                ef.write("\n\n")






