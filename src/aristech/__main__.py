"""`python -m aristech` entry point; delegates to the CLI."""

from aristech.interface.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
