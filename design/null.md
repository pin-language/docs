# Pin — Null

**Status (2026-11-08):** steps 1–4 of the build plan are **built**: `?string`, `?list<T>`, `?map<K,V>` and
`?ClassName`; checks that narrow (N2, for variables); `?->`, `??`, `?? throw` (N3, N4); JSON (N8). Steps 5
(`?int`, `?float`, `?bool`) and 6 (`list<?T>`, `map<K,?T>`) are not built and are compile errors that say so.
See "As built" at the end. N5 (every property set when the constructor ends) was built in 0.5 with classes.

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

## As built (2026-11-08)

What steps 1–4 do, and where they differ from the rules above.

- **Layout (N6):** a `?T` value is the same pointer as a `T`, with null = 0. Nothing changes for code that uses no
  `?T`: the IR of every existing test, example and benchmark is byte-for-byte the same apart from one unused
  `declare` line, so benchmark numbers cannot move. Every free function already accepted null; copy and JSON of
  a `?T` go through a generated helper that checks for null first (`pn_str_dup(NULL)` would give `""`).
- **`null` takes its type from where it goes**, like `[]`: a `?T` variable, parameter, property, return value,
  `??` default or `?:` arm. `$u = null;` for a new variable is an error that suggests `?User $u = null;` (a typed
  declaration starting with `?` is new syntax). A parameter or property default may be `null`.
- **Narrowing (N2) is per variable,** a set in `class Flow` intersected where paths meet. It understands `!== null`,
  `=== null`, `isset($u)`, `!`, `&&`, `||` in `if`, `while`, `for` and `?:`, so
  `if ($u === null) { return; }` narrows the rest of the function and `while ($u === null) { ... }` narrows after
  the loop. Assigning a `?T` value, a move, or lending the variable with `&` to a `?T &` parameter removes it; a
  loop removes every variable it may write before the first round (the next round may see null again).
- **Not built from N2: narrowing a property.** `if ($u->email !== null) { strlen($u->email); }` is still an error;
  the message says to read it into a variable first (`$e = $u->email;`), which for lists and objects is a borrow,
  not a copy. Tracking "unchanged since the check" for paths is the part that needs the borrow machinery, and it is
  not needed to write correct code.
- **`=== null` on a value that can never be null is a compile error** (always true or always false), as is `?->`
  on a non-null value. This catches PHP habits that hide a type mistake.
- **`?->`** gives `?T` (`?string` for a string property, `?Address` for an object one). A field or method that
  gives `int`/`float`/`bool` would need step 5 and is an error. `$u?->save();` works as a statement (void
  methods too). On a variable it keeps all ownership checks, so a changing method is allowed; on a call result
  or property path a changing method is an error (put it in a variable first).
- **`??` on a `?T` value** gives `T` when the default is `T`. Ownership: strings come out owned on both paths. For
  lists, maps and objects, if the left side is a function result and the default a variable, the default is
  copied (the result must own one value either way); if the left side is borrowed and the default is new, the
  result is borrowed and the default is freed at the end of the statement. `$m[$k] ?? $x` keeps its meaning.
- **`?? throw error(...)`** leaves through the normal error path (the function must be `throws`, or inside `try`),
  and the value is `T` after it.
- **A class may hold `?Itself`** (linked lists, trees): null ends the chain, so it can be built. Free, copy and
  JSON follow the chain recursively, the same as `list<Node>` already did. Walking one in a loop needs a borrow
  of a borrow, which Pin does not have; recursion works.
- **JSON (N8):** `json_encode` writes `null` and keeps null properties (`"email":null`). `json_decode` accepts JSON
  `null` or a missing field for a `?T` property or constructor parameter; a wrong type is still a 400.
- **A lexer fix found on the way:** `list<?string>` used to lex `<?` as the PHP open tag. `<?` now opens only
  when a letter does not follow.
- Tests: `tests/null_basics.pn`, `null_more.pn`, `null_linked.pn`, `null_json.pn`, `null_narrow.pn`, `null_ownership.pn`, and 14
  compile errors `tests/errors/null_*.pn`. ASAN + UBSAN clean on macOS; the macOS `leaks` tool finds 0 leaks;
  LeakSanitizer runs in CI on Linux.
- **Fresh-agent test (Sonnet, AI guide only, 2026-11-09):** a lookup returning `?User` (404 when null), an
  optional `X-Request-Id` header as a `?string`, and a POST with an optional `email` field. `pin check` was clean
  on the first round and every curl case was right. One gap, in the guide: the agent declared `?string $email`
  as a property beside a constructor, and `json_decode` refused `email` as an unknown field (with a constructor
  the fields are its parameters). The guide now shows the shape for an optional field
  (`public ?string $email = null` as a constructor parameter).
