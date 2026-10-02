#!/usr/bin/env python3

# Name:         clq (Command Line Quiz)
# Version:      0.0.8
# Release:      1
# License:      CC BY-NC-SA (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)
#               http://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
# Group:        System
# Source:       N/A
# URL:          http://lateralblast.com.au/
# Distribution: UNIX
# Vendor:       UNIX
# Packager:     Richard Spindler <richard@lateralblast.com.au>
# Description:  A python script to turn a formatted csv file into multiple choice quiz

import argparse
import csv
import datetime
import html
import io
import json
import os
import random
import re
import sqlite3
import sys
import tempfile
import textwrap
import zipfile

LETTERS = "abcde"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
RESET = "\033[0m"
BOLD = "\033[1m"

SCRIPT = os.path.abspath(__file__)
QUIZ_DIRS = ["quizes", os.path.join(os.path.dirname(SCRIPT), "..", "quizes")]


def get_header(field):
    """Read a field (e.g. Version) from the comment header of this script."""
    with open(SCRIPT, encoding="utf-8") as handle:
        for line in handle:
            match = re.match(r"^#\s+%s:\s+(.*)$" % field, line)
            if match:
                return match.group(1).strip()
    return ""


def print_version():
    print("%s v. %s %s" % (get_header("Name"), get_header("Version"), get_header("Packager")))


def find_quiz_dir():
    for path in QUIZ_DIRS:
        if os.path.isdir(path):
            return path
    return QUIZ_DIRS[0]


def list_quizzes():
    print("Available quizes:")
    quiz_dir = find_quiz_dir()
    if os.path.isdir(quiz_dir):
        for name in sorted(os.listdir(quiz_dir)):
            print(name)


def find_quiz(name):
    if os.path.isfile(name):
        return name
    for path in QUIZ_DIRS:
        for ext in ("", ".json", ".yaml", ".yml", ".apkg", ".txt"):
            candidate = os.path.join(path, name + ext)
            if os.path.isfile(candidate):
                return candidate
    return None


def make_question(question, answer, choices, explanation, source):
    """Normalise one question, or return None (with a warning) if it is unusable."""
    question = str(question or "").strip()
    choices = {l: str(t).strip() for l, t in choices.items() if l in LETTERS and str(t or "").strip()}
    if isinstance(answer, (list, tuple)):
        answer = "".join(str(a) for a in answer)
    answer = "".join(sorted(set(re.sub(r"[,\s]", "", str(answer or "").lower())) & set(choices)))
    if not question or not answer:
        print("Skipping question with no valid answer in %s: %s" % (source, question or "(blank)"), file=sys.stderr)
        return None
    return {"question": question, "answer": answer, "choices": choices,
            "explanation": str(explanation or "").strip()}


def load_csv(path):
    questions = []
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="|", quoting=csv.QUOTE_NONE)
        header = next(reader, None)
        if not header or header[0].strip().lower() != "question":
            sys.exit("Quiz %s is missing the Question|Answer|A|B|C|D|E header" % path)
        names = [h.strip().lower() for h in header]
        explanation_col = names.index("explanation") if "explanation" in names else None
        for row in reader:
            if len(row) < 3 or not row[0].strip():
                continue
            row = row + [""] * (max(len(header), 2 + len(LETTERS)) - len(row))
            choices = {l: row[2 + i] for i, l in enumerate(LETTERS)}
            explanation = row[explanation_col] if explanation_col is not None else ""
            item = make_question(row[0], row[1], choices, explanation, path)
            if item:
                questions.append(item)
    return questions


def load_structured(path, data):
    """Questions from parsed JSON/YAML: a list (or {"questions": [...]}) of objects.

    Each object has question, answer (string or list), choices (list in A-E order
    or an {a: text} mapping) and an optional explanation.
    """
    if isinstance(data, dict):
        data = data.get("questions")
    if not isinstance(data, list):
        sys.exit("Quiz %s must contain a list of questions" % path)
    questions = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        choices = entry.get("choices") or {}
        if isinstance(choices, list):
            choices = dict(zip(LETTERS, choices))
        else:
            choices = {str(k).lower(): v for k, v in choices.items()}
        item = make_question(entry.get("question"), entry.get("answer"), choices,
                             entry.get("explanation"), path)
        if item:
            questions.append(item)
    return questions


