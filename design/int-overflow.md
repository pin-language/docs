# Pin — Integer overflow

**Status (Pin 0.4, 2026-10-25):**
- **Built:** the memory-safety fixes S1–S3 (checked allocation sizes, `intdiv(PHP_INT_MIN, -1)` panics,
  `(int)` of NAN/INF/huge floats panics) and `wrapping_add` / `wrapping_sub` / `wrapping_mul`.
- **Built, then removed (O1):** panicking on `+ - *` overflow. It cost up to 23% on integer loops (collatz
  +23%, sieve +10%), and the owner asked to cut what made benchmark scores drop. `+ - *` now wrap around in
  64 bits — defined behaviour, not undefined behaviour. It comes back once check elision (O3) makes it cheap.
- **Changed in 0.2:** `intval()` and `json_int()` of a number that does not fit **saturate** at
  `PHP_INT_MAX` / `PHP_INT_MIN`, like PHP, instead of panicking — a number sent by a client should get a 400
  from the handler's range check, not a 500.

Decision rule: memory safety > speed > clarity > looking like PHP.

## Decisions

| # | question | chosen |
|---|---|---|
| O1 | int `+ - *` overflow | **panic** in every build, no flag to turn it off — *removed for now, see Status* |
| O2 | wrapping on purpose (hashes, checksums) | say so: `wrapping_add()`, `wrapping_sub()`, `wrapping_mul()` (built) |
| O3 | making checks cheap | remove checks the compiler can prove unnecessary; a built-in `array_sum()` |
| O4 | allocation sizes in the runtime | every size multiplication/addition is checked, always (memory safety, separate from O1; built) |

Rejected: silent wrapping as the long-term answer (silent money bugs), Rust's "wrap in release" (production
gets the silent bug), PHP's "become a float" (breaks one-type-per-variable and is slow).

## Memory-safety and DoS fixes (built in 0.1)

| # | problem | effect |
|---|---|---|
| S1 | `fill($n)` computed `cap * esize` unchecked: `n = 2^61` wrapped to a 1-byte buffer while the list claimed `n` items, so bounds checks passed and writes went past the buffer | **heap overflow** (ASAN-confirmed on the old runtime) |
| S2 | the same unchecked size arithmetic in list growth, list copy and string growth | potential overflows |
| S3 | `intdiv(PHP_INT_MIN, -1)` and `PHP_INT_MIN % -1` are undefined behaviour in LLVM and crash the process on x86 | **DoS**: one URL could take a server down |

Fixes: `checked_size()` (`__builtin_mul_overflow` / `__builtin_add_overflow`) at every size computation; `intdiv`
checks `rv == -1 && lv == INT64_MIN` and panics; `%` by -1 divides by 1 instead, giving PHP's answer 0. Each
has a test in `tests/panics/` or `tests/arith.pn` and runs clean under ASAN.

## O1 — how it worked (when re-enabled)

- `llvm.sadd/ssub/smul.with.overflow.i64`, branching to a cold `@pn_overflow(line)`.
- `-$x` with `$x == PHP_INT_MIN`, and `++ -- += -= *=`, follow the same rule.
- In a server: a panic answers 500.

```
orders.pn:14: panic: integer overflow in $price * $qty (9223372036854775807 * 2).
  Use wrapping_mul() if wrapping around is what you want
```

## O3 — making it cheap (to do)

1. **Remove provable checks**, starting with loop counters: `for ($i = A; $i < $n; $i++)` where `$i` is not
   changed in the body cannot overflow. LLVM proves some of this by itself.
2. **`array_sum(list<int>)`**: `$total += $x` loops are where checks cost SIMD; add in blocks and check after
   (for example with 128-bit partial sums).
3. Floats are unchanged (IEEE 754 overflow gives INF, not a memory problem).

Measure with the CPU benchmarks (pin-language/benchmarks) with and without checks; the risky ones are
`listsum` (`$total += $x`) and `collatz` (`3 * $n + 1`).
