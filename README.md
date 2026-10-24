# Pin documentation

Documentation for [Pin](https://github.com/pin-language/pin): a PHP-like language for AI coding agents,
compiled to native code through LLVM, with compile-time ownership instead of a garbage collector.

| document | for | language |
|---|---|---|
| [ai-guide.md](ai-guide.md) | **AI coding agents** — the whole v0.1 language on one page: rules, idioms, PHP → Pin table, error → fix table | English |
| [language.md](language.md) | people learning Pin | English |
| [reference/](reference/README.md) | **every built-in function, constant and cast** — signature, example with its real output, edge cases, differences from PHP | English |
| [design/](design/) | design decisions for features that are agreed but mostly not built yet (ownership v2 with classes, error handling, null, strings/UTF-8, concurrency, int overflow) | Thai |

## Using the AI guide with an agent

Tell the agent to read the guide before writing Pin, and to check every change:

```
This project is written in Pin. Before writing code, read
https://raw.githubusercontent.com/pin-language/docs/HEAD/ai-guide.md
After every change run `pin check --json FILE.pn` and fix what it reports.
```

Each document describes the Pin version named at its top. The compiler, examples and install steps are in
the [main repository](https://github.com/pin-language/pin).

## License

MIT — see [LICENSE](LICENSE).