ANKI_SEPARATORS = {"tab": "\t", "comma": ",", "semicolon": ";", "pipe": "|", "space": " "}
ANKI_COLLECTIONS = ("collection.anki21b", "collection.anki21", "collection.anki2")


def clean_html(text):
    """Reduce an Anki field to plain text."""
    text = re.sub(r"(?i)<br\s*/?>|</div>|</p>|</li>", " ", text)
    text = re.sub(r"\[sound:[^\]]*\]", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def decompress_zstd(data):
    try:
        from compression import zstd  # Python 3.14+
        return zstd.decompress(data)
    except ImportError:
        pass
    try:
        import zstandard
    except ImportError:
        sys.exit("This Anki deck uses zstd compression: use Python 3.14+, pip install zstandard, "
                 "or export it from Anki with 'Support older Anki versions' ticked")
    return zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)).read()


def read_apkg(path):
    """Note fields from an Anki .apkg package: [[field, ...], ...]."""
    with zipfile.ZipFile(path) as package:
        names = package.namelist()
        name = next((n for n in ANKI_COLLECTIONS if n in names), None)
        if not name:
            sys.exit("%s does not contain an Anki collection" % path)
        data = package.read(name)
    if name.endswith("b"):
        data = decompress_zstd(data)
    with tempfile.TemporaryDirectory() as tmp:
        database = os.path.join(tmp, "collection.db")
        with open(database, "wb") as handle:
            handle.write(data)
        connection = sqlite3.connect(database)
        try:
            rows = connection.execute("SELECT flds FROM notes ORDER BY id").fetchall()
        finally:
            connection.close()
    return [row[0].split("\x1f") for row in rows]


def read_anki_text(path):
    """Note fields from an Anki plain text export (tab separated by default)."""
    separator = "\t"
    rows = []
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.rstrip("\r\n")
            if line.startswith("#"):
                match = re.match(r"#separator:(.*)", line)
                if match:
                    value = match.group(1).strip()
                    separator = ANKI_SEPARATORS.get(value.lower(), value or separator)
                continue
            if line.strip():
                rows.append(line.split(separator))
    return rows


def cards_to_questions(rows, source, reverse=False):
    """Turn flashcard notes (front, back, ...) into multiple choice questions.

    Wrong choices are the backs of other cards. Cloze and incomplete notes are skipped.
    """
    cards = []
    skipped = 0
    for fields in rows:
        if len(fields) < 2 or any("{{c" in f for f in fields[:2]):
            skipped += 1
            continue
        front, back = clean_html(fields[0]), clean_html(fields[1])
        if not front or not back:
            skipped += 1
            continue
        cards.append((back, front) if reverse else (front, back))
    if skipped:
        print("Skipped %d note(s) that are not basic front/back cards in %s" % (skipped, source), file=sys.stderr)
    backs = sorted({back for _, back in cards})
    if len(backs) < 2:
        sys.exit("%s needs at least two cards with different answers" % source)
    questions = []
    for front, back in cards:
        options = random.sample([b for b in backs if b != back], min(len(LETTERS) - 1, len(backs) - 1)) + [back]
        random.shuffle(options)
        item = make_question(front, LETTERS[options.index(back)], dict(zip(LETTERS, options)), "", source)
        if item:
            questions.append(item)
    return questions


