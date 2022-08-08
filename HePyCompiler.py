from email import message
from io import TextIOWrapper
import re
from bidi.algorithm import get_display
import sys

from matplotlib.pyplot import cla

"""
    5 - 3 + 10 => ((5 - 3) + 10)

    5 * 10 / (3 + 33) => (5 * 10) / (3 + 33)
    5 * 10 / 3 * 2 => (((5 * 10) / 3) * 2)

    <pt> := <Number>
            | ( <nop> )

    <Vals> := <String>
            | <Number>

    <sop> := <String>
            | <sop> + <String>
            | <sop> + <Number>

    <nop> := <pt>
            | <nop> + <pt>
            | <nop> - <pt>
            | <nop> / <pt>
            | <nop> * <pt>

    <bop> := 'True
            |   'False
            |   <nop>
            |   <sop>
            |  ( <bop> or <bop>  )
            |  ( <bop> and <bop> )
            |   <bop> == <bop>
            |   <sop> == <sop>
            |   <sop> != <sop>
            |   <bop> != <bop>
            |   <nop> == <nop>
            |   <nop> != <nop>
            |   <nop> > <nop>
            |   <nop> < <nop>
            |   <nop> <= <nop>
            |   <nop> >= <nop>
"""

TYPE_MAIN = 0
TYPE_ELSE = 1
TYPE_IF = 2
TYPE_GET = 3
TYPE_SET = 4
TYPE_INIT = 5
TYPE_IFSCOPE = 6
TYPE_IFSCOPE_HOLDER = 9
TYPE_WHILE_LOOP = 7
TYPE_PRINT = 8

VAR_TYPE_INT = 33
VAR_TYPE_STRING = 34
VAR_TYPE_BOOLEAN = 35
VAR_TYPE_FLOAT = 36


def type_to_string(self) -> str:
    if self.type == TYPE_ELSE:
        return "TYPE_ELSE"
    if self.type == TYPE_GET:
        return "TYPE_GET"
    if self.type == TYPE_IF:
        return "TYPE_IF"
    if self.type == TYPE_IFSCOPE:
        return "TYPE_IFSCOPE"
    if self.type == TYPE_IFSCOPE_HOLDER:
        return "TYPE_IFSCOPE_HOLDER"
    if self.type == TYPE_INIT:
        return "TYPE_INIT"
    if self.type == TYPE_MAIN:
        return "TYPE_MAIN"
    if self.type == TYPE_PRINT:
        return "TYPE_PRINT"
    if self.type == TYPE_SET:
        return "TYPE_SET"
    if self.type == TYPE_WHILE_LOOP:
        return "TYPE_WHILE_LOOP"


def hError(line, error):
    sys.exit(get_display("שגיאה בשורה " + str(line) + " : " + error))


def clear_scope(args: list, vals: list):
    current = args.pop()
    vals.pop()
    while current != "$":
        current = args.pop()
        vals.pop()


def override_variable(args: list, vals: list, arg, val):
    for i in range(len(args) - 1, -1, -1):
        if args[i] == arg:
            vals[i] = val
            return True
    return False


def add_variable(args: list, vals: list, arg, val):
    for i in range(len(args) - 1, -1, -1):
        if args[i] == "$":
            break

        if args[i] == arg:
            vals[i] = val
            return
    args.append(arg)
    vals.append(val)


def get_val(args, vals, arg, line_number):
    if arg[0] == "\"":
        return arg[1:]

    if arg.isdigit():
        return int(arg)
    if arg.replace('.', '', 1).isdigit():
        return float(arg)
    elif arg == "לא":
        return False
    elif arg == "כן":
        return True
    else:
        for i in range(len(args) - 1, -1, -1):
            if args[i] == arg:
                return vals[i]
    hError(line_number, " : המשתנה " + arg + " לא מוגדר!")


operations = ["+", "-", "*", "/", "==", "!=",
              "<=", ">=", "<", ">", ",", "=", "(", ")", ")"]


def find_split(word, symbols: list):
    words = []
    ln = len(symbols) - 1

    def fs(word, current):
        symbol = symbols[current]
        x = word.find(symbol)
        while x >= 0:
            if current >= ln:
                words.append(word[: x])
            else:
                fs(word[: x], current + 1)
                words.append("$" + symbol)
            word = word[x + len(symbol):]
            x = word.find(symbol)

        if(len(word) > 0):
            if current >= ln:
                words.append(word)
            else:
                fs(word, current + 1)

    fs(word, 0)
    return words


