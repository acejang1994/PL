############################################################
# HOMEWORK 4
#
# Team members: James Jang and Sidd Singal
#
# Emails: acejang1994@gmail.com, ssingal@gmail.com
#
# Remarks:
#

import sys
from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums


#
# Expressions
#

class Exp (object):
    def type ():
        return "expression"


class EValue (Exp): # Value literal (could presumably replace EInteger and EBoolean)
    def __init__ (self,v):
        self._value = v
    
    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,fun_dict):
        return self._value

    def substitute (self,id,new_e):
        return self

    def evalEnv (self,fun_dict,env):
        return self._value


class EInteger (Exp):
    # Integer literal

    def __init__ (self,i):
        self._integer = i

    def __str__ (self):
        return "EInteger({})".format(self._integer)

    def eval (self,fun_dict):
        return VInteger(self._integer)

    def substitute (self,id,new_e):
        return self

    def evalEnv (self,fun_dict,env):
        return VInteger(self._integer)

class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self,fun_dict):
        return VBoolean(self._boolean)

    def substitute (self,id,new_e):
        return self

    def evalEnv (self,fun_dict,env):
        return VBoolean(self._boolean)

class EPrimCall (Exp):
    # Call an underlying Python primitive, passing in Values
    #
    # simplifying the prim call
    # it takes an explicit function as first argument

    def __init__ (self,prim,es):
        self._prim = prim
        self._exps = es

    def __str__ (self):
        return "EPrimCall(<prim>,[{}])".format(",".join([ str(e) for e in self._exps]))

    def eval (self,fun_dict):
        vs = [ e.eval(fun_dict) for e in self._exps ]
        return apply(self._prim,vs)

    def substitute (self,id,new_e):
        new_es = [ e.substitute(id,new_e) for e in self._exps]
        return EPrimCall(self._prim,new_es)

    def evalEnv (self,fun_dict,env):
        vs = [ e.evalEnv(fun_dict,env) for e in self._exps ]
        return apply(self._prim,vs)

class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,fun_dict):
        v = self._cond.eval(fun_dict)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(fun_dict)
        else:
            return self._else.eval(fun_dict)

    def substitute (self,id,new_e,env):
        return EIf(self._cond.substitute(id,new_e),
                   self._then.substitute(id,new_e),
                   self._else.substitute(id,new_e))

    def evalEnv (self,fun_dict,env):
        v = self._cond.evalEnv(fun_dict,env)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.evalEnv(fun_dict,env)
        else:
            return self._else.evalEnv(fun_dict,env)

class ELet (Exp):
    # local binding
    # allow multiple bindings
    # eager (call-by-avlue)

    def __init__ (self,bindings,e2):
        self._bindings = bindings
        self._e2 = e2

    def __str__ (self):
        return "ELet([{}],{})".format(",".join([ "({},{})".format(id,str(exp)) for (id,exp) in self._bindings ]),self._e2)

    def eval (self,fun_dict):
        # by this point, all substitutions in bindings expressions have happened already (!)
        new_e2 = self._e2
        for (id,e) in self._bindings:
            v = e.eval(fun_dict)
            new_e2 = new_e2.substitute(id,EValue(v))
        return new_e2.eval(fun_dict)

    def substitute (self,id,new_e):
        new_bindings = [ (bid,be.substitute(id,new_e)) for (bid,be) in self._bindings]
        if id in [ bid for (bid,_) in self._bindings]:
            return ELet(new_bindings, self._e2)
        return ELet(new_bindings, self._e2.substitute(id,new_e))

    def evalEnv (self,fun_dict,env):
        # by this point, all substitutions in bindings expressions have happened already (!)
        new_e2 = self._e2
        new_env = env.copy()
        for (id,e) in self._bindings:
                new_env[id] = e.evalEnv(fun_dict,env)
        return new_e2.evalEnv(fun_dict,new_env)

class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,fun_dict):
        raise Exception("Runtime error: unknown identifier {}".format(self._id))

    def substitute (self,id,new_e):
        if id == self._id:
            return new_e
        return self

    def evalEnv (self,fun_dict,env):
        return env[self._id]

class ECall (Exp):
    # Call a defined function in the function dictionary

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "ECall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,fun_dict):
        vs = [ e.eval(fun_dict) for e in self._exps ]
        params = fun_dict[self._name]["params"]
        body = fun_dict[self._name]["body"]
        if len(params) != len(vs):
            raise Exception("Runtime error: wrong number of argument calling function {}".format(self._name))
        for (val,p) in zip(vs,params):
            body = body.substitute(p,EValue(val))
        return body.eval(fun_dict)

    def substitute (self,var,new_e):
        new_es = [ e.substitute(var,new_e) for e in self._exps]
        return ECall(self._name,new_es)

    def evalEnv (self,fun_dict,env):
        vs = [ e.evalEnv(fun_dict,env) for e in self._exps ]
        params = fun_dict[self._name]["params"]
        body = fun_dict[self._name]["body"]
        if len(params) != len(vs):
            raise Exception("Runtime error: wrong number of argument calling function {}".format(self._name))
        newEnv = env.copy()
        for (val,p) in zip(vs,params):
            newEnv[p] = val
        return body.evalEnv(fun_dict,newEnv)


    
#
# Values
#

class Value (object):
    pass


class VInteger (Value):
    # Value representation of integers
    
    def __init__ (self,i):
        self.value = i
        self.type = "integer"

    def __str__ (self):
        return str(self.value)

class VBoolean (Value):
    # Value representation of Booleans
    
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def __str__ (self):
        return "true" if self.value else "false"



# Primitive operations

def oper_plus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to subtract non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to multiply non-numbers")

