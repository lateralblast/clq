#!/usr/bin/env xcrun swift

// Name:         clq (Command Line Quiz)
// Version:      0.0.2
// Release:      1
// License:      CC-BA (Creative Commons By Attribution)
//               http://creativecommons.org/licenses/by/4.0/legalcode
// Group:        System
// Source:       N/A
// URL:          http://lateralblast.com.au/
// Distribution: UNIX
// Vendor:       UNIX
// Packager:     Richard Spindler <richard@lateralblast.com.au>
// Description:  A POC swift code to turn a formatted csv file into multiple choice quiz

import Darwin
import Foundation

extension Array {
  func shuffled() -> [Element] {
    var results = [Element]()
    var indexes = (0 ..< count).map { $0 }
    while indexes.count > 0 {
      let indexOfIndexes = Int(arc4random_uniform(UInt32(indexes.count)))
      let index = indexes[indexOfIndexes]
      results.append(self[index])
      indexes.remove(at: indexOfIndexes)
    }
    return results
  }
}
    

let script = CommandLine.arguments[0]

func file_to_array(file: String) -> [String] {
  let path = NSString(string: file).expandingTildeInPath
  if let text = try? String(contentsOfFile:path, encoding: String.Encoding.utf8) {
    let lines = text.components(separatedBy: "\n")
    return lines
  }
  else {
    return []
  }
} 

func print_usage(file: String) -> Void {
  print("")
  print("Usage \(file)")
  print("")
  let lines = file_to_array(file: file)
  for line in lines {
    if var _ = line.range(of: "-[a-z,A-Z]", options: .regularExpression) {
      if line.range(of: "License|regularExpression", options: .regularExpression) == nil {
        var output = line.replacingOccurrences(of: "case", with: "")
        output     = output.replacingOccurrences(of: "// ", with: "")
        output     = output.replacingOccurrences(of: "^\\s+", with: "", options: .regularExpression)
        print(output)
      }
    }
  }
  print("")
  exit(0)
}

func print_version(file: String) -> Void {
  let lines = file_to_array(file: file)
  for line in lines {
    if var _ = line.range(of: "^// Version", options: .regularExpression) {
      var version = line.components(separatedBy: ":")[1]
      version     = version.replacingOccurrences(of: " ", with: "")
      print(version)
    }
  }
  exit(0)
}

func list_quizes() -> Void {
  print("Available quizes:")
  let fd = FileManager.default
  fd.enumerator(atPath: "quizes")?.forEach({ (e) in
    if let e = e as? String, let url = URL(string: e) {
        print(url)
    }
  })
  exit(0)
}

func wrap_text(text: String, indent: String) -> String {
  var count = 0
  let fields = text.components(separatedBy: " ")
  var array  = [String]()
  for field in fields {
    let length = field.characters.count
    if count + length < 80 {
      array.append("\(field) ")
      count = count + length
    }
    else {
      array.append("\(field)\n\(indent)")
      count = 0
    }
  }
  let result = array.joined(separator: "")
  return result
}

func sort_answer(text: String) -> String {
  var result = text.replacingOccurrences(of: " |,", with: "", options: .regularExpression)
  var array  = Array(result.characters)
  array      = array.sorted { $0 < $1 }
  result     = array.map({String(describing: $0)}).joined(separator: "")
  return result
}

func print_results(no_quest: Int, no_right: Int, no_wrong: Int) -> Void {
  let white = "\u{001B}[0;37m"
  var percentage :Double = 0
  if no_quest != 0 {
    percentage = (Double(no_right) / Double(no_quest)) * 100
    percentage = Double(round(10*percentage)/10)
  }
  print("\(white)")
  print("Results:")
  print("")
  print("Questions:  \(no_quest)")
  print("Correct:    \(no_right)")
  print("Wrong:      \(no_wrong)")
  if no_quest != 0 {
    print("Percentage: \(percentage)")
  }
  print("")
  exit(0)
}

