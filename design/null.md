# Pin — Null

**Status (Pin 0.4, 2026-10-25):** **not built yet.** Today `null` and `?Type` are compile errors that say so;
code uses defaults such as `-1`, `""` or `$m[$k] ?? $default` instead. Agreed with the owner on 2026-10-24.
N5 (every property set when the constructor ends, no `$this` use before that) is built in 0.5 with classes.

Decision rule: memory safety > speed > clarity > looking like PHP.

## Rules

### N1 — nothing is null unless its type says so
No type may be null unless written with a leading `?`: `?User`, `?int`, `?string`, `?list<int>`.
```php
function findUser(int $id): ?User { ... }
function name(User $u): string { ... }      // $u is never null
```
`null` can only go into a variable, parameter, return value or property of a `?T` type.

### N2 — check before use; the compiler follows the check (flow typing)
```php
$u = findUser($id);
echo $u->name;                  // error
if ($u !== null) { echo $u->name; }        // fine
if ($u === null) { return "{}"; }
echo $u->name;                  // fine
```
- Forms the compiler understands: `!== null`, `=== null` followed by return/throw/break/continue,
  `isset($u)`, `&&` / `||`.
- Assigning `$u` again after the check means checking again.
- A `?T` property `$u->x` stays narrowed only while `$u` is not changed or lent with `&` in between.
- Uses the same per-path analysis (`class Flow`) as the ownership checks.

### N3 — PHP 8 syntax
```php
$name = $u?->name;                                   // ?string
$name = $u?->name ?? "guest";                        // string
$len  = $u?->getName()?->length();                   // chains
$u = findUser($id) ?? throw error(404, "not found"); // User
```

### N4 — no force-unwrap (`!` / `!!`)
Use `?? throw error(...)` instead: it shows what happens when the value is null.

### N5 — every property has a value when the constructor ends (checked at compile time)
```php
class User {
    public int $id;
    public string $name;
    public ?string $email;           // a ?T property starts as null if not set
    function __construct(int $id, string $name) { $this->id = $id; }
}
// error: User::__construct() does not set $this->name on every path
```
A constructor may not call `$this` methods before every property is set.

### N6 — layout (speed)
| type | stored as | cost |
|---|---|---|
| `?User`, `?string`, `?list<T>`, `?map<K,V>` | a pointer; null = 0 | none |
| `?int`, `?float`, `?bool` in variables, arguments, returns | `{i64, i1}` in two registers | tiny |
| `list<?int>` and similar | the data plus a separate bitmap, 1 bit per item | +1.6% memory |
| `map<K, ?V>` | a bit in the existing entry | none |

### N7 — `?T` or `throws`?
- **Not found is normal** → `?T` (looking up a user, an optional header, an optional JSON field).
- **A failure with a reason** → `throws` (malformed JSON, database down, invalid input).
- A missing key in `$m[$k]` still panics; `$m[$k] ?? $x` keeps working.

### N8 — `json_encode`
`null` → `null`; null properties appear in the output (`"email":null`), like PHP.

## Example error messages
```
users.pn:8: error: $u may be null (findUser() returns ?User). Check it with if ($u !== null), or use $u?->name / ??
users.pn:3: error: cannot pass null to name(): parameter $u is User, not ?User
users.pn:12: error: User::__construct() does not set $this->name on every path
users.pn:20: error: $u was checked on line 15 but assigned again on line 18. Check it again before using it
```
