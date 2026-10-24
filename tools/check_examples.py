#!/usr/bin/env python3
"""Compile and run every ```php example in the given Markdown files and compare it with the page.

  python3 tools/check_examples.py learn/*.md            check (exit 1 on any mismatch)
  python3 tools/check_examples.py --fix learn/*.md      rewrite the ```text blocks with the real output

Each ```php block is checked according to an optional comment on the line before it:
  (none)                      compile and run; must exit 0
  <!-- check: panic -->       compile and run; must panic (exit 1)
  <!-- check: error -->       must NOT compile
  <!-- check: server -->      compile only (also the default for any block that calls serve())
  <!-- check: skip -->        not checked (a fragment)
  <!-- check: file NAME -->   not run: saved as NAME (e.g. prices.pn or util/text.pn) next to every later
                              example on the same page, so those can `import` it
If the block is followed by a line "Output:" (or "Error:" / "Panic:") and a ```text block, that block must
equal what the program printed: stdout for run, the compiler's message for error, stderr for panic.
The file is always compiled as example.pn, so messages read "example.pn:LINE: error: ...".

Finds the compiler in $PIN, then `pin` on the PATH, then ../pin/pin.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

FENCE = re.compile(r"^```(\w*)\s*$")


def find_pin():
    for cand in (os.environ.get("PIN"), shutil.which("pin"),
                 os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "pin", "pin")):
        if cand and os.path.exists(cand):
            return cand
    sys.exit("cannot find pin: set PIN=/path/to/pin")


PIN = find_pin()


def blocks(lines):
    """Yield (kind, code_start, code_end, out_start, out_end) for each php block; *_end exclusive."""
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        lang, start = m.group(1), i + 1
        end = start
        while end < len(lines) and not lines[end].startswith("```"):
            end += 1
        if lang != "php":
            i = end + 1
            continue
        kind = "run"
        j = i - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        if j >= 0:
            c = re.match(r"\s*<!--\s*check:\s*(\w+)(?:\s+([\w./-]+))?\s*-->", lines[j])
            if c:
                kind = c.group(1) if c.group(1) != "file" else "file:" + (c.group(2) or "")
        # an Output:/Error:/Panic: label and a ```text block right after
        k = end + 1
        while k < len(lines) and lines[k].strip() == "":
            k += 1
        out = None
        if k < len(lines) and lines[k].strip() in ("Output:", "Error:", "Panic:"):
            k += 1
            while k < len(lines) and lines[k].strip() == "":
                k += 1
            if k < len(lines) and lines[k].strip() == "```text":
                o_end = k + 1
                while o_end < len(lines) and not lines[o_end].startswith("```"):
                    o_end += 1
                out = (k + 1, o_end)
        yield kind, start, end, out
        i = end + 1


def run(kind, code, files=None):
    with tempfile.TemporaryDirectory(prefix="pin-learn-") as d:
        for name, text in (files or {}).items():
            os.makedirs(os.path.dirname(os.path.join(d, name)), exist_ok=True)
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(text)
        with open(os.path.join(d, "example.pn"), "w", encoding="utf-8") as f:
            f.write(code)
        b = subprocess.run([PIN, "build", "example.pn", "-o", "example"], cwd=d, capture_output=True, text=True)
        if kind == "error":
            if b.returncode == 0:
                return False, "expected a compile error, but it compiled"
            return True, b.stderr.strip()
        if b.returncode:
            return False, "does not compile: " + b.stderr.strip()
        if kind == "server":
            return True, None
        try:
            r = subprocess.run([os.path.join(d, "example")], cwd=d, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return False, "still running after 30 s (mark it <!-- check: server --> or fix the loop)"
        if kind == "panic":
            if r.returncode != 1 or "panic:" not in r.stderr:
                return False, f"expected a panic, got exit {r.returncode}: {r.stderr!r}"
            return True, r.stderr.strip()
        if r.returncode:
            return False, f"exit {r.returncode}: {r.stderr.strip()}"
        return True, r.stdout.rstrip("\n")


def main():
    args = sys.argv[1:]
    fix = "--fix" in args
    files = [a for a in args if a != "--fix"]
    failures = checked = 0
    for path in files:
        lines = open(path, encoding="utf-8").read().split("\n")
        edits = []
        files = {}
        for kind, s, e, out in blocks(lines):
            if kind == "skip":
                continue
            if kind.startswith("file:"):
                files[kind[5:]] = "\n".join(lines[s:e]) + "\n"
                continue
            checked += 1
            code = "\n".join(lines[s:e]) + "\n"
            if kind == "run" and "serve(" in code:
                kind = "server"
            ok, got = run(kind, code, files)
            where = f"{path}:{s}"
            if not ok:
                failures += 1
                print(f"FAIL {where}: {got}")
                continue
            if out is None or got is None:
                continue
            want = "\n".join(lines[out[0]:out[1]])
            if want != got:
                if fix:
                    edits.append((out, got))
                else:
                    failures += 1
                    print(f"FAIL {where}: output differs\n  page: {want!r}\n  real: {got!r}")
        for (o_s, o_e), got in sorted(edits, reverse=True):
            lines[o_s:o_e] = got.split("\n")
        if edits:
            open(path, "w", encoding="utf-8").write("\n".join(lines))
            print(f"fixed {len(edits)} output block(s) in {path}")
    print(f"{checked} examples checked, {failures} failed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
