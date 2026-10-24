# 2. Values and types

[Learn Pin](README.md) · previous: [1. Your first program](01-first-program.md) · next: [3. Control flow](03-control-flow.md)

## The basic types

| type | examples |
|---|---|
| `int` | `42`, `-7`, `PHP_INT_MAX` |
| `float` | `3.14`, `2.0`, `1.5e3` |
| `bool` | `true`, `false` |
| `string` | `"text"`, `'raw text'` |

```php
$age = 30;          // int
$price = 49.5;      // float
$open = true;       // bool
$shop = "PinaTo";   // string
echo $shop, " ", $age, " ", $price, "\n";
```

Output:

```text
PinaTo 30 49.5
```

## A variable keeps one type

A variable gets its type from the first value you give it, and keeps it. This is the biggest change from
PHP, and it is what lets Pin compile to fast native code.

<!-- check: error -->
```php
$count = 10;
$count = "ten";
```

Error:

```text
example.pn:2: error: assigning to $count: expected int but got string
```

Use a new variable for a new kind of value, or convert: `$label = strval($count);`.

## Numbers

`+ - * %` work on ints and floats. `/` always gives a float, like PHP; `intdiv()` divides ints.

```php
echo 7 + 2, " ", 7 - 2, " ", 7 * 2, " ", 7 % 2, "\n";
echo 7 / 2, " ", intdiv(7, 2), "\n";
echo 10 / 4 * 2, "\n";
```

Output:

```text
9 5 14 1
3.5 3
5
```

Mixing an int and a float gives a float. Whole floats print without `.0`, like PHP.

## Strings

Join strings with `.`. Double quotes put variables inside the text; single quotes do not.

```php
$item = "coffee";
$qty = 2;
echo "You ordered " . $qty . " " . $item . "\n";
echo "You ordered $qty $item\n";
echo 'Single quotes keep $item as written', "\n";
echo "Braces help: {$item}s\n";
```

Output:

```text
You ordered 2 coffee
You ordered 2 coffee
Single quotes keep $item as written
Braces help: coffees
```

`+` does not join strings:

<!-- check: error -->
```php
echo "total: " + 5;
```

Error:

```text
example.pn:1: error: '+' cannot combine string and int (use . to join strings)
```

## Converting

```php
$text = "42";
$n = intval($text) + 1;
$f = floatval("2.5") * 2;
$s = strval(3.0) . "!";
echo $n, " ", $f, " ", $s, " ", (int)9.99, " ", (float)7 / 2, "\n";
```

Output:

```text
43 5 3! 9 3.5
```

`intval("abc")` is 0 and never fails; a number too big for an int becomes `PHP_INT_MAX`. See
[Conversions](../reference/conversions.md) for every rule.

## Booleans

Comparisons give a `bool`. `echo true` prints `1`, `echo false` prints nothing — like PHP.

```php
$a = 5;
echo $a > 3, "|", $a == 4, "|", $a != 4 && $a < 10, "\n";
```

Output:

```text
1||1
```

## Try it

A shop sells tea at 40 baht. Print the price of 3 teas with 7% VAT added, as a float.

<details><summary>One answer</summary>

```php
$price = 40;
$qty = 3;
$total = $price * $qty * 1.07;
echo "total: ", $total, " baht\n";
```

Output:

```text
total: 128.4 baht
```

</details>
