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


operations = ["+", "-", "*", "/", "==", "!=", "או",
              "וגם", "<=", ">=", "<", ">", ",", "=", "(", ")", ")"]


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
        arr += find_split(word, operations)
    return arr


def compute_val(args, vals, vec: list, line_number):
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
        elif operation == "or":
            return bool(right or left)
        elif operation == "and":
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


class CodeCommand():
    def __init__(self, ctype, line_number) -> None:
        self.type = ctype
        self.line_number = line_number

    def run(self, args, vals, heep):
        """
        Run code as is
        """
        pass


class Scope(CodeCommand):
    def __init__(self, ctype, line_number) -> None:
        super().__init__(ctype, line_number)
        self._code = []

    def insert(self, line: CodeCommand):
        self._code.append(line)

    def run(self, args: list, vals: list, heep: map):
        command: CodeCommand
        for command in self._code:
            command.run(args, vals, heep)

    def __str__(self) -> str:
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


class GetStatement(CodeCommand):
    def __init__(self, args, line_number) -> None:
        super().__init__(TYPE_GET, line_number)
        # Get some args, compute return value.
        self.args = args

    def run(self, args, vals, heep):
        return compute_val(
            args, vals, self.args, self.line_number)


class PrintStatement(CodeCommand):
    def __init__(self, message: GetStatement, flip, line_number) -> None:
        super().__init__(TYPE_PRINT, line_number)
        self.message = message
        self.flip = flip

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

    def run(self, args, vals, heep):
        arg = self.name
        val = self.value.run(args, vals, heep)
        add_variable(args, vals, arg, val)


class SetStatement(CodeCommand):
    def __init__(self, name, value: GetStatement, line_number) -> None:
        super().__init__(TYPE_SET, line_number)
        self.name = name
        self.value = value

    def run(self, args, vals, heep):
        arg = self.name
        val = self.value.run(args, vals, heep)
        if not override_variable(args, vals,  arg, val):
            hError(self.line_number, "השמתנה " + arg + " לא הוגדרת!")


class WhileScope(Scope):
    def __init__(self, condition: GetStatement, scope: Scope, line_number) -> None:
        super().__init__(TYPE_WHILE_LOOP, line_number)
        self.condition = condition

    def run(self, args, vals, heep):
        while self.condition.run(args, vals, heep):
            super().run(args, vals, heep)


class IfStatement(Scope):
    def __init__(self, condition: GetStatement, scope: Scope, line_number) -> None:
        super().__init__(TYPE_IF, line_number)
        self.condition = condition
        self.scope = scope

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
                    wscope = WhileScope(cond, Scope(
                        TYPE_IFSCOPE, current_line), current_line)
                    current.insert(wscope)
                    scopes.append(wscope)
                else:
                    hError(current_line, "קוד שגוי אחרי כל מצפה ל-עוד")

            elif line_words[0] == "אם":
                cond = GetStatement(line_words[1:], current_line)
                nscope = Scope(TYPE_IFSCOPE, current_line)
                ifscope = IfScope(cond, nscope, current_line)
                current = scopes[-1]
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

    def run(self):
        args = []
        vals = []
        heep = {}
        self.main.run(args, vals, heep)
