# 1. Your first program

[Learn Pin](README.md) · next: [2. Values and types](02-values-and-types.md)

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/pin-language/pin/HEAD/install.sh | sh
pin -v
```

The installer needs Python 3.10+ and clang and tells you how to get them if they are missing
(macOS: `xcode-select --install`, Ubuntu: `sudo apt install clang`).

## Hello

Make a file `hello.pn`:

```php
echo "Hello, world!\n";
```

Run it:

```bash
pin hello.pn
```

Output:

```text
Hello, world!
```

A Pin file is code from the first line — there is no `<?php` tag. `pin hello.pn` compiles the file to a
native program and runs it straight away.

## echo

`echo` prints one or more values separated by commas. `"\n"` is a new line.

```php
$name = "Pin";
echo "Hello, ", $name, "!\n";
echo "1 + 2 = ", 1 + 2, "\n";
echo "สวัสดี\n";
```

Output:

```text
Hello, Pin!
1 + 2 = 3
สวัสดี
```

## Comments

```php
// a line comment
# also a line comment
/* a block
   comment */
echo "comments are ignored\n";   // after code too
```

Output:

```text
comments are ignored
```

## The pin command

| command | what it does |
|---|---|
| `pin file.pn` | compile and run |
| `pin check file.pn` | only look for mistakes; nothing runs |
| `pin build file.pn -o app` | make a native program `app` you can copy and run without Pin |
| `pin -v` | the version |

`pin build` makes one self-contained file. Pin programs start in milliseconds and need no runtime
installed on the machine that runs them.

## When something is wrong

Pin checks your program before it runs. A mistake stops the build with the line number and what to do:

<!-- check: error -->
```php
echo "missing semicolon"
echo "next line";
```

Error:

```text
example.pn:2: error: expected ';' but found 'echo'
```

## Try it

Write `about.pn` that prints your name on one line and your city on the next.

<details><summary>One answer</summary>

```php
$name = "Somchai";
$city = "Bangkok";
echo $name, "\n", $city, "\n";
```

Output:

```text
Somchai
Bangkok
```

</details>
