#!/usr/bin/env python3

# Name:         clq (Command Line Quiz)
# Version:      0.0.1
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
import os
import random
import re
import sys
import textwrap

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
        candidate = os.path.join(path, name)
        if os.path.isfile(candidate):
            return candidate
    return None


def load_quiz(path):
    """Return a list of questions: {question, answer, choices: {letter: text}}."""
    questions = []
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="|", quoting=csv.QUOTE_NONE)
        header = next(reader, None)
        if not header or header[0].strip().lower() != "question":
            sys.exit("Quiz %s is missing the Question|Answer|A|B|C|D|E header" % path)
        for row in reader:
            if len(row) < 3 or not row[0].strip():
                continue
            row = row + [""] * (2 + len(LETTERS) - len(row))
            choices = {l: row[2 + i].strip() for i, l in enumerate(LETTERS) if row[2 + i].strip()}
            answer = "".join(sorted(set(re.sub(r"[,\s]", "", row[1].lower())) & set(choices)))
            if not answer:
                print("Skipping question with no valid answer: %s" % row[0].strip(), file=sys.stderr)
                continue
            questions.append({"question": row[0].strip(), "answer": answer, "choices": choices})
    return questions


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


def run_quiz(path, shuffle, mix):
    questions = load_quiz(path)
    if shuffle:
        random.shuffle(questions)
    pool = []
    if mix:
        pool = sorted({t for q in questions for t in q["choices"].values()})
    asked = right = wrong = 0
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
                    print_results(asked, right, wrong)
                    return
                if key in valid and key not in response:
                    response.append(key)
                    print(key, end="", flush=True)
        except EOFError:
            print_results(asked, right, wrong)
            return
        print("\n")
        text = "\n".join(wrap("%s: %s" % (l.upper(), t), "   ") for l, t, ok in choices if ok)
        asked += 1
        if sorted(response) == correct:
            right += 1
            print(GREEN + text + RESET)
        else:
            wrong += 1
            print(RED + text + RESET)
        print()
    print_results(asked, right, wrong)


def main():
    parser = argparse.ArgumentParser(prog="clq.py", description="Command Line Quiz")
    parser.add_argument("-l", "--list", action="store_true", help="List quizes")
    parser.add_argument("-r", "--random", action="store_true", help="Randomise questions and choices")
    parser.add_argument("-m", "--mix", action="store_true", help="Mix choices between questions")
    parser.add_argument("-q", "--quiz", metavar="QUIZ", help="Quiz")
    parser.add_argument("-V", "--version", action="store_true", help="Print version information")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    if args.version:
        print_version()
        return
    if args.list:
        list_quizzes()
    if args.quiz:
        path = find_quiz(args.quiz)
        if not path:
            sys.exit("Quiz %s does not exist" % args.quiz)
        run_quiz(path, args.random, args.mix)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