func handle_quiz(file: String, random: Int) -> Void {
  var no_quest = 0
  var no_right = 0
  var no_wrong = 0
  let green    = "\u{001B}[0;32m"
  let red      = "\u{001B}[0;31m"
  let white    = "\u{001B}[0;37m"
  var lines    = file_to_array(file: file)
  if random == 1 {
    lines = lines.shuffled()
  }
  for line in lines {
    if line.characters.count > 0 {
      if var _ = line.range(of: "|", options: .regularExpression) {
        if let fields = line.components(separatedBy: "|") as [String]? {
          if var question = fields[0] as String? {
            if question != "Question" {
              var answer  = fields[1]
              answer      = sort_answer(text: answer)
              answer      = answer.lowercased()
              var array   = [String]()
              let letters = Array(answer.characters)
              for letter in letters {
                let upper = String(letter).uppercased()
                let value = String(letter).unicodeScalars.first?.value
                var count: Int = Int(value!)
                count      = count - 95
                var string = fields[count]
                string     = "\(upper): \(string)"
                string     = wrap_text(text: string, indent: "   ")
                array.append(string)
              }
              let correct = array.map({String(describing: $0)}).joined(separator: "")
              question    = wrap_text(text: question, indent: "")
              print("\(white)\(question)")
              print("")
              if var choice_a = fields[2] as String? {
                if var _ = choice_a.range(of: "[A-Z,a-z,0-9]", options: .regularExpression) {
                  choice_a = wrap_text(text: choice_a, indent: "   ")
                  print("A: \(choice_a)")
                }
              }
              if var choice_b = fields[3] as String? {
                if var _ = choice_b.range(of: "[A-Z,a-z,0-9]", options: .regularExpression) {
                  choice_b = wrap_text(text: choice_b, indent: "   ")
                  print("B: \(choice_b)")
                }
              }
              if var choice_c = fields[4] as String? {
                if var _ = choice_c.range(of: "[A-Z,a-z,0-9]", options: .regularExpression) {
                  choice_c = wrap_text(text: choice_c, indent: "   ")
                  print("C: \(choice_c)")
                }
              }
              if var choice_d = fields[5] as String? {
                if var _ = choice_d.range(of: "[A-Z,a-z,0-9]", options: .regularExpression) {
                  choice_d = wrap_text(text: choice_d, indent: "   ")
                  print("D: \(choice_d)")
                }
              }
              if var choice_e = fields[6] as String? {
                if var _ = choice_e.range(of: "[A-Z,a-z,0-9]", options: .regularExpression) {
                  choice_e = wrap_text(text: choice_e, indent: "   ")
                  print("E: \(choice_e)")
                }
              }
              print("")
              print("Answer: ", terminator: "")
              var response = readLine()
              response = response!.lowercased()
              response = sort_answer(text: response!)
              no_quest = no_quest + 1
              switch response! {
                case "q", "quit", "exit":
                  no_quest = no_quest - 1
                  print_results(no_quest: no_quest, no_right: no_right, no_wrong: no_wrong)
                case answer:
                  print("")
                  print("\(green)\(correct)")
                  no_right = no_right + 1
                default:
                  print("")
                  print("\(red)\(correct)")
                  no_wrong = no_wrong + 1
              }
            }
          }
          print("")
        }
      }
    }
  }
  print_results(no_quest: no_quest, no_right: no_right, no_wrong: no_wrong)
  print("")
}

if CommandLine.arguments.count == 1 {
  print_usage(file: script) 
}

var argument = CommandLine.arguments[1]

switch argument {
  case "h", "-h": // Print Usage
    print_usage(file: script)
  case "V", "-V": // Print Version
    print_version(file: script)
  case "l", "-l": // List Quizes
    list_quizes()
  case "q", "-q": // Perform quiz
    if CommandLine.arguments.count > 2 {
      var quiz   = CommandLine.arguments[2]
      var random = 0
      if quiz.range(of: "quizes/", options: .regularExpression) == nil {
        quiz = "quizes/\(quiz)"
      }
      if CommandLine.arguments.count == 4 {
        let mode = CommandLine.arguments[3] 
        switch mode {
          case "s", "-s", "--shuffle":
            random = 1
          case "r", "-r", "--random":
            random = 2
          default:
            random = 0
        }
      }
      else {
        random = 0
      }
      handle_quiz(file: quiz, random: random)
    }
    else {
      print("No quiz specified")
    }
  default:
    print_usage(file: script);
}