def extended_split(vec: list):
    arr = []
    for word in vec:
        if word[0] == "\"":
            arr.append(word)
            continue
        elif word == "או":
            arr.append("$או")
            continue
        elif word == "וגם":
            arr.append("$וגם")
            continue
        arr += find_split(word, operations)
    return arr


def compute_value(args, vals, vec: list, line_number):
    if len(vec) == 0:
        return

    def execute_operation(operation, right, left):
        # print(right, operation, left)
        if operation == "+":
            if type(right) == str or type(left) == str:
                return str(right) + str(left)
            right += left
        elif operation == "-":
            right -= left
        elif operation == "*":
            right *= left
        elif operation == "/":
            right /= left
        elif operation == "==":
            right = right == left
        elif operation == "!=":
            right = right != left
        elif operation == ">":
            right = right > left
        elif operation == "<":
            right = right < left
        elif operation == ">=":
            right = right >= left
        elif operation == "<=":
            right = right <= left
        elif operation == "או":
            return bool(right or left)
        elif operation == "וגם":
            return bool(right and left)
        elif operation == "<>":
            hError(line_number, "פעולה לא מוגדרת")
        return right

    i = 0
    depth = 0
    operation = "+"
    val = 0
    if type(get_val(
            args, vals, vec[0], line_number)) == str:
        val = ""

    prev = []
    while i < len(vec):
        word = vec[i]
        i += 1
        if word[0] == "$":
            if word[1] == "(":
                # cv(word)
                depth += 1
                prev.append((operation, val))
                val = 0
                operation = "+"
                continue
            elif word[1] == ")":
                depth -= 1
                if depth < 0:
                    hError(line_number, "יש סוגר סגירה מיותר (.")
                po, pval = prev.pop()
                val = execute_operation(po, pval, val)
                operation = "<>"
            else:
                operation = word[1:]
        else:
            val = execute_operation(operation, val, get_val(
                args, vals, word, line_number))
            operation = "<>"

    if depth > 0:
        hError(line_number, "יש סוגר פתיחה ( אבל אין סוגר סיומת ).")
    return val


def compute_type(args, types, vec: list, line_number):
    if len(vec) == 0:
        return

    def find_type(arg):
        if arg[0] == "\"":
            return VAR_TYPE_STRING

        if arg.isdigit():
            return VAR_TYPE_INT
        if arg.replace('.', '', 1).isdigit():
            return VAR_TYPE_FLOAT
        elif arg == "לא":
            return VAR_TYPE_BOOLEAN
        elif arg == "כן":
            return VAR_TYPE_BOOLEAN
        else:
            for i in range(len(args) - 1, -1, -1):
                if args[i] == arg:
                    return types[i]
        hError(line_number, " : המשתנה " + arg +
               " לא מוגדר!" + "\n" + str(args))

    def execute_operation(operation, right, left):
        #print(right, operation, left)
        if operation == "+":
            if right == VAR_TYPE_STRING or left == VAR_TYPE_STRING:
                return VAR_TYPE_STRING
            elif right == VAR_TYPE_FLOAT or left == VAR_TYPE_FLOAT:
                return VAR_TYPE_FLOAT
            return VAR_TYPE_INT
        elif operation == "-":
            if right == VAR_TYPE_STRING or left == VAR_TYPE_STRING:
                hError(line_number, "לא ניתן לחסר מחרוזות!")
            elif right == VAR_TYPE_FLOAT or left == VAR_TYPE_FLOAT:
                return VAR_TYPE_FLOAT
            return VAR_TYPE_INT
        elif operation == "*":
            if right == VAR_TYPE_STRING or left == VAR_TYPE_STRING:
                hError(line_number, "לא ניתן להכפיל מחרוזות!")
            elif right == VAR_TYPE_FLOAT or left == VAR_TYPE_FLOAT:
                return VAR_TYPE_FLOAT
            return VAR_TYPE_INT
        elif operation == "/":
            if right == VAR_TYPE_STRING or left == VAR_TYPE_STRING:
                hError(line_number, "לא ניתן לחלק מחרוזות!")
            elif right == VAR_TYPE_FLOAT or left == VAR_TYPE_FLOAT:
                return VAR_TYPE_FLOAT
            return VAR_TYPE_INT
        elif operation == "==":
            return VAR_TYPE_BOOLEAN
        elif operation == "!=":
            return VAR_TYPE_BOOLEAN
        elif operation == ">":
            return VAR_TYPE_BOOLEAN
        elif operation == "<":
            return VAR_TYPE_BOOLEAN
        elif operation == ">=":
            return VAR_TYPE_BOOLEAN
        elif operation == "<=":
            return VAR_TYPE_BOOLEAN
        elif operation == "או":
            return VAR_TYPE_BOOLEAN
        elif operation == "וגם":
            return VAR_TYPE_BOOLEAN
        hError(line_number, "פעולה לא מוגדרת" + "\n" +
               str(right) + " " + str(operation) + " " + str(left))

    if len(vec) == 1:
        return find_type(vec[0])

    i = 0
    depth = 0
    operation = 0
    ctype = 0

    prev = []
    while i < len(vec):
        arg = vec[i]
        i += 1
        if arg[0] == "$":
            if arg[1] == "(":
                # cv(word)
                depth += 1
                prev.append((operation, ctype))
                ctype = 0
                operation = 0
                continue
            elif arg[1] == ")":
                depth -= 1
                if depth < 0:
                    hError(line_number, "יש סוגר סגירה מיותר (.")
                po, ptype = prev.pop()
                if po != 0:
                    ctype = execute_operation(po, ptype, ctype)
                operation = 1
            else:
                operation = arg[1:]
        elif operation == 0:
            ctype = find_type(arg)
        else:
            ctype = execute_operation(operation, ctype, find_type(arg))
            operation = 1

    if depth > 0:
        hError(line_number, "יש סוגר פתיחה ( אבל אין סוגר סיומת ).")
    return ctype


