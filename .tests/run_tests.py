#!/usr/bin/env python3
"""
Test runner for ICS 3U0 labs.

Press Ctrl+Shift+B in VS Code to run this, or run it directly.
It reads tests.json, runs main.py against each case, and reports pass or fail.

Uses only the Python standard library. Nothing needs to be installed.
"""

import io
import json
import os
import re
import subprocess
import sys
import textwrap
import tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parent   # the hidden .tests folder
FOLDER = HERE.parent                     # the lesson folder the student opens
TARGET = FOLDER / "main.py"
TESTS = HERE / "tests.json"
TEMPLATE = HERE / "template.py"

TIMEOUT = 5
WIDTH = 64
WRAP_AT = 80
HEADER_FIELDS = ["Name", "Purpose", "Author", "Created", "Updated"]
MUST_CHANGE = ["Purpose", "Author", "Created", "Updated"]

PAD = "  "          # left margin
BODY = " " * 8      # detail text, aligned under the test name
CODE = " " * 10     # numbered output lines


# ----------------------------------------------------------------------------
# Colour
# ----------------------------------------------------------------------------

def _enable_windows_ansi():
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        return True
    except Exception:
        return False


USE_COLOUR = (
    not os.environ.get("NO_COLOR")
    and (os.environ.get("FORCE_COLOR") or sys.stdout.isatty())
    and _enable_windows_ansi()
)

CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
}


def paint(text, *styles):
    if not USE_COLOUR or not styles:
        return text
    prefix = "".join(CODES[style] for style in styles if style in CODES)
    return "{}{}{}".format(prefix, text, CODES["reset"])


# Each detail line is (style_key, text). Styles map to colours here.
STYLE = {
    "label": ("dim",),
    "hint": ("dim",),
    "problem": ("yellow",),
    "want": ("green",),
    "got": ("red",),
    "error": ("red",),
    "plain": (),
}


def emit(style, text, indent=BODY, wrap=True):
    styles = STYLE.get(style, ())
    room = WRAP_AT - len(indent)
    if wrap and len(text) > room:
        lines = textwrap.wrap(text, width=room)
    else:
        lines = [text]
    for line in lines:
        print(indent + paint(line, *styles))


# ----------------------------------------------------------------------------
# Reading the student's file
# ----------------------------------------------------------------------------

def read_source():
    return TARGET.read_text(encoding="utf-8", errors="replace")


def header_range(src):
    """Line numbers (1-based) of the first and second #--- rule lines."""
    rules = []
    for i, line in enumerate(src.split("\n"), start=1):
        if re.match(r"^\s*#-{3,}", line):
            rules.append(i)
        if len(rules) == 2:
            return rules[0], rules[1]
    return None


def header_values(src):
    """Map each header field to the text written after its colon."""
    values = {field: "" for field in HEADER_FIELDS}
    for line in src.split("\n")[:25]:
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        body = stripped.lstrip("#").strip()
        for field in HEADER_FIELDS:
            if body.lower().startswith(field.lower() + ":"):
                values[field] = body[len(field) + 1:].strip()
    return values


def comment_lines(src):
    """Line numbers of real comments outside the header, or None if unparseable."""
    block = header_range(src)
    found = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(src).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            line_no = token.start[0]
            if block and block[0] <= line_no <= block[1]:
                continue
            if token.string.lstrip("#").strip():
                found.append(line_no)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    return found


# ----------------------------------------------------------------------------
# Comparing output
# ----------------------------------------------------------------------------

