# 6. Strings

[Learn Pin](README.md) · previous: [5. Lists and maps](05-lists-and-maps.md) · next: [7. Ownership](07-ownership.md)

Strings work much like PHP. Every function used here is in the [string reference](../reference/strings.md).

## Building strings

```php
$name = "Mint";
$s = "Hello, ";
$s .= $name;                    // append
$s .= "!";
echo $s, " (", strlen($s), " bytes)\n";
echo str_repeat("-", 10), "\n";
```

Output:

```text
Hello, Mint! (12 bytes)
----------
```

## Searching and cutting

```php
$path = "/users/42/orders";
echo strpos($path, "42"), " ", strpos($path, "x"), "\n";       // -1 when not found
echo substr($path, 7, 2), " ", substr($path, -6), "\n";
echo str_starts_with($path, "/users/") ? "user url" : "other", "\n";
echo strtoupper("tea"), " [", trim("  padded  "), "]\n";
```

Output:

```text
7 -1
42 orders
user url
TEA [padded]
```

`strpos` returns `-1` when there is no match (PHP returns `false`), so test with `< 0`.

## Splitting and joining

`explode` splits into a `list<string>`; `implode` joins a list back together.

```php
$csv = "tea,cake,,coffee";
$parts = explode(",", $csv);
echo count($parts), " parts\n";
list<string> $kept = [];
foreach ($parts as $p) {
    if (strlen($p) > 0) { $kept[] = strtoupper($p); }
}
echo implode(" | ", $kept), "\n";
```

Output:

```text
4 parts
TEA | CAKE | COFFEE
```

## Thai text and bytes

Pin strings are always valid UTF-8. Thai characters take 3 bytes each, so `strlen` and `substr` count bytes,
like PHP; the `mb_*` functions count characters (code points), and the `grapheme_*` functions count what a
reader sees — a Thai letter with its vowel and tone mark is one:

```php
$word = "ที่นี่";
echo strlen($word), " ", mb_strlen($word), " ", grapheme_strlen($word), "\n";
echo substr($word, 0, 3), " ", mb_substr($word, 0, 2), " ", grapheme_substr($word, 0, 1), "\n";
```

Output:

```text
18 6 2
ท ที ที่
```

To shorten text for display use `grapheme_substr()`: `mb_substr()` can leave a tone mark behind. A `substr()`
whose offset falls inside a character panics instead of returning broken text, so cut at offsets you got from
`strpos` or from known ASCII text. For names and emails people type, `normalizer_normalize($s,
Normalizer::FORM_KC)` makes look-alike spellings equal before you store or compare them.

## Numbers inside text

```php
$line = "qty=3 price=12.50";
$qty = intval(substr($line, strpos($line, "=") + 1));
$price = floatval(substr($line, strpos($line, "price=") + 6));
echo $qty * $price, "\n";
```

Output:

```text
37.5
```

## Try it

Turn `"  Mint,  Ann ,beam "` into `"Ann, Mint, beam"`: split on commas, trim each name, sort, join.

<details><summary>One answer</summary>

```php
$raw = "  Mint,  Ann ,beam ";
list<string> $names = [];
foreach (explode(",", $raw) as $n) { $names[] = trim($n); }
sort($names);
echo implode(", ", $names), "\n";
```

Output:

```text
Ann, Mint, beam
```

</details>
