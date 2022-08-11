import TagHandler
import re

# Implementation of shuning yard algorithm
class QueryEvaluator :
    def __init__(self, tagsdbfile) :
        self.tagsdb = tagsdbfile
        self.th = TagHandler.TagHandler(self.tagsdb)
        self.operators = []
        self.values = []
        self.fullresources = []

    def tokenize(self, querystr):
        tokens = re.findall("[()&|~]|[a-z0-9]+", querystr)
        return tokens

    def peek(self):
        return self.operators[-1] if self.operators else None

    def apply_operator(self) :
        operator = self.operators.pop()
        if operator == "&" :
            v1 = self.values.pop()
            v2 = self.values.pop()
            self.values.append(v1.intersection(v2))
        elif operator == "|" :
            v1 = self.values.pop()
            v2 = self.values.pop()
            self.values.append(v1.union(v2))
        elif operator == "~" :
            v1 = self.values.pop()
            if len(self.fullresources) == 0 :
                self.fullresources = set(self.th.get_resource_ids())
            self.values.append(self.fullresources.difference(v1))
        else :
            print("invalid operator")
            exit(1)

    def greater_precedence(self, op1, op2):
        precedences = {"|": 0, "~": 0, "&": 1}
        return precedences[op1] > precedences[op2]

    def evaluate_query(self, expression):
        tokens = self.tokenize(expression)
        self.values = []
        self.operators = []
        for token in tokens:
            if token == "(":
                self.operators.append(token)
            elif token == ")":
                top = self.peek()
                while top is not None and top != "(":
                    self.apply_operator()
                    top = self.peek()
                self.operators.pop()  # Discard the '('
            elif token[0] not in ['|','&','~']:
                tag_closure = self.th.get_tag_closure([token])
                tag_closure_ids = list(map(self.th.get_tag_id, tag_closure))
                r = set(self.th.get_resources_by_tag_id(tag_closure_ids))                
                self.values.append(r)
            else:
                # Operator
                top = self.peek()
                while top is not None and top != "(" and self.greater_precedence(top, token):
                    self.apply_operator()
                    top = self.peek()
                self.operators.append(token)
        while self.peek() is not None:
            self.apply_operator()
        res = list(map(self.th.get_resource_url, self.values[0]))
        return res
