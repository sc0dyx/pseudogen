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

  void blockgen() {
    std::ifstream file(this->input);
    std::ofstream out(this->output);
    std::string line;
    struct BlockData {
      std::string text, type;
      int y;
    };
    std::vector<BlockData> v_blocks;

    int currentY = 100;
    while (std::getline(file, line)) {
      line = std::regex_replace(line, std::regex("^\\s+|\\s+$"), ""); // trim
      if (line.empty() || line.find("#include") != std::string::npos ||
          line.find("using namespace") != std::string::npos || line == "{" ||
          line == "}")
        continue;

      // Жесткое экранирование для JSON
      std::string escaped = "";
      for (char c : line) {
        if (c == '\"')
          escaped += "\\\"";
        else if (c == '\\')
          escaped += "\\\\";
        else
          escaped += c;
      }

      std::string type = "Процесс";
      if (std::regex_search(line, std::regex("\\b(if|while|for|switch)\\b")))
        type = "Условие";
      else if (line.find("main") != std::string::npos ||
               line.find("return") != std::string::npos)
        type = "Начало / конец";

      v_blocks.push_back({escaped, type, currentY});
      currentY += 100;
    }

    out << "{\"blocks\":[";
    for (size_t i = 0; i < v_blocks.size(); ++i) {
      out << "{\"x\":360,\"y\":" << v_blocks[i].y << ",\"text\":\""
          << v_blocks[i].text << "\",\"width\":120,\"height\":40,\"type\":\""
          << v_blocks[i].type
          << "\",\"isMenuBlock\":false,\"fontSize\":14,\"textHeight\":14,"
          << "\"isBold\":false,\"isItalic\":false,\"textAlign\":\"center\","
             "\"labelsPosition\":1}";
      if (i < v_blocks.size() - 1)
        out << ",";
    }

    out << "],\"arrows\":[";
    for (size_t i = 0; i + 1 < v_blocks.size(); ++i) {
      int y1 = v_blocks[i].y + 20;
      int y2 = v_blocks[i + 1].y - 20;
      out << "{\"startIndex\":" << i << ",\"endIndex\":" << i + 1
          << ",\"startConnectorIndex\":2,\"endConnectorIndex\":0,\"nodes\":["
          << "{\"x\":360,\"y\":" << y1 << "},{\"x\":360,\"y\":" << (y1 + y2) / 2
          << "},{\"x\":360,\"y\":" << y2 << "}],"
          << "\"counts\":[1,1,1]}";
      if (i + 2 < v_blocks.size())
        out << ",";
    }
    out << "],\"x0\":0,\"y0\":0}";
  }
};
#endif