def normalize(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def expected_lines(expect):
    if isinstance(expect, list):
        lines = [str(item).rstrip() for item in expect]
        while lines and lines[-1] == "":
            lines.pop()
        return lines
    return normalize(str(expect))


def first_difference(expected, actual):
    for i in range(max(len(expected), len(actual))):
        got = actual[i] if i < len(actual) else None
        want = expected[i] if i < len(expected) else None
        if got != want:
            return i
    return None


def show_block(label, lines, style, mark=None):
    emit("label", label + ":", wrap=False)
    if not lines:
        emit("hint", "(nothing was printed)", indent=CODE, wrap=False)
        return
    for i, line in enumerate(lines):
        arrow = ">" if mark == i else " "
        emit(style, "{} {:>2} | {}".format(arrow, i + 1, line),
             indent=CODE, wrap=False)


# ----------------------------------------------------------------------------
# Running the program
# ----------------------------------------------------------------------------

def run_program(stdin_text):
    """Return (stdout, stderr, status). Status is 'ok', 'timeout' or 'crash'."""
    try:
        proc = subprocess.run(
            [sys.executable, str(TARGET)],
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(FOLDER),
        )
    except subprocess.TimeoutExpired:
        return "", "", "timeout"
    status = "ok" if proc.returncode == 0 else "crash"
    return proc.stdout, proc.stderr, status


def tidy_error(stderr):
    """Drop the runner's own frames and shorten the path to just main.py."""
    text = stderr.replace(str(TARGET), "main.py").replace(str(FOLDER) + os.sep, "")
    lines = [line.rstrip() for line in text.strip().split("\n") if line.strip()]
    return lines[-5:]


# ----------------------------------------------------------------------------
# The three kinds of check
# ----------------------------------------------------------------------------

def template_values():
    """Header values as shipped, so untouched fields can be spotted."""
    if not TEMPLATE.exists():
        return {}
    return header_values(TEMPLATE.read_text(encoding="utf-8", errors="replace"))


def check_header(case, src):
    values = header_values(src)

    blank = [field for field in HEADER_FIELDS if not values[field]]
    if blank:
        emit("problem", "Still blank: {}".format(", ".join(blank)))
        emit("hint", "Fill in every field at the top of main.py.")
        return False

    if values["Name"].lower() in ("your name", "name"):
        emit("problem", "Name should be the name of the program, not your own name.")
        return False

    shipped = template_values()
    stale = [field for field in MUST_CHANGE
             if shipped.get(field)
             and values[field].strip().lower() == shipped[field].strip().lower()]
    if stale:
        for field in stale:
            emit("problem", "{} still says \"{}\".".format(field, values[field]))
        emit("hint", "Replace the template's information with your own.")
        return False

    return True


def check_comments(case, src):
    minimum = case.get("min", 1)
    found = comment_lines(src)
    if found is None:
        emit("problem", "Could not read main.py.")
        emit("hint", "Fix the errors in your code first, then run the tests again.")
        return False
    if len(found) < minimum:
        emit("problem", "Found {} comment(s) below the header, expected at least {}."
             .format(len(found), minimum))
        emit("hint", "A comment starts with # and runs to the end of the line.")
        return False
    return True


def check_output(case, src):
    stdin_text = case.get("stdin", "")
    if isinstance(stdin_text, list):
        stdin_text = "\n".join(str(item) for item in stdin_text)
    if stdin_text and not stdin_text.endswith("\n"):
        stdin_text += "\n"

    stdout, stderr, status = run_program(stdin_text)

    if status == "timeout":
        emit("problem", "Your program ran for more than {} seconds and was stopped."
             .format(TIMEOUT))
        emit("hint", "Check for a loop that never ends, or an input() with nothing to read.")
        return False

    if status == "crash":
        emit("problem", "Your program stopped with an error:")
        for line in tidy_error(stderr):
            emit("error", line, indent=CODE, wrap=False)
        return False

    expected = expected_lines(case.get("expect", ""))
    actual = normalize(stdout)

    if actual == expected:
        return True

    index = first_difference(expected, actual)
    show_block("Expected", expected, "want", mark=index)
    show_block("Your output", actual, "got", mark=index)
    if index is not None:
        emit("hint", "First difference is on line {}.".format(index + 1))
    return False


CHECKS = {
    "header": check_header,
    "comments": check_comments,
    "output": check_output,
}

DEFAULT_NAMES = {
    "header": "Header is filled in",
    "comments": "Code is commented",
    "output": "Output is correct",
}


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def rule():
    print(PAD + paint("-" * WIDTH, "dim"))


def main():
    if not TARGET.exists():
        print(PAD + paint("Could not find main.py next to this script.", "red"))
        return 1
    if not TESTS.exists():
        print(PAD + paint("Could not find tests.json next to this script.", "red"))
        return 1

    try:
        data = json.loads(TESTS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(PAD + paint("tests.json is not valid JSON: {}".format(error), "red"))
        return 1

    cases = data.get("cases", [])
    src = read_source()
    title = data.get("title", FOLDER.name)

    print()
    print(PAD + paint(title, "bold", "cyan"))
    rule()
    print()

    passed = 0
    failed_numbers = []

    for number, case in enumerate(cases, start=1):
        kind = case.get("type", "output")
        check = CHECKS.get(kind)
        name = case.get("name", DEFAULT_NAMES.get(kind, kind))

        if check is None:
            print(PAD + paint("FAIL", "bold", "red") + "  " + name)
            emit("problem", "Unknown test type '{}' in tests.json.".format(kind))
            failed_numbers.append(number)
            print()
            continue

        # Capture the detail lines so the verdict can be printed first.
        buffer = io.StringIO()
        real_stdout = sys.stdout
        sys.stdout = buffer
        try:
            result = check(case, src)
        finally:
            sys.stdout = real_stdout

        label = "{}. {}".format(number, name)
        if result:
            print(PAD + paint("PASS", "bold", "green") + "  " + paint(label, "dim"))
        else:
            print(PAD + paint("FAIL", "bold", "red") + "  " + paint(label, "bold"))
        detail = buffer.getvalue()
        if detail.strip():
            print(detail.rstrip("\n"))
        if result:
            passed += 1
        else:
            failed_numbers.append(number)
        print()

    rule()
    total = len(cases)
    if passed == total:
        print(PAD + paint("{} of {} tests passed.".format(passed, total), "bold", "green"))
        print(PAD + paint("All tests passed. Save your work.", "green"))
    else:
        print(PAD + paint("{} of {} tests passed.".format(passed, total), "bold", "red"))
        print(PAD + paint("Still to fix: test {}".format(
            ", ".join(str(n) for n in failed_numbers)), "dim"))
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
