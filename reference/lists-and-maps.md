# Lists and maps

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`array_map`](#array_map) | A new list: the function applied to each item. |
| [`array_filter`](#array_filter) | A new list of the items the function keeps. |
| [`array_key_first`](#array_key_first) | The first key of a map, or null when it is empty. |
| [`array_key_last`](#array_key_last) | The last key of a map, or null when it is empty. |
| [`ksort`](#ksort) | Sort a map by its keys, in place. |
| [`krsort`](#krsort) | Sort a map by its keys, largest first, in place. |
| [`asort`](#asort) | Sort a map by its values (int, float, bool or string), keeping each key with its value. |
| [`arsort`](#arsort) | Sort a map by its values, largest first, keeping the keys. |
| [`range`](#range) | The ints from `$from` to `$to` (counting down when `$from` is larger). |
| [`array_count_values`](#array_count_values) | How many times each value occurs, in first-seen order. |
| [`array_flip`](#array_flip) | Values become keys and keys values (values must be int or string). |
| [`array_combine`](#array_combine) | A map from a list of keys and a list of values. |
| [`usort`](#usort) | Sort a list in place with your own comparison function. |
| [`array_pop`](#array_pop) | Take the last item out of the list, or null when it is empty. |
| [`array_shift`](#array_shift) | Take the first item out of the list, or null when it is empty. |
| [`array_slice`](#array_slice) | A copy of part of a list. |
| [`array_merge`](#array_merge) | A new list: the items of `$a`, then those of `$b` (copied). |
| [`array_reverse`](#array_reverse) | A copy of the list in reverse order. |
| [`array_search`](#array_search) | The index of the first item equal to `$value`, or -1. |
| [`array_unique`](#array_unique) | The list without repeated items (first ones kept, in order). |
| [`in_array`](#in_array) | Whether the list holds the value (lists of int, float, bool, string). |
| [`array_keys`](#array_keys) | The keys of a map, in insertion order. |
| [`array_values`](#array_values) | The values of a map, in insertion order (copied). |
| [`array_sum`](#array_sum) | The sum of a list of numbers. |
| [`count`](#count) | Number of items in a list or entries in a map. |
| [`fill`](#fill) | A new list with `$n` copies of `$value`. |
| [`copy`](#copy) | An independent copy you own, with everything inside it. |
| [`sort`](#sort) | Sort a list variable in place, smallest first. |
| [`rsort`](#rsort) | Sort a list variable in place, largest first. |
| [`isset`](#isset) | Whether a list index is in range, a map key exists, or a ?T variable is not null. |
| [`array_key_exists`](#array_key_exists) | Same as `isset($m[$key])`. |
| [`unset`](#unset) | Remove a map entry (nothing happens if it is missing). |

## array_map

```php
array_map(string $function, list<T> $xs): list<R>
```

A new list: the function applied to each item.

```php
function label(int $satang): string { return number_format($satang / 100, 2); }
echo json_encode(array_map("label", [4500, 12000])), "\n";
```

Output:

```
["45.00","120.00"]
```

- `$function` is the name of a function in the same file taking one `T` and giving any `R`; it cannot be `throws`. The compiler writes the loop: no callback at run time.
- One-argument built-ins work by name too: `array_map("strtoupper", $names)`, `array_map("intval", $parts)`, `array_filter($xs, "ctype_digit")`.
- **PHP:** `array_map('label', $xs)` with a function name (Pin has no closures yet); one list.

## array_filter

```php
array_filter(list<T> $xs, string $keep): list<T>
```

A new list of the items the function keeps.

```php
function cheap(int $price): bool { return $price < 100; }
echo json_encode(array_filter([45, 120, 30], "cheap")), "\n";
```

Output:

```
[45,30]
```

- `$keep` names a function of the same file `(T $x): bool`. The kept items are copied, and the new list is renumbered from 0 (PHP keeps the old keys).
- **PHP:** PHP keeps the original keys; Pin's result is a list numbered from 0.

## array_key_first

```php
array_key_first(map<K,V> $m): ?K
```

The first key of a map, or null when it is empty.

```php
echo array_key_first(["b" => 2, "a" => 1]) ?? "none", "\n";
```

Output:

```
b
```

## array_key_last

```php
array_key_last(map<K,V> $m): ?K
```

The last key of a map, or null when it is empty.

```php
echo array_key_last([3 => "c", 7 => "g"]) ?? -1, "\n";
```

Output:

```
7
```

## ksort

```php
ksort(map<K,V> $m): void
```

Sort a map by its keys, in place.

```php
map<string,int> $m = ["b" => 2, "a" => 1];
ksort($m);
echo json_encode($m), "\n";
```

Output:

```
{"a":1,"b":2}
```

- Stable, as PHP 8. `krsort()` sorts the other way.

## krsort

```php
krsort(map<K,V> $m): void
```

Sort a map by its keys, largest first, in place.

```php
map<int,string> $m = [1 => "a", 3 => "c"];
krsort($m);
echo json_encode($m), "\n";
```

Output:

```
{"3":"c","1":"a"}
```

## asort

```php
asort(map<K,V> $m): void
```

Sort a map by its values (int, float, bool or string), keeping each key with its value.

```php
map<string,int> $votes = ["tea" => 5, "coffee" => 9, "milk" => 2];
asort($votes);
echo json_encode($votes), "\n";
```

Output:

```
{"milk":2,"tea":5,"coffee":9}
```

- `arsort()` sorts the other way (largest first).

## arsort

```php
arsort(map<K,V> $m): void
```

Sort a map by its values, largest first, keeping the keys.

```php
map<string,int> $votes = ["tea" => 5, "coffee" => 9, "milk" => 2];
arsort($votes);
echo json_encode(array_keys($votes)), "\n";
```

Output:

```
["coffee","tea","milk"]
```

## range

```php
range(int $from, int $to, int $step = 1): list<int>
```

The ints from `$from` to `$to` (counting down when `$from` is larger).

```php
echo json_encode(range(1, 5)), json_encode(range(10, 0, 5)), "\n";
foreach (range(1, 3) as $i) { echo $i; }
echo "\n";
```

Output:

```
[1,2,3,4,5][10,5,0]
123
```

- A step of 0 panics. Ints only (a for loop for floats).

## array_count_values

```php
array_count_values(list<int|string> $xs): map<T,int>
```

How many times each value occurs, in first-seen order.

```php
echo json_encode(array_count_values(["tea", "milk", "tea"])), "\n";
```

Output:

```
{"tea":2,"milk":1}
```

## array_flip

```php
array_flip(map<K,V> $m): map<V,K>
```

Values become keys and keys values (values must be int or string).

```php
echo json_encode(array_flip(["a" => "x", "b" => "y"])), "\n";
```

Output:

```
{"x":"a","y":"b"}
```

- When two keys have the same value, the later one wins (as PHP).

## array_combine

```php
array_combine(list<K> $keys, list<V> $values): map<K,V>
```

A map from a list of keys and a list of values.

```php
echo json_encode(array_combine(["id", "qty"], [7, 2])), "\n";
```

Output:

```
{"id":7,"qty":2}
```

- Lists of different lengths panic (PHP throws).

## usort

```php
usort(list<T> $xs, string $compare): void
```

Sort a list in place with your own comparison function.

```php
class Item { public function __construct(public string $name, public int $price) {} }
function by_price(Item $a, Item $b): int { return $a->price - $b->price; }
list<Item> $items = [new Item("cake", 120), new Item("tea", 45), new Item("rice", 30)];
usort($items, "by_price");
foreach ($items as $i) { echo $i->name, " "; }
echo "\n";
```

Output:

```
rice tea cake 
```

- `$compare` is the name of a function in the same file, `(T $a, T $b): int`: negative puts `$a` first, positive `$b`, 0 keeps their order (the sort is stable). It cannot be `throws`.
- Lists of int, float, string, objects, lists or maps. A list of bools: `sort()`.
- **PHP:** `usort($xs, 'by_price')` with a function name; Pin has no closures yet.

## array_pop

```php
array_pop(list<T> $xs): ?T
```

Take the last item out of the list, or null when it is empty.

```php
list<int> $stack = [1, 2, 3];
$top = array_pop($stack);
echo $top ?? -1, " ", count($stack), "\n";
```

Output:

```
3 2
```

- The item moves out to the result (no copy); `array_pop($xs) ?? $default` when the list may be empty.
- **PHP:** Same, null when empty (Pin's result type is `?T`).

## array_shift

```php
array_shift(list<T> $xs): ?T
```

Take the first item out of the list, or null when it is empty.

```php
list<string> $queue = ["a", "b"];
echo array_shift($queue) ?? "none", " ", json_encode($queue), "\n";
```

Output:

```
a ["b"]
```

- Moves every other item down: O(n).

## array_slice

```php
array_slice(list<T> $xs, int $offset, int $length = rest): list<T>
```

A copy of part of a list.

```php
echo json_encode(array_slice([1, 2, 3, 4, 5], 1, 2)), json_encode(array_slice([1, 2, 3, 4, 5], -2)), "\n";
```

Output:

```
[2,3][4,5]
```

- `substr()`'s rules for negative values, counted in items. The items are copied.

## array_merge

```php
array_merge(list<T> $a, list<T> $b): list<T>
```

A new list: the items of `$a`, then those of `$b` (copied).

```php
echo json_encode(array_merge([1, 2], [3])), "\n";
```

Output:

```
[1,2,3]
```

- **PHP:** Two lists of one type (no maps, no more than two).

## array_reverse

```php
array_reverse(list<T> $xs): list<T>
```

A copy of the list in reverse order.

```php
echo json_encode(array_reverse(["a", "b", "c"])), "\n";
```

Output:

```
["c","b","a"]
```

## array_search

```php
array_search(T $value, list<T> $xs): int
```

The index of the first item equal to `$value`, or -1.

```php
echo array_search("b", ["a", "b"]), " ", array_search(9, [1, 2]), "\n";
```

Output:

```
1 -1
```

- **PHP:** PHP returns `false` when not found; Pin returns `-1` (as `strpos`). Strict comparison.

## array_unique

```php
array_unique(list<T> $xs): list<T>
```

The list without repeated items (first ones kept, in order).

```php
echo json_encode(array_unique(["b", "a", "b", "c", "a"])), "\n";
```

Output:

```
["b","a","c"]
```

- Lists of int, float, bool or string.

## in_array

```php
in_array(T $value, list<T> $xs): bool
```

Whether the list holds the value (lists of int, float, bool, string).

```php
echo in_array("tea", ["coffee", "tea"]) ? "yes" : "no", " ", in_array(4, [1, 2, 3]) ? "yes" : "no", "\n";
```

Output:

```
yes no
```

- Compares strictly, like `in_array($v, $xs, true)`. For many lookups use a `map<string,bool>` and `isset()`.

## array_keys

```php
array_keys(map<K,V> $m): list<K>
```

The keys of a map, in insertion order.

```php
echo json_encode(array_keys(["a" => 1, "b" => 2])), "\n";
```

Output:

```
["a","b"]
```

## array_values

```php
array_values(map<K,V> $m): list<V>
```

The values of a map, in insertion order (copied).

```php
echo json_encode(array_values(["a" => 1, "b" => 2])), "\n";
```

Output:

```
[1,2]
```

- Not for maps of `?int` / `?float` / `?bool` yet.

## array_sum

```php
array_sum(list<int> $xs): int  /  array_sum(list<float> $xs): float
```

The sum of a list of numbers.

```php
echo array_sum([1, 2, 3]), " ", array_sum([0.5, 0.25]), "\n";
```

Output:

```
6 0.75
```

- Ints wrap around like `+`.

## count

```php
count(list|map $xs): int
```

Number of items in a list or entries in a map.

```php
echo count([1, 2, 3]), " ", count(["a" => 1]), "\n";
```

Output:

```
3 1
```

## fill

```php
fill(int $n, int|float|bool|string $value): list
```

A new list with `$n` copies of `$value`.

```php
$flags = fill(3, false);
$flags[1] = true;
echo json_encode($flags), " ", json_encode(fill(2, "x")), "\n";
```

Output:

```
[false,true,false] ["x","x"]
```

- A negative or impossibly large `$n` panics.
- **PHP:** Pin's version of `array_fill(0, $n, $value)`.

## copy

```php
copy(list|map|object|string|?T $x): same type
```

An independent copy you own, with everything inside it.

```php
$a = [1, 2];
$b = copy($a);
$b[] = 3;
$grid = [[1], [2]];
$g2 = copy($grid);
$g2[0][] = 9;
echo count($a), " ", count($b), " ", json_encode($grid), " ", json_encode($g2), "\n";
```

Output:

```
2 3 [[1],[2]] [[1,9],[2]]
```

- Lists, maps and objects move on `$b = $a`; use `copy()` when you need two of them.
- A function parameter is read-only; `copy()` it before changing it (or declare it `&`).
- Copies deeply: nested lists, maps and objects are copied too. A value holding a `db` or `rows` cannot be copied.

## sort

```php
sort(list $xs): void
```

Sort a list variable in place, smallest first.

```php
$xs = [3, 1, 2];
sort($xs);
$names = ["bob", "Alice", "carol"];
sort($names);
echo json_encode($xs), " ", json_encode($names), "\n";
```

Output:

```
[1,2,3] ["Alice","bob","carol"]
```

- Works on lists of int, float, bool and string; strings sort by bytes, so upper case comes before lower case.
- The argument must be a list variable you own (not a parameter, not an expression), and not one a `foreach` is walking.
- **PHP:** There are no sort flags or custom comparisons (`usort`) yet.

## rsort

```php
rsort(list $xs): void
```

Sort a list variable in place, largest first.

```php
$xs = [3, 1, 2];
rsort($xs);
echo json_encode($xs), "\n";
```

Output:

```
[3,2,1]
```

- Same rules as `sort()`.

## isset

```php
isset($list[$i] | $map[$key] | ?T $x): bool
```

Whether a list index is in range, a map key exists, or a ?T variable is not null.

```php
$m = ["tea" => 40];
$xs = [10, 20];
echo isset($m["tea"]) ? "y" : "n", isset($m["cake"]) ? "y" : "n", isset($xs[1]) ? "y" : "n", isset($xs[5]) ? "y" : "n", "\n";
?string $note = null;
echo isset($note) ? "set" : "null", "\n";
```

Output:

```
ynyn
null
```

- Use it (or `??`) before reading a key that may be missing: reading a missing map key panics.
- `isset($x)` on a `?T` variable is the same as `$x !== null`, and like it, counts `$x` as checked in the branch where it is true.
- **PHP:** Works on one list item, one map entry, or one `?T` variable; not on a property path or an expression.

## array_key_exists

```php
array_key_exists(key, map|list $m): bool
```

Same as `isset($m[$key])`.

```php
$m = ["a" => 1];
echo array_key_exists("a", $m) ? "yes" : "no", "\n";
```

Output:

```
yes
```

- The container must be a variable or a function result, not a literal.

## unset

```php
unset($map[$key]): void
```

Remove a map entry (nothing happens if it is missing).

```php
$m = ["a" => 1, "b" => 2];
unset($m["a"]);
unset($m["zzz"]);
echo json_encode($m), "\n";
```

Output:

```
{"b":2}
```

- Maps only. To drop items from a list, build a new list without them.
- Not allowed while a `foreach` walks the map.
