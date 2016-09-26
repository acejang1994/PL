############################################################
# HOMEWORK 2
#
# Team members: James Jang and Sidd Singal
#
# Emails: acejang1994@gmail.com, siddharth.singal@students.olin.edu
#
# Remarks:
#



#
# Expressions
#

class Exp (object):
    pass



class EInteger (Exp):
    # Integer literal

    def __init__ (self,i):
        self._integer = i

    def __str__ (self):
        return "EInteger({})".format(self._integer)

    def eval (self,prim_dict,fun_dict=None):
        return VInteger(self._integer)

    def substitute (self,id,new_e):
        return self

class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self,prim_dict,fun_dict=None):
        return VBoolean(self._boolean)

    def substitute (self,id,new_e):
        return self


class EPrimCall (Exp):

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "EPrimCall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,prim_dict,fun_dict=None):
        vs = [ e.eval(prim_dict,fun_dict) for e in self._exps ]
        return apply(prim_dict[self._name],vs)

    def substitute (self,id,new_e):
        new_es = [ e.substitute(id,new_e) for e in self._exps]
        return EPrimCall(self._name,new_es)

class ECall (Exp):

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "ECall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,prim_dict,fun_dict):
        bindings = list(zip(fun_dict[self._name]["params"], self._exps))
        return ELet(bindings, fun_dict[self._name]["body"]).eval(prim_dict,fun_dict)

    def substitute (self,id,new_e):
        new_es = [ e.substitute(id,new_e) for e in self._exps]
        return ECall(self._name,new_es)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,prim_dict,fun_dict=None):
        v = self._cond.eval(prim_dict,fun_dict)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(prim_dict,fun_dict)
        else:
            return self._else.eval(prim_dict,fun_dict)

    def substitute (self,id,new_e):
        return EIf(self._cond.substitute(id,new_e),
                   self._then.substitute(id,new_e),
                   self._else.substitute(id,new_e))


class ELet (Exp):
    # local binding

    def __init__ (self,array,e1):
        self._array = array
        self._e1 = e1

    def __str__ (self):
        return "ELet({},{})".format(self._array,self._e1)

    def eval (self,prim_dict,fun_dict=None):
        new_e2 = reduce(lambda acc,h: acc.substitute(h[0],h[1]), self._array, self._e1)
        return new_e2.eval(prim_dict,fun_dict)

    def substitute (self,id,new_e):
        newarray = []
        exists = False
        for (id2,e2) in self._array:
            if id==id2:
                exists = True
            newarray.append((id2,e2.substitute(id,new_e)))
        if not exists:
            newarray.append((id,new_e))
        return ELet(newarray,self._e1)

class ELetS (Exp):
    # local binding

    def __init__ (self,array,e1):
        self._array = array
        self._e1 = e1

    def __str__ (self):
        return "ELet({},{})".format(self._array,self._e1)

    def eval (self,prim_dict,fun_dict=None):
        return self.expand().eval(prim_dict,fun_dict)
    
    def substitute (self,id,new_e):
        return self.expand().substitute(id,new_e)

    def expand(self):
        return reduce(lambda acc,h: ELet([h],acc), self._array[::-1],self._e1)
        

class ELetV (Exp):
    # local binding

    def __init__ (self,id,e1,e2):
        self._id = id
        self._e1 = e1
        self._e2 = e2

    def __str__ (self):
        return "ELetV({},{},{})".format(self._id,self._e1,self._e2)

    def eval (self,prim_dict,fun_dict=None):
        new_e2 = self._e2.substitute(self._id,self._e1.eval(prim_dict,fun_dict).toExpr())
        return new_e2.eval(prim_dict,fun_dict)

    def substitute (self,id,new_e):
        if id == self._id:
            return ELetV(self._id,
                        self._e1.substitute(id,new_e),
                        self._e2)
        return ELetV(self._id,
                    self._e1.substitute(id,new_e),
                    self._e2.substitute(id,new_e))


class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,prim_dict,fun_dict=None):
        raise Exception("Runtime error: unknown identifier {}".format(self._id))

    def substitute (self,id,new_e):
        if id == self._id:
            return new_e
        return self
    
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

    def toExpr(self):
        return EInteger(self.value)

class VBoolean (Value):
    # Value representation of Booleans
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def toExpr(self):
        return EBoolean(self.value)





# Primitive operations

def oper_plus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")


# Initial primitives dictionary

INITIAL_PRIM_DICT = {
    "+": oper_plus,
    "*": oper_times,
    "-": oper_minus
}
# we need a zero? operation in the initial primitives dictionary
def oper_zero (v1):
       if v1.type == "integer":
           return VBoolean(v1.value==0)
       raise Exception ("Runtime error: type error in zero?")

INITIAL_PRIM_DICT["zero?"] = oper_zero

# here's a function dictionary
FUN_DICT = {
      "square": {"params":["x"],
                 "body":EPrimCall("*",[EId("x"),EId("x")])},
      "=": {"params":["x","y"],
            "body":EPrimCall("zero?",[EPrimCall("-",[EId("x"),EId("y")])])},
      "+1": {"params":["x"],
             "body":EPrimCall("+",[EId("x"),EInteger(1)])},
      "sum_from_to": {"params":["s","e"],
                      "body":EIf(ECall("=",[EId("s"),EId("e")]),
                                 EId("s"),
                                 EPrimCall("+",[EId("s"),
                                                ECall("sum_from_to",[ECall("+1",[EId("s")]),
                                                                     EId("e")])]))}
    }
