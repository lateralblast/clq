![alt tag](https://raw.githubusercontent.com/lateralblast/clq/master/clq.jpg)

CLQ
===

Command Line Quiz

Introduction
------------

A simple shell and ruby script that converts a formatted CSV file into a multiple choice quiz.

Shell script: shell/clq.sh

Ruby script: ruby/clq.rb

Python script: python/clq.py (Python 3, no dependencies; see python/requirements.txt)

Swift script: swift/clq.swift (macOS and Linux)

Run the scripts from the repository root so the `quizes` directory is found.

Supported Operating Systems
---------------------------

Any operating system with sh/bash or ruby

License
-------

This software is licensed as CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike). See the LICENSE file.

https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode

Features
--------

Some of the features:

- Doesn't wait for enter key to be pressed increasing speed users can go through questions
- Responds with correct answer, coloring the text green if the answer was correct or red if it wasn't
- Has support for multiple answer questions (i.e. choose to or more correct answers)
- Keeps track of correct and wrong answers providing a tally at the end
- Allows quiting at anytime with 'q'
- Ability to ask questions in random order
- Ability to mix choices from other questions
  - Handy for learning vocabulary where you want to mix things up and avoid pattern recognition
  - Not necessarily handy for quiz with disparate questions types as the outliers are obvious


Shell Script Usage Information
------------------------------

Get help:

```
$ ./shell/clq.sh -h

Usage: ./shell/clq.sh -[h|V|q] [quiz]

-h:        Print usage
-V:        Print version
-q [quiz]: Quiz (ask questions in sequential order)
-r [quiz]: Quiz (ask questions in random order)
```

List available quizes:

```
$ ./shell/clq.sh -l
Available quizes:
example
```

Do the multiple choice quiz example:

```
$ ./shell/clq.sh -q example
```

Ask questions in random order:

```
$ ./shell/clq.sh -r example
```

Ruby Script Usage Information
-----------------------------

The Ruby script needs the gems listed in `ruby/Gemfile` (getopt, smarter_csv, colorize).
It installs them itself if missing, or install them with Bundler:

```
$ bundle install --gemfile=ruby/Gemfile
$ BUNDLE_GEMFILE=ruby/Gemfile bundle exec ruby ruby/clq.rb -q example
```

Get help:

```
$ ./ruby/clq.rb -h

Usage: ./ruby/clq.rb

"--list",     "-l"  List quizes
"--random",   "-r"  Randomise quizes
"--mix",      "-m"  Mix choices between questions
"--quiz",     "-q"  Quiz
"--help",     "-h"  Print help information
"--version",  "-V"  Print version information
```

List available quizes:

```
$ ./ruby/clq.rb -l
Available quizes:
example
```

Do the multiple choice quiz example:

```
$ ./ruby/clq.rb -q example
```

Ask questions in random order:

```
$ ./ruby/clq.rb -q example -r
```

Ask questions in random order and mix choices between questions

```
$ ./ruby/clq.rb -q example -r -m
```

Python Script Usage Information
------------------------------

Same options as the Ruby script (`-l`, `-q`, `-r`, `-m`, `-V`), plus:

```
-n N          Only ask N questions
-w            Only ask questions last answered wrongly
-H [quiz]     Show saved results history
-i DECK       Import an Anki deck as a JSON quiz
--reverse     Anki decks: ask the back, answer the front
--no-retry    Do not offer to retry missed questions
--no-save     Do not record results in the history file
```

```
$ ./python/clq.py -q example -r -m -n 10
$ ./python/clq.py -q example -w
$ ./python/clq.py -H example
```

Results are saved to `~/.local/share/clq/history.json` (override with `CLQ_HISTORY`).
After a round, the script offers to retry the questions you missed.

An optional `Explanation` column after `E` in a CSV quiz is shown after each answer
(see `quizes/example-explained`). Quizes can also be JSON (see `quizes/example.json`)
or YAML, which needs `pip install -r python/requirements.txt`. Each question has
`question`, `answer` (`"b"` or `["b", "c"]`), `choices` (a list in A-E order or a
mapping) and an optional `explanation`.

Anki decks can be used directly, or imported as a quiz:

```
$ ./python/clq.py -q mydeck.apkg -r -n 20
$ ./python/clq.py -i mydeck.apkg        # writes quizes/mydeck.json
$ ./python/clq.py -q mydeck.apkg --reverse
```

