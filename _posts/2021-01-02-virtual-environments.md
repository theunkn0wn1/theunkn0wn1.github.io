---
layout: post
title:  "Virtual Environments"
date:   2021-01-02 16:30:00 -0800
categories: 
    - "python"
author: "Joshua Salzedo"
---
`Virtual Environments` Are how Python developers maintain dependency isolation between projects.

This post aims to explain what they are, how to create them, and how they can be used.

- Note: while there are third-party libraries that wrap the standard-library component that can make it easier to handle virtual environments, this post will focus on the standard-library route.

# Definitions
An `Environment` in Python specifically refers to the Python interpreter a project uses, as well as some of its configuration.

An `System Interpreter` is a Python interpreter that is installed system-wide, typically via the Operating System's (OS) package manager.

An `Virtual Environment` is an Isolated clone of a System Interpreter, typically associated with a single `Project`.

`venv` is an alias for `Virtual Environment`.

A `dependency` is any library a `Project` depends on, and is provided externally.
 - This term typically refers to third-party libraries installed via `pip` or similar.

A `Project` typically refers to some specific library or program that a developer is working on.

`OS`  = `Operating System`

# Why should I care about `Virtual Environments`?
Virtual Environments provide multiple benefits, and are also best practice. 
 - They provide dependency isolation
 - They (can) ensure a clean working environment, that is easy to [tear down](#destroying-a-virtual-environment) and [rebuild](#creation-of-a-virtual-environment)
 - It removes direct dependency on a system interpreter, and all the asterisks attached to it.
 - Venvs don't require elevated rights to install packages within.

## Dependency isolation
In Python, any package that is installed to the interpreter is available to all code running within that interpreter.

Python does not differentiate between projects, nor does it inherently understand
a project's dependencies.

In software development, its not uncommon to be working on multiple projects on the same machine,
each with different dependencies. Further it is not uncommon for one project's dependencies to be incompatible with another.  Some examples:
 - Maintaining legacy python 2.7 Flask server while also writing its >=3.5 migration.
 - Maintaining a relatively current python3 library while developing the next version of it, where this next version upgrades dependencies in a way that breaks the old version.
 - Investigating a reported bug / regression by selecting specific dependency versions

In all these cases, sharing the same environment is not necessarily the best idea.

Dependency Isolation would go a long way to resolving common development headaches.

Virtual Environments provide Dependency Isolation, as packages installed 
within one Virtual Environment are **not installed or available** on other
Virtual Environments or the System Interpreter.


## Creation of a virtual environment
Python includes the [`venv`](https://docs.python.org/3/library/venv.html) built-in library to handle the creation of virtual environments.
 - Note: System Interpreters on Linux OSes tend not to ship this module by default, you may need to manually install this.
 - On Debian-based systems this can be achieved via `apt install python3-venv`

The creation of a virtual environment can be achieved by invoking this venv package, passing it the path in which to generate the virtual environment in.

```shell
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:25:39
$ python3 --version
Python 3.6.9

~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:25:42
$ python3 -m venv python_3.6_venv

~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:25:48
$ ls
grpc_python  python_3.6_venv  some_project


```

## Activation of a virtual environment
The creation of a virtual environment is straight-forward, as is activating it.

To use a virtual environment, it must first be activated.

On linux OSes, this can typically be achieved via
```shell
source /path/to/venv/bin/activate
```
For example,
```shell
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:51:27
$ which python3
/usr/bin/python3

~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:51:29
$ source python_3.6_venv/bin/activate

(python_3.6_venv) 
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:51:32
$ which python3
/home/orion/projects/theunkn0wn1.github.io/code/python_3.6_venv/bin/python3

```

On Microsoft Windows, the process is similar but not quite the same.
```shell
./venv/scripts/activate
```
 - With powershell, you may be prompted to enable scripts for this command to work.

Activating a virtual environment temporarily patches the `PYTHONPATH` and some other important python environment variables,
such that all references to `python` and its aliases point into the virtual environment.

Activation also means all imports will look into the virtual environment's installed packages instead of the system interpreter.

## Usage of the virtual environment
The virtual environment, for all intents and purposes, is logically equivalent to the system interpreter it was derived from.

This means the usage of a virtual environment is logically identical to that of the system interpreter.

```shell
(python_3.6_venv) 
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 11:56:42
$ pip install attrs
#<snip for brevity>
Successfully installed attrs-20.3.0
```

## Deactivating a virtual environment
the activation of a virtual environment provides an extra command, `deactivate`.
This command undoes the environment modifications done by activation.

```shell
(python_3.6_venv) 
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 12:00:53
$ which python3
/home/orion/projects/theunkn0wn1.github.io/code/python_3.6_venv/bin/python3

(python_3.6_venv) 
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 12:00:57
$ which python
/home/orion/projects/theunkn0wn1.github.io/code/python_3.6_venv/bin/python

(python_3.6_venv) 
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 12:01:00
$ deactivate

~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 12:01:01
$ which python
/usr/bin/python

~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 12:01:03
$ which python3
/usr/bin/python3

```

## Destroying a virtual environment
Destroying a virtual environment is as straight-forward as creating one: Delete the generated virtual environment folder.

Doing so will remove the virtual environment as well as anything installed within it.
```shell
~/projects/theunkn0wn1.github.io/code on  python_venvs! ⌚ 12:01:04
$ rm -r python_3.6_venv 

```
 - Note: doing the same with a System Interpreter is not advisable, due to its entanglements with the OS.

# Notes about Virtual Environments, version control, and deployment.
- Treat a virtual environment as a generated directory. 

- Best practice is not to commit generated files and directories to version control.
  
- Virtual Environments are not portable. 
  
- It is also best to avoid deploying virtual environments, since they are not portable.
Instead, it is better to create  a virtual environment in the deployment environment and build it to meet the project's deployment requirements.
