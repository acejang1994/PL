############################################################
# HOMEWORK 1
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

    def eval (self):
        return VInteger(self._integer)


class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self):
        return VBoolean(self._boolean)


class EPlus (Exp):
    # Addition operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EPlus({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "vector" and v2.type == "vector":
            return map2(v1,v2,lambda x1,x2: VInteger(x1 + x2),"integer")
        elif v1.type == "vector" and v2.type == "integer":
            return map2(v1,v1,lambda x1,x2: VInteger(x1 + v2.value),"integer")
        elif v1.type == "integer" and v2.type == "vector":
            return map2(v2,v2,lambda x1,x2: VInteger(x1 + v1.value),"integer")
        elif v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value + v2.value)
        elif v1.type == "integer" and v2.type == "rational":
            num, den = v1.value * v2.denom + v2.numer, v2.denom
        elif v1.type == "rational" and v2.type == "integer":
            num, den = v1.numer + v1.denom * v2.value, v1.denom
        elif v1.type == "rational" and v2.type == "rational":
            num, den = v1.numer * v2.denom + v2.numer * v1.denom, v1.denom * v2.denom
        else:
            raise Exception ("Runtime error: trying to add non-numbers")
        return simplify(num, den)


class EMinus (Exp):
    # Subtraction operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EMinus({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "vector" and v2.type == "vector":
            return map2(v1,v2,lambda x1,x2: VInteger(x1 - x2),"integer")
        elif v1.type == "vector" and v2.type == "integer":
            return map2(v1,v1,lambda x1,x2: VInteger(x1 - v2.value),"integer")
        elif v1.type == "integer" and v2.type == "vector":
            return map2(v2,v2,lambda x1,x2: VInteger(v1.value - x1),"integer")
        elif v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value - v2.value)
        elif v1.type == "integer" and v2.type == "rational":
            num, den = v1.value * v2.denom - v2.numer, v2.denom
        elif v1.type == "rational" and v2.type == "integer":
            num, den = v1.numer - v1.denom * v2.value, v1.denom
        elif v1.type == "rational" and v2.type == "rational":
            num, den = v1.numer * v2.denom - v2.numer * v1.denom, v1.denom * v2.denom
        else:
            raise Exception ("Runtime error: trying to subtract non-numbers")
        return simplify(num, den)


class ETimes (Exp):
    # Multiplication operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "ETimes({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "vector" and v2.type == "vector":
            return VInteger(reduce(lambda acc, h: acc + h.value, map2(v1,v2,lambda x1,x2: VInteger(x1 * x2),"integer").value, 0))
        elif v1.type == "vector" and v2.type == "integer":
            return map2(v1,v1,lambda x1,x2: VInteger(x1 * v2.value),"integer")
        elif v1.type == "integer" and v2.type == "vector":
            return map2(v2,v2,lambda x1,x2: VInteger(x1 *v1.value),"integer")
        elif v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value * v2.value)
        elif v1.type == "integer" and v2.type == "rational":
            num, den = v1.value * v2.numer, v2.denom
        elif v1.type == "rational" and v2.type == "integer":
            num, den = v1.numer * v2.value, v1.denom
        elif v1.type == "rational" and v2.type == "rational":
            num, den = v1.numer * v2.numer, v1.denom * v2.denom
        else:
            raise Exception ("Runtime error: trying to multiply non-numbers")
        return simplify(num, den)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self):
        v = self._cond.eval()
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval()
        else:
            return self._else.eval()

class EIsZero (Exp):
    # Multiplication operation

    def __init__ (self,e1):
        self._exp1 = e1

    def __str__ (self):
        return "EIsZero({})".format(self._exp1)

    def eval (self):
        v1 = self._exp1.eval()
        if v1.type == "integer":
            return VBoolean(v1.value == 0)
        raise Exception ("Runtime error: cannot perform EIsZero on a non integer")

