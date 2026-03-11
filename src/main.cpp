#include "../vendors/CLI11.hpp"
#include "pseudogen.hpp"
#include <iostream>
#include <string>

int main(int argc, char **argv) {
  std::string input_file, pgen_file, output_file;
  std::string type = "pseudocode";

  CLI::App app{"pseudogen - pseudocode and flowchart generator"};

  app.add_option("-i,--input", input_file, "path to code")
      ->check(CLI::ExistingFile);
  app.add_option("-g,--pgen", pgen_file, "path to pgen")
      ->check(CLI::ExistingFile);
  app.add_option("-o,--output", output_file, "output file");
  app.add_option("-t,--type", type, "blockscheme or pseudocode")
      ->check(CLI::IsMember({"blockscheme", "pseudocode"}));
  ;
  CLI11_PARSE(app, argc, argv);
  PseudoGen pg;
  // pg.init_files(input_file, pgen_file, output_file);
  pg.input = input_file;
  pg.output = output_file;
  if (type == "blockscheme")
    pg.blockgen();
  else {
    pg.pgen = pgen_file;
    pg.pseudocode();
  }

  return 0;
}
