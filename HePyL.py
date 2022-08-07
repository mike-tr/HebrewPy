import re
from bidi.algorithm import get_display
import sys

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


class Interpretor():
    def __init__(self, filename) -> None:
        self.filename = filename
        self.IsDebug = True
        self.flip = True

    def log(self, output):
        if self.flip:
            print(get_display(str(output)))
        else:
            print(output)

    def debug(self, output):
        if self.IsDebug:
            print(output)

    def run(self):
        file1 = open(self.filename, 'r', encoding="utf-8")
        Lines = file1.readlines()

        args = []
        vals = []

        depth = 0
        skipDepth = 0
        doElse = False

        depth_arr = []
        # Strips the newline character
        skip = False

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
            #self.debug(str(current_line) + " : " + str(x))

            if len(x) == 0:
                continue

            if len(x) == 1:
                if(x[0] == "$-"):
                    if(depth == 0):
                        hError(current_line, "סיומת של סקציה - במקום לא חוקי!")
                    do = depth_arr.pop()
                    if skipDepth == 0:
                        clear_scope(args, vals)
                    else:
                        skipDepth -= 1
                    depth -= 1
                    doElse = do[0]
                    goto = do[1]

                    if goto >= 0:
                        next_line = goto
                        #print("goto", goto)
                    continue

            if(x[0] == "אחרת"):
                if skipDepth > 1:
                    continue
                elif skipDepth == 1:
                    if doElse:
                        if len(x) > 1 and x[1] == "אם":
                            condition = compute_val(
                                args, vals, x[2:], current_line)
                            if condition:
                                args.append("$")
                                vals.append("-")
                                doElse = False
                                skipDepth = 0
                        else:
                            skipDepth = 0
                            args.append("$")
                            vals.append("-")
                else:
                    skipDepth = 1
                continue

            if skipDepth > 0:
                if x[0] == "אם" or x[0] == "כל":
                    depth += 1
                    skipDepth += 1
                    depth_arr.append([doElse, -1])
                    doElse = False
                continue

            if len(x) > 1:
                if x[0] == "כל":
                    if x[1] == "עוד":
                        depth += 1
                        goto = current_line
                        condition = compute_val(
                            args, vals, x[2:], current_line)
                        if condition:
                            args.append("$")
                            vals.append("-")
                        else:
                            goto = -1
                            skipDepth += 1
                        # print(condition)
                        depth_arr.append([doElse, goto])
                        doElse = False

                    else:
                        hError(current_line, "קוד שגוי אחרי כל מצפה ל-עוד")

                elif x[0] == "אם":
                    depth_arr.append([doElse, -1])
                    depth += 1
                    condition = compute_val(
                        args, vals, x[1:], current_line)
                    if condition:
                        args.append("$")
                        vals.append("-")
                        doElse = False
                    else:
                        skipDepth += 1
                        doElse = True

                elif x[0] == "תדפיס":
                    message = compute_val(
                        args, vals, x[1:], current_line)
                    self.log(message)
                elif x[0] == "ויהי":
                    if len(x) < 3 or x[2] != "$=":
                        hError(current_line, "קוד שגוי!")
                    arg = x[1]
                    val = compute_val(
                        args, vals, x[3:], current_line)
                    add_variable(args, vals, arg, val)
                elif x[1] == "$=":
                    arg = x[0]
                    val = compute_val(
                        args, vals, x[2:], current_line)
                    # add_variable(args, vals, arg, val)
                    if not override_variable(args, vals,  arg, val):
                        hError(current_line, "השמתנה " + arg + " לא הוגדרת!")
                        # else:
                        #     sys.exit(get_display("שגיאה בשורה " +
                        #              str(line_number) + " : סינטקס לא נכון."))
        if depth > 0:
            hError(current_line, "קוד שגוי חסר סוף סקציה!")
        # self.debug(str(args) + "\n" + str(vals))
