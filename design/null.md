# Pin — Null

**Status (2026-10-26):** **not built yet** — deliberately left for its own round (see "Build plan" at the end):
it touches the type system, the flow analysis and value layout at once, and a rushed version risks memory
safety. Parameter defaults (built 2026-10-26) already cover optional query values and optional JSON fields.
Earlier status (Pin 0.4, 2026-10-25): **not built yet.** Today `null` and `?Type` are compile errors that say so;
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

## Build plan (2026-10-26)

Each step is a release-sized piece with its own tests, compile errors and ASAN run; stop after any of them.

1. **Pointer types first.** `?string`, `?list<T>`, `?map<K,V>`, `?Class` in variables, parameters, returns and
   properties, stored as a pointer with null = 0 (N6: no cost). `null` takes its type from where it goes (like
   `[]`). Every free / copy / json function must accept 0 — audit them, then ASAN. `?T` inside lists and maps is
   a compile error until step 6.
2. **`=== null` / `!== null` and narrowing (N2)** as one more field in `class Flow`: a set of variables known not
   null, intersected where paths meet; an assignment (other than of a non-null value) or a `&` loan removes the
   variable. `if ($u === null) { return ...; }` narrows after the `if` because that path does not reach it.
3. **`??`, `?->`, `?? throw error(...)`** (N3, N4). `$m[$k] ?? $x` keeps its current meaning.
4. **JSON (N8):** `json_encode` writes `null`; `json_decode` accepts `null` or a missing field for a `?T` field.
5. **`?int`, `?float`, `?bool`** as `{i64, i1}` in locals, parameters and returns (N6); properties use the value
   slot plus a flag slot. Measure: the benchmarks must not change (they use no `?T`).
6. **Containers of `?T`** (bitmap for scalars, null pointers for the rest).

Fresh-agent test after step 3 (AI guide only): a lookup that may find nothing, an optional header, an optional
JSON field.
