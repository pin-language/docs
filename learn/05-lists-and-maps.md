# 5. Lists and maps

[Learn Pin](README.md) · previous: [4. Functions](04-functions.md) · next: [6. Strings](06-strings.md)

PHP has one `array` for everything. Pin has two containers, each holding one type of value:

| type | is | example |
|---|---|---|
| `list<T>` | items in order, numbered from 0 | `[55, 40, 89]` |
| `map<K,V>` | keys to values, kept in insertion order (like PHP) | `["tea" => 40]` |

`T` and `V` are `int`, `float`, `bool` or `string`; keys are `int` or `string`.

## Lists

```php
$prices = [55, 40, 89];
$prices[] = 120;            // append
$prices[0] = 60;            // replace
echo count($prices), " items, first ", $prices[0], ", last ", $prices[count($prices) - 1], "\n";
echo json_encode($prices), "\n";
```

Output:

```text
4 items, first 60, last 120
[60,40,89,120]
```

An empty list needs its type written out, because there is no first value to learn it from:

```php
list<string> $names = [];
$names[] = "Ann";
$names[] = "Ben";
echo implode(" and ", $names), "\n";
```

Output:

```text
Ann and Ben
```

## Reading past the end

Every index is checked. Reading outside the list stops the program with a clear message (a *panic*)
instead of returning garbage:

<!-- check: panic -->
```php
$xs = [1, 2, 3];
echo $xs[5];
```

Panic:

```text
panic: index 5 out of range (list has 3 items)
```

Check first, or give a default with `??`:

```php
$xs = [1, 2, 3];
echo isset($xs[5]) ? "yes" : "no", " ", $xs[5] ?? 0, "\n";
```

Output:

```text
no 0
```

## Maps

```php
$stock = ["tea" => 12, "cake" => 3];
$stock["coffee"] = 20;           // add
$stock["cake"] -= 1;             // change
$stock["juice"] += 5;            // a missing key starts at 0 for += -= *=
unset($stock["tea"]);            // remove
foreach ($stock as $item => $n) {
    echo "$item: $n\n";
}
echo json_encode($stock), "\n";
```

Output:

```text
cake: 2
coffee: 20
juice: 5
{"cake":2,"coffee":20,"juice":5}
```

Reading a key that is not there is a panic, like reading past the end of a list. Use `isset()` or `??`:

```php
$price = ["tea" => 40];
echo $price["coffee"] ?? -1, " ", isset($price["tea"]) ? "has tea" : "no tea", "\n";
```

Output:

```text
-1 has tea
```

## Sorting

`sort()` and `rsort()` sort a list variable in place:

```php
$scores = [72, 95, 58, 88];
sort($scores);
echo json_encode($scores), "\n";
$names = ["mint", "Ann", "beam"];
sort($names);
echo implode(",", $names), "\n";
```

Output:

```text
[58,72,88,95]
Ann,beam,mint
```

Strings sort by bytes, so upper case comes first. Sorting a map by value, or with your own comparison, is not
there yet — see [the AI guide's top-N idiom](../ai-guide.md#idioms) for a loop that does it.

## One value type per container

<!-- check: error -->
```php
$user = ["name" => "Ann", "age" => 30];
```

Error:

```text
example.pn:1: error: a map holds one value type: this literal is map<string,string> (from its first value), but a value here is int. For a JSON object with values of different types, declare a class with those properties and json_encode() an object of it (see the AI guide, Classes)
```

Lists of lists and maps of lists are not there yet either. For records with mixed fields, use separate
variables or parallel maps, and build JSON as a string (chapter 8 shows how).

## Try it

Given `[3, 8, 3, 1, 8, 8]`, count how often each number appears and print the result as JSON.

<details><summary>One answer</summary>

```php
$xs = [3, 8, 3, 1, 8, 8];
map<int,int> $count = [];
foreach ($xs as $x) { $count[$x] += 1; }
echo json_encode($count), "\n";
```

Output:

```text
{"3":2,"8":3,"1":1}
```

</details>