def oper_zero (v1):
    if v1.type == "integer":
        return VBoolean(v1.value==0)
    raise Exception ("Runtime error: type error in zero?")


# Initial primitives dictionary

INITIAL_FUN_DICT = {
    "+": {"params":["x","y"],
          "body":EPrimCall(oper_plus,[EId("x"),EId("y")])},
    "-": {"params":["x","y"],
          "body":EPrimCall(oper_minus,[EId("x"),EId("y")])},
    "*": {"params":["x","y"],
          "body":EPrimCall(oper_times,[EId("x"),EId("y")])},
    "zero?": {"params":["x"],
              "body":EPrimCall(oper_zero,[EId("x")])},
    "square": {"params":["x"],
               "body":ECall("*",[EId("x"),EId("x")])},
    "=": {"params":["x","y"],
          "body":ECall("zero?",[ECall("-",[EId("x"),EId("y")])])},
    "+1": {"params":["x"],
           "body":ECall("+",[EId("x"),EValue(VInteger(1))])},
    "sum_from_to": {"params":["s","e"],
                    "body":EIf(ECall("=",[EId("s"),EId("e")]),
                               EId("s"),
                               ECall("+",[EId("s"),
                                          ECall("sum_from_to",[ECall("+1",[EId("s")]),
                                                               EId("e")])]))}
}



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/


def parse (input):
    # parse a string into an element of the abstract representation

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( let ( ( <name> <expr> ) ) <expr> )
    #            ( <name> <expr> ... )
    #


    idChars = alphas+"_+*-?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EId(result[0]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("-0123456789","0123456789")
    pINTEGER.setParseAction(lambda result: EInteger(int(result[0])))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EBoolean(result[0]=="true"))

    pEXPR = Forward()

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    def parseCond(result):
        if len(result) == 0:
            return EBoolean(False)
        else:
            return EIf(result[0][0], result[0][1], parseCond(result[1:]))
        
    pCOND = "(" + Keyword("cond") + ZeroOrMore("(" + pEXPR + pEXPR + ")") + ")"
    pCOND.setParseAction(lambda result: parseCond( [(result[i*4+3],result[i*4+4]) for i in range( ( len(result)-3)/4)] ))

    pBINDING = "(" + pNAME + pEXPR + ")"
    pBINDING.setParseAction(lambda result: (result[1],result[2]))

    pBINDINGS = OneOrMore(pBINDING)
    pBINDINGS.setParseAction(lambda result: [ result ])

    pLET = "(" + Keyword("let") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLET.setParseAction(lambda result: ELet(result[3],result[5]))

    def parseLetS(result, expr):
        if len(result) == 1:
            return ELet( [result[0]], expr)
        else:
            return ELet([result[0]], parseLetS(result[1:],expr))

    pLETS = "(" + Keyword("let*") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLETS.setParseAction(lambda result: parseLetS(result[3],result[5]))

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    pCALL = "(" + pNAME + pEXPRS + ")"
    pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    def parseAnd(result):
        if len(result) == 0:
            return EBoolean(True)
        elif len(result) == 1:
            return result[0]
        else:
            return EIf(result[0],parseAnd(result[1:]),EBoolean(False))

    pAND = "(" + Keyword("and") + ZeroOrMore(pEXPR) + ")"
    pAND.setParseAction(lambda result: parseAnd(result[2:-1]))
    
    def parseOr(result):
        if len(result) == 0:
            return EBoolean(False)
        elif len(result) == 1:
            return result[0]
        else:
            return EIf(result[0],EBoolean(True), parseOr(result[1:]))

    pOR = "(" + Keyword("or") + ZeroOrMore(pEXPR) + ")"
    pOR.setParseAction(lambda result: parseOr(result[2:-1]))

    pEXPR << (pINTEGER | pBOOLEAN | pIDENTIFIER | pIF | pCOND | pLET | pLETS | pAND | pOR | pCALL)

    # can't attach a parse action to pEXPR because of recursion, so let's duplicate the parser
    pTOPEXPR = pEXPR.copy()
    pTOPEXPR.setParseAction(lambda result: {"result":"expression","expr":result[0]})
    
    pDEFUN = "(" + Keyword("defun") + pNAME + "(" + pNAMES + ")" + pEXPR + ")"
    pDEFUN.setParseAction(lambda result: {"result":"function",
                                          "name":result[2],
                                          "params":result[4],
                                          "body":result[6]})

    pTOP = (pDEFUN | pTOPEXPR)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 4 - Calc Language"

    # work on a copy because we'll be adding to it
    fun_dict = INITIAL_FUN_DICT.copy()
    
    while True:
        inp = raw_input("calc> ")
        if not inp:
            return
        result = parse(inp)
        if result["result"] == "expression":
            exp = result["expr"]
            print "Abstract representation:", exp
            v = exp.eval(fun_dict)
            print v
        elif result["result"] == "function":
            # a result is already of the right form to put in the
            # functions dictionary
            fun_dict[result["name"]] = result
            print "Function {} added to functions dictionary".format(result["name"])

def shellEnv ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 4 - Calc Language (with environment)"

    # work on a copy because we'll be adding to it
    fun_dict = INITIAL_FUN_DICT.copy()
    
    while True:
        inp = raw_input("calc> ")
        if not inp:
            return
        result = parse(inp)
        env = {}
        if result["result"] == "expression":
            exp = result["expr"]
            print "Abstract representation:", exp
            v = exp.evalEnv(fun_dict,env)
            print v
        elif result["result"] == "function":
            # a result is already of the right form to put in the
            # functions dictionary
            fun_dict[result["name"]] = result
            print "Function {} added to functions dictionary".format(result["name"])

# increase stack size to let us call recursive functions quasi comfortably
sys.setrecursionlimit(10000)