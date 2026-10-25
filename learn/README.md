# Learn Pin

Fourteen short chapters, from your first program to a JSON web API backed by a database, classes, and tasks. Each one has runnable examples with their
real output — every example on these pages is compiled and run automatically, so what you read is what
Pin does — and ends with a small exercise and an answer.

You should know some programming; knowing PHP helps, since Pin keeps most of its syntax.

| | chapter | you will learn |
|---|---|---|
| 1 | [Your first program](01-first-program.md) | install, `echo`, comments, the `pin` command |
| 2 | [Values and types](02-values-and-types.md) | `int float bool string`, one type per variable, converting |
| 3 | [Control flow](03-control-flow.md) | `if`, loops, `break`/`continue`, bool conditions, values on every path |
| 4 | [Functions](04-functions.md) | typed parameters and returns, recursion, no globals |
| 5 | [Lists and maps](05-lists-and-maps.md) | `list<T>`, `map<K,V>`, `isset`, `??`, sorting |
| 6 | [Strings](06-strings.md) | building, searching, `explode`/`implode`, Thai text and bytes |
| 7 | [Ownership](07-ownership.md) | move, copy, lend — memory without a garbage collector |
| 8 | [A web API](08-web-api.md) | `serve`, routing, query strings, JSON bodies, status codes |
| 9 | [Errors and panics](09-errors-and-panics.md) | reading errors, `--json`, writing code that does not panic |
| 10 | [Coming from PHP](10-from-php.md) | translating a script, a PHP → Pin checklist |
| 11 | [A database](11-database.md) | SQLite: queries, rows, JSON results, an API that stores data |
| 12 | [Modules and packages](12-modules-and-packages.md) | `import`, `export`, `module::fn()`, `pin get` and `pin.lock` |
| 13 | [Classes](13-classes.md) | properties, methods, `new`, `&` parameters, objects in lists, borrowing |
| 14 | [Tasks and real time](14-tasks-and-realtime.md) | `go` / `await`, the Hub, Server-Sent Events, calling servers and programs |

Then: the [built-in reference](../reference/README.md) for every function, and the
[language guide](../language.md) for the complete rules. Using an AI agent? Give it the
[AI guide](../ai-guide.md).
