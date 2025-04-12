from enum import Enum
from utils.PrettyStream import PrettyStream
from lark import Tree, Token
from itertools import permutations, product
from utils.PrettyStream import vprint, QUIET, INFO, VERBOSE, DEBUG, ALL

class Module():
    def __init__(self, name):
        self.name = name
        self.vars = {}
        self.inputs = set()
        self.outputs = set()
        self.deps = {}

    def add_var(self, var, expr = None, dep = None):
        if(var in self.vars and self.vars[var] is None):
            self.vars[var] = expr
            self.deps[var] = dep
        elif (not var in self.vars):
            self.vars[var] = expr
            self.deps[var] = dep
        else:
            raise ValueError(f"Duplicate definition of variable {var} in module {self.name}")

    def add_input(self, var, expr = None):
        if var in self.inputs:
            raise ValueError(f"Input {var} already exists in module {self.name}")
        self.inputs.add(var)
        self.add_var(var, expr)

    def add_output(self, var, expr = None):
        if var in self.outputs:
            raise ValueError(f"Output {var} already exists in module {self.name}")
        self.outputs.add(var)
        self.add_var(var, expr)

    def to_json(self):
        return {
            "name": self.name,
            "inports": self.inports,
            "outports": self.outports
        }
    
    def pretty(self):
        p = PrettyStream()
        p << ["module", self.name]
        with p:
            p << ["inputs"]
            with p:
                for i in self.inputs:
                    p << i
            p << ["outputs"]
            with p:
                for o in self.outputs:
                    p << o
            p << ["vars"]
            with p:
                for k, v in self.vars.items():
                    p << [ k, ":", str(v), ]
                    if(k in self.deps and self.deps[k] is not None and len(self.deps[k]) > 0):
                        with p:
                            p << ["dep", ":"] + list(self.deps[k])
        return p.cache

def int_to_barr(n:int, size:int):
    return [((n >> i) & 1) for i in range(size)]

def barr_to_int(barr):
    return sum([b << i for i, b in enumerate(barr)])
    
class TruthTable():
    def find_canon(self):
        for name, tt, num_in, _ in CELLS:
            if(tt == self.canon[0] and num_in == len(self.ins)):
                return f"({name})"
        return ""

    def __init__(self, ins, out, skip_canon = False):
        if isinstance(out, int):
            out = int_to_barr(out, 2**len(ins))
        self.ins = ins
        if(2**len(ins) != len(out)):
            raise ValueError(f"Invalid Truth Table")
        self.out = out
        self.canon = (0, range(len(ins)))
        self.id = "."
        if(not skip_canon):
            vprint("CANONING", ins, out, v=ALL)
            self.canon = self.canonical()
            self.id = self.compute_id()

    def compute_id(self):
        can = self.canonicalize()
        id = ""
        for i in can.ins:
            id += str(i) + "."
        id+=str(self.canon[0])
        return id

    def eval(self, *inputs):
        if(len(inputs) == 1 and isinstance(inputs[0], list)):
            inputs = inputs[0]
        index = 0
        for i in inputs:
            index = (index << 1) | i
        return self.out[index]

    def permute(self, *perm):
        if(len(perm) == 1 and isinstance(perm[0], (tuple,list))):
            perm = perm[0]
        if(len(perm) != len(self.ins)):
            raise ValueError("Invalid permutation")
        if(isinstance(perm[0], str)):
            perm = [self.ins.index(p) for p in perm]
        new_ins = [self.ins[i] for i in perm]
        new_out = [ 0 for i in range(len(self.out))]
        for i in range(len(self.out)):
            index = int_to_barr(i, len(self.out))
            new_barr = [index[perm[j]] for j in range(len(perm))]
            new_index = barr_to_int(new_barr)
            new_out[i] = self.out[new_index]
        new_t = TruthTable(new_ins, new_out, True)

        new_canon_perm = [i for i in range(len(new_ins))]
        for i in range(len(perm)):
            new_canon_perm[perm[i]] = i
        new_t.canon = (self.canon[0], new_canon_perm)
        new_t.id = self.id
        return new_t

    def canonical(self):
        best = -1
        for perm in permutations(range(len(self.ins))):
            permuted = self.permute(*perm)
            new_canon = barr_to_int(permuted.out)
            if(new_canon > best):
                best = new_canon
        return best, perm
    
    def prune(self):
        if len(self.ins) <= 1:
            return self
        for perm in permutations(range(len(self.ins))):
            permuted = self.permute(*perm)
            # if upper and lower is equal, input is irrelevant
            l = 2**len(self.ins)-1
            pout = barr_to_int(permuted.out)
            if pout >> l == pout & ((1 << l) - 1):
                permuted.ins.remove(len(permuted.ins)-1)
                return TruthTable(permuted.ins, pout >> l).prune()
        return self

    def canonicalize(self):
        return self.permute(*self.canon[1])

    def __repr__(self):
        out_str = ""
        for i in range(len(self.out)-1, -1, -1):
            out_str += f"{self.out[i]}"
        ins_str = ",".join(self.ins)
        repr = f"({ins_str})->{out_str}/{self.canon[0]}"
        repr += self.find_canon()
        return repr
    

    def combine(self, *input_truths):
        if(len(input_truths) == 1 and isinstance(input_truths[0], (tuple, list))):
            input_truths = input_truths[0]
        if(isinstance(input_truths, tuple)):
            input_truths = list(input_truths)
        if(len(input_truths) != len(self.ins)):
            vprint("in_tt: ", input_truths, "| ins:", self.ins, v=DEBUG)
            raise ValueError("Invalid number of inputs")
        fc = self.find_canon()
        if(len(fc) > 0):
            vprint("COMBINE", fc , "with", input_truths, v=DEBUG)
        else:
            vprint("COMBINE", self.canon[0], "with", input_truths,v=DEBUG)
        for i in range(len(input_truths)):
            if(isinstance(input_truths[i], Token)):
                input_truths[i] = TruthTable([input_truths[i].value], 0b10)
            elif(isinstance(input_truths[i], str)):
                input_truths[i] = TruthTable([input_truths[i]], 0b10)
        
        new_ins = set()
        for itt in input_truths:
            new_ins = new_ins.union(itt.ins)
        new_ins = list(new_ins)
        all_entries = range(2**len(new_ins))
        new_ins_dict = dict([(new_ins[i], len(new_ins)-1-i) for i in range(len(new_ins))])
        vprint("NEW INS:", new_ins_dict, v=DEBUG)
        if(len(new_ins) > 5):
            raise ValueError("Combining more than 5 inputs")
        new_outs = [0 for i in range(2**len(new_ins))]

        for perm in all_entries:
            evals = []
            perm_barr = int_to_barr(perm, len(new_ins))
            for itt in input_truths:
                itt_inss = []
                for itt_in in itt.ins:
                    itt_inss.append(perm_barr[new_ins_dict[itt_in]])
                evals.append(itt.eval(itt_inss))

            vprint(f"{perm}:{evals},{self.eval(evals)}", v=ALL)
            new_outs[perm] = self.eval(evals)

        result = TruthTable(new_ins, new_outs)

        vprint("RESULT:", result, v=DEBUG)
        return result

    def __matmul__(self, input_truths):
        return self.combine(input_truths)

