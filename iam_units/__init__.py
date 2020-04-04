from pathlib import Path

import pint

registry = pint.UnitRegistry()
registry.load_definitions(
    str(Path(__file__).parent / 'data' / 'definitions.txt'))