def load_quiz(path, reverse=False):
    """Return a list of questions: {question, answer, choices: {letter: text}, explanation}."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, encoding="utf-8") as handle:
            return load_structured(path, json.load(handle))
    if ext in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            sys.exit("YAML quizes need PyYAML: pip install -r python/requirements.txt")
        with open(path, encoding="utf-8") as handle:
            return load_structured(path, yaml.safe_load(handle))
    if ext == ".apkg":
        return cards_to_questions(read_apkg(path), path, reverse)
    if ext == ".txt":
        return cards_to_questions(read_anki_text(path), path, reverse)
    return load_csv(path)


def import_deck(path, reverse):
    """Convert an Anki deck into a JSON quiz in the quiz directory."""
    questions = load_quiz(path, reverse)
    dest = os.path.join(find_quiz_dir(), os.path.splitext(os.path.basename(path))[0] + ".json")
    if os.path.exists(dest):
        sys.exit("%s already exists" % dest)
    data = [{"question": q["question"], "answer": q["answer"],
             "choices": [q["choices"][l] for l in LETTERS if l in q["choices"]]} for q in questions]
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as handle:
        json.dump({"questions": data}, handle, indent=2, ensure_ascii=False)
    print("Imported %d questions to %s" % (len(questions), dest))


def get_key():
    """Read a single keypress without waiting for enter."""
    if not sys.stdin.isatty():
        char = sys.stdin.read(1)
        if not char:
            raise EOFError
        return char
    try:
        import termios
        import tty
    except ImportError:
        import msvcrt
        return msvcrt.getwch()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def build_choices(item, shuffle, pool):
    """Return display choices as [(label, text, is_correct)]."""
    letters = [l for l in LETTERS if l in item["choices"]]
    if shuffle:
        random.shuffle(letters)
    own = set(item["choices"].values())
    shown = []
    result = []
    for index, letter in enumerate(letters):
        text = item["choices"][letter]
        correct = letter in item["answer"]
        if pool and not correct:
            options = [t for t in pool if t not in own and t not in shown]
            if options:
                text = random.choice(options)
        shown.append(text)
        result.append((LETTERS[index], text, correct))
    return result


def history_path():
    override = os.environ.get("CLQ_HISTORY")
    if override:
        return override
    base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "clq", "history.json")


def load_history():
    try:
        with open(history_path(), encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict) and isinstance(data.get("runs"), list):
            return data
    except (OSError, ValueError):
        pass
    return {"runs": []}


def save_run(quiz, results):
    """Append a run to the history file. results is [(question dict, correct bool)]."""
    history = load_history()
    right = sum(1 for _, ok in results if ok)
    history["runs"].append({
        "quiz": quiz,
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "asked": len(results),
        "right": right,
        "wrong": len(results) - right,
        "results": {item["question"]: ok for item, ok in results},
    })
    path = history_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(history, handle, indent=2)
    except OSError as error:
        print("Could not save history to %s: %s" % (path, error), file=sys.stderr)


def missed_questions(history, quiz):
    """Question texts whose most recent recorded result for this quiz was wrong."""
    latest = {}
    for run in history["runs"]:
        if run.get("quiz") == quiz:
            latest.update(run.get("results", {}))
    return {question for question, ok in latest.items() if not ok}


def show_history(quiz):
    runs = [r for r in load_history()["runs"] if not quiz or r.get("quiz") == quiz]
    if not runs:
        print("No history recorded")
        return
    print("%-19s  %-20s  %5s  %5s  %7s" % ("Date", "Quiz", "Asked", "Right", "Percent"))
    for run in runs:
        asked = run.get("asked", 0)
        percent = 100.0 * run.get("right", 0) / asked if asked else 0.0
        print("%-19s  %-20s  %5d  %5d  %6.1f%%" % (
            run.get("time", "").replace("T", " "), run.get("quiz", "")[:20], asked, run.get("right", 0), percent))
    total = sum(r.get("asked", 0) for r in runs)
    right = sum(r.get("right", 0) for r in runs)
    if total:
        print("\n%d runs, %d questions, %.1f%% correct overall" % (len(runs), total, 100.0 * right / total))


def print_results(asked, right, wrong):
    if asked:
        print("\n\nResults:\n")
        print("Questions: %d" % asked)
        print("Correct:   %d" % right)
        print("Wrong:     %d" % wrong)
        print("Percent:   %.1f%%" % (100.0 * right / asked))
    print()


def wrap(text, indent=""):
    return textwrap.fill(text, width=80, subsequent_indent=indent)


def ask_questions(questions, shuffle, pool):
    """Ask each question. Returns ([(question, correct)], quit_early)."""
    results = []
    for item in questions:
        choices = build_choices(item, shuffle, pool)
        correct = sorted(label for label, _, ok in choices if ok)
        valid = [label for label, _, _ in choices]
        print()
        print(wrap(item["question"]))
        print()
        for label, text, _ in choices:
            print("%s%s%s: %s\n" % (BOLD, label.upper(), RESET, wrap(text, "   ")))
        print("Answer? ", end="", flush=True)
        response = []
        try:
            while len(response) < len(correct):
                key = get_key().lower()
                if key in ("q", "\x03", "\x04"):
                    return results, True
                if key in valid and key not in response:
                    response.append(key)
                    print(key, end="", flush=True)
        except EOFError:
            return results, True
        print("\n")
        text = "\n".join(wrap("%s: %s" % (l.upper(), t), "   ") for l, t, ok in choices if ok)
        ok = sorted(response) == correct
        print((GREEN if ok else RED) + text + RESET)
        if item["explanation"]:
            print()
            print(wrap("Explanation: " + item["explanation"], "             "))
        print()
        results.append((item, ok))
    return results, False


def run_quiz(path, args):
    questions = load_quiz(path, args.reverse)
    name = os.path.basename(path)
    pool = sorted({t for q in questions for t in q["choices"].values()}) if args.mix else []
    if args.wrong:
        missed = missed_questions(load_history(), name)
        questions = [q for q in questions if q["question"] in missed]
        if not questions:
            print("No missed questions recorded for %s" % name)
            return
    if args.random:
        random.shuffle(questions)
    if args.number:
        questions = questions[:args.number]
    while True:
        results, quit_early = ask_questions(questions, args.random, pool)
        right = sum(1 for _, ok in results if ok)
        print_results(len(results), right, len(results) - right)
        if results and not args.no_save:
            save_run(name, results)
        missed = [item for item, ok in results if not ok]
        if quit_early or not missed or args.no_retry or not sys.stdin.isatty():
            return
        print("Retry the %d missed question(s)? [y/N] " % len(missed), end="", flush=True)
        key = get_key().lower()
        print(key)
        if key != "y":
            return
        questions = missed
        if args.random:
            random.shuffle(questions)


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return number


def main():
    parser = argparse.ArgumentParser(prog="clq.py", description="Command Line Quiz")
    parser.add_argument("-l", "--list", action="store_true", help="List quizes")
    parser.add_argument("-r", "--random", action="store_true", help="Randomise questions and choices")
    parser.add_argument("-m", "--mix", action="store_true", help="Mix choices between questions")
    parser.add_argument("-q", "--quiz", metavar="QUIZ", help="Quiz (csv, json, yaml, or an Anki deck)")
    parser.add_argument("-i", "--import", dest="import_deck", metavar="DECK",
                        help="Import an Anki deck (.apkg or text export) as a quiz")
    parser.add_argument("--reverse", action="store_true", help="Anki decks: ask the back of each card, answer the front")
    parser.add_argument("-n", "--number", type=positive_int, metavar="N", help="Only ask N questions")
    parser.add_argument("-w", "--wrong", action="store_true", help="Only ask questions last answered wrongly")
    parser.add_argument("--no-retry", action="store_true", help="Do not offer to retry missed questions")
    parser.add_argument("--no-save", action="store_true", help="Do not record results in the history file")
    parser.add_argument("-H", "--history", nargs="?", const="", metavar="QUIZ", help="Show history (optionally for one quiz)")
    parser.add_argument("-V", "--version", action="store_true", help="Print version information")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    if (args.number or args.wrong or args.mix) and not args.quiz:
        parser.error("-n, -w and -m need a quiz (-q)")
    if args.reverse and not (args.quiz or args.import_deck):
        parser.error("--reverse needs a quiz (-q) or an import (-i)")
    if args.version:
        print_version()
        return
    if args.import_deck:
        import_deck(args.import_deck, args.reverse)
    if args.list:
        list_quizzes()
    if args.history is not None:
        show_history(os.path.basename(find_quiz(args.history) or args.history))
    if args.quiz:
        path = find_quiz(args.quiz)
        if not path:
            sys.exit("Quiz %s does not exist" % args.quiz)
        run_quiz(path, args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
