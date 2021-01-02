# /project_root/some_other_package/some_nested_package/potato.py
from . import (
    bob,
)  # import the bob package, which also lives in `some_other_package.some_nested_package`

# similarly, importing a single name,
from .bob import Bob

# One can also import stuff from parent packages, as long as they are in the same root package
from ..carrot import Carrot