Both `.apkg` packages and Anki plain text exports (`.txt`, tab separated by default)
are supported. Flashcards have no wrong answers, so each card becomes a question with
its back as the answer and the backs of other cards as the wrong choices. `--reverse`
asks the back and answers with the front. Cloze and other non front/back notes are
skipped. Media is ignored. New format packages are zstd compressed, which needs
Python 3.14 or `pip install zstandard`, or export with "Support older Anki versions".

Run the tests with `python3 python/test_clq.py`.

Question File Information
-------------------------

This script uses a CSV file to generate a set of multi-choice questions.

It uses the pipe "|" symbol as a delimiter.

The header, and format of the CSV file is as follows:

```
Question|Answer|A|B|C|D|E
```

The header must be included as the first line of the CSV file.

An example of a file:

```
Question|Answer|A|B|C|D|E
Amazon Glacier is designed for: (Choose 2 answers)|B,C|active database storage.|infrequently accessed data.|data archives.|frequently accessed data.|cached session data.
Your web application front end consists of multiple EC2 instances behind an Elastic Load Balancer. You configured ELB to perform health checks on these EC2 instances. If an instance fails to pass health checks, which statement will be true?|C|The instance is replaced automatically by the ELB.|The instance gets terminated automatically by the ELB.|The ELB stops sending traffic to the instance that failed its health check.|The instance gets quarantined by the ELB for root cause analysis.|
You are building a system to distribute confidential training videos to employees. Using CloudFront, what method could be used to serve content that is stored in S3, but not publically accessible from S3 directly?|A|Create an Origin Access Identity (OAI) for CloudFront and grant access to the objects in your S3 bucket to that OAI.|Add the CloudFront account security group “amazon-cf/amazon-cf-sg” to the appropriate S3 bucket policy.|Create an Identity and Access Management (IAM) User for CloudFront and grant access to the objects in your S3 bucket to that IAM User.|Create a S3 bucket policy that lists the CloudFront distribution ID as the Principal and the target bucket as the Amazon Resource Name (ARN).|
```

From this example we can see the first question allows two answers, B and C.
In this case the user would enter 'bc' when asked for an answer.

The second question has C as the correct answer

Examples
--------

List available quizes:

```
$ ./shell/clq.sh -l
Available quizes:
example
```

Do the multiple choice quiz example in random order and mix choices amongst questions:

```
$ ./ruby/clq.rb -q example -m -r

Your web application front end consists of multiple EC2 instances behind an
Elastic Load Balancer. You configured ELB to perform health checks on these EC2
instances. If an instance fails to pass health checks, which statement will be
true?

A: The instance gets quarantined by the ELB for root cause analysis.

B: Create an Origin Access Identity (OAI) for CloudFront and grant access to the
   objects in your S3 bucket to that OAI.

C: The instance gets terminated automatically by the ELB.

D: The ELB stops sending traffic to the instance that failed its health check.


Answer? d

D: The ELB stops sending traffic to the instance that failed its health check.


You are building a system to distribute confidential training videos to
employees. Using CloudFront, what method could be used to serve content that is
stored in S3, but not publically accessible from S3 directly?

A: cached session data.

B: active database storage.

C: Create an Origin Access Identity (OAI) for CloudFront and grant access to the
   objects in your S3 bucket to that OAI.

D: The instance gets quarantined by the ELB for root cause analysis.


Answer? c

C: Create an Origin Access Identity (OAI) for CloudFront and grant access to the
objects in your S3 bucket to that OAI.


Amazon Glacier is designed for: (Choose 2 answers)

A: Create an Identity and Access Management (IAM) User for CloudFront and grant
   access to the objects in your S3 bucket to that IAM User.

B: infrequently accessed data.

C: Create a S3 bucket policy that lists the CloudFront distribution ID as the
   Principal and the target bucket as the Amazon Resource Name (ARN).

D: data archives.

E: Create an Origin Access Identity (OAI) for CloudFront and grant access to the
   objects in your S3 bucket to that OAI.


Answer? bd

B: infrequently accessed data.
D: data archives.



Results:

Questions: 3
Correct:   3
Wrong:     0
Percent:   100.0%
```

Help Support Development
------------------------

If you find this software useful and would like to support its development, please consider buying me a coffee:

https://ko-fi.com/richardatlateralblast
