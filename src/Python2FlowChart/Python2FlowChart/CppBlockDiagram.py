from .PyChart.PyChart import BlockDiagram


class CppBlockDiagram(BlockDiagram):
    @staticmethod
    def _get_struct_type(line: str) -> str:
        line = line.strip()

        # C++ ключевые слова (с учетом возможных пробелов перед скобкой)
        if line.startswith("if"):
            return "if"
        elif line.startswith("else if"):
            return "elif"
        elif line.startswith("else"):
            return "else"
        elif line.startswith("for"):
            return "loop"
        elif line.startswith("while"):
            return "loop"
        elif line.startswith("do"):
            return "loop"
        elif line.startswith("switch") or line.startswith("case"):
            return "if"
        else:
            # Ищем плюсовый вывод (cout, printf, а также cin для ввода)
            if "cout" in line or "printf" in line or "cin" in line or "scanf" in line:
                return "output"
            else:
                return "block"

    @staticmethod
    def _get_bd_type_of_line(line: str) -> str:
        line = line.strip()

        if (
            line.startswith("if")
            or line.startswith("else if")
            or line.startswith("switch")
            or line.startswith("case")
        ):
            return "Условие"
        elif line.startswith("else") or line.startswith("do"):
            return "none"
        elif line.startswith("for"):
            return "Цикл for"
        elif line.startswith("while"):
            return "Условие"
        elif "cout" in line or "printf" in line or "cin" in line or "scanf" in line:
            return "Ввод / вывод"
        elif "return " in line:
            return "Начало / конец"
        else:
            return "Блок"
