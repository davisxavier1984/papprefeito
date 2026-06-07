"""Permite `python -m SIAPS ...`."""

import sys

from .baixa_siaps import main

if __name__ == "__main__":
    sys.exit(main())
