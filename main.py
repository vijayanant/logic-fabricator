#!/usr/bin/env python
import sys


def main():
    """A shim for running the workbench from the project root."""
    # This allows us to run the workbench without installing the package
    sys.path.insert(0, 'src')
    from logic_fabricator.workbench import main as workbench_main
    workbench_main()

if __name__ == "__main__":
    main()
