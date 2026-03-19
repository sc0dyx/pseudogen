import re
import argparse
import json
from const import START, BLOCK, CONDITION, INPUT_OUTPUT, END


class PseudoGen:
    def __init__(self, input_path=None, pgen_path=None, output_path=None):
        self.input = input_path
        self.pgen = pgen_path
        self.output = output_path

    def pseudocode(self):
        rules = []

        # Читаем правила из pgen файла
        with open(self.pgen, "r", encoding="utf-8") as pgen_file:
            for line in pgen_file:
                line = line.strip()
                if not line or "->" not in line:
                    continue

                # Разбиваем по ->
                pos = line.find("->")
                search = line[:pos].replace('"', "").strip()
                replace = line[pos + 2 :].replace('"', "").strip()

                # Добавляем скомпилированную регулярку и строку замены
                rules.append((re.compile(search), replace))

        # Читаем входной файл и записываем результат в выходной
        with (
            open(self.input, "r", encoding="utf-8") as input_file,
            open(self.output, "w", encoding="utf-8") as output_file,
        ):
            for source_line in input_file:
                processed = source_line
                for pattern, replacement in rules:
                    processed = pattern.sub(replacement, processed)
                output_file.write(processed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="pseudogen - pseudocode and flowchart generator"
    )
    # Обязательный аргумент
    parser.add_argument("-i", "--input", required=True, help="path to code")
    parser.add_argument("-g", "--pgen", help="path to pgen")
    parser.add_argument("-o", "--output", required=True, help="output file")
    # parser.add_argument(
    #     "-t",
    #     "--type",
    #     choices=["blockscheme", "pseudocode"],
    #     help="blockscheme or pseudocode",
    # )
    args = parser.parse_args()
    # if args.type == "pseudocode":
    pg = PseudoGen(args.input, args.pgen, args.output)
    pg.pseudocode()
    # elif args.type == "blockscheme":
    #     pg = PseudoGen(args.input, output_path=args.output)
    #     pg.blockgen()
