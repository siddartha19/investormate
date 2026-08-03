"""Allow ``python -m investormate`` to invoke the CLI."""

from .cli import main

raise SystemExit(main())
