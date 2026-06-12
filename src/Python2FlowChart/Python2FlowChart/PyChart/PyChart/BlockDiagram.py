import uuid
from abc import ABC, abstractmethod
from pprint import pprint


class BlockDiagram(ABC):
    """
    Базовый класс для построения блок-схемы из дерева кода.
    """

    # Атрибуты класса (общие для всех экземпляров)
    _direction = {
        "UP": 0,
        "RIGHT": 1,
        "DOWN": 2,
        "LEFT": 3,
    }

    # Переменные, которые обычно переопределяются в __init__, но пока оставим на уровне класса
    _last_x = 0
    _last_y = 0
    _last_if_id_list = []
    _last_arrow_pos_delta = 15
    _blocks_indent = 100
    _diagram = {
        "blocks": [],
        "arrows": [],
        "x0": 0,
        "y0": 100,
    }

    def __init__(
        self,
        pseudocode,
        code_tree: list,
        variables: list,
        base_coor=None,
        name="main",
        start_block_index=0,
    ) -> None:
        if base_coor is None:
            base_coor = {"y": 0, "x": 0}

        self._pseudocode = pseudocode
        self._last_x = base_coor["x"]
        self._last_y = base_coor["y"]
        self._name = name
        self._code_tree = self._connect_same_lines_in_tree(code_tree)
        self._variables = variables
        self._forbidden_aria = []
        self._start_block_index = start_block_index
        self._final_merge = []

    def build(self) -> dict:
        name = self._name
        if name == "main":
            name = ""

        self._diagram["blocks"].insert(
            0,
            self._return_block(
                f"Начало {name}",
                {"y": self._last_y - 100, "x": self._last_x},
                -1,
                "Начало / конец",
            ),
        )
        last_index, final_merge = self._add_blocks(self._code_tree, 0)

        self._diagram["blocks"].append(
            self._return_block(
                "Конец",
                {"y": self._last_y - 100, "x": self._last_x},
                final_merge if final_merge else [last_index],
                "Начало / конец",
            )
        )

        # --- inline _align_if_else_bodies() ---
        # if_structs = self._find_blocks_by_property("struct_type", "if")
        # for if_struct in if_structs:
        #     struct_id = if_struct["cur_el_id"]
        #     if_body = self._find_blocks_by_property("parent_id", struct_id)
        #     else_body = self._find_blocks_by_property("parent_id", struct_id + "-else")
        #     if not if_body:
        #         continue
        #     max_width_if_body = max(b["width"] for b in if_body)
        #     base_x = if_struct["x"]
        #     for b in if_body:
        #         b["x"] = base_x + max_width_if_body
        #     if else_body:
        #         base_y = if_body[0]["y"]
        #         for b in else_body:
        #             b["y"] = base_y
        #             b["x"] = base_x - max_width_if_body
        #             base_y += 100

        # --- inline _set_all_forbidden_areas() ---
        for block in self._diagram["blocks"]:
            x0 = block["x"] - block["width"] / 2
            x1 = block["x"] + block["width"] / 2
            y0 = block["y"] - block["height"] / 2
            y1 = block["y"] + block["height"] / 2
            self._forbidden_aria.append({"x0": x0, "x1": x1, "y0": y0, "y1": y1})

        # --- вызов отрисовки стрелок (тоже один раз, но рекурсивный, оставляем как есть) ---
        self._connect_all_blocks_by_arrows()

        return self._diagram

    @staticmethod
    def build_from_programs_list(programs: list, pseudocode, diagram_class):
        """Создаёт общую диаграмму из списка программ (например, функций)."""
        y = 0
        last_index = 0
        super_diagram = {
            "blocks": [],
            "arrows": [],
            "x0": 0,
            "y0": 0,
        }

        for prog in programs:
            diagram = diagram_class(
                pseudocode,
                prog["code"],
                prog["variables"],
                {"y": y, "x": 0},
                prog["name"],
                last_index,
            )
            diagram = diagram.build()

            # Вычисляем максимальный индекс для продолжения нумерации
            last_index = max(b["index"] for b in diagram["blocks"]) + 1

            super_diagram["blocks"] += diagram["blocks"]
            super_diagram["arrows"] += diagram["arrows"]
            y += len(diagram["blocks"]) * diagram_class._blocks_indent

            # Очищаем временные данные (костыль для избежания ссылок)
            diagram_class._diagram["blocks"] = []
            diagram_class._diagram["arrows"] = []

        return super_diagram

    def debug(self) -> dict:
        """Возвращает диаграмму и запретные зоны для отладки."""
        self.build()
        return {"diagram": self._diagram, "forb_area": self._forbidden_aria}

    def _return_block(
        self, text="", pos=None, parentIndex: list[int] | int = 1, block_type="none"
    ):
        """Создаёт словарь блока."""
        if isinstance(parentIndex, int):
            parentIndex = [parentIndex]
        if pos is None:
            pos = {"x": 0, "y": 0}
        if block_type == "none":
            block_type = self._get_bd_type_of_line(text.strip().split("\n")[0])

        text = text.strip()
        code = text
        struct_type = self._get_struct_type(code)
        size = BlockDiagram._get_size_of_block(text.split("\n"))

        if block_type == "none":
            return

        text = self._to_pseudocode(text)
        if text.strip() == "":
            return

        block = {
            "code": code,
            "parentIndex": parentIndex,
            "struct_type": struct_type,
            "x": pos["x"],
            "y": pos["y"],
            "text": text,
            "width": size["width"],
            "height": size["height"],
            "type": block_type,
            "isMenuBlock": False,
            "fontSize": 14,
            "textHeight": 14,
            "isBold": False,
            "isItalic": False,
            "textAlign": "center",
            "labelsPosition": 1,
            "index": len(self._diagram["blocks"]),
        }
        return block

    @abstractmethod
    def _get_bd_type_of_line(line: str) -> str:
        """Возвращает тип блока для отображения на сайте."""
        if line:
            return "Блок"

    # --- Абстрактные методы, переопределяемые в наследниках ---
    @abstractmethod
    def _get_struct_type(line: str) -> str:
        """
        Определяет тип конструкции: 'if', 'else', 'elif', 'loop', 'function', 'output', 'block'.
        """
        if line:
            return "block"

    @staticmethod
    def _get_size_of_block(lines: list) -> dict:
        """Вычисляет ширину и высоту блока по тексту."""
        height = len(lines) * 8
        width = 100
        for line in lines:
            if isinstance(line, str):
                line = line.strip()
                width = max(width, len(line) * 9)
        return {"width": max(100, width), "height": max(height, 40)}

    # --- Работа с запретными зонами и путями ---
    def _is_point_free(self, position: dict) -> bool:
        """Проверяет, свободна ли точка (не занята другим блоком)."""
        x = position["x"]
        y = position["y"]
        for pos in self._forbidden_aria:
            if not (
                (x < pos["x0"] or x > pos["x1"]) or (y < pos["y0"] or y > pos["y1"])
            ):
                return False
        return True

    def _is_path_free(self, position: dict, coor="y") -> bool:
        """Проверяет, свободен ли путь между двумя точками."""
        coor1 = position["start"]
        coor2 = position["end"]

        if coor2[coor] - coor1[coor] > 0:
            direction_coef = 1
        else:
            direction_coef = -1

        coor1[coor] += 25 * direction_coef
        begin = 0
        end = abs(coor2[coor] - coor1[coor])
        while begin <= end:
            if self._is_point_free(coor1):
                coor1[coor] += 1 * direction_coef
            elif coor1[coor] == coor2[coor]:
                return True
            else:
                return False
            begin += 1
        return True

    # --- Основной парсер дерева кода (рекурсивный) ---
    def _add_blocks(
        self,
        code_tree: list,
        current_parent: int = 0,
    ) -> tuple[int, list]:
        """
        Рекурсивно обходит дерево.
        Модифицирует self._diagram["blocks"] напрямую.
        Возвращает индекс последнего добавленного в этой ветке блока.
        """
        pending_merge = []
        last_index = current_parent

        for code in code_tree:
            if isinstance(code, str):
                self._last_y += self._blocks_indent
                parent = pending_merge if pending_merge else last_index
                # pending_merge.append(last_index)
                # parent = pending_merge

                new_block = self._return_block(
                    code, {"x": 0, "y": self._last_y}, parent
                )
                # ок, привязываем последний индекс, допустим произошел рекурсивный вызов

                if new_block:
                    self._diagram["blocks"].append(new_block)
                    last_index = new_block["index"]
                    pending_merge = []
                else:
                    self._last_y -= self._blocks_indent

            else:
                self._last_y += self._blocks_indent
                key = list(code.keys())[0]
                value = list(code.values())[0]

                if key.startswith("if "):
                    parent_for_if = pending_merge if pending_merge else last_index
                    pending_merge = []
                    # 1. Создаем if-блок
                    if_block = self._return_block(
                        key, {"x": 0, "y": self._last_y}, parent_for_if
                    )
                    self._diagram["blocks"].append(if_block)

                    # 2. Сохраняем в стек индекс условия
                    self._last_if_id_list.append(if_block["index"])

                    # 3. Рекурсивно заполняем тело IF, передавая ID условия как родителя
                    last_index, inner_merge = self._add_blocks(value, if_block["index"])
                    pending_merge.append(if_block["index"])
                    if inner_merge:
                        pending_merge.extend(inner_merge)
                    else:
                        pending_merge.append(last_index)

                elif key.startswith("elif "):
                    self._last_y -= self._blocks_indent
                    # 1. Создаем elif-блок, привязывая к IF-условию
                    elif_block = self._return_block(
                        key, {"x": 0, "y": self._last_y}, self._last_if_id_list[-1]
                    )
                    self._diagram["blocks"].append(elif_block)

                    cond_idx = self._last_if_id_list[-1]
                    if cond_idx in pending_merge:
                        pending_merge.remove(cond_idx)

                    # 2. Обновляем ID в стеке на текущий elif
                    self._last_if_id_list[-1] = elif_block["index"]

                    # 3. Рекурсивно заполняем тело ELIF
                    last_index, inner_merge = self._add_blocks(
                        value, elif_block["index"]
                    )
                    if inner_merge:
                        pending_merge.extend(inner_merge)
                    else:
                        pending_merge.append(last_index)
                elif "else:" in key:
                    self._last_y -= self._blocks_indent
                    # Рекурсивно заполняем тело ELSE, передавая ID условия из стека
                    last_index, inner_merge = self._add_blocks(
                        value, self._last_if_id_list[-1]
                    )
                    cond_idx = self._last_if_id_list[-1]
                    if cond_idx in pending_merge:
                        pending_merge.remove(cond_idx)
                    if inner_merge:
                        pending_merge.extend(inner_merge)
                    else:
                        pending_merge.append(last_index)
                    self._last_if_id_list.pop()
                elif "for " in key or "while " in key:
                    self._last_y += self._blocks_indent
                    pending_merge = []

                    parent_for_loop = pending_merge if pending_merge else last_index
                    loop_block = self._return_block(
                        key, {"x": 0, "y": self._last_y}, parent_for_loop
                    )

                    self._diagram["blocks"].append(loop_block)
                    # тело цикла
                    last_index, inner_merge = self._add_blocks(
                        value, loop_block["index"]
                    )
                    pending_merge.append(loop_block["index"])
                    # выход из цикла (false) – добавляем индекс цикла как родителя
                    if inner_merge:
                        # Добавляем все концы ветвей, чтобы все они замыкались на цикл
                        loop_block["parentIndex"].extend(inner_merge)
                    else:
                        # Добавляем просто последний блок тела
                        loop_block["parentIndex"].append(last_index)
                    # if inner_merge:
                    #     pending_merge.extend(inner_merge)
                    # else:
                    #     pending_merge.append(last_index)
                    # pending_merge.append(loop_block["index"])

        self._final_merge = pending_merge
        return last_index, pending_merge

    def _connect_same_lines_in_tree(self, code_tree: list) -> list:
        """Склеивает строки одного типа в один блок (оптимизация)."""
        tree = []
        lines = ""
        for i, line in enumerate(code_tree):
            if isinstance(line, str):
                lines += line + "\n"
                last_type = self._get_bd_type_of_line(line)
                if i + 1 < len(code_tree):
                    next_line = code_tree[i + 1]
                    if not isinstance(next_line, str):
                        tree.append(lines)
                        lines = ""
                    elif self._get_bd_type_of_line(next_line) not in [
                        "Блок",
                        "Ввод / вывод",
                        "Дисплей",
                    ] or last_type != self._get_bd_type_of_line(next_line):
                        tree.append(lines)
                        lines = ""
                else:
                    tree.append(lines)
                    lines = ""
            else:
                tree.append(
                    {
                        list(line.keys())[0]: self._connect_same_lines_in_tree(
                            list(line.values())[0]
                        )
                    }
                )
        return tree

    def _to_pseudocode(self, lines: str) -> str:
        """Преобразует строку кода в псевдокод."""
        return self._pseudocode.to_pseudocode(lines)

    # --- Рисование стрелок ---
    def _draw_arrow(
        self,
        start_end_pos: dict,
        start_end_indexes: dict,
        direction: dict,
        y_correction=0,
    ) -> None:
        """Рисует одну стрелку между двумя блоками."""
        dirs = self._direction
        delta = self._last_arrow_pos_delta - 1
        arrow = {
            "startIndex": start_end_indexes["start"],
            "endIndex": start_end_indexes["end"],
            "startConnectorIndex": direction["start"],
            "endConnectorIndex": direction["end"],
            "nodes": [],
            "counts": [],
        }

        x1 = start_end_pos["start"]["x"]
        y1 = start_end_pos["start"]["y"]
        x2 = start_end_pos["end"]["x"]
        y2 = start_end_pos["end"]["y"]

        x_direction_coef = 1
        if direction["start"] == dirs["LEFT"]:
            x_direction_coef = -1

        # Случай: влево-вправо (ветвление)
        if direction["start"] == dirs["LEFT"] and direction["end"] == dirs["RIGHT"]:
            arrow["nodes"].append({"x": x1, "y": y1})
            while not self._is_path_free(
                {"start": {"x": x1, "y": y1}, "end": {"x": x2, "y": y1}}, "x"
            ):
                y1 += 50
            y1 += y_correction - y1
            arrow["nodes"].append({"x": x1 + delta, "y": y1})
            while not self._is_path_free(
                {"start": {"x": x1, "y": y1}, "end": {"x": x1, "y": y2}}, "y"
            ):
                x1 += 100
            arrow["nodes"].append({"x": x1 + delta, "y": y1})
            arrow["nodes"].append({"x": x1 + delta, "y": y2})
            arrow["nodes"].append({"x": x2, "y": y2})

        # Случай: вниз-вправо (цикл)
        elif direction["start"] == dirs["DOWN"] and direction["end"] == dirs["RIGHT"]:
            arrow["nodes"].append({"x": x1, "y": y1})
            y1 += 50
            arrow["nodes"].append({"x": x1, "y": y1})
            while not self._is_path_free(
                {"start": {"x": x1, "y": y1}, "end": {"x": x1, "y": y2}}, "y"
            ):
                x1 += 100 * x_direction_coef
            arrow["nodes"].append({"x": x1 + delta, "y": y1})
            arrow["nodes"].append({"x": x1 + delta, "y": y2})
            arrow["nodes"].append({"x": x2, "y": y2})

        # Остальные случаи (обычная стрелка вниз)
        else:
            arrow["nodes"].append({"x": x1, "y": y1})
            if not self._is_path_free(
                {"start": {"x": x1, "y": y1}, "end": {"x": x2, "y": y2}}
            ):
                while not self._is_path_free(
                    {"start": {"x": x1, "y": y1}, "end": {"x": x1, "y": y2}}
                ):
                    x1 += 30 * x_direction_coef
                arrow["nodes"].append({"x": x1 + delta, "y": y1})
                arrow["nodes"].append({"x": x1 + delta, "y": y2 - 40})
                arrow["nodes"].append({"x": x2, "y": y2 - 40})
                arrow["nodes"].append({"x": x2, "y": y2 + 40})
            else:
                arrow["nodes"].append({"x": x2, "y": y2})

        # Заполнение счётчиков (всегда 1)
        for _ in arrow["nodes"]:
            arrow["counts"].append(1)
        self._last_arrow_pos_delta -= 1
        self._diagram["arrows"].append(arrow)

    def _connect_blocks(self, block1: dict, block2: dict, direction: dict) -> None:
        """Соединяет два блока стрелкой (временное упрощение без y-коррекции)."""
        y_correction = 0
        # TODO: вычислить y_correction для условий через parentIndex
        self._draw_arrow(
            {
                "start": {"y": block1["y"], "x": block1["x"]},
                "end": {"y": block2["y"], "x": block2["y"]},
            },
            {"start": block1["index"], "end": block2["index"]},
            direction,
            y_correction,
        )

    def _find_blocks_by_property(
        self, block_property: str, value, required_field="", block_list=None
    ) -> list:
        """Поиск блоков по значению свойства (например, parent_id)."""
        if block_list is None:
            block_list = []
        if not block_list:
            block_list = self._diagram["blocks"]
        result = []
        for block in block_list:
            if block.get(block_property) == value:
                if required_field:
                    result.append(block[required_field])
                else:
                    result.append(block)
        return result

    # --- Центральный метод связывания всех блоков стрелками ---
    def _connect_all_blocks_by_arrows(self) -> None:
        dirs = self._direction
        blocks = self._diagram["blocks"]
        # сохраняем словарь, где можно по индексу обращаться к блоку, где ключ это сам индекс, а значение сам блок
        block_map = {b["index"]: b for b in blocks}

        # Собираем потомков для каждого управляющего родителя
        # простыми словами находим детей родителя, где ключ - родитель, значение - дети (блок/слварь)
        control_children = {}
        for b in blocks:
            # перебираем индексыы родителей внутри блока (напоминаю что у блока может быть несколько родителей)
            for p in b.get("parentIndex", []):
                # проверяем, есть ли индекс родителя в наших блоках и по значению индекса в словаре blockmap
                # мы проверяем является ли наш родитель (родительский блок), if, elif, loop который мы перебираем из всех родителей
                if p in block_map and block_map[p]["struct_type"] in (
                    "if",
                    "elif",
                    "loop",
                ):
                    # затем сохраняем где ключ - родитель, значение - его потомки/дети которые хранятся в виде полноценных блоках
                    control_children.setdefault(p, []).append(b)
        # по итогу у нас block_map где содержатся индексы, и по индексам (ключу) можно обращаться к блокам
        # и control_children, блоки которые содержат индексы (блоков которые являются родителями и которые являются if, elif или циклом), а затем сохраняются все блоки потомков

        # Сортируем потомков по индексу
        for p in control_children:
            # от меньшего к большему
            control_children[p].sort(key=lambda x: x["index"])

        # Рисуем стрелки

        # [ 3, 4 , 6 , 7]
        # если в 3 лежит цикл, то остальные блоки надо соединять до тех пор пора паренты совпадают, т.е. замыкать
        for child in blocks:
            # last_loop = None
            # перебирая блоки, мы еще перебираем индексы (родителей может быть несколько)
            parents = child.get("parentIndex", [])
            for p_id in parents:
                # если такого индекса не существует, то скипаем итерацию
                if p_id not in block_map:
                    continue
                # получаем родительский блок
                parent = block_map[p_id]
                # получаем его тип
                p_type = parent["struct_type"]
                # нам нужно сделать проверку
                # если родительский блок являтся обычным блоком или блоком ввода вывода нашего текущего блока, то просто линейно соединяем

                # Линейная связь
                if p_type in ("block", "i/o"):
                    # Если текущий блок — цикл, а родитель — обычный блок,
                    # то замыкаем
                    # если текущий блок (цикл) к примеру с индексом 2, а родительский блок (обычный блок) с индексом 1, значит 2 - 1 > 1 ложь
                    # если текущий блок цикл к примеру с индексом 2, а родительский блок (обычный блок) с индексом 3, значит 2 - 3 > 1 ложь
                    # значит придумаем свою формулу для определения
                    # 2 - 1 < 1 - ложь, 2 - 3 < 1 правда
                    if (
                        child["struct_type"] == "loop"
                        and child["index"] - parent["index"] < 0
                    ):
                        self._connect_blocks(
                            parent, child, {"start": dirs["LEFT"], "end": dirs["DOWN"]}
                        )
                    else:
                        self._connect_blocks(
                            parent, child, {"start": dirs["DOWN"], "end": dirs["UP"]}
                        )
                # Управляющая связь (if/elif/loop)
                # если родительский блок является циклом или условием, то мы соединяем от стрелки "да", если родительский блок находится далеко от текущего блока, то от стрелки "нет"
                elif p_type in ("if", "elif", "loop"):
                    # p_id это индекс родителя, мы получаем список блоков потомков if elif else
                    # определяем откуда рисовать стрелку (от "да" или "нет")
                    if child["index"] - parent["index"] > 1:  # false ветка
                        self._connect_blocks(
                            parent, child, {"start": dirs["LEFT"], "end": dirs["UP"]}
                        )
                    elif (
                        child["struct_type"] == "loop"
                        and child["index"] - parent["index"] < 0
                    ):  # если текущий блок цикл и родитель тоже цикл, то его false ветка будет ввести слева вниз, также делаем проверку на то, что родительский блок находится ниже на плоскости
                        self._connect_blocks(
                            parent, child, {"start": dirs["LEFT"], "end": dirs["DOWN"]}
                        )
                    else:  # true ветка
                        self._connect_blocks(
                            parent,
                            child,
                            {"start": dirs["RIGHT"], "end": dirs["UP"]},
                        )

                        #

    def _find_farthest_children(self, blocks: list) -> list:
        """Находит самые дальние дочерние блоки (для замыкания стрелок)."""
        children = []
        if not blocks:
            return children
        for block in blocks:
            struct_type = block["struct_type"]
            body = self._find_blocks_by_property("parent_id", block["cur_el_id"])
            else_body = self._find_blocks_by_property(
                "parent_id", block["cur_el_id"] + "-else"
            )
            if struct_type == "loop":
                if body:
                    children += self._find_farthest_children([body[-1]])
            elif struct_type == "if":
                if body:
                    children += self._find_farthest_children([body[-1]])
                if else_body:
                    children += self._find_farthest_children([else_body[-1]])
                else:
                    children.append(block)
            else:
                children.append(block)
        return children