class EAnd (Exp):
    # Multiplication operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EAnd({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "boolean":
            if v1.value:
                if v2.type == "boolean":
                    return VBoolean(v2.value)
            else:
                return VBoolean(v1.value)
        if v1.type == "vector" and v2.type == "vector":
            return map2(v1,v2,lambda x1,x2: VBoolean(x1 and x2),"boolean")        
        elif v1.type == "vector" and v2.type == "boolean":
            return map2(v1,v1,lambda x1,x2: VBoolean(x1 and v2.value),"boolean")
        elif v1.type == "boolean" and v2.type == "vector":
            return map2(v2,v2,lambda x1,x2: VBoolean(x1 and v1.value),"boolean")


        raise Exception ("Runtime error: cannot perform EAnd on non boolean")


class EOr (Exp):
    # Multiplication operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EOr({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "boolean":
            if v1.value:
                return VBoolean(v1.value)
            else:
                if v2.type == "boolean":
                    return VBoolean(v2.value)
        if v1.type == "vector" and v2.type == "vector":
            return map2(v1,v2,lambda x1,x2: VBoolean(x1 or x2),"boolean")
        elif v1.type == "vector" and v2.type == "boolean":
            return map2(v1,v1,lambda x1,x2: VBoolean(x1 or v2.value),"boolean")
        elif v1.type == "boolean" and v2.type == "vector":
            return map2(v2,v2,lambda x1,x2: VBoolean(x1 or v1.value),"boolean")

        raise Exception ("Runtime error: cannot perform EOr on non boolean")


class ENot (Exp):
    # Multiplication operation

    def __init__ (self,e1):
        self._exp1 = e1

    def __str__ (self):
        return "ENot({})".format(self._exp1)

    def eval (self):
        v1 = self._exp1.eval()
        if v1.type == "boolean":
            return VBoolean(not (v1.value))
        if v1.type == "vector":
            return map2(v1,v1,lambda x1,x2: VBoolean(not x1),"boolean")
        raise Exception ("Runtime error: cannot perform ENot on non boolean")

class EVector (Exp):
    # Multiplication operation

    def __init__ (self,e1):
        self._exp1 = e1

    def __str__ (self):
        return "EVector({})".format(self._exp1)

    def eval (self):
        return VVector(map(lambda x: x.eval(), self._exp1))

class EDiv (Exp):
    # Multiplication operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EDiv({},{}})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            num, den = v1.value, v2.value
        elif v1.type == "integer" and v2.type == "rational":
            num, den = v1.value * v2.denom, v2.numer
        elif v1.type == "rational" and v2.type == "integer":
            num, den = v1.numer , v1.denom * v2.value
        elif v1.type == "rational" and v2.type == "rational":
            num, den = v1.numer * v2.denom, v1.denom * v2.numer
        else:
            raise Exception ("Runtime error: inputs must be rational")
        return simplify(num, den)
        

def simplify(num, den):
    a = gcd(num, den)
    if a == den:
        return VInteger(num/a)
    return VRational(num/a, den/a)

def gcd(a, b):
    while b:
        a, b = b, a%b
    return a

def lcm(a, b):
    return a*b/gcd(a,b)

def map2(v1,v2,f,t):
    if v1.length == v2.length:
        for i in range(v1.length):
            if v1.get(i).type != t or v2.get(i).type != t:
                raise Exception ("Runtime error: vectors must contain values of type " + t)
        return VVector([f(v1.get(i).value,v2.get(i).value) for i in range(v1.length)])
    raise Exception ("Runtime error: vectors are not the same length")

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

class VBoolean (Value):
    # Value representation of Booleans
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

class VVector (Value):

    def __init__(self,v):
        self.value = v
        self.type = "vector"
        self.length = len(v)

    def get(self,index):
        return self.value[index]

class VRational (Value):

    def __init__(self,n,d):
        self.numer = n
        self.denom = d
        self.type = "rational"
