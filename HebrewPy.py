import imp


import HePyL
import HePyCompiler
import sys

# interpretor = HePyL.Interpretor(sys.argv[1])
# interpretor.run()

debug = False
flip = True
compiler = HePyCompiler.Compiler(sys.argv[1], debug, flip)
#compiler.IsDebug = False
print("----- Compiler test ------")
compiler.run()
