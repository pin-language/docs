# 7. Ownership

[Learn Pin](README.md) · previous: [6. Strings](06-strings.md) · next: [8. A web API](08-web-api.md)

PHP frees memory with reference counting and a garbage collector while your program runs. Pin frees
memory without either: the compiler works out, before the program runs, exactly when each list, map and
string is no longer needed. For that it needs a few rules about who *owns* a value. They are the rules
most likely to surprise a PHP developer, and every one of them is checked when you compile.

## 1. Lists and maps move

`$b = $a` does not copy a list: it hands it over. `$b` owns it now, and `$a` can no longer be used.

<!-- check: error -->
```php
$a = [1, 2, 3];
$b = $a;
echo count($a);
```

Error:

```text
example.pn:3: error: $a was moved on line 2 and can no longer be used here. Use copy($a) if you need two separate values
```

Moving is free — no items are copied. When you really want two lists, say so:

```php
$a = [1, 2, 3];
$b = copy($a);
$b[] = 4;
echo count($a), " ", count($b), "\n";
```

Output:

```text
3 4
```

Giving `$a` a new value makes it usable again: `$a = [9];`.

## 2. Strings copy

Strings behave like PHP: `$t = $s` gives `$t` its own string.

```php
$s = "tea";
$t = $s;
$t .= "!";
echo $s, " ", $t, "\n";
```

Output:

```text
tea tea!
```

## 3. Passing to a function lends

A function receives a read-only loan of a list, map or string. Nothing is copied, and the caller still owns
the value afterwards:

```php
function total(list<int> $xs): int {
    $sum = 0;
    foreach ($xs as $x) { $sum += $x; }
    return $sum;
}
$prices = [55, 40, 89];
echo total($prices), " ", count($prices), "\n";
```

Output:

```text
184 3
```

Because it is a loan, the function cannot change it:

<!-- check: error -->
```php
function add_fee(list<int> $xs): list<int> {
    $xs[] = 10;
    return $xs;
}
```

Error:

```text
example.pn:2: error: $xs is a parameter lent to this code, so it cannot be changed. Work on a copy instead: $copy = copy($xs);
```

Copy it, change the copy, return the copy — the caller becomes the owner of what you return:

```php
function add_fee(list<int> $xs): list<int> {
    $out = copy($xs);
    $out[] = 10;
    return $out;
}
$prices = [55, 40];
$with_fee = add_fee($prices);
echo json_encode($prices), " ", json_encode($with_fee), "\n";
```

Output:

```text
[55,40] [55,40,10]
```

(In PHP the function would silently change its own copy. Pin makes the copy visible, so you always know
when memory is duplicated.)

## 4. No changes while foreach walks

While `foreach` goes through a list or map, you cannot add to it, remove from it or replace it — the loop
is reading it.

<!-- check: error -->
```php
$xs = [1, 2, 3];
foreach ($xs as $x) {
    $xs[] = $x * 10;
}
```

Error:

```text
example.pn:3: error: cannot append to $xs while a foreach is looping over it
```

Collect into another list and use it after the loop:

```php
$xs = [1, 2, 3];
list<int> $more = [];
foreach ($xs as $x) { $more[] = $x * 10; }
foreach ($more as $m) { $xs[] = $m; }
echo json_encode($xs), "\n";
```

Output:

```text
[1,2,3,10,20,30]
```

## 5. Moving inside a loop

A value moved inside a loop would be gone on the next round:

<!-- check: error -->
```php
$batch = [1, 2];
for ($i = 0; $i < 3; $i++) {
    $sent = $batch;
}
```

Error:

```text
example.pn:3: error: $batch is moved inside a loop, so the next round would use a moved value. Move it after the loop, or use copy($batch)
```

Moving right before `break` or `return` is fine, because there is no next round.

## 6. Each path is checked on its own

Moving a value in one branch of an `if` leaves it usable in the other branch:

```php
$order = [1, 2, 3];
$express = count($order) > 2;
if ($express) {
    $queue = $order;              // moved only on this path
    echo "express: ", count($queue), "\n";
} else {
    echo "normal: ", count($order), "\n";
}
```

Output:

```text
express: 3
```

After the `if`, `$order` counts as moved, because one of the paths moved it.

## Why bother

- No garbage-collection pauses and no reference counts: memory is freed at a point the compiler chose.
- No accidental sharing: two variables never point at the same list, so a function can never change your
  data behind your back.
- Handlers of the web server share nothing, so they run on all CPU cores without locks.

## Try it

Write `without(list<int> $xs, int $drop): list<int>` that returns a new list without any `$drop` values,
and show that the original list is unchanged.

<details><summary>One answer</summary>

```php
function without(list<int> $xs, int $drop): list<int> {
    list<int> $out = [];
    foreach ($xs as $x) {
        if ($x != $drop) { $out[] = $x; }
    }
    return $out;
}
$xs = [1, 2, 1, 3];
$ys = without($xs, 1);
echo json_encode($xs), " ", json_encode($ys), "\n";
```

Output:

```text
[1,2,1,3] [2,3]
```

</details>
