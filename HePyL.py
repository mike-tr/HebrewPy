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


def get_val(args, vals, val, line_number):
    if val[0] == "\"":
        return val[1:]

    if val.isdigit():
        return int(val)
    if val.replace('.', '', 1).isdigit():
        return float(val)
    elif val == "לא":
        return False
    elif val == "כן":
        return True
    else:
        for i in range(len(args) - 1, -1, -1):
            if args[i] == val:
                return vals[i]
    hError(line_number, " : המשתנה " + val + " לא מוגדר!")


operations = ["+", "-", "*", "/", "==", "!=", "או",
              "וגם", "<=", ">=", "<", ">", "(", ")", ")"]


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
        arr += find_split(word, operations)
    return arr


def compute_val(args, vals, vec: list, line_number):
    if len(vec) == 0:
        return

    def execute_operation(operation, right, left):
        #print(right, operation, left)
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
    return sp


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

        line_number = 0
        args = []
        vals = []

        depth = 0
        doSection = True
        doElse = False

        depth_arr = []
        # Strips the newline character
        skip = False
        for line in Lines:
            if len(line) > 0:
                if line[0] == ";":
                    skip = not skip
                    line_number += 1
                    continue

            if skip:
                line_number += 1
                continue
            x = text_spliter(line, line_number)
            self.debug(str(line_number) + " : " + str(x))

            if len(x) == 0:
                continue

            if len(x) == 1:
                if(x[0] == "-"):
                    if(depth == 0):
                        hError(line_number, "סיומת של סקציה -, במקום לא חוקי!")
                    do = depth_arr.pop()
                    depth = do[0]
                    doSection = do[1]
                    doElse = do[2]

                if(x[0] == "אחרת"):
                    if not doSection:
                        doSection = True
                        doElse = False
                    else:
                        doSection = False
                        doElse = False
                continue

            if not doSection:
                continue

            if len(x) > 1:
                if x[1] == "=":
                    args.append(x[0])
                    #vals.append(get_val(args, vals, x[2], line_number))
                    vals.append(compute_val(
                        args, vals, extended_split(x[2:]), line_number))
                if x[0] == "אם":
                    depth_arr.append([depth, doSection, doElse])
                    depth += 1
                    condition = compute_val(
                        args, vals, extended_split(x[1:]), line_number)
                    if condition:
                        print("do if!")
                        doElse = False
                        doSection = True
                    else:
                        doElse = True
                        doSection = False

                if x[0] == "תדפיס":
                    message = compute_val(
                        args, vals, extended_split(x[1:]), line_number)
                    # for i in range(1, len(x)):
                    #     message = ""
                    #     if x[i][0] == '\"':
                    #         message += x[i][1:]
                    #     else:
                    #         message += str(get_val(args, vals,
                    #                        x[i], line_number))
                    # count += 1
                    self.log(message)
            # else:
            #     sys.exit(get_display("שגיאה בשורה " +
            #              str(line_number) + " : סינטקס לא נכון."))
            line_number += 1
        if depth > 0:
            hError(line_number, "קוד שגוי חסר סוף סקציה!")
