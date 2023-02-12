import os
from pathlib import Path

__current_path = Path(os.path.dirname(os.path.realpath(__file__)))
resources_path = __current_path / "resources"
