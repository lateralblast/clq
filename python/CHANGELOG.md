# Changelog

All notable changes to `clq.py` are documented in this file.

## [0.0.8] - 2026-10-02

- Added --reverse to ask the back of Anki cards and answer with the front

## [0.0.7] - 2026-10-02

- Added Anki deck support: .apkg packages (including zstd compressed) and plain text exports can be used with -q, or converted to a JSON quiz with -i

## [0.0.6] - 2026-10-02

- Added JSON and YAML quiz files (YAML needs the optional PyYAML package), and example.json

## [0.0.5] - 2026-10-02

- Added optional Explanation column, shown after each answer, and the example-explained quiz

## [0.0.4] - 2026-10-02

- Added -w to ask only the questions last answered wrongly, and an offer to retry missed questions after a round (--no-retry to disable)

## [0.0.3] - 2026-10-02

- Added saved results history (~/.local/share/clq/history.json or $CLQ_HISTORY), -H to show it and --no-save to skip recording

## [0.0.2] - 2026-10-02

- Added -n to ask only N questions

## [0.0.1] - 2026-10-02

- Initial python version with the features of the ruby script (list, random, mix, quit and results)
