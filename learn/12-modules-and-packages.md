# 12. Modules and packages

[Learn Pin](README.md) · previous: [11. A database](11-database.md)

When a program grows, split it into files. Each `.pn` file is a **module**; `import` loads one, and you call
its functions as `module::function()`. Everything still compiles into one native binary.

## Two files

`prices.pn`, next to your main file:

<!-- check: file prices.pn -->
```php
export function price(string $item): int {
    return table()[$item] ?? -1;
}

export function menu(): list<string> {
    list<string> $out = [];
    foreach (table() as $name => $p) { $out[] = $name; }
    return $out;
}

function table(): map<string,int> {          // no export: only prices.pn can call it
    return ["tea" => 40, "cake" => 89];
}
```

The main file:

```php
import prices;

echo prices::price("tea"), " ", prices::price("pizza"), "\n";
echo implode(", ", prices::menu()), "\n";
```

Output:

```text
40 -1
tea, cake
```

`import prices;` reads `prices.pn` from the **project folder** — the folder of the main file you run. Run the
main file as usual (`pin main.pn`); Pin finds the imports itself.

## export

A function without `export` belongs to its file. Calling it from another file is an error that says how to
fix it:

<!-- check: error -->
```php
import prices;
echo prices::table()["tea"];
```

Error:

```text
example.pn:2: error: prices::table() is not exported. Add `export` before `function table` in prices.pn to let other files call it
```

Keep `export` for the functions other files need; everything else can change freely without breaking
them.

## Folders and aliases

`import util/text;` reads `util/text.pn` and calls it `text::`. Import paths always start at the project
folder, whichever file contains the `import`, so a file in `blog/` that needs `util/text.pn` also writes
`import util/text;` — no `../`. Pick a different name with `as`:

<!-- check: file util/text.pn -->
```php
export function shout(string $s): string {
    return strtoupper($s) . "!";
}
```

```php
import util/text as t;
echo t::shout("hello"), "\n";
```

Output:

```text
HELLO!
```

Function names only need to be unique within a file: `prices::total()` and a `total()` in your main file
never clash, because calls into other files always say which file.

## The rules

- An imported file may contain only functions and imports. Code outside functions runs only in the main
  file, so importing a module never does anything by itself.
- Imports cannot go round in a circle (`a` imports `b` imports `a`); Pin names the circle and you move the
  shared functions into a third file.
- Lists, maps and strings move between files exactly as within one file (chapter 7): a function returning
  a list hands it to the caller, and arguments are lent.
- Compile errors name the file they are in, e.g. `prices.pn:4: error: ...`.

## Packages

A package is a Git repository of Pin modules. Add one to your project with `pin get` and the version you
want (a tag, a branch or a commit):

```bash
pin get github.com/someone/strutil@v1.0.0
```

That downloads it and writes the exact commit and a SHA-256 of all its `.pn` files to `pin.lock` in the
current folder:

```text
github.com/someone/strutil v1.0.0 4f2c9e1d... sha256:9b1d...
```

Then import a module from it by its full path:

<!-- check: skip -->
```php
import github.com/someone/strutil/words;
echo words::greet("pin"), "\n";
```

- **Commit `pin.lock`.** Everyone who builds the project gets exactly the same code.
- **The hash is checked on every build.** If the package's code changes after you locked it — a tag moved,
  a cached file was edited — the build stops with `the code does not match pin.lock`. Run `pin get` again
  only if you trust the change.
- Packages are cached in `~/.cache/pin/pkg`; a clean machine downloads the locked commit by itself.
- Inside a package, import paths start at the package's own root folder. If a package needs another package,
  `pin get` that one too.
- If the build stops with `does not match pin.lock`, delete the package's folder in the cache (the message
  names it) to download the locked code again. Run `pin get` for a new version only after reading what
  changed.
- `PIN_CACHE` moves the cache; `PIN_GIT_BASE` downloads from another Git server or a local folder instead of
  `https://` (useful for private mirrors and tests).

There is no central registry: a package is wherever its Git repository is.

## Try it

Move `money()` from chapter 4 into `money.pn`, export it, and use it from a main file that prints
`money(123450)`.

<details><summary>One answer</summary>

<!-- check: file money.pn -->
```php
export function money(int $satang): string {
    $baht = intdiv($satang, 100);
    $rest = $satang % 100;
    return $baht . "." . ($rest < 10 ? "0" . $rest : strval($rest));
}
```

```php
import money;
echo money::money(123450), "\n";
```

Output:

```text
1234.50
```

</details>
