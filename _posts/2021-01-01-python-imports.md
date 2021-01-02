---
layout: post
title:  "Python imports"
date:   2021-01-01 16:30:00 -0800
categories: 
    - "python"
author: "Joshua Salzedo"
---
Python's import system can be a tad confusing, this post aims to help clarify how it works.

For the sake of simplicity, this post will *not* go into the inner-machinations of the import system,
but rather the practical aspect of using it.

This document also assumes a modern (>= python3.5) python version, 
though most of this information also applies to EOL `python2`. For specific considerations, 
please see [the Dead Snakes consideration](#considerations-for-dead-snakes).


# Definitions
Lets start with some definitions:
- A `module` is a `.py` source file. 
- A `package` is a directory that contains one or more `.py` modules, and optionally other packages.
    - All modules and packages in the package's directory are members of that package.
    - Note: in older python versions, a package **must** contain a `__init__.py` file; while this isn't a requirement in modern python, its a good idea to include it anyways even if its blank. More on this later.

Both a `module` and a `package` are `importable` by name.

The name of an `importable` object depends on where it exists on the `PYTHONPATH` environment variable.
More on this [Below](#the-pythonpath)
# Basic usage
An `import` allows one module to access the contents of another module or package. For example
```python
import pathlib
```
This statement brings the standard library [`pathlib`](https://docs.python.org/3/library/pathlib.html) package into scope, and binds it to the name `pathlib`.
 - By default, the name of the imported object will be the same as the source, unless specifically specified otherwise.

## Renaming imports
```python
import pathlib as path
```
This statement imports the same module as before, but binds it to the name `path`.
- It can sometimes be useful to rename symbols as they are imported, as to prevent conflicts with other names in the module.


## Importing specific things from a module or package
It can also be useful to import specific names from a module or package.
```python
from pathlib import Path
```
This will import the `Path` name from `pathlib` and bind it to the name `Path`.
 - import renaming syntax also can apply here, as previously shown. 

### Importing multiple specific things from a package
An import can include multiple things in one go, this can be useful when selecting a subset of names from a package.
```python
from io import BytesIO, StringIO
```
This code fragment imports the names `BytesIO` and `StringIO` from the stdlib [`io`](https://docs.python.org/3/library/io.html) package.


# The `PYTHONPATH`
Now that basic usage of imports has been established, its important to talk about how imports work.

There are various environment variables that python uses to regulate its behaviors, the `PYTHONPATH` is one of them.

Specifically, the `PYTHONPATH` is used by the import machinery to specify the OS directories it should look in while importing modules.

By default, the `PYTHONPATH` points at some standard directories (such as those packages installed via `pip` end up, as well as those installed as part of the interpreter itself), as well as the directory `__main__` lives in.

Any module or package at the same OS file-system level as entries in the `PYTHONPATH` will be directly importable.

Here is an example file structure
```
/project_root/
/project_root/__main__.py
/project_root/foo.py
/project_root/some_package/
/project_root/some_package/__init__.py
/project_root/some_package/bar.py
```

In this file structure, `/root_project` would be added to the end of the `PYTHONPATH` if `__main__.py` were to be directly executed.

This means that `foo.py` and `some_package` are directly importable however `some_package/bar.py` is not.

The `bar.py` is still importable, as it's a member of the `some_package` package, its name would be `some_package.bar`.

- Packages and modules possess absolute paths that are anchored to the `PYTHONPATH`.


## How the way in which running python effects the `PYTHONPATH`
If you run a script directly, the path that script file lives in would be appended to the `PYTHONPATH`.
Using the above file structure, Give some content to `__main__.py`.
```python
# cat /project_root/__main__.py 
from some_package import bar
import foo

print("successfully imported all the things!")

```
If `__main__.py` were to be directly executed, it would succeed as both `foo` and `some_package` are present on the one of the directories on the `PYTHONPATH`. 
```shell
root@d04358033ae8:/# python3 /project_root/__main__.py 
successfully imported all the things!
root@d04358033ae8:/# 
```

However, the same would not be true if `__main__` were to be indirectly executed by a script launched from a different directory.
```python
root@d04358033ae8:/# python3
Python 3.9.1 (default, Dec 12 2020, 13:15:12) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import project_root.__main__
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/project_root/__main__.py", line 1, in <module>
    from some_package import bar
ModuleNotFoundError: No module named 'some_package'

```
 - The reason this occurs is `/` is added to the `PYTHONPATH` and not `/project_root`

# Absolute imports: Direct module execution
In modern Python, all imports are absolute, anchored to the directories in `PYTHONPATH`.

Here is an example file structure:
```
root@d04358033ae8:/project_root# tree
.
├── __init__.py
├── __main__.py
├── foo.py
├── some_other_package
│   ├── __init__.py
│   ├── carrot.py
│   └── some_nested_package
│       ├──  __init__.py
│       ├──  potato.py
│       └──  bob.py
└── some_package
    ├── __init__.py
    └── bar.py

```
If we assume `some_project/__main__.py` were to be executed directly, then both `some_package` and `some_other_package` are importable directly.

Accessing packages below them, such as `some_other_package/some_nested_package` would be to import members of packages directly accessible.
```python
from some_other_package import some_nested_package
# or, for a specific member
from some_other_package.some_nested_package import bob
```

# Relative imports
Absolute imports are fine, but in large applications it can often be beneficial have a viable shorthand.

Luckily relative imports are a thing, and can save some typing.

Using the above structure, the following will demonstrate how to perform relative imports
```python
# /project_root/some_other_package/some_nested_package/potato.py
from . import bob  # import the bob package, which also lives in `some_other_package.some_nested_package`
# similarly, importing a single name,
from .bob import Bob

# One can also import stuff from parent packages, as long as they are in the same root package
from ..carrot import Carrot
```
- `.` refers to the module's immediate parent package.
- `..` Refers to the package one level up (GrandParent)

The pattern goes on, each added `.` goes one level higher, right up until you reach `__main__`.
- Note: Relative imports from `__main__.py` are disallowed when running that file directly, as `__main__.py` is not a package or a child of one.

# Importing directories above `__main__`
The short answer is this is not possible. Please consider refactoring the project as to avoid this scenario.

## The long answer
It is technically possible, by resorting to magic. 

As imports are anchored by the `PYTHONPATH`, logically accessing packages above `__main__` 
can be achieved by extending the `PYTHONPATH` at runtime via `sys.path`.
- This is bad practice, and can lead to brittle code and significant technical debt.


# Executing a package as an executable
Running a python file directly is only one mode of executing python, and is better suited to small scripts that only import from other, installed packages.

For larger applications, it can be beneficial for the project root to, itself, be importable as a package.

One such example is `pip`, the Python Package Installer, which runs under the `pip` package.
```shell
python3 -m pip install --upgrade pip
```
This command executes `pip` as a package, passing it the cli arguments `install --upgrade pip` (update the package installer using itself.)

The `-m` argument accepts the *absolute* name of a package to execute, which is located on the `PYTHONPATH`. (The `PYTHONPATH` is extended with the Current Working Directory (CWD))

 - Note, `-m pip` will execute `pip.__main__` by default, but a specific module may be specified.

For the above file structure, an example invocation would be
```shell
python3 -m project_root
```
 - This example won't run until the fixes described in the next section are applied!

## Absolute imports: inside a package

When executing a project as a package, the package itself is available as a top-level import; instead of the project's root directory being extended onto the `PYTHONPATH`.

To adapt the above `__main__.py` to work in this scenario,
```python
# cat project_root/__main__.py 

# `project_root` is the top-level package available for import, not `some_package` or `foo`!
from project_root.some_package import bar
import project_root.foo

print("successfully imported all the things!")

```
Example invocation:
```shell
root@d04358033ae8:/# python -m project_root
successfully imported all the things!

```

# How installing a package effects how its imported
When you install a package via `pip`, the top-level package is placed in one of the standard directories of the `PYTHONPATH`, and is importable under that package's name.

For the above examples, `project_root` would be what can be imported, once the `project_root` is installed.

This also means that `project_root` is accessible from anywhere, since it will always live on that interpreter's `PYTHONPATH` it can be discovered.




# Considerations for dead snakes
This chapter has some information specific to **End of Life** python2 as it relates to imports, and is offered in the hopes 
it maybe found useful.
No guarantees are offered for completeness. 


## Relative imports
In `python2`, all imports are *relative* to the current module, instead of absolute to the `PYTHONPATH`.

To ease the transition to python3, 
please consider including the following [`__future__`](https://docs.python.org/3/library/__future__.html) directive
, which opts-into the python3 import behavior. 
```python
from __future__ import absolute_import  # as of python2.5.0a1
```

# `__init__.py`
Packages are, themselves, importable. a package's `__init__.py` defines what gets imported in this scenario.

Using the above file structure, `/project_root/some_package/__init__.py` is what is imported when the interpreter executes
```python
import some_package
```

This module may be blank, or it may contain executable python code like any other module.

A common use for this file is to provide a public interface for a package, re-exporting names from the package's members.


# Questions, comments, concerns?
Python's import system can be confusing at times, and Ive done what I can to explain it as clearly as possible but undoubtedly there is room for improvement.

Feel free to leave questions, comments, suggestions,  or your concerns on this blog's [Github repository](https://github.com/theunkn0wn1/theunkn0wn1.github.io)