def text_spliter(s, line_number):
    sp = []
    x = s.find("\"") + 1
    while x > 0:
        current = x
        y = s[x:].find("\"")
        while s[x + y - 1] == '\\':
            current = x + y + 1
            y = s[current:].find("\"")
        if y == -1:
            hError(line_number, "התחיל טקסט אבל אין סוגר טקסט")
        sp += s[:x - 1].split()
        mystring = "\"" + s[x: current + y]
        sp.append(mystring)

        s = s[current + y + 1:]
        x = s.find("\"") + 1
    sp += s.split()
    return extended_split(sp)
    # return sp


def write_tabbed_line(file: TextIOWrapper, line: str, tabs: int):
    for _ in range(tabs):
        file.write("\t")
    file.write(line)


class CodeCommand():
    def __init__(self, ctype, line_number) -> None:
        self.type = ctype
        self.line_number = line_number

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        pass

    def run(self, args, vals, heep):
        """
        Run code as is
        """
        pass

    def __str__(self) -> str:
        return type_to_string(self.type)


class Scope(CodeCommand):
    def __init__(self, ctype, line_number) -> None:
        super().__init__(ctype, line_number)
        self._code = []

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        file.write("{\n")
        command: CodeCommand
        for command in self._code:
            command.compile_cpp(depth + 1, args, types, file)
        write_tabbed_line(file, "}", depth)

    def insert(self, line: CodeCommand):
        self._code.append(line)

    def run(self, args: list, vals: list, heep: map):
        command: CodeCommand
        for command in self._code:
            command.run(args, vals, heep)

    def __str__(self) -> str:
        return type_to_string(self.type)


class GetStatement(CodeCommand):
    def __init__(self, args, line_number) -> None:
        super().__init__(TYPE_GET, line_number)
        # Get some args, compute return value.
        self._args = args

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        if self._args[0] == "$CALL":
            pass

        statement = ""
        rtype = compute_type(args, types, self._args, self.line_number)
        for word in self._args:
            if word[0] == "$":
                if word == "$או":
                    statement += " || "
                elif word == "$וגם":
                    statement += " && "
                else:
                    statement += " " + word[1:] + " "
            elif word[0] == "\"":
                statement += "std::wstring(L\"" + word[1:] + "\")"
            else:
                statement += word
                # This is a variable!

                # return super().compile_c(file)
        return rtype, statement

    def run(self, args, vals, heep):
        return compute_value(
            args, vals, self._args, self.line_number)


