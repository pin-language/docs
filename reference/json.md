# JSON

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`json_encode`](#json_encode) | JSON text for a value. |
| [`json_raw`](#json_raw) | The JSON text of one value of an object (an object, an array or anything), to read further with the json_* functions. |
| [`json_len`](#json_len) | The number of items of a JSON array (or keys of an object); -1 when the text is neither. |
| [`json_at`](#json_at) | The JSON text of item `$i` (from 0) of a JSON array, or `""` when there is no such item. |
| [`json_has`](#json_has) | Whether a JSON object has a top-level key. |
| [`json_string`](#json_string) | A top-level string value, or `""`. |
| [`json_int`](#json_int) | A top-level integer value, or 0. |
| [`json_float`](#json_float) | A top-level number as a float, or 0.0. |
| [`json_bool`](#json_bool) | Whether a top-level value is `true`. |

## json_encode

```php
json_encode(int|float|bool|string|list|map|object $x): string
```

JSON text for a value.

```php
class Line {
    public function __construct(public string $item, public int $qty, private int $cost) {}
}
echo json_encode(["name" => "ไทย", "note" => "a\"b"]), " ", json_encode([1.5, 2.0]), " ", json_encode("x"), "\n";
echo json_encode([new Line("tea", 2, 80)]), " ", json_encode([[1, 2], [3]]), "\n";
```

Output:

```
{"name":"ไทย","note":"a\"b"} [1.5,2.0] "x"
[{"item":"tea","qty":2}] [[1,2],[3]]
```

- UTF-8 text is kept as is (like `JSON_UNESCAPED_UNICODE`); whole floats keep `.0`.
- Objects become JSON objects of their public properties, in declaration order; private properties are left out.
- A map has one value type; for a JSON object with mixed values, use a class.
- **PHP:** PHP escapes non-ASCII as `\uXXXX` and drops `.0` unless `JSON_PRESERVE_ZERO_FRACTION` is set.

## json_raw

```php
json_raw(string $json, string $key): string
```

The JSON text of one value of an object (an object, an array or anything), to read further with the json_* functions.

```php
$body = "{\"params\": {\"name\": \"add\", \"arguments\": {\"a\": 5, \"b\": 10}}}";
$params = json_raw($body, "params");
$args = json_raw($params, "arguments");
echo json_string($params, "name"), " ", json_int($args, "a") + json_int($args, "b"), "\n";
```

Output:

```
add 15
```

- `""` when the key is missing or the text is not a JSON object.
- The key `""` means "the text itself": `json_string(json_at($list, 0), "")` reads an array item.
- The text is copied as it was sent, so `json_raw($body, "id")` can be written back into an answer as is.
- **PHP:** Instead of `json_decode($body, true)['params']['arguments']`: one level at a time.

## json_len

```php
json_len(string $json): int
```

The number of items of a JSON array (or keys of an object); -1 when the text is neither.

```php
echo json_len("[1, 2, 3]"), " ", json_len("{\"a\": 1}"), " ", json_len("7"), "\n";
```

Output:

```
3 1 -1
```

## json_at

```php
json_at(string $json, int $i): string
```

The JSON text of item `$i` (from 0) of a JSON array, or `""` when there is no such item.

```php
$tags = "[\"tea\", \"cake\"]";
for ($i = 0; $i < json_len($tags); $i++) {
    echo json_string(json_at($tags, $i), ""), "\n";
}
```

Output:

```
tea
cake
```

- Read an item with key `""`: `json_int(json_at($nums, 0), "")`; an item that is an object with its keys.

## json_has

```php
json_has(string $json, string $key): bool
```

Whether a JSON object has a top-level key.

```php
$b = "{\"title\": \"tea\", \"qty\": null}";
echo json_has($b, "title") ? "y" : "n", json_has($b, "qty") ? "y" : "n", json_has($b, "x") ? "y" : "n", json_has("not json", "title") ? "y" : "n", "\n";
```

Output:

```
yynn
```

- True even when the value is `null`. False when the text is not a JSON object.

## json_string

```php
json_string(string $json, string $key): string
```

A top-level string value, or `""`.

```php
echo json_string("{\"name\": \"Som\\u0e01\", \"n\": 5}", "name"), "|", json_string("{\"n\": 5}", "n"), "|\n";
```

Output:

```
Somก||
```

- `""` when the key is missing, the value is not a string, or the text is not a JSON object.
- Escapes are decoded (`\n`, `\"`, `\uXXXX` including surrogate pairs).
- **PHP:** Instead of `json_decode($body, true)['name']`. Pin reads top-level keys of a JSON object with these functions; nested objects and arrays are skipped safely (a full `json_decode` for nested data comes later).

## json_int

```php
json_int(string $json, string $key): int
```

A top-level integer value, or 0.

```php
echo json_int("{\"qty\": 3}", "qty"), " ", json_int("{\"qty\": 1.5}", "qty"), " ", json_int("{\"qty\": \"3\"}", "qty"), " ", json_int("{\"qty\": 99999999999999999999}", "qty"), "\n";
```

Output:

```
3 0 0 9223372036854775807
```

- 0 when missing, not an integer (`1.5`, `"3"`), or not a JSON object — use `json_has` to tell missing from 0.
- Too big for an int: `PHP_INT_MAX` / `PHP_INT_MIN`.

## json_float

```php
json_float(string $json, string $key): float
```

A top-level number as a float, or 0.0.

```php
echo json_float("{\"price\": 12.5}", "price"), " ", json_float("{\"price\": 3}", "price"), " ", json_float("{\"price\": 1e999}", "price"), "\n";
```

Output:

```
12.5 3 0
```

- Integers are accepted. Out-of-range numbers like `1e999` give 0.

## json_bool

```php
json_bool(string $json, string $key): bool
```

Whether a top-level value is `true`.

```php
echo json_bool("{\"ok\": true}", "ok") ? "y" : "n", json_bool("{\"ok\": 1}", "ok") ? "y" : "n", "\n";
```

Output:

```
yn
```

- Only the JSON literal `true` counts.
