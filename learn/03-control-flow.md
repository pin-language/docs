# 3. Control flow

[Learn Pin](README.md) · previous: [2. Values and types](02-values-and-types.md) · next: [4. Functions](04-functions.md)

## if, elseif, else

```php
$score = 72;
if ($score >= 80) {
    echo "A\n";
} elseif ($score >= 70) {
    echo "B\n";
} else {
    echo "C or below\n";
}
```

Output:

```text
B
```

Braces are always required.

## Conditions must be bool

PHP treats `0`, `""` and `[]` as false. Pin does not guess: write the comparison you mean.

<!-- check: error -->
```php
$items = 3;
if ($items) { echo "not empty\n"; }
```

Error:

```text
example.pn:2: error: condition must be bool but got int (write the comparison, e.g. $x != 0)
```

```php
$items = 3;
$name = "";
if ($items != 0 && strlen($name) == 0) { echo "items but no name\n"; }
```

Output:

```text
items but no name
```

Logic operators: `&&`, `||`, `!`. Comparisons: `== != < <= > >=` (and `===`, `!==`, which mean the same
here because values never change type).

## The ternary operator

```php
$stock = 0;
echo $stock > 0 ? "in stock" : "sold out", "\n";
```

Output:

```text
sold out
```

Both sides must have the same type: `$n > 0 ? "yes" : strval($n)`, not `... : $n`.

## for and while

```php
for ($i = 1; $i <= 3; $i++) {
    echo "round $i\n";
}
$n = 10;
while ($n > 1) {
    $n = intdiv($n, 2);
}
echo "n = $n\n";
```

Output:

```text
round 1
round 2
round 3
n = 1
```

## foreach

`foreach` walks a list (or a map — see [chapter 5](05-lists-and-maps.md)).

```php
$prices = [55, 40, 89];
$total = 0;
foreach ($prices as $i => $p) {
    echo "item $i costs $p\n";
    $total += $p;
}
echo "total $total\n";
```

Output:

```text
item 0 costs 55
item 1 costs 40
item 2 costs 89
total 184
```

## break and continue

```php
for ($i = 1; $i <= 10; $i++) {
    if ($i % 2 == 0) { continue; }     // skip even numbers
    if ($i > 7) { break; }             // stop the loop
    echo $i, " ";
}
echo "\n";
```

Output:

```text
1 3 5 7 
```

## A variable must have a value on every path

Pin follows every path through your code. A variable set only inside an `if` (without `else`) or only
inside a loop might not exist afterwards, so using it there is an error:

<!-- check: error -->
```php
$vip = true;
if ($vip) { $discount = 10; }
echo $discount;
```

Error:

```text
example.pn:3: error: $discount may be used before it is assigned: on some paths to this line it never gets a value (an if without else, or a loop that can run zero times). Give $discount a value before the if/loop
```

Give it a value first:

```php
$vip = true;
$discount = 0;
if ($vip) { $discount = 10; }
echo $discount, "\n";
```

Output:

```text
10
```

There is no `switch` or `match` in Pin; use `if / elseif / else`.

## Try it

Print FizzBuzz from 1 to 15: multiples of 3 print `Fizz`, of 5 `Buzz`, of both `FizzBuzz`.

<details><summary>One answer</summary>

```php
for ($i = 1; $i <= 15; $i++) {
    if ($i % 15 == 0) { echo "FizzBuzz\n"; }
    elseif ($i % 3 == 0) { echo "Fizz\n"; }
    elseif ($i % 5 == 0) { echo "Buzz\n"; }
    else { echo $i, "\n"; }
}
```

Output:

```text
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

</details>
