---
layout: post
title:  "Compiling python3 from sources"
date:   2020-07-11 23:34:10 -0700
categories: "Python"
author: "Joshua Salzedo"
---


You want to build Python3 from sources. Whatever your reason, this guide should help.

This path has been tested on a RPi 4B, as well as an Ubuntu 18.04 workstation.

# Prerequisites
- This guide assumes a `linux` distribution, and has been written against Debian linux commands. Commands may vary for other distributions.
- This guide assumes you have the rights on the box to install dependencies.
- Basic development tools such as a text editor, a compiler, and git are previously installed.

# Step 1: retrieve the CPython source

To build CPython from sources, we naturally need to acquire the source code of the interpreter.

Replace `3.8` below with your desired python version.

### important note:: `--depth 1` is intentionally used here to create a shallow clone, as failing to do so results in an unnecessary large and lengthy download.

{% highlight bash %}
git clone https://github.com/python/cpython --depth 1 --branch 3.8
cd cpython
{% endhighlight %}

# Step 2: enable `deb-src` to retrieve build dependencies from the package manager
While the package manager couldn't provide a suitable python interpreter for us, it can provide the build dependencies for one!

For the following command to work, you need to enable at least one `deb-src` in your `/etc/apt/sources.list` file.
As far as I can tell, it doesn't matter which one is enabled(?).

To enable, simply remove the leading `#` comment for the relevant line. 

Example:
```
deb http://us.archive.ubuntu.com/ubuntu/ focal main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ focal restricted universe multiverse main #Added by software-properties
# deb-src http://us.archive.ubuntu.com/ubuntu/ bionic main restricted
```


# Step 3: fetch build dependencies
This step varies depending on the system's default python distribution, start from the python version your distribution officially supports and work backwards in point releases until one succeeds.
- For Ubuntu Focal (20.04 LTS), start with `python3.8` since that is what that distribution ships with its default `python3` binaries.

{% highlight bash %}
sudo apt update
sudo apt build-dep python3.8
{% endhighlight %}

As stated above, if that command doesn't work, try 3.7, then 3.6, then ... in the 3.x series.
Eventually one of them should succeed. The build dependencies for Python3.x don't appear to change much, so using the build-dependencies for an older version should be safe.

# Step 4: debug build
Python has several external dependencies that need to be installed before compiling, which we *should* have done in the previous step. This step is to double-check this.

Before building python in release (optimized) configuration, it's best to do a debug build first to ensure all the optional components get built.

The optimized build takes far longer to complete, so to save time it's best  to do at least one of these first.

{% highlight bash %}
./configure
make -j 4
{% endhighlight %}

- You can use more cores for a faster build (up to the total number of available cores) by adjusting the `-j n` flag.

Once the build completes, check the output for anything that looks like
```
Python build finished successfully!
The necessary bits to build these optional modules were not found:
_uuid
To find the necessary bits, look in setup.py in detect_modules() for the module's name.


The following modules found by detect_modules() in setup.py, have been
built by the Makefile instead, as configured by the Setup files:
_abc                  atexit                pwd
time
```

In this sample, the external uuid library wasn't found; this would result in the standard library `uuid` library being unavailable in the built interpreter.
If this list is not empty, you will need to figure out what dependencies you are missing and retrieve them.
Once retrieved, re-run Step 4.

# Step 5: the actual build
Now that the debug build's output has been verified, it's time to build the Python interpreter in release mode.
- This step may take a while, depending on the machine's capabilities.

{% highlight bash %}
./configure --enable-optimizations
make -j 4
{% endhighlight %}


# Step 6: Install

At this point, a fully functional interpreter now exists at `./python`.

All that remains is to install it.

To prevent overriding existing python interpreters, which may break things, it is recommended to use `altinstall`.

To give this installation a custom name / location, use the `--prefix flag`.

{% highlight bash %}
make altinstall
{% endhighlight %}
