import re
from .PyChart.PyChart import Preprocessor


class CppPreprocessor(Preprocessor):
    def __init__(self, f) -> None:
        self._file = f.readlines() if hasattr(f, "readlines") else f
        self._parsed_code = []
        self._serealized_code = []
        self._parse()

    def _parse(self) -> None:
        # 1. Склеиваем весь файл в одну строку
        code = "".join(self._file) if isinstance(self._file, list) else self._file

        # 2. Вычищаем директивы и комментарии.
        # Используем (?:\n|$) чтобы корректно обрабатывать конец файла
        code = re.sub(r"#.*?(?:\n|$)", " ", code)
        code = re.sub(r"//.*?(?:\n|$)", " ", code)
        code = re.sub(r"/\*.*?\*/", " ", code, flags=re.DOTALL)

        # 3. Уничтожаем лишние пробелы и переносы — в C++ они не имеют смысла
        code = re.sub(r"\s+", " ", code).strip()

        self._parsed_code = []
        i = 0
        level = 0
        force_indent = []  # Стек для отслеживания однострочных тел (без скобок)

        while i < len(code):
            if code[i] == " ":
                i += 1
                continue

            # Закрытие обычного блока
            if code[i] == "}":
                if level > 0:
                    level -= 1
                i += 1
                # Сбрасываем висящие однострочные отступы, если блок закрылся
                while force_indent and force_indent[-1] >= level:
                    force_indent.pop()
                continue

            # Проверяем управляющие конструкции и функции (они задают скоуп)
            ctrl_match = re.match(
                r"^(else\s+if|if|while|for|else|switch|do)\b", code[i:]
            )
            func_match = re.match(
                r"^(?:inline\s+)?(?:void|int|float|double|char|bool|string|auto)\s+\w+\s*\(",
                code[i:],
            )

            if ctrl_match or func_match:
                if ctrl_match:
                    keyword = ctrl_match.group(1)
                    i += len(keyword)
                else:
                    keyword = ""

                stmt = keyword

                # Если это не else/do, собираем условие целиком с учетом вложенных круглых скобок
                if keyword not in ("else", "do"):
                    while i < len(code) and code[i] != "(":
                        stmt += code[i]
                        i += 1
                    if i < len(code):
                        start_paren = i
                        paren_count = 1
                        i += 1
                        while i < len(code) and paren_count > 0:
                            if code[i] == "(":
                                paren_count += 1
                            elif code[i] == ")":
                                paren_count -= 1
                            i += 1
                        stmt += code[start_paren:i]

                stmt = stmt.strip()
                if stmt.startswith("else if"):
                    # Отрезаем "else if" и приклеиваем "elif " (с пробелом для твоего .startswith("elif "))
                    stmt = "elif " + stmt[7:].strip()
                elif stmt == "else":
                    # Добавляем двоеточие для совместимости с "else:" in key
                    stmt = "else:"
                is_main = "main(" in stmt

                # Добавляем в AST всё, кроме сигнатуры main()
                if not is_main:
                    self._parsed_code.append("    " * level + stmt)

                # Проверяем, есть ли фигурные скобки (блок) или тело будет однострочным
                while i < len(code) and code[i] == " ":
                    i += 1

                if i < len(code) and code[i] == "{":
                    i += 1
                    if not is_main:
                        level += 1
                elif not is_main:
                    # Фигурных скобок нет -> следующее выражение до ';' будет телом
                    level += 1
                    force_indent.append(level)
                continue

            # Если мы здесь, значит это обычное выражение, парсим до ';'
            start_stmt = i
            brace_count = 0
            paren_count = 0

            while i < len(code):
                if code[i] == "{":
                    brace_count += 1
                elif code[i] == "}":
                    if brace_count > 0:
                        brace_count -= 1
                    else:
                        break  # Встретили конец чужого блока
                elif code[i] == "(":
                    paren_count += 1
                elif code[i] == ")":
                    if paren_count > 0:
                        paren_count -= 1
                elif code[i] == ";" and brace_count == 0 and paren_count == 0:
                    i += 1
                    break
                i += 1

            stmt = code[start_stmt:i].strip()
            if stmt:
                stmt = stmt.rstrip(";").strip()
                # Игнорируем мусорные строки, чтобы они не лезли в блок-схемы
                if not (
                    stmt.startswith("using") or stmt == "return 0" or stmt == "return"
                ):
                    self._parsed_code.append("    " * level + stmt)

            # Как только распарсили одно полноценное выражение, снимаем однострочный отступ
            while force_indent and force_indent[-1] == level:
                force_indent.pop()
                level -= 1

        # Собираем итоговое дерево
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
            or line.startswith("do")
            or is_cpp_function
        )

    def _cut_functions(self, serealized_code):
        return []

    def _get_function_name(self, line):
        return ""

    def _get_fun_args(self, line, fun_name=""):
        return []

