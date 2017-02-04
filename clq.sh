#!/bin/sh

# Name:         clq (Command Line Quiz)
# Version:      0.0.2
# Release:      1
# License:      CC-BA (Creative Commons By Attribution)
#               http://creativecommons.org/licenses/by/4.0/legalcode
# Group:        System
# Source:       N/A
# URL:          http://lateralblast.com.au/
# Distribution: UNIX
# Vendor:       UNIX
# Packager:     Richard Spindler <richard@lateralblast.com.au>
# Description:  A POC shell script to turn a formatted csv file into multiple choice quiz

# Get command line args

args=$@

# Set some defaults

quiz_dir="quizes"
text_green="\e[0;32m"
text_red="\e[0;31m"
text_white="\e[0;37m"

# Get the path the script starts from

start_path=`pwd`

# Get the version of the script from the script itself

script_version=`cd $start_path ; cat $0 | grep '^# Version' |awk '{print $3}'`

# Get the script name

script_name=`cd $start_path ; cat $0 | grep '^# Name' |awk '{print $3}'`

# print_usage
#
# If given a -h or no valid switch print usage information

print_usage () {
  echo ""
  echo "Usage: $0 -[h|V|q] [quiz]"
  echo ""
  echo "-h:        Print usage"
  echo "-V:        Print version"
  echo "-q [quiz]: Quiz (ask questions in sequential order)"
  echo "-r [quiz]: Quiz (ask questions in random order)"
  echo ""
}

# If given no command line arguments print usage information

if [ `expr "$args" : "\-"` != 1 ]; then
  print_usage
fi

# List quizes

list_quizes () {
  echo "Available quizes:"
  ls $quiz_dir
}

# Get ASCII value for letter

ord() {
  LC_CTYPE=C printf '%d' "'$1"
}

# Print results

print_results () {
  no_questions=$1
  no_correct=$2
  no_wrong=$3
  percent=$(awk "BEGIN { pc=100*$no_correct/$no_questions; i=int(pc); print (pc-i<0.5)?i:i+1 }")
  echo ""
  echo ""
  echo "Results:"
  echo ""
  echo "Questions: $no_questions"
  echo "Correct:   $no_correct"
  echo "Wrong:     $no_wrong"
  echo "Percent:   $percent%"
  echo ""
}

# Handle quiz

handle_quiz () {
  quiz_file=$1
  random=$2
  printf $text_white
  if [ ! -f "$quiz_file" ]; then
    orig_file="$quiz_file"
    quiz_file="$quiz_dir/$orig_file"
    if [ ! -f "$quiz_file" ]; then
      echo "Cannot find quiz: $orig_file"
      exit
    fi
  fi 
  no_questions=0
  no_correct=0
  no_wrong=0
  header=`cat $quiz_file |grep "^Question"`
  header_a=`echo "$header" |cut -f3 -d'|'`
  header_b=`echo "$header" |cut -f4 -d'|'`
  header_c=`echo "$header" |cut -f5 -d'|'`
  header_d=`echo "$header" |cut -f6 -d'|'`
  header_e=`echo "$header" |cut -f7 -d'|'`
  if [ "$random" -eq 1 ]; then
    quiz_data=`cat $quiz_file |awk 'BEGIN{srand();} {printf "%06d %s\n", rand()*1000000, $0;}' | sort -n | cut -c8-`
  else
    quiz_data=`cat $quiz_file`
  fi
  while read -r line <&3; do
    if [ ! "$line" = "" ]; then
      question=`echo "$line" |cut -f1 -d'|'`
      if [ ! "$question" = "Question" ]; then
        echo ""
        echo "$question" |fmt -w 80
        echo ""
        correct=`echo "$line" |cut -f2 -d'|' |sed 's/[ ,\,]//g' |tr "[:upper:]" "[:lower:]"`
        answer=""
        for counter in $(seq 1 ${#correct}); do
          char=${correct:counter-1:1}
          ascii=$(ord $char)
          field=`expr $ascii - 94`
          char=`echo $char |tr "[:lower:]" "[:upper:]"`
          string=`echo "$line" |cut -f$field -d'|'`
          if [ "$answer" = "" ]; then
            answer="$char - $string"
          else
            answer="$answer $char - $string"
          fi
        done
        chars=`echo "$correct" |wc -c`
        chars=`expr $chars - 1`
        choice_a=`echo "$line" |cut -f3 -d'|'`
        if [ ! "$choice_a" = "" ]; then
          string="$header_a: $choice_a"
          echo "$string" |fmt -w 80
        fi
        choice_b=`echo "$line" |cut -f4 -d'|'`
        if [ ! "$choice_b" = "" ]; then
          string="$header_b: $choice_b"
          echo "$string" |fmt -w 80
        fi
        choice_c=`echo "$line" |cut -f5 -d'|'`
        if [ ! "$choice_c" = "" ]; then
          string="$header_c: $choice_c"
          echo "$string" |fmt -w 80
        fi
        choice_d=`echo "$line" |cut -f6 -d'|'`
        if [ ! "$choice_d" = "" ]; then
          string="$header_d: $choice_d"
          echo "$string" |fmt -w 80
        fi
        choice_e=`echo "$line" |cut -f7 -d'|'`
        if [ ! "$choice_e" = "" ]; then
          string="$header_e: $choice_e"
          echo "$string" |fmt -w 80
        fi
        echo ""
        read -p "Answer? " -n$chars response
        response=`echo "$response" | tr "[:upper:]" "[:lower:]"`
        if [ "$response" = "q" ]; then
          print_results $no_questions $no_correct $no_wrong
          exit
        fi
        if [ "$response" = "$correct" ]; then
          no_correct=`expr $no_correct + 1`
          text_colour=$text_green
        else
          no_wrong=`expr $no_wrong + 1`
          text_colour=$text_red
        fi
        no_questions=`expr $no_questions + 1`
        echo ""
        echo ""
        printf "$text_colour$answer$text_white"
        echo ""
      fi
    fi
  done 3<<< "$quiz_data"
  print_results $no_questions $no_correct $no_wrong
}

while getopts hlrVq: args; do
  case $args in
    l)
      list_quizes
      ;;
    r)
      quiz_file=$2
      random=1
      handle_quiz $quiz_file $random
      exit
      ;;
    q)
      quiz_file=$2
      random=0
      handle_quiz $quiz_file $random
      exit
      ;;
    h)
      print_usage
      ;;
    V)
      echo $script_version
      exit
      ;;
    *)
      print_usage
      exit
  esac
done

