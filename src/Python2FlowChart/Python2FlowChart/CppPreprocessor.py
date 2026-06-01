import re


class CppPreprocessor:
    def __init__(self, f) -> None:
        # Читаем файл в массив строк
        self._file = f.readlines() if hasattr(f, "readlines") else f
        self._parsed_code = []
        self._serealized_code = []
        self._parse()

    def _parse(self) -> None:
        level = 0
        for line in self._file:
            # 1. Удаляем комментарии C++
            line = re.sub(r"//.*", "", line)
            line = re.sub(r"/\*.*?\*/", "", line)
            striped = line.strip()

            # 2. Удаляем инклуды, пространства имен, int main() и return 0
            if (
                not striped
                or striped.startswith("#")
                or striped.startswith("using")
                or "main(" in striped
                or "return 0" in striped
                or striped == "return;"
            ):
                # Следим за скобками, даже если саму строку с main() или return выкидываем
                if "{" in striped:
                    level += 1
                if "}" in striped:
                    level = max(0, level - striped.count("}"))
                continue

            # Пропускаем одиночные фигурные скобки
            if striped == "{" or striped == "}" or striped == "};":
                if striped == "{":
                    level += 1
                elif striped == "}" or striped == "};":
                    level = max(0, level - 1)
                continue

            if "}" in striped:
                level = max(0, level - striped.count("}"))
                striped = striped.replace("}", "").strip()

            pseudo_line = "    " * level + striped
            if pseudo_line.endswith(";"):
                pseudo_line = pseudo_line[:-1]

            if striped:
                self._parsed_code.append(pseudo_line)

            if "{" in striped:
                level += 1

        # Сериализуем дерево
        self._serealized_code = self._get_serealized_code(self._parsed_code)

    def _get_serealized_code(self, code: list) -> list:
        levels = []
        i = 0
        while i < len(code):
            item = code[i]
            if self._is_control_structure(item):
                end = self._find_end_of_body(code, i)
                levels.append(
                    {item.strip(): self._get_serealized_code(code[i + 1 : end + 1])}
                )
                i = end
            else:
                levels.append(item.strip())
            i += 1
        return levels

    def _find_end_of_body(self, code: list, position: int) -> int:
        last_level = self._get_level_of_line(code[position])
        end = position
        for i in code[position + 1 : :]:
            if self._get_level_of_line(i) > last_level:
                end += 1
            else:
                break
        return end

    @staticmethod
    def _get_level_of_line(line) -> int:
        return line.count("    ")

    def _find_all_veribles(self, code: list) -> list:
        m = []
        types_regex = r"\b(int|float|double|char|bool|string|auto)\b\s+(\w+)"

        for string in code:
            if type(string) == str:
                try:
                    m += [t[1] for t in re.findall(types_regex, string)]
                    m += re.findall(r"for\s*\(\s*\w+\s+(\w+)", string)
                    m += re.findall(r"cin\s*>>\s*(\w+)", string)
                except ValueError:
                    pass
            elif type(string) == dict:
                value = list(string.values())[0]
                m += self._find_all_veribles(value)

        return list(set([e for e in m if not e.isdigit() and len(e) > 0]))

    def get_programs_list(self) -> list:
        main_code = self._serealized_code
        variables = self._find_all_veribles(main_code)
        return [{"code": main_code, "name": "main", "variables": variables}]

    @staticmethod
    def _is_control_structure(line: str) -> bool:
        line = line.strip()
        is_cpp_function = bool(
            re.match(r"\b(void|int|float|double|char|bool|string)\b\s+\w+\s*\(", line)
        )
        return (
            line.startswith("if")
            or line.startswith("for")
            or line.startswith("while")
            or line.startswith("else")
            or line.startswith("switch")
            or is_cpp_function
        )
