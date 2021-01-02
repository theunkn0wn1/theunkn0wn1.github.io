# cat some_project/__main__.py
# `project_root` is the top-level package available for import, not `some_package` or `foo`!
from some_project.some_package import bar
import some_project.foo

print("successfully imported all the things!")
