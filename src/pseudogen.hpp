#ifndef PSEUDOGEN_HPP
#define PSEUDOGEN_HPP
#include <algorithm>
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <utility>
#include <vector>

class PseudoGen {
private:
  std::string apply_pgen_rules(std::string line) {
    struct Rule {
      std::regex re;
      std::string rep;
    };
    static const std::vector<Rule> rules = {
        {std::regex(R"(\busing namespace std;?\b)"), ""},
        {std::regex(R"(#include\s*<.*>)"), ""},
        {std::regex(R"(\b(int|bool|string|float|double|char|long)\s+)"), ""},
        {std::regex(R"(\bif\s*\()"), "если "}, // Убрал скобку в замене
        {std::regex(R"(\belse if\b)"), "иначе если "},
        {std::regex(R"(\belse\b)"), "иначе"},
        {std::regex(R"(\bfor\s*\()"), "цикл "},   // Убрал скобку
        {std::regex(R"(\bwhile\s*\()"), "пока "}, // Убрал скобку
        {std::regex(R"(\bcout\s*<<\s*)"), "вывод: "},
        {std::regex(R"(\bcin\s*>>\s*)"), "ввод: "},
        // Экранируем { и } для регулярок и чистим мусор
        {std::regex(R"(std::|;|"|endl|<<|>>|\{|\})"), " "},
        {std::regex(R"(\s*&&\s*)"), " И "},
        {std::regex(R"(\s*\|\|\s*)"), " ИЛИ "}};

    for (const auto &rule : rules) {
      line = std::regex_replace(line, rule.re, rule.rep);
    }

    // Убираем лишние пробелы и финальные скобки С++, которые могли остаться
    line = std::regex_replace(line, std::regex(R"(\)\s*$)"), "");
    line = std::regex_replace(line, std::regex(R"(\s+)"), " ");
    line = std::regex_replace(line, std::regex(R"(^\s+|\s+$)"), "");

    return line;
  }

public:
  std::string output, input, pgen;
  void init_files(std::string input, std::string pgen, std::string output) {
    this->input = input;
    this->pgen = pgen;
    this->output = output;
  }
  void pseudocode() {
    std::ifstream inputFile(this->input);
    std::ifstream pgenFile(this->pgen);
    std::ofstream outputFile(this->output);

    std::string sourceLine;

    std::vector<std::pair<std::regex, std::string>> rules;

    std::string ruleLine;
    while (std::getline(pgenFile, ruleLine)) {
      if (ruleLine.empty())
        continue;
      size_t pos = ruleLine.find("->");

      if (pos != std::string::npos) {
        std::string search = ruleLine.substr(0, pos);
        std::string replace = ruleLine.substr(pos + 2);

        search.erase(std::remove(search.begin(), search.end(), '\"'),
                     search.end());
        replace.erase(std::remove(replace.begin(), replace.end(), '\"'),
                      replace.end());

        // Создаем регулярку. Используем \b для точного поиска слов, если это не
        // спецсимволы
        rules.push_back({std::regex(search), replace});
      }
    }

    while (std::getline(inputFile, sourceLine)) {
      std::string processed = sourceLine;
      for (const auto &rule : rules) {
        processed = std::regex_replace(processed, rule.first, rule.second);
      }
      outputFile << processed << "\n";
    }
  }

  void blockgen_html() {
    std::ifstream file(this->input);
    std::ofstream out(this->output + ".html");

    // "Бессмертный" шаблон с библиотекой внутри
    out << "<!DOCTYPE html>\n<html>\n<head><meta charset='UTF-8'>\n"
        << "<script "
           "src='https://cdn.jsdelivr.net/npm/mermaid@10/dist/"
           "mermaid.min.js'></script>\n"
        << "</head>\n<body>\n<div class='mermaid'>\n  graph TD\n";

    std::string line;
    int id = 0;
    std::vector<int> node_ids;

    while (std::getline(file, line)) {
      // Убираем лишние пробелы
      line = std::regex_replace(line, std::regex("^\\s+|\\s+$"), "");
      if (line.empty() || line == "{" || line == "}")
        continue;

      std::string clean_text = apply_pgen_rules(line);

      // Определяем форму блока Mermaid
      std::string start_cap = "[", end_cap = "]"; // Процесс по умолчанию

      if (line.find("for") != std::string::npos) {
        start_cap = "{{";
        end_cap = "}}"; // Шестиугольник (цикл)
      } else if (line.find("if") != std::string::npos ||
                 line.find("while") != std::string::npos) {
        start_cap = "{";
        end_cap = "}"; // Ромб (условие)
      } else if (line.find("cout") != std::string::npos ||
                 line.find("cin") != std::string::npos) {
        start_cap = "[/";
        end_cap = "/]"; // Параллелограмм (ввод/вывод)
      } else if (line.find("main") != std::string::npos ||
                 line.find("return") != std::string::npos) {
        start_cap = "([";
        end_cap = "])"; // Скругленный (начало/конец)
      }

      out << "    node" << id << start_cap << "\"" << clean_text << "\""
          << end_cap << "\n";
      node_ids.push_back(id);
      id++;
    }

    // Простейшая связь сверху вниз
    for (size_t i = 0; i + 1 < node_ids.size(); ++i) {
      out << "    node" << node_ids[i] << " --> node" << node_ids[i + 1]
          << "\n";
    }

    out << "  </div>\n<script>mermaid.initialize({startOnLoad:true, "
           "theme:'neutral'});</script>\n"
        << "</body>\n</html>";
  }
};
#endif
