import contextlib

class PrettyStream():
    def __init__(self):
        self.depth = 0
        self.notabdepth = 0
        self.sep = '  '
        self.cache = ""
        self.prefix = ""

    def clear(self):
        self.cache = ""

    def make_indent(self):
        return self.depth*self.sep

    def put_line(self, *others):
        self.cache += self.make_indent() + self.prefix 
        for other in others:
            if(isinstance(other, tuple) or isinstance(other, list)):
                for item in other:
                    self.append_token(item)
            else:
                self.append_token(other)
        self.prefix = ""
        self.cache += '\n'
        return self
    
    def __lshift__(self, other):
        return self.put_line(other)
        
    
    def __or__(self, other):
        self.cache += self.get_sep() + str(other)
        return self
    
    def get_sep(self):
        if (self.cache == '' or self.cache[-1] == '\n'):
            return ''
        return ' '
    
    def append(self, *others):
        for other in others:
            if(isinstance(other, tuple) or isinstance(other, list)):
                for item in other:
                    self.append_token(item)
            else:
                self.append_token(other)
        return self
    
    def append_token(self, token):
        s = str(token)
        if (s != ''):
            self.cache += self.get_sep() + s
        return self

    def put(self, other):
        self.cache += str(other)
        return self

    def __rshift__(self, other):
        self.prefix += str(other)
        return self

    def set_indent(self, depth):
        self.depth = depth
        return self

    def __pos__(self):
        self.depth += 1
        return self
    
    def __neg__(self):
        self.depth -= 1
        return self
    
    def __xor__(self, other):
        self.depth += other
        return self
    
    def __enter__(self):
        self.depth += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.depth -= 1
    
    def __repr__(self):
        return self.cache