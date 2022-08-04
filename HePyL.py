import re
from bidi.algorithm import get_display

"""
    5 - 3 + 10 => ((5 - 3) + 10)

    5 * 10 / (3 + 33) => (5 * 10) / (3 + 33)
    5 * 10 / 3 * 2 => (((5 * 10) / 3) * 2)

    <pt> := <Number>
            | ( <nop> )

    <nop> := <pt>
            | <nop> + <pt>
            | <nop> - <pt>
            | <nop> / <pt>
            | <nop> * <pt>

    <bop> := 'True
            |   'False
            |   <nop>
            |  ( <bop> or <bop>  )
            |  ( <bop> and <bop> )
            |   <bop> == <bop>
            |   <bop> != <bop>
            |   <nop> == <nop>
            |   <nop> != <nop>
            |   <nop> > <nop>
            |   <nop> < <nop>
            |   <nop> <= <nop>
            |   <nop> >= <nop>
"""


def get_val(args, vals, val, line_number):
    if val[0] == "\"":
        return val[1:]

    if val.isnumeric():
        return float(val)
    else:
        for i in range(len(args) - 1, -1, -1):
            if args[i] == val:
                return vals[i]
    print(get_display("שגיאה בשורה " + str(line_number) +
          " : המשתנה " + val + " לא מוגדר!"))


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
            print(get_display("שגיאה בשורה " + str(line_number) +
                  " : התחיל טקסט אבל אין סוגר טקסט"))
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

    def run(self):
        file1 = open(self.filename, 'r', encoding="utf-8")
        Lines = file1.readlines()

        line_number = 0
        args = []
        vals = []
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
            print(line_number, " : ", x)
            if len(x) > 1:
                if x[1] == "=":
                    if len(x) > 3 and x[2][-1] != '(':
                        print(get_display("שגיאה בשורה " +
                              str(line_number) + " : ניתן להתחל רק משתנה 1"))
                        return
                    args.append(x[0])
                    vals.append(get_val(args, vals, x[2], line_number))
                if x[0] == "אם":
                    pass
                if x[0] == "תדפיס":
                    for i in range(1, len(x)):
                        message = ""
                        if x[i][0] == '\"':
                            message += x[i][1:]
                        else:
                            message += str(get_val(args, vals,
                                           x[i], line_number))
                    # count += 1
                    print(get_display(message))
            line_number += 1
