import argparse
import unittest
from pathlib import Path



def export_filestructure(args: argparse.Namespace) -> None:
    export_file = Path(__file__).parent / "exported_file_structure.txt"
    root_dir = Path(args.root)
    files = list(root_dir.glob("**/*.py"))
    # Attach to export file
    for file in files:
        if file.name == "exported_code.py":
            continue
        with open(file, "r") as f:
            content = f"{str(file)}\n"
        with open(export_file, "a") as ef:
            ef.write(content)

def export_py(args):
    export_file = Path(__file__).parent / "exported_code.py"
    root_dir = Path(args.root)
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


def export_toml(args):
    export_file = Path(__file__).parent / "exported_toml.toml"
    root_dir = Path(args.root)
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



def main() -> None:
    parser = argparse.ArgumentParser()
    root_dir = Path(__file__).parent.parent  / "packages"
    parser.add_argument("--root", default=root_dir)
    args = parser.parse_args()
    export_filestructure(args)
    export_py(args)
    export_toml(args)

if __name__ == "__main__":
    main()