class PrintStatement(CodeCommand):
    def __init__(self, message: GetStatement, flip, line_number) -> None:
        super().__init__(TYPE_PRINT, line_number)
        self.message = message
        self.flip = flip

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        vtype, statement = self.message.compile_cpp(depth, args, types, file)

        if vtype == VAR_TYPE_STRING:
            write_tabbed_line(file, "std::wcout << reverse(" +
                              statement + ") << std::endl;\n", depth)
            return
        write_tabbed_line(file, "std::wcout << " +
                          statement + " << std::endl;\n", depth)

    def run(self, args, vals, heep):
        if self.flip:
            print(get_display(str(self.message.run(args, vals, heep))))
        else:
            print(self.message.run(args, vals, heep))


class InitStatement(CodeCommand):
    def __init__(self, name, value: GetStatement, line_number) -> None:
        super().__init__(TYPE_INIT, line_number)
        self.name = name
        self.value = value

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        vtype, statement = self.value.compile_cpp(depth, args, types, file)
        add_variable(args, types, self.name, vtype)
        write_tabbed_line(file, "auto " + self.name +
                          " = " + statement + ";\n", depth)

    def run(self, args, vals, heep):
        arg = self.name
        val = self.value.run(args, vals, heep)
        add_variable(args, vals, arg, val)


class SetStatement(CodeCommand):
    def __init__(self, name, value: GetStatement, line_number) -> None:
        super().__init__(TYPE_SET, line_number)
        self.name = name
        self.value = value

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        vtype, statement = self.value.compile_cpp(depth, args, types, file)
        write_tabbed_line(file, self.name + " = " + statement + ";\n", depth)

    def run(self, args, vals, heep):
        arg = self.name
        val = self.value.run(args, vals, heep)
        if not override_variable(args, vals,  arg, val):
            hError(self.line_number, "השמתנה " + arg + " לא הוגדרת!")


class WhileScope(Scope):
    def __init__(self, condition: GetStatement, line_number) -> None:
        super().__init__(TYPE_WHILE_LOOP, line_number)
        self.condition = condition

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        vtype, statement = self.condition.compile_cpp(depth, args, types, file)
        write_tabbed_line(file, "while (" + statement + ") ", depth)
        super().compile_cpp(depth, args, types, file)
        file.write("\n")

    def run(self, args, vals, heep):
        while self.condition.run(args, vals, heep):
            super().run(args, vals, heep)


class IfStatement(CodeCommand):
    def __init__(self, condition: GetStatement, scope: Scope, line_number) -> None:
        super().__init__(TYPE_IF, line_number)
        self.condition = condition
        self.scope = scope

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        if self.condition != TYPE_ELSE:
            vtype, statement = self.condition.compile_cpp(
                depth, args, types, file)
            file.write("(" + statement + ") ")
        self.scope.compile_cpp(depth, args, types, file)

    def run(self, args, vals, heep):
        if(self.condition == TYPE_ELSE):
            # If this is an ELSE statement always run.
            self.scope.run(args, vals, heep)
            return True

        condition = self.condition.run(args, vals, heep)
        if condition:
            self.scope.run(args, vals, heep)
        return condition


class IfScope(Scope):
    def __init__(self, condition: GetStatement, scope: Scope, line_number) -> None:
        super().__init__(TYPE_IFSCOPE_HOLDER, line_number)
        self._statements = []
        self._statements.append(IfStatement(condition, scope, line_number))

    def compile_cpp(self, depth, args, types, file: TextIOWrapper):
        ifstatement: IfStatement = self._statements[0]
        write_tabbed_line(file, "if ", depth)
        ifstatement.compile_cpp(depth, args, types, file)

        ln = len(self._statements)
        if ln > 1:
            for i in range(1, ln-1):
                ifstatement: IfStatement = self._statements[i]
                file.write(" else if ")
                ifstatement.compile_cpp(depth, args, types, file)

            ifstatement: IfStatement = self._statements[-1]
            file.write(" else ")
            ifstatement.compile_cpp(depth, args, types, file)
        file.write("\n")

    def insert(self, ifstatement: IfStatement):
        if ifstatement.type != TYPE_IF:
            hError(self.line_number, "שגיאה מצפה ל IF קיבל משהו אחר.")
        self.add_else(ifstatement)

    def add_else(self, ifstatement: IfStatement):
        self._statements.append(ifstatement)

    def run(self, args, vals, heep):
        ifstatement: IfStatement
        for ifstatement in self._statements:
            if ifstatement.run(args, vals, heep):
                return


