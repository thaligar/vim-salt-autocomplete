#!/usr/bin/env python3

import os
import ast
import astunparse

path="/home/sebastian/source/salt-stack/salt/states/"
extension=".py"

def python_name(node):
    return node.id

def python_name_constant(node):
    return node.value

def python_str(node):
    return '"' + node.s + '"'

def python_num(node):
    return node.n

def python_tuple(node):
    return astunparse.unparse(node)

def python_attrib(node):
    return astunparse.unparse(node)

def python_unaryop(node):
    return 'UNARY: ' + astunparse.unparse(node)

def is_valid_string(s):
    return s not in (None, '') and s.strip() and '..' not in s

def remove_bad_lines(strings):
    return [s for s in strings if is_valid_string(s)]

def get_description(node):
    probable_doc_string = ast.get_docstring(node)

    if probable_doc_string is not None:
        lines = ast.get_docstring(node).splitlines()
        lines = remove_bad_lines(lines)
        return lines[0]
    else:
        return ''


states = {}

dispatcher = {
        ast.Name: python_name,
        ast.NameConstant: python_name_constant,
        ast.Num: python_num,
        ast.Str: python_str,
        ast.Tuple: python_tuple,
        ast.Attribute: python_attrib,
        ast.UnaryOp: python_unaryop,
        }

for filename in [f for f in os.listdir(path) if f.endswith(extension)]:
    with open(path + filename, 'r') as item:
        source = item.read()
    print(filename)
    states['name'] = filename[:-3]
    states['methods'] = []
    tree = ast.parse(source)
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.FunctionDef):
            if not stmt.name.startswith("_"):
                fn = {}
                print('  ' + stmt.name)
                fn['name'] = stmt.name
                fn['args'] = []
                fn['docs'] = get_description(stmt)
                print('  * ' + fn['docs'])

                args = stmt.args.args
                defs = stmt.args.defaults
            
                print(len(args))
                print(len(defs))
                print(len(args)-len(defs))
                difference = len(args) - len(defs)

                for i, a in enumerate(stmt.args.args):
                    
                    defix = i - difference

                    if defix >= 0:
                        node = defs[defix]
                        translator = dispatcher[type(node)]
                        value_as_string = str(translator(node))
                        fn['args'].append(a.arg + ': ' + value_as_string)
                        print('    ' + a.arg + ': ' + value_as_string)
                    else:
                        fn['args'].append(a.arg)
                        print('    ' + a.arg)

                states['methods'].append(fn)





