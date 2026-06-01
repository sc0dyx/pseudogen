import re
from .PyChart.PyChart import PseudoCode


class CppPseudoCode(PseudoCode):
    @staticmethod
    def to_pseudocode(lines: str) -> str:
        pseudocode = ""
        lines = lines.split("\n")  # type: ignore

        for line in lines:
            line = line.strip()

            # 1. Смертельный клининг фигурных скобок, чтобы они не лезли в ромбы
            line = line.replace("{", "").replace("}", "").strip()
            if not line:
                continue

            # 2. ЗАХАРДКОЖЕНО: Автоматически срезаем явную типизацию C++ по умолчанию
            line = re.sub(
                r"^\b(int|bool|float|double|char|string|auto)\b\s+",
                "",
                line,
            )

            # Заменяем математические операторы на красивые по ГОСТу
            line = line.replace("*", "×")
            line = line.replace("/", "÷")
            line = line.replace("==", "=")
            line = line.replace("!=", "≠")
            line = line.replace("&&", " и ")
            line = line.replace("||", " или ")

            # Разворачиваем плюсовые инкременты/декременты и сокращенные операции
            line = re.sub(r"(\w+)\+\+", r"\1 = \1 + 1", line)
            line = re.sub(r"\+\+(\w+)", r"\1 = \1 + 1", line)
            line = re.sub(r"(\w+)\-\-", r"\1 = \1 - 1", line)
            line = re.sub(r"\-\-(\w+)", r"\1 = \1 - 1", line)
            line = re.sub(r"(\w+)\s*\+=\s*(.*)", r"\1 = \1 + \2", line)
            line = re.sub(r"(\w+)\s*\-=\s*(.*)", r"\1 = \1 - \2", line)

            # Очищаем ввод и вывод
            if "cout" in line:
                line = re.sub(r"(std::)?cout\s*<<\s*", "Вывод, ", line)
                line = re.sub(r"\s*<<\s*(std::)?endl\s*;?$", "", line)
                line = line.rstrip(";")
                line = line.replace("<<", ",")
                line = line.strip().rstrip(",")
                pseudocode += f"{line}\n"
                continue

            if "cin" in line:
                line = re.sub(r"(std::)?cin\s*>>\s*", "Ввод, ", line)
                line = line.rstrip(";")
                line = line.replace(">>", ",")
                line = line.strip().rstrip(",")
                pseudocode += f"{line}\n"
                continue

            # 3. Превращаем управляющие конструкции в чистые условия без скобок
            if line.startswith("if"):
                cond = line[2:].strip()
                if cond.startswith("(") and cond.endswith(")"):
                    cond = cond[1:-1].strip()
                pseudocode += cond
            elif line.startswith("else if"):
                cond = line[7:].strip()
                if cond.startswith("(") and cond.endswith(")"):
                    cond = cond[1:-1].strip()
                pseudocode += cond
            elif line.startswith("else"):
                pseudocode += ""
            elif line.startswith("for"):
                cond = line[3:].strip()
                if cond.startswith("(") and cond.endswith(")"):
                    cond = cond[1:-1].strip()
                pseudocode += cond
            elif line.startswith("while"):
                cond = line[5:].strip()
                if cond.startswith("(") and cond.endswith(")"):
                    cond = cond[1:-1].strip()
                pseudocode += cond
            elif bool(
                re.match(
                    r"\b(void|int|float|double|char|bool|string)\b\s+\w+\s*\(", line
                )
            ):
                line = re.sub(
                    r"\b(void|int|float|double|char|bool|string)\b\s+", "функция ", line
                )
                pseudocode += line
            else:
                if "return " in line:
                    pseudocode += line.replace("return", "передача")
                else:
                    pseudocode += f"{line}\n"

        return pseudocode
