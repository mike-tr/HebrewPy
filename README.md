# HebrewPy


I dont know why would anyone need this, but this is just a very simple compiler/interpreter, that can run/compile hebrew code.
Currently, one can interpret and run the code as python, or compile it into C++.

### To run the code, one would need to call:
```
compiler = HePyCompiler.Compiler( sourcefile, debug=false, flip=true)
compiler.run()
```
* this will run the code in python *
* debug - prints some debug info, flip = mirrors the output *

### To compile into Cpp file.
compiler = HePyCompiler.Compiler( sourcefile, debug=false)
compiler.compile_cpp("outputfile.cpp")

* this will rewrite/create a new file outputfile.cpp with the Cpp code *

## What currently supported
- Set/Initialize variables. (keyword ויהי)
  - ויהי שם_משתנה = ערך_כלשהו
- Print. (keyword הדפס)
  - הדפס "משהו" + שם_משתנה
- Supports +,-,/,* and or as well as ().
  - ויהיה איקס = 5/10+(33/(10/2))
  - Can add to string number, with will simply append it, and can combine strings by +.
- if, else if, else, while
```
כל עוד א > 0
	תדפיס "א = " + א
	אם א > 10
		תדפיס "א>10"
		אם א > 20
			תדפיס "וגם א>20 : " + א
			א=א-2
		אחרת
			תדפיס "וגם א<20 : " + א
			א = א-1
		-
		א=א-1
		תדפיס "סוף א>10 : " + א
	אחרת	אם א>5
		א = א-1
		תדפיס "א>5"
	אחרת
		תדפיס "א<5"
	-
	א=א - 1
-
```
- We end a scope by the symbol -, scope starts after if,if else, else automaticaly.

#### Remark
The code can be easily modified to work with any language one simply needs to rename all accurances of keywords, for instance "אם" might be renamed to "check",
and soo on, i will likely in the future add a file with keywords, so one can change the language to look diffrently, but with same format i guess.

#### python vs c++
There might be differences in behaviour for instance as python allows one to override existing variable with a value of a different type, code that does exactly that would 
work fine in python (i.e if we run compiler.run() ), but will return an uncompilable code for c++ (i.e compiler.compile_cpp("outputfile.cpp")).

#### this was done for fun.
