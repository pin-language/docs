# Lists and maps

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
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
