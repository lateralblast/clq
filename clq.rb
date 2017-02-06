#!/usr/bin/env ruby

# Name:         clq (Command Line Quiz)
# Version:      0.0.8
# Release:      1
# License:      CC-BA (Creative Commons By Attribution)
#               http://creativecommons.org/licenses/by/4.0/legalcode
# Group:        System
# Source:       N/A
# URL:          http://lateralblast.com.au/
# Distribution: UNIX
# Vendor:       UNIX
# Packager:     Richard Spindler <richard@lateralblast.com.au>
# Description:  A POC ruby script to turn a formatted csv file into multiple choice quiz

require 'rubygems'
require 'io/console'

def install_gem(load_name,install_name)
  puts "Information:\tInstalling #{install_name}"
  %x[gem install #{install_name}]
  Gem.clear_paths
  require "#{load_name}"
end

begin
  require 'getopt/long'
rescue LoadError
  install_gem("getopt/long","getopt")
end
begin
  require 'smarter_csv'
rescue LoadError
  install_gem('smarter_csv','smarter_csv')
end
begin
  require 'colorize'
rescue LoadError
  install_gem('colorize','colorize')
end

class String
  def wrap_text(col = 80)
    gsub(/(.{1,#{col}})( +|$)\n?|(.{#{col}})/,"\\1\\3\n")
  end
  def wrap_text_with_indent(col = 80, indent = "   ")
    gsub(/(.{1,#{col}})( +|$)\n?|(.{#{col}})/,"\\1\\3\n#{indent}")
  end
end

include Getopt

# Set some defaults

$quiz_dir = "quizes"
$script   = $0

# Print script usage information

def print_usage()
  switches     = []
  long_switch  = ""
  short_switch = ""
  help_info    = ""
  puts ""
  puts "Usage: #{$script}"
  puts ""
  file_array  = IO.readlines $0
  option_list = file_array.grep(/\[ "--/)
  option_list.each do |line|
    if !line.match(/file_array/)
      help_info    = line.split(/# /)[1]
      switches     = line.split(/,/)
      long_switch  = switches[0].gsub(/\[/,"").gsub(/\s+/,"")
      short_switch = switches[1].gsub(/\s+/,"")
      if short_switch.match(/REQ|BOOL/)
        short_switch = ""
      end
      if long_switch.gsub(/\s+/,"").length < 7
        puts "#{long_switch},\t\t#{short_switch}\t#{help_info}"
      else
        puts "#{long_switch},\t#{short_switch}\t#{help_info}"
      end
    end
  end
  puts ""
  return
end

# Get version

def get_version()
  file_array = IO.readlines $0
  version    = file_array.grep(/^# Version/)[0].split(":")[1].gsub(/^\s+/,'').chomp
  packager   = file_array.grep(/^# Packager/)[0].split(":")[1].gsub(/^\s+/,'').chomp
  name       = file_array.grep(/^# Name/)[0].split(":")[1].gsub(/^\s+/,'').chomp
  return version,packager,name
end

# Print script version information

def print_version()
  (version,packager,name) = get_version()
  puts "#{name} v. #{version} #{packager}"
  return
end

# Get command line arguments
# Print help if specified none

if !ARGV[0]
  print_usage()
end

# List quizes

def list_quizes
  puts "Available quizes:"
  list = %x[ls #{$quiz_dir}]
  puts list
end

# Print results

def print_results(no_quest,no_right,no_wrong)
  if no_quest != 0
    percent = ( no_right.to_f / no_quest.to_f ) * 100
    percent = percent.round(1)
    puts ""
    puts ""
    puts "Results:"
    puts ""
    puts "Questions: "+no_quest.to_s
    puts "Correct:   "+no_right.to_s
    puts "Wrong:     "+no_wrong.to_s
    puts "Percent:   "+percent.to_s+"%"
  end
  puts ""
  return
end

# Handle quizes

def handle_quiz(quiz_file,random,mix)
  no_right = 0
  no_wrong = 0
  no_quest = 0
  if !File.exist?(quiz_file)
    test_file = $quiz_dir+"/"+quiz_file
    if !File.exist?(test_file)
      puts "Quiz "+quiz_file+" does not exist"
      exit
    else
      quiz_file = test_file
    end
  end
  quiz_data = SmarterCSV.process(quiz_file,:col_sep => "|")
  if random == true
    quiz_data = quiz_data.shuffle
  end
  if mix == true
    q_mix = []
    quiz_data.each do |key, value|
      [ 'a', 'b', 'c', 'd', 'e' ].each do |letter|
        q_mix.push(key[:"#{letter}"])
      end
    end
  end
  quiz_data.each do |key, value|
    r_correct = []
    answer    = ""
    correct   = key[:answer].downcase.gsub(/,| /,"").chars.sort.join
    question  = key[:question]
    question  = question.wrap_text
    puts
    puts question
    puts
    if random == true
      counter = 0
      [ 'a', 'b', 'c', 'd', 'e' ].shuffle.each do |letter|
        if key[:"#{letter}"]
          choice  = "a".ord+counter
          choice  = choice.chr
          counter = counter + 1
          line    = ""
          if correct.match(/#{letter}/)
            r_correct.push(choice)
            if answer.length < 1
              answer = choice.upcase+": "+key[:"#{letter}"]
            else
              answer = answer+" - "+choice.upcase+": "+key[:"#{letter}"]
            end
            line = choice.upcase.bold+": "+key[:"#{letter}"].wrap_text_with_indent
          else
            if mix == true
              text = q_mix.sample
              while text.match(/key[:"#{letter}"]/)
                text = q_mix.sample
              end
              line = choice.upcase.bold+": "+text.wrap_text_with_indent
            else 
              line = choice.upcase.bold+": "+key[:"#{letter}"].wrap_text_with_indent
            end
          end
          puts line
        end
      end
      correct = r_correct.join
    else
      [ 'a', 'b', 'c', 'd', 'e' ].each do |letter|
        line = ""
        if key[:"#{letter}"]
          if correct.match(/#{letter}/)
            if answer.length < 1
              answer = letter.upcase+": "+key[:"#{letter}"]
            else
              answer = answer+" - "+letter.upcase+": "+key[:"#{letter}"]
            end
            line = letter.upcase.bold+": "+key[:"#{letter}"].wrap_text_with_indent
          else
            if mix == true
              text = q_mix.sample
              while text.match(/key[:"#{letter}"]/)
                text = q_mix.sample
              end
              line = letter.upcase.bold+": "+text.wrap_text_with_indent
            else
              line = letter.upcase.bold+": "+key[:"#{letter}"].wrap_text_with_indent
            end
          end
          puts line
        end
      end
    end
    puts
    print "Answer? "
    response = ""
    while response.length < correct.length
      input = STDIN.getch.chomp.downcase.gsub(/,| /,"").chars.sort.join
      print input
      if input.match(/q/)
        print_results(no_quest,no_right,no_wrong)
        exit
      end
      if input.match(/[a-e]/)
        response = response+input
      end
    end
    puts
    puts
    no_quest = no_quest + 1
    if response == correct
      no_right = no_right + 1
      puts answer.green
    else
      no_wrong = no_wrong + 1
      puts answer.red
    end
  end
  print_results(no_quest,no_right,no_wrong)
  return
end

# Process options

begin
  option = Long.getopts(
    [ "--list",    "-l", BOOLEAN ],  # List quizes
    [ "--random",  "-r", BOOLEAN ],  # Randomise quizes
    [ "--mix",     "-m", BOOLEAN ],  # Mix choices between questions
    [ "--quiz",    "-q", REQUIRED ], # Quiz
    [ "--help",    "-h", BOOLEAN ],  # Print help information
    [ "--version", "-V", BOOLEAN ]   # Print version information
  )
rescue
  print_usage()
  exit
end

if option["l"]
  list_quizes()
end

if option["h"]
  print_usage()
end

if option["V"]
  print_version()
end

# Ask questions in random order

if option ["r"]
  random = true
else
  random = false
end

# Mix choices between questions

if option ["m"]
  mix = true
else
  mix = false
end

if option["q"]
  handle_quiz(option["q"],random,mix)
end
