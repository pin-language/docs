# Pin documentation

Documentation for [Pin](https://github.com/pin-language/pin): a PHP-like language for AI coding agents,
compiled to native code through LLVM, with compile-time ownership instead of a garbage collector.

| document | for | language |
|---|---|---|
| [learn/](learn/README.md) | **start here** — 10 short chapters from your first program to a JSON web API, with exercises | English |
| [ai-guide.md](ai-guide.md) | **AI coding agents** — the whole language on one page: rules, idioms, PHP → Pin table, error → fix table | English |
| [language.md](language.md) | people learning Pin | English |
| [reference/](reference/README.md) | **every built-in function, constant and cast** — signature, example with its real output, edge cases, differences from PHP | English |
| [design/](design/) | design decisions for features that are agreed but mostly not built yet (ownership v2 with classes, error handling, null, strings/UTF-8, concurrency, int overflow, the Tack web framework); each starts with its current status | English |

## Using the AI guide with an agent

Tell the agent to read the guide before writing Pin, and to check every change:

```
This project is written in Pin. Before writing code, read
https://raw.githubusercontent.com/pin-language/docs/HEAD/ai-guide.md
After every change run `pin check --json FILE.pn` and fix what it reports.
```

Every example in `learn/`, `ai-guide.md` and `language.md` is compiled and run by
`tools/check_examples.py` (CI does it on every push), and the reference is generated from the compiler's own
list of built-ins, so the pages show what Pin really does. Each document describes the Pin version named at
its top. The compiler, examples and install steps are in
the [main repository](https://github.com/pin-language/pin).

## License

MIT — see [LICENSE](LICENSE).