class Node(Tree):
    NO_MATCH = None 
    counter = 0
    
    counter_map = {}
    enum_tts_map = {}

    def new_var(ptr):
        var =  f"{Node.counter}w"
        Node.counter_map[var] = ptr
        Node.counter += 1
        return var
    
    def find_var(var):
        if(var in Node.counter_map):
            return Node.counter_map[var]
        return None

    def __init__(self, data, children, base_tt=0b10, base_cost=1, var=None):
        self.base_tt = base_tt
        self.var = var if var is not None else Node.new_var(self)
        self.base_cost = base_cost
        super().__init__(data, children)
        self.cost = base_cost
        self.input_vars = []
        self.terms = 0
        for i in range(len(self.children)):
            c = self.children[i]
            assert isinstance(c,(Node,Token,str))
            if isinstance(c, Node):
                self.input_vars.append(c.var)
                self.cost += c.cost
            elif isinstance(c, Token):
                c = c.value
            if isinstance(c, str):
                self.terms += 1
                self.input_vars.append(c)
                n = Node.find_var(c)
                if(n is not None):
                    self.cost += n.cost
        self.is_leaf = self.terms == len(self.children)
        self.tt = TruthTable(self.input_vars, self.base_tt)
        self.optimal_match = None
        self.cuts = []

    def __repr__(self):
        str_children = []
        for c in self.children:
            str_children.append(str(c))
        joined = ",".join(str_children)
        return f"{self.data}|{self.var}({joined})"
    
    def pretty(self):
        return self.pretty_print(PrettyStream()).cache

    def pretty_print(self, p:PrettyStream):
        p << [f'{self.data}|{self.var}']
        with p:
            for c in self.children:
                if isinstance(c, Node):
                    c.pretty_print(p)
                else:
                    p << c
        return p

    def enum_tts(self, crush = False):
        if(self in Node.enum_tts_map):
            vprint("Found Memoized enum_tts of", self, v=ALL)
            return Node.enum_tts_map[self]

        if(crush):
            children_tts = []
            for c in self.children:
                if isinstance(c, Node):
                    children_tts.append(c.enum_tts())
                else:
                    children_tts.append(c)
            return [self.tt @ children_tts]

        tts = [self.tt]
        tt_set = set()

        if self.is_leaf:
            return tts
        else:
            children_tts = []
            for c in self.children:
                if isinstance(c, Node):
                    children_tts.append(c.enum_tts())
                else:
                    children_tts.append([c])

            for perm in product(*children_tts):
                try:
                    stxct = (self.tt @ perm).prune()
                    if(len(stxct.ins) < 5 and stxct.id not in tt_set):
                        tt_set.add(stxct.id)
                        tts.append(stxct)
                except ValueError:
                    continue
                
        Node.enum_tts_map[self] = list(tts)
        return list(tts)
                
#          NAME     TT              NUM_IN  COST
INV     = ("INV",   0b01,           1,      1   )
NAND    = ("NAND",  0b0111,         2,      2   )
NOR     = ("NOR",   0b0001,         2,      2   )
XOR     = ("XOR",   0b0110,         2,      1   )
AND3    = ("AND3",  0b10000000,     3,      3   )
XOR3    = ("XOR3",  0b10010110,     3,      2   )
OR3     = ("OR3",   0b11111110,     3,      3   )
AND     = ("AND",   0b1000,         2,      2.5 )

CELLS = [INV, NAND, NOR, XOR, AND]

def m_inv(node):
    return Node(INV[0], [node], INV[1], INV[3])

def m_nand(node1, node2):
    return Node(NAND[0], [node1, node2], NAND[1], NAND[3])

def m_nor(node1, node2):
    return Node(NOR[0], [node1, node2], NOR[1], NOR[3])

def m_xor(node1, node2):
    return Node(XOR[0], [node1, node2], XOR[1], XOR[3])

    

    
