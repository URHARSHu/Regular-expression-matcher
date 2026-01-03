from collections import defaultdict

EPS = None   # epsilon


# -------------------------------
# NFA structure
# -------------------------------
class NFA:
    def __init__(self, start, accepts, transitions):
        self.start = start
        self.accepts = accepts          # set
        self.transitions = transitions  # dict[(state, symbol)] -> [states]


# -------------------------------
# Regex → Postfix
# -------------------------------
def re2post(regex):
    precedence = {'|': 1, '.': 2, '?': 3, '*': 3, '+': 3}
    output = []
    stack = []

    def add_concat(r):
        res = []
        for i, c in enumerate(r):
            res.append(c)
            if c in "(|":
                continue
            if i + 1 < len(r):
                d = r[i + 1]
                if d not in "|)*+?":
                    res.append('.')
        return res

    regex = add_concat(regex)

    for c in regex:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif c in precedence:
            while (stack and stack[-1] in precedence and
                   precedence[stack[-1]] >= precedence[c]):
                output.append(stack.pop())
            stack.append(c)
        else:
            output.append(c)

    while stack:
        output.append(stack.pop())

    return ''.join(output)


# -------------------------------
# Thompson construction
# -------------------------------
class Frag:
    def __init__(self, start, out):
        self.start = start
        self.out = out  # list of dangling (state, symbol)


state_id = 0
def new_state():
    global state_id
    s = state_id
    state_id += 1
    return s


def post2nfa(postfix):
    global state_id
    state_id = 0

    transitions = defaultdict(list)
    stack = []

    def patch(out_list, target):
        for (s, sym) in out_list:
            transitions[(s, sym)].append(target)

    for c in postfix:
        if c not in ".|*+?":
            s = new_state()
            e = new_state()
            transitions[(s, c)].append(e)
            stack.append(Frag(s, [(e, EPS)]))

        elif c == '.':
            e2 = stack.pop()
            e1 = stack.pop()
            patch(e1.out, e2.start)
            stack.append(Frag(e1.start, e2.out))

        elif c == '|':
            e2 = stack.pop()
            e1 = stack.pop()
            s = new_state()
            transitions[(s, EPS)] += [e1.start, e2.start]
            stack.append(Frag(s, e1.out + e2.out))

        elif c == '?':
            e = stack.pop()
            s = new_state()
            transitions[(s, EPS)] += [e.start]
            stack.append(Frag(s, e.out + [(s, EPS)]))

        elif c == '*':
            e = stack.pop()
            s = new_state()
            transitions[(s, EPS)] += [e.start]
            patch(e.out, s)
            stack.append(Frag(s, [(s, EPS)]))

        elif c == '+':
            e = stack.pop()
            s = new_state()
            patch(e.out, s)
            transitions[(s, EPS)] += [e.start]
            stack.append(Frag(e.start, [(s, EPS)]))

    e = stack.pop()
    accept = new_state()
    patch(e.out, accept)

    return NFA(e.start, {accept}, transitions)


# -------------------------------
# NFA simulation (Thompson)
# -------------------------------
def epsilon_closure(nfa, states):
    stack = list(states)
    closure = set(states)

    while stack:
        s = stack.pop()
        for nxt in nfa.transitions.get((s, EPS), []):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure


def move(nfa, states, char):
    res = set()
    for s in states:
        for nxt in nfa.transitions.get((s, char), []):
            res.add(nxt)
    return res


def match(nfa, text):
    current = epsilon_closure(nfa, {nfa.start})

    for ch in text:
        current = epsilon_closure(nfa, move(nfa, current, ch))
        if not current:
            return False

    return any(s in nfa.accepts for s in current)


# -------------------------------
# Public API
# -------------------------------
def regex_match(regex, text):
    postfix = re2post(regex)
    nfa = post2nfa(postfix)
    return match(nfa, text)


# -------------------------------
# Tests
# -------------------------------
if __name__ == "__main__":
    tests = [
        ("a*b", "b", True),
        ("a*b", "aaab", True),
        ("a*b", "aaa", False),
        ("ab|cd", "ab", True),
        ("ab|cd", "cd", True),
        ("ab|cd", "ad", False),
        ("a+", "aaa", True),
        ("a?", "", True),
        ("(ab)*c", "abababc", True),
    ]

    for r, s, ans in tests:
        print(r, s, regex_match(r, s), "✓" if regex_match(r, s) == ans else "✗")