class Compiler():
    def __init__(self, filename, debug=False, flip=True) -> None:
        self.filename = filename
        self.IsDebug = debug
        self.flip = flip
        self.main = Scope(TYPE_MAIN, 0)
        self._encode()

    def log(self, output):
        if self.flip:
            print(get_display(str(output)))
        else:
            print(output)

    def debug(self, output):
        if self.IsDebug:
            print(output)

    def _encode(self):
        file1 = open(self.filename, 'r', encoding="utf-8")
        Lines = file1.readlines()

        # Strips the newline character
        skip = False

        scopes = []
        scopes.append(self.main)

        efo = len(Lines)
        next_line = 0
        while next_line < efo:
            line = Lines[next_line]
            current_line = next_line
            next_line += 1
            if len(line) > 0:
                if line[0] == ";":
                    skip = not skip
                    continue

            if skip:
                continue
            x = text_spliter(line, current_line)
            self.line_ecoder(x, current_line, scopes)
            # self.debug(str(current_line) + " : " + str(x))

        if len(scopes) > 1:
            hError(current_line, "קוד שגוי חסר סוף סקציה!")

    def line_ecoder(self, line_words: list, current_line, scopes: list) -> CodeCommand:
        self.debug(str(current_line) + " : " + str(line_words))
        if len(line_words) == 0:
            return

        if len(line_words) == 1:
            if(line_words[0] == "$-"):
                if len(scopes) == 1:
                    hError(current_line,
                           "מופיע סוף סקציה אבל אין תחילת סקציה חדשה!")
                scopes.pop()
                if scopes[-1].type == TYPE_IFSCOPE_HOLDER:
                    scopes.pop()
                return

        if(line_words[0] == "אחרת"):
            scopes.pop()
            ifscope: IfScope = scopes[-1]
            if ifscope.type != TYPE_IFSCOPE_HOLDER:
                hError(current_line, "מופיע אחרת אבל לא היה ביטוי אם!" +
                       "\nEXPECTS TYPE_IFSCOPE_HOLDER but got " + str(ifscope) + "\n" + str(line_words))

            nscope = Scope(TYPE_IFSCOPE, current_line)
            scopes.append(nscope)
            if len(line_words) > 1 and line_words[1] == "אם":
                cond = GetStatement(line_words[2:], current_line)
                ifscope.add_else(IfStatement(cond, nscope, current_line))
            else:
                ifscope.add_else(IfStatement(TYPE_ELSE, nscope, current_line))
            return

        if len(line_words) > 1:
            if line_words[0] == "כל":
                if line_words[1] == "עוד":
                    current: Scope = scopes[-1]
                    cond = GetStatement(line_words[2:], current_line)
                    wscope = WhileScope(cond, current_line)
                    current.insert(wscope)
                    scopes.append(wscope)
                else:
                    hError(current_line, "קוד שגוי אחרי כל מצפה ל-עוד")

            elif line_words[0] == "אם":
                current: Scope = scopes[-1]
                cond = GetStatement(line_words[1:], current_line)
                nscope = Scope(TYPE_IFSCOPE, current_line)
                ifscope = IfScope(
                    cond, nscope, current_line)
                current.insert(ifscope)
                scopes.append(ifscope)
                scopes.append(nscope)

            elif line_words[0] == "תדפיס":
                current = scopes[-1]
                message = GetStatement(line_words[1:], current_line)
                current.insert(PrintStatement(
                    message, self.flip, current_line))

            elif line_words[0] == "ויהי":
                if len(line_words) < 3 or line_words[2] != "$=":
                    hError(current_line, "קוד שגוי!")

                current = scopes[-1]
                var_name = line_words[1]
                var_value = GetStatement(line_words[3:], current_line)
                current.insert(InitStatement(
                    var_name, var_value, current_line))

            elif line_words[1] == "$=":
                current = scopes[-1]
                var_name = line_words[0]
                var_value = GetStatement(line_words[2:], current_line)
                current.insert(SetStatement(var_name, var_value, current_line))

    def compile_cpp(self, outfile):
        f = open(outfile, "w", encoding="utf-8")
        file1 = open("template/cpp/maintp.cpp", 'r', encoding="utf-8")
        Lines = file1.readlines()
        for line in Lines:
            f.write(line)

        f.write("\nvoid main_hebrew() ")
        args = []
        types = []
        self.main.compile_cpp(0, args, types, f)
        f.close()

    def run(self):
        args = []
        vals = []
        heep = {}
        self.main.run(args, vals, heep)
