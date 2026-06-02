import re
import argparse
import json
import os
import sys
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from Python2FlowChart.Python2FlowChart.PyPreprocessor import PyPreprocessor
from Python2FlowChart.Python2FlowChart.Py2BlockDiagram import Py2BlockDiagram
from Python2FlowChart.Python2FlowChart.Py2PseudoCode import Py2PseudoCode
from Python2FlowChart.Python2FlowChart.CppBlockDiagram import CppBlockDiagram
from Python2FlowChart.Python2FlowChart.CppPseudoCode import CppPseudoCode
from Python2FlowChart.Python2FlowChart.CppPreprocessor import CppPreprocessor


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

    def _generate_py_scheme(self):
        with open(self.input, "r", encoding="utf-8") as read:
            p = PyPreprocessor(read)
        programs_list = p.get_programs_list()
        return Py2BlockDiagram.build_from_programs_list(
            programs_list, Py2PseudoCode, Py2BlockDiagram
        )

    def _generate_cpp_scheme(self):
        with open(self.input, "r", encoding="utf-8") as read:
            p = CppPreprocessor(read)
        programs_list = p.get_programs_list()
        return CppBlockDiagram.build_from_programs_list(
            programs_list, CppPseudoCode, CppBlockDiagram
        )

    def blockgen(self):
        # Проверяем расширение
        is_cpp = (
            self.input.endswith(".cpp")
            or self.input.endswith(".hpp")
            or self.input.endswith(".h")
        )

        # Вызываем строго изолированный метод под конкретный язык
        if is_cpp:
            diagram = self._generate_cpp_scheme()
            lang_name = "C++"
        else:
            diagram = self._generate_py_scheme()
            lang_name = "Python"

        if not self.output.endswith(".json"):
            self.output = f"{self.output}.json"

        with open(self.output, "w+", encoding="utf-8") as write:
            write.write(json.dumps(diagram, indent=4))

        print(f"[{lang_name}] Diagram has been saved as {self.output}")
        print("Upload it here: https://programforyou.ru/block-diagram-redactor")


def main():
    parser = argparse.ArgumentParser(
        description="pseudogen - pseudocode and flowchart generator"
    )
    # Обязательные аргументы
    parser.add_argument("-i", "--input", required=True, help="path to code")
    parser.add_argument("-g", "--pgen", help="path to pgen")
    parser.add_argument("-o", "--output", required=True, help="output file")
    parser.add_argument(
        "-t",
        "--type",
        choices=["blockscheme", "pseudocode"],
        default="pseudocode",
        help="blockscheme or pseudocode",
    )
    args = parser.parse_args()

    if args.type == "pseudocode":
        pg = PseudoGen(args.input, args.pgen, args.output)
        pg.pseudocode()
    elif args.type == "blockscheme":
        pg = PseudoGen(args.input, output_path=args.output)
        pg.blockgen()


if __name__ == "__main__":
    main()
