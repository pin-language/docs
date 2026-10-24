# 4. Functions

[Learn Pin](README.md) · previous: [3. Control flow](03-control-flow.md) · next: [5. Lists and maps](05-lists-and-maps.md)

## Declaring a function

Every parameter and the return value have a type. A function that returns nothing returns `void`.

```php
function vat(int $amount): float {
    return $amount * 0.07;
}

function show(string $label, float $value): void {
    echo $label, ": ", $value, "\n";
}

show("VAT on 200", vat(200));
```

Output:

```text
VAT on 200: 14
```

Functions can be declared anywhere in the file, before or after they are used.

## Types are checked at the call

<!-- check: error -->
```php
function double(int $n): int { return $n * 2; }
echo double("4");
```

Error:

```text
example.pn:2: error: argument of double(): expected int but got string
```

## Every path must return

<!-- check: error -->
```php
function grade(int $score): string {
    if ($score >= 50) { return "pass"; }
}
echo grade(70);
```

Error:

```text
example.pn:1: error: grade() can reach its end without returning a string. Add a return at the end (or in every branch)
```

```php
function grade(int $score): string {
    if ($score >= 50) { return "pass"; }
    return "fail";
}
echo grade(70), " ", grade(20), "\n";
```

Output:

```text
pass fail
```

## Recursion

```php
function factorial(int $n): int {
    if ($n <= 1) { return 1; }
    return $n * factorial($n - 1);
}
echo factorial(10), "\n";
```

Output:

```text
3628800
```

## No globals

A function only sees its parameters. Variables at the top of the file are not visible inside functions —
pass what the function needs. (This is also why Pin's web server can run on every CPU core without locks.)

<!-- check: error -->
```php
$rate = 7;
function tax(int $amount): int {
    return intdiv($amount * $rate, 100);
}
```

Error:

```text
example.pn:3: error: variable $rate is used before it is assigned
```

```php
function tax(int $amount, int $rate): int {
    return intdiv($amount * $rate, 100);
}
$rate = 7;
echo tax(1000, $rate), "\n";
```

Output:

```text
70
```

## What is not there (yet)

Default parameter values, named arguments, variadic `...$args`, closures (`function () {}`, `fn() =>`) and
classes. Write named functions and pass every argument.

## Try it

Write `money(int $satang): string` that turns `123450` into `"1234.50"` (100 satang = 1 baht).

<details><summary>One answer</summary>

```php
function money(int $satang): string {
    $baht = intdiv($satang, 100);
    $rest = $satang % 100;
    return $baht . "." . ($rest < 10 ? "0" . $rest : strval($rest));
}
echo money(123450), " ", money(5), " ", money(100), "\n";
```

Output:

```text
1234.50 0.05 1.00
```

</details>
