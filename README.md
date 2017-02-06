![alt tag](https://raw.githubusercontent.com/lateralblast/clq/master/clq.jpg)

CLQ
===

Command Line Quiz

Introduction
------------

A simple shell and ruby script that converts a formatted CSV file into a multiple choice quiz.

Shell script: clq.sh

Ruby script: clq.rb

Supported Operating Systems
---------------------------

Any operating system with sh/bash or ruby

License
-------

This software is licensed as CC-BA (Creative Commons By Attrbution)

http://creativecommons.org/licenses/by/4.0/legalcode

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
$ ./clq.sh -h

Usage: ./clq.sh -[h|V|q] [quiz]

-h:        Print usage
-V:        Print version
-q [quiz]: Quiz (ask questions in sequential order)
-r [quiz]: Quiz (ask questions in random order)
```

List available quizes:

```
$ ./clq.sh -l
Available quizes:
example
```

Do the multiple choice quiz example:

```
$ ./clq.sh -q example
```

Ask questions in random order:

```
$ ./clq.sh -r example
```

Ruby Script Usage Information
-----------------------------

Get help:

```
$ ./clq.rb -h

Usage: ./clq.rb

"--list",     "-l"  List quizes
"--random",   "-r"  Randomise quizes
"--mix",      "-m"  Mix choices between questions
"--quiz",     "-q"  Quiz
"--help",     "-h"  Print help information
"--version",  "-V"  Print version information
```

List available quizes:

```
$ ./clq.rb -l
Available quizes:
example
```

Do the multiple choice quiz example:

```
$ ./clq.rb -q example
```

Ask questions in random order:

```
$ ./clq.rb -q example -r
```

Ask questions in random order and mix choices between questions

```
$ ./clq.rb -q example -r -m
```

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
$ ./clq.sh -l
Available quizes:
example
```

Do the multiple choice quiz example:

```
$ ./clq.sh -q example

Amazon Glacier is designed for: (Choose 2 answers)

A: active database storage.
B: infrequently accessed data.
C: data archives.
D: frequently accessed data.
E: cached session data.

Answer? bc

B - infrequently accessed data. C - data archives.

Your web application front end consists of multiple EC2 instances behind an
Elastic Load Balancer. You configured ELB to perform health checks on these EC2
instances. If an instance fails to pass health checks, which statement will be
true?

A: The instance is replaced automatically by the ELB.
B: The instance gets terminated automatically by the ELB.
C: The ELB stops sending traffic to the instance that failed its health check.
D: The instance gets quarantined by the ELB for root cause analysis.

Answer? g

C - The ELB stops sending traffic to the instance that failed its health check.

You are building a system to distribute confidential training videos to
employees. Using CloudFront, what method could be used to serve content that is
stored in S3, but not publically accessible from S3 directly?

A: Create an Origin Access Identity (OAI) for CloudFront and grant access to the
objects in your S3 bucket to that OAI.
B: Add the CloudFront account security group “amazon-cf/amazon-cf-sg” to the
appropriate S3 bucket policy.
C: Create an Identity and Access Management (IAM) User for CloudFront and grant
access to the objects in your S3 bucket to that IAM User.
D: Create a S3 bucket policy that lists the CloudFront distribution ID as the
Principal and the target bucket as the Amazon Resource Name (ARN).

Answer? g

A - Create an Origin Access Identity (OAI) for CloudFront and grant access to the objects in your S3 bucket to that OAI.


Results:

Questions: 3
Correct:   1
Wrong:     2
Percent:   33%
```