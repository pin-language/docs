# Security (hashes, passwords, random)

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`env`](#env) | An environment variable, or `""` when it is not set. |
| [`filter_var`](#filter_var) | Check a value from a client: the value when it is valid, null when not. |
| [`FILTER_VALIDATE_EMAIL`](#filter_validate_email) | For `filter_var()`: an email address (?string). |
| [`FILTER_VALIDATE_URL`](#filter_validate_url) | For `filter_var()`: a URL with a scheme and host (?string). |
| [`FILTER_VALIDATE_IP`](#filter_validate_ip) | For `filter_var()`: an IPv4 or IPv6 address (?string). |
| [`FILTER_VALIDATE_INT`](#filter_validate_int) | For `filter_var()`: an int (?int). |
| [`FILTER_VALIDATE_FLOAT`](#filter_validate_float) | For `filter_var()`: a number (?float). |
| [`FILTER_VALIDATE_BOOL`](#filter_validate_bool) | For `filter_var()`: yes/no, on/off, true/false, 1/0 (?bool). |
| [`FILTER_VALIDATE_BOOLEAN`](#filter_validate_boolean) | For `filter_var()`: the same as FILTER_VALIDATE_BOOL. |
| [`hash`](#hash) | SHA-256 of a string, as 64 lowercase hex characters. |
| [`hash_hmac`](#hash_hmac) | HMAC-SHA256 of `$data` with `$key`, as hex: a signature only someone with the key can make. |
| [`hash_equals`](#hash_equals) | Compare two strings in a time that does not depend on where they differ. |
| [`random_token`](#random_token) | `$bytes` random bytes from the operating system, as hex (twice as many characters). |
| [`random_int`](#random_int) | A random integer from `$min` to `$max` (both included), from the operating system's secure source. |
| [`password_hash`](#password_hash) | A salted, slow hash of a password, to store instead of the password. |
| [`password_verify`](#password_verify) | Whether `$password` matches a hash made by `password_hash()`. |

## env

```php
env(string $name): string
```

An environment variable, or `""` when it is not set.

```php
echo env("PIN_SURELY_NOT_SET") == "" ? "not set\n" : "set\n";
```

Output:

```
not set
```

- Read secrets from here (database URLs, API keys, signing keys), never from string literals: literals end up in git and in the binary.
- Read once per request is fine (it is cheap); a name containing a zero byte gives `""`.
- **PHP:** `getenv('NAME')`, but `""` instead of `false` when unset.

## filter_var

```php
filter_var(string $value, int $filter): ?T
```

Check a value from a client: the value when it is valid, null when not.

```php
echo filter_var("ann@example.com", FILTER_VALIDATE_EMAIL) ?? "bad", " ", filter_var("ann@", FILTER_VALIDATE_EMAIL) ?? "bad", "\n";
$age = filter_var(" 42 ", FILTER_VALIDATE_INT);
echo $age === null ? "not a number" : strval($age + 1), "\n";
```

Output:

```
ann@example.com bad
43
```

- `FILTER_VALIDATE_EMAIL`, `_URL`, `_IP` give `?string`; `_INT` `?int` (no leading zeros, within 64 bits, spaces around allowed); `_FLOAT` `?float`; `_BOOL` `?bool` (`yes on true 1` / `no off false 0 ""`).
- The filter must be one of these constants written in the call (the result type depends on it).
- Email: ASCII addresses with a dotted domain, as PHP's default (no Unicode addresses).
- **PHP:** PHP returns `false` where Pin gives null; no options or flags argument.

## FILTER_VALIDATE_EMAIL

```php
FILTER_VALIDATE_EMAIL: int
```

For `filter_var()`: an email address (?string).

```php
echo FILTER_VALIDATE_EMAIL > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## FILTER_VALIDATE_URL

```php
FILTER_VALIDATE_URL: int
```

For `filter_var()`: a URL with a scheme and host (?string).

```php
echo FILTER_VALIDATE_URL > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## FILTER_VALIDATE_IP

```php
FILTER_VALIDATE_IP: int
```

For `filter_var()`: an IPv4 or IPv6 address (?string).

```php
echo FILTER_VALIDATE_IP > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## FILTER_VALIDATE_INT

```php
FILTER_VALIDATE_INT: int
```

For `filter_var()`: an int (?int).

```php
echo FILTER_VALIDATE_INT > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## FILTER_VALIDATE_FLOAT

```php
FILTER_VALIDATE_FLOAT: int
```

For `filter_var()`: a number (?float).

```php
echo FILTER_VALIDATE_FLOAT > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## FILTER_VALIDATE_BOOL

```php
FILTER_VALIDATE_BOOL: int
```

For `filter_var()`: yes/no, on/off, true/false, 1/0 (?bool).

```php
echo FILTER_VALIDATE_BOOL > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## FILTER_VALIDATE_BOOLEAN

```php
FILTER_VALIDATE_BOOLEAN: int
```

For `filter_var()`: the same as FILTER_VALIDATE_BOOL.

```php
echo FILTER_VALIDATE_BOOLEAN > 0 ? "a filter" : "", "\n";
```

Output:

```
a filter
```

## hash

```php
hash(string $algo, string $data): string
```

SHA-256 of a string, as 64 lowercase hex characters.

```php
echo hash("sha256", "abc"), "\n";
```

Output:

```
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

- `$algo` must be the literal `"sha256"`: MD5 and SHA-1 are broken, so they do not compile.
- For passwords use `password_hash()`, not a plain hash: it is salted and slow on purpose.
- **PHP:** `hash('sha256', $data)`; no `md5()` / `sha1()`.

## hash_hmac

```php
hash_hmac(string $algo, string $data, string $key): string
```

HMAC-SHA256 of `$data` with `$key`, as hex: a signature only someone with the key can make.

```php
$sig = hash_hmac("sha256", "user=7", "server-secret");
echo strlen($sig), " ", hash_equals($sig, hash_hmac("sha256", "user=7", "server-secret")) ? "valid" : "forged", "\n";
```

Output:

```
64 valid
```

- `$algo` must be the literal `"sha256"`.
- Compare a signature that came from a client with `hash_equals()`, never `==`.
- **PHP:** Same argument order as PHP: algorithm, data, key.

## hash_equals

```php
hash_equals(string $known, string $user): bool
```

Compare two strings in a time that does not depend on where they differ.

```php
echo hash_equals("abc", "abc") ? "same" : "differ", " ", hash_equals("abc", "abd") ? "same" : "differ", "\n";
```

Output:

```
same differ
```

- Use it for tokens, API keys and signatures: `==` stops at the first different byte, which lets a client guess a secret one byte at a time by measuring.

## random_token

```php
random_token(int $bytes): string
```

`$bytes` random bytes from the operating system, as hex (twice as many characters).

```php
$t = random_token(16);
echo strlen($t), "\n";                    // 32 hex characters: a 128-bit session token
```

Output:

```
32
```

- Secure for session tokens, API keys, password-reset links. 16 bytes is enough for a token.
- `$bytes` must be 1 to 1024 (else panic).
- **PHP:** `bin2hex(random_bytes($bytes))`.

## random_int

```php
random_int(int $min, int $max): int
```

A random integer from `$min` to `$max` (both included), from the operating system's secure source.

```php
$d = random_int(1, 6);
echo $d >= 1 && $d <= 6 ? "a dice roll\n" : "impossible\n";
```

Output:

```
a dice roll
```

- Every value is equally likely (no modulo bias). `$min > $max` panics.
- **PHP:** Same as PHP's `random_int`. There is no `rand()` / `mt_rand()`: use this.

## password_hash

```php
password_hash(string $password): string
```

A salted, slow hash of a password, to store instead of the password.

```php
$h = password_hash("correct horse");
echo substr($h, 0, 22), "...\n";
```

Output:

```
$pbkdf2-sha256$600000$...
```

- PBKDF2-HMAC-SHA256 with 600,000 rounds (OWASP's figure for this algorithm) and a random 16-byte salt, stored as `$pbkdf2-sha256$600000$<salt>$<hash>`; two calls give different strings.
- Slow on purpose: about 0.04 s on an Apple M2 (the CPU's SHA-256 instructions on arm64), about 0.5 s where the portable code runs (x86 for now). It keeps the server thread busy meanwhile: call it at sign-up, sign-in and password change only.
- Store the whole string (it fits in TEXT); check with `password_verify()`.
- **PHP:** `password_hash($password, PASSWORD_DEFAULT)` without the second argument; PHP uses bcrypt, Pin PBKDF2, so hashes do not move between them.

## password_verify

```php
password_verify(string $password, string $hash): bool
```

Whether `$password` matches a hash made by `password_hash()`.

```php
$h = password_hash("correct horse");
echo password_verify("correct horse", $h) ? "yes" : "no", " ", password_verify("wrong", $h) ? "yes" : "no", "\n";
```

Output:

```
yes no
```

- A string that is not such a hash gives `false` (never a panic): it usually comes from a database.
- As slow as `password_hash()`; the comparison takes constant time.
