import contextlib
from textwrap import indent

ERROR = -1
QUIET = 0
FAILED = 1
PASSED = 2
INFO = 3
VERBOSE = 4
DEBUG = 5
ALL = 100

verbose_level = QUIET

def set_verbose_level(v):
    global verbose_level
    verbose_level = v

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'

print_colors = {
    ERROR:      RED,
    QUIET:      WHITE,
    FAILED:     RED,
    PASSED:     GREEN,
    INFO:       CYAN,
    VERBOSE:    BLUE,
    DEBUG:      YELLOW,
    ALL:        WHITE
}

print_header = {
    ERROR:      f'[ ERROR] ' ,
    QUIET:      "",
    FAILED:     f'[FAILED] ',
    PASSED:     f'[PASSED] ',
    INFO:       f'[  INFO] ',
    VERBOSE:    f'[  VERB] ',
    DEBUG:      f'[ DEBUG] ',
    ALL:        ""
}

def color(text, color):
    return f'{color}{text}{RESET}'

def vprint(*args, v=INFO, h=True, **kwargs):
    if verbose_level >= v:
        result = ""
        if h:
            result += color(print_header[v],print_colors[v])
        sep = kwargs.get("sep", " ")
        text = sep.join(map(str, args))
        lines = text.splitlines() or [text]
        content = ""
        if len(lines) > 1:
            content += "\n  ┌ "+"\n  │ ".join(lines[0:-1]) + "\n  └ " + lines[-1]
        else:
            content += lines[0]
        result += color(content,print_colors[v])
        if h:
            result += RESET
        print(result, **kwargs)

def vprint_pretty(obj, v=INFO, h=True):
    if hasattr(obj, "pretty"):
        vprint("Pretty Printing ... " , v=v, h=h, end="")
        vprint(obj.pretty(PrettyStream()), v=v, h=False)
        return
    vprint(obj, v=v, h=h)

def err_msg(*args, **kwargs):
    vprint(*args, v=ERROR, **kwargs)

def vprint_title(title, v=INFO):
    l_pad_len = (120 - len(title))//2
    r_pad_len = 120 - len(title) - l_pad_len
    vprint(f"{'='*l_pad_len} {title} {'='*r_pad_len}\n",v=v)

class PrettyStream():
    def __init__(self):
        self.depth = 0
        self.notabdepth = 0
        self.sep = '  '
        self.cache = ""
        self.prefix = ""
        self.empty_line = True
        self.trail_sep = '- '

    def clear(self):
        self.cache = ""

    def make_indent(self):
        if self.trail_sep is not None and self.depth > 0:
            return self.sep * (self.depth - 1) + self.trail_sep
        return self.depth*self.sep

    def put_line(self, *others):
        if(len(others) == 0 or others == ""):
            return self
        self.cache += self.make_indent() + self.prefix 
        if(self.prefix != ""):
            self.empty_line = False
        else:
            self.empty_line = True
        for other in others:
            if(isinstance(other, tuple) or isinstance(other, list)):
                for item in other:
                    self.append_token(item)
            else:
                self.append_token(other)
        self.prefix = ""
        self.cache += '\n'
        self.empty_line = True
        return self
    
    def __lshift__(self, other):
        return self.put_line(other)
    
    def __or__(self, other):
        self.cache += self.get_sep() + str(other)
        return self
    
    def get_sep(self):
        if (self.empty_line):
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
            self.empty_line = False
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