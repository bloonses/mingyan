import math
import random
import time
import json
import os
from ast_nodes import *


class MingyanObject:
    def __init__(self, class_name, properties=None):
        self.class_name = class_name
        self.properties = properties or {}
        self.methods = {}

    def __repr__(self):
        return f'<{self.class_name} {self.properties}>'

    def get(self, name):
        if name in self.methods:
            return self.methods[name]
        if name in self.properties:
            return self.properties[name]
        return None

    def set(self, name, value):
        self.properties[name] = value


class MingyanClass:
    def __init__(self, name, parent=None, methods=None, init_body=None, init_params=None):
        self.name = name
        self.parent = parent
        self.methods = methods or {}
        self.init_body = init_body
        self.init_params = init_params or []

    def __repr__(self):
        return f'<类 {self.name}>'

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.parent:
            return self.parent.find_method(name)
        return None


class MingyanFunc:
    def __init__(self, name, params, body, closure, defaults=None):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
        self.defaults = defaults or []

    def __repr__(self):
        return f'<函数 {self.name}({", ".join(self.params)})>'

    def bind(self, obj):
        bound = MingyanFunc(self.name, self.params, self.body, self.closure, self.defaults)
        bound._bound_obj = obj
        return bound


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.consts = set()
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f'未定义的变量: {name}')

    def set(self, name, value):
        if name in self.consts:
            raise RuntimeError(f'不能修改常量: {name}')
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            try:
                self.parent.set(name, value)
                return
            except RuntimeError:
                pass
        self.vars[name] = value

    def define(self, name, value, is_const=False):
        if is_const:
            self.consts.add(name)
        self.vars[name] = value

    def has(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value=None):
        self.value = value


class MingyanError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.classes = {}
        self._setup_builtins()

    def _setup_builtins(self):
        builtins = {
            '打印': self._builtin_print,
            '长度': self._builtin_len,
            '类型': self._builtin_type,
            '转整数': self._builtin_int,
            '转浮点': self._builtin_float,
            '转字符串': self._builtin_str,
            '输入': self._builtin_input,
            '范围': self._builtin_range,
            '绝对值': self._builtin_abs,
            '最大值': self._builtin_max,
            '最小值': self._builtin_min,
            '排序': self._builtin_sorted,
            '反转': self._builtin_reversed,
            '追加': self._builtin_append,
            '弹出': self._builtin_pop,
            '合并': self._builtin_join,
            '分割': self._builtin_split,
            '替换': self._builtin_replace,
            '包含': self._builtin_contains,
            '删除': self._builtin_remove,
            '插入': self._builtin_insert,
            '取键': self._builtin_keys,
            '取值': self._builtin_values,
            '有键': self._builtin_has_key,
            '转JSON': self._builtin_to_json,
            '从JSON': self._builtin_from_json,
            '随机整数': self._builtin_randint,
            '随机浮点': self._builtin_random,
            '当前时间': self._builtin_time,
            '等待': self._builtin_sleep,
            '取整': self._builtin_floor,
            '上取整': self._builtin_ceil,
            '四舍五入': self._builtin_round,
            '平方根': self._builtin_sqrt,
            '幂': self._builtin_pow,
            '正弦': self._builtin_sin,
            '余弦': self._builtin_cos,
            '正切': self._builtin_tan,
            '对数': self._builtin_log,
            '圆周率': math.pi,
            '自然常数': math.e,
            '文件读取': self._builtin_file_read,
            '文件写入': self._builtin_file_write,
            '文件存在': self._builtin_file_exists,
            '执行系统': self._builtin_system,
            '映射': self._builtin_map,
            '过滤': self._builtin_filter,
            '归约': self._builtin_reduce,
            '枚举': self._builtin_enumerate,
            '拉链': self._builtin_zip,
            '字符': self._builtin_chr,
            '编码': self._builtin_ord,
            '是数字': self._builtin_is_number,
            '是字符串': self._builtin_is_string,
            '是列表': self._builtin_is_list,
            '是字典': self._builtin_is_dict,
            '是函数': self._builtin_is_func,
            '是空': self._builtin_is_null,
        }
        for name, val in builtins.items():
            self.global_env.define(name, val)

    def _builtin_print(self, *args, **kwargs):
        parts = []
        for arg in args:
            parts.append(self._format_value(arg))
        output = ' '.join(parts)
        print(output)
        return None

    def _format_value(self, val):
        if val is None:
            return '空'
        if isinstance(val, bool):
            return '真' if val else '假'
        if isinstance(val, float):
            if val == int(val):
                return str(int(val))
            return str(val)
        if isinstance(val, list):
            return '[' + ', '.join(self._format_value(v) for v in val) + ']'
        if isinstance(val, dict):
            pairs = []
            for k, v in val.items():
                pairs.append(f'{self._format_value(k)}: {self._format_value(v)}')
            return '{' + ', '.join(pairs) + '}'
        if isinstance(val, MingyanObject):
            return f'<{val.class_name}>'
        if isinstance(val, MingyanClass):
            return f'<类 {val.name}>'
        if isinstance(val, MingyanFunc):
            return f'<函数 {val.name}>'
        if callable(val):
            return f'<内置函数>'
        return str(val)

    def _builtin_len(self, val):
        return len(val)

    def _builtin_type(self, val):
        if val is None:
            return '空'
        if isinstance(val, bool):
            return '布尔'
        if isinstance(val, int):
            return '整数'
        if isinstance(val, float):
            return '浮点'
        if isinstance(val, str):
            return '字符串'
        if isinstance(val, list):
            return '列表'
        if isinstance(val, dict):
            return '字典'
        if isinstance(val, MingyanObject):
            return val.class_name
        if isinstance(val, (MingyanFunc,)) or callable(val):
            return '函数'
        return '未知'

    def _builtin_int(self, val):
        return int(val)

    def _builtin_float(self, val):
        return float(val)

    def _builtin_str(self, val):
        return self._format_value(val)

    def _builtin_input(self, prompt=''):
        if prompt:
            print(self._format_value(prompt), end='')
        return input()

    def _builtin_range(self, *args):
        return list(range(*args))

    def _builtin_abs(self, val):
        return abs(val)

    def _builtin_max(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            return max(args[0])
        return max(args)

    def _builtin_min(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            return min(args[0])
        return min(args)

    def _builtin_sorted(self, lst, **kwargs):
        return sorted(lst)

    def _builtin_reversed(self, lst):
        return list(reversed(lst))

    def _builtin_append(self, lst, val):
        lst.append(val)
        return lst

    def _builtin_pop(self, lst, index=-1):
        return lst.pop(index)

    def _builtin_join(self, sep, lst):
        return sep.join(self._format_value(v) for v in lst)

    def _builtin_split(self, s, sep=None):
        if sep is None:
            return s.split()
        return s.split(sep)

    def _builtin_replace(self, s, old, new):
        return s.replace(old, new)

    def _builtin_contains(self, container, item):
        return item in container

    def _builtin_remove(self, lst, val):
        lst.remove(val)
        return lst

    def _builtin_insert(self, lst, index, val):
        lst.insert(index, val)
        return lst

    def _builtin_keys(self, d):
        return list(d.keys())

    def _builtin_values(self, d):
        return list(d.values())

    def _builtin_has_key(self, d, key):
        return key in d

    def _builtin_to_json(self, val):
        return json.dumps(val, ensure_ascii=False, default=str)

    def _builtin_from_json(self, s):
        return json.loads(s)

    def _builtin_randint(self, a, b):
        return random.randint(a, b)

    def _builtin_random(self):
        return random.random()

    def _builtin_time(self):
        return time.time()

    def _builtin_sleep(self, seconds):
        time.sleep(seconds)
        return None

    def _builtin_floor(self, val):
        return math.floor(val)

    def _builtin_ceil(self, val):
        return math.ceil(val)

    def _builtin_round(self, val, n=0):
        return round(val, n)

    def _builtin_sqrt(self, val):
        return math.sqrt(val)

    def _builtin_pow(self, base, exp):
        return math.pow(base, exp)

    def _builtin_sin(self, val):
        return math.sin(val)

    def _builtin_cos(self, val):
        return math.cos(val)

    def _builtin_tan(self, val):
        return math.tan(val)

    def _builtin_log(self, val, base=math.e):
        return math.log(val, base)

    def _builtin_file_read(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _builtin_file_write(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self._format_value(content))
        return None

    def _builtin_file_exists(self, path):
        return os.path.exists(path)

    def _builtin_system(self, cmd):
        return os.system(cmd)

    def _builtin_map(self, func, lst):
        result = []
        for item in lst:
            result.append(self._call_function(func, [item]))
        return result

    def _builtin_filter(self, func, lst):
        result = []
        for item in lst:
            if self._is_truthy(self._call_function(func, [item])):
                result.append(item)
        return result

    def _builtin_reduce(self, func, lst, initial=None):
        it = iter(lst)
        if initial is None:
            acc = next(it)
        else:
            acc = initial
        for item in it:
            acc = self._call_function(func, [acc, item])
        return acc

    def _builtin_enumerate(self, lst, start=0):
        return list(enumerate(lst, start))

    def _builtin_zip(self, *lists):
        return list(zip(*lists))

    def _builtin_chr(self, code):
        return chr(code)

    def _builtin_ord(self, char):
        return ord(char)

    def _builtin_is_number(self, val):
        return isinstance(val, (int, float)) and not isinstance(val, bool)

    def _builtin_is_string(self, val):
        return isinstance(val, str)

    def _builtin_is_list(self, val):
        return isinstance(val, list)

    def _builtin_is_dict(self, val):
        return isinstance(val, dict)

    def _builtin_is_func(self, val):
        return isinstance(val, MingyanFunc) or callable(val)

    def _builtin_is_null(self, val):
        return val is None

    def _call_function(self, func, args):
        if isinstance(func, MingyanFunc):
            env = Environment(func.closure)
            bound_obj = getattr(func, '_bound_obj', None)
            if bound_obj is not None:
                env.define('这个', bound_obj)
            for i, param in enumerate(func.params):
                if i < len(args):
                    env.define(param, args[i])
                elif i < len(func.defaults) and func.defaults[i] is not None:
                    env.define(param, self.evaluate(func.defaults[i], env))
                else:
                    raise RuntimeError(f'函数 {func.name} 缺少参数: {param}')
            try:
                result = None
                for stmt in func.body:
                    result = self.execute(stmt, env)
                return result
            except ReturnSignal as r:
                return r.value
        elif callable(func):
            return func(*args)
        else:
            raise RuntimeError(f'不可调用的对象: {func}')

    def _is_truthy(self, val):
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return len(val) > 0
        if isinstance(val, list):
            return len(val) > 0
        if isinstance(val, dict):
            return len(val) > 0
        return True

    def _values_equal(self, a, b):
        return a == b

    def run(self, program):
        result = None
        for stmt in program.statements:
            result = self.execute(stmt, self.global_env)
        return result

    def execute(self, node, env):
        method_name = f'_exec_{type(node).__name__}'
        method = getattr(self, method_name, None)
        if method:
            return method(node, env)
        raise RuntimeError(f'未知的AST节点: {type(node).__name__}')

    def _exec_Program(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.execute(stmt, env)
        return result

    def _exec_NumberLiteral(self, node, env):
        return node.value

    def _exec_StringLiteral(self, node, env):
        return node.value

    def _exec_BooleanLiteral(self, node, env):
        return node.value

    def _exec_NullLiteral(self, node, env):
        return None

    def _exec_Identifier(self, node, env):
        try:
            return env.get(node.name)
        except RuntimeError:
            if node.name in self.classes:
                return self.classes[node.name]
            raise

    def _exec_ListLiteral(self, node, env):
        return [self.evaluate(elem, env) for elem in node.elements]

    def _exec_DictLiteral(self, node, env):
        result = {}
        for key_node, val_node in node.pairs:
            key = self.evaluate(key_node, env)
            val = self.evaluate(val_node, env)
            result[key] = val
        return result

    def _exec_BinaryOp(self, node, env):
        if node.op in ('且', '或'):
            left = self.evaluate(node.left, env)
            if node.op == '且':
                if not self._is_truthy(left):
                    return left
                return self.evaluate(node.right, env)
            else:
                if self._is_truthy(left):
                    return left
                return self.evaluate(node.right, env)

        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)

        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '%': lambda a, b: a % b,
            '**': lambda a, b: a ** b,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
        }
        if node.op in ops:
            try:
                return ops[node.op](left, right)
            except TypeError:
                raise RuntimeError(f'类型错误: 无法对 {self._builtin_type(left)} 和 {self._builtin_type(right)} 执行 {node.op}')
        raise RuntimeError(f'未知的运算符: {node.op}')

    def _exec_UnaryOp(self, node, env):
        operand = self.evaluate(node.operand, env)
        if node.op == '-':
            return -operand
        if node.op == '非':
            return not self._is_truthy(operand)
        if node.op == '!':
            return not self._is_truthy(operand)
        raise RuntimeError(f'未知的一元运算符: {node.op}')

    def _exec_Assignment(self, node, env):
        value = self.evaluate(node.value, env)
        env.set(node.name, value)
        return value

    def _exec_CompoundAssignment(self, node, env):
        current = env.get(node.name)
        value = self.evaluate(node.value, env)
        ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b,
               '*': lambda a, b: a * b, '/': lambda a, b: a / b}
        new_val = ops[node.op](current, value)
        env.set(node.name, new_val)
        return new_val

    def _exec_VarDeclaration(self, node, env):
        value = self.evaluate(node.value, env)
        env.define(node.name, value, node.is_const)
        return value

    def _exec_IfStatement(self, node, env):
        if self._is_truthy(self.evaluate(node.condition, env)):
            return self._exec_block(node.body, env)
        for cond, body in node.elif_clauses:
            if self._is_truthy(self.evaluate(cond, env)):
                return self._exec_block(body, env)
        if node.else_body:
            return self._exec_block(node.else_body, env)
        return None

    def _exec_WhileStatement(self, node, env):
        result = None
        while self._is_truthy(self.evaluate(node.condition, env)):
            try:
                result = self._exec_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return result

    def _exec_ForStatement(self, node, env):
        iterable = self.evaluate(node.iterable, env)
        result = None
        for item in iterable:
            env.define(node.var_name, item)
            try:
                result = self._exec_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return result

    def _exec_FuncDeclaration(self, node, env):
        func = MingyanFunc(node.name, node.params, node.body, env, node.defaults)
        env.define(node.name, func)
        return func

    def _exec_ReturnStatement(self, node, env):
        value = None
        if node.value:
            value = self.evaluate(node.value, env)
        raise ReturnSignal(value)

    def _exec_BreakStatement(self, node, env):
        raise BreakSignal()

    def _exec_ContinueStatement(self, node, env):
        raise ContinueSignal()

    def _exec_FuncCall(self, node, env):
        callee = self.evaluate(node.callee, env)
        args = [self.evaluate(arg, env) for arg in node.args]
        return self._call_function(callee, args)

    def _exec_MethodCall(self, node, env):
        obj = self.evaluate(node.obj, env)
        args = [self.evaluate(arg, env) for arg in node.args]

        if isinstance(obj, list):
            list_methods = {
                '追加': lambda: obj.append(args[0]) or obj,
                '弹出': lambda: obj.pop(int(args[0])) if args else obj.pop(),
                '插入': lambda: obj.insert(int(args[0]), args[1]) or obj,
                '删除': lambda: obj.remove(args[0]) or obj,
                '排序': lambda: sorted(obj),
                '反转': lambda: list(reversed(obj)),
                '包含': lambda: args[0] in obj,
                '长度': lambda: len(obj),
                '索引': lambda: obj.index(args[0]),
                '计数': lambda: obj.count(args[0]),
                '合并': lambda: obj + args[0],
                '切片': lambda: obj[int(args[0]):int(args[1])] if len(args) >= 2 else obj[int(args[0]):],
                '映射': lambda: [self._call_function(args[0], [x]) for x in obj],
                '过滤': lambda: [x for x in obj if self._is_truthy(self._call_function(args[0], [x]))],
                '归约': lambda: self._builtin_reduce(args[0], obj, args[1] if len(args) > 1 else None),
                '连接': lambda: args[0].join(self._format_value(x) for x in obj),
                '去重': lambda: list(dict.fromkeys(obj)),
                '首个': lambda: obj[0] if obj else None,
                '末个': lambda: obj[-1] if obj else None,
                '取范围': lambda: obj[int(args[0]):int(args[1])] if len(args) >= 2 else obj[int(args[0]):],
            }
            if node.method in list_methods:
                return list_methods[node.method]()
            raise RuntimeError(f'列表没有方法: {node.method}')

        if isinstance(obj, str):
            str_methods = {
                '长度': lambda: len(obj),
                '包含': lambda: args[0] in obj,
                '开头是': lambda: obj.startswith(args[0]),
                '结尾是': lambda: obj.endswith(args[0]),
                '分割': lambda: obj.split(args[0]) if args else obj.split(),
                '替换': lambda: obj.replace(args[0], args[1]),
                '去空白': lambda: obj.strip(),
                '大写': lambda: obj.upper(),
                '小写': lambda: obj.lower(),
                '居中': lambda: obj.center(int(args[0]), args[1] if len(args) > 1 else ' '),
                '左对齐': lambda: obj.ljust(int(args[0])),
                '右对齐': lambda: obj.rjust(int(args[0])),
                '计数': lambda: obj.count(args[0]),
                '查找': lambda: obj.find(args[0]),
                '重复': lambda: obj * int(args[0]),
                '是数字': lambda: obj.isdigit(),
                '是字母': lambda: obj.isalpha(),
                '子串': lambda: obj[int(args[0]):int(args[1])] if len(args) >= 2 else obj[int(args[0]):],
                '字符列表': lambda: list(obj),
                '反转': lambda: obj[::-1],
            }
            if node.method in str_methods:
                return str_methods[node.method]()
            raise RuntimeError(f'字符串没有方法: {node.method}')

        if isinstance(obj, dict):
            dict_methods = {
                '键列表': lambda: list(obj.keys()),
                '值列表': lambda: list(obj.values()),
                '项列表': lambda: list(obj.items()),
                '有键': lambda: args[0] in obj,
                '删除': lambda: obj.pop(args[0], args[1] if len(args) > 1 else None),
                '长度': lambda: len(obj),
                '合并': lambda: {**obj, **args[0]},
                '取值': lambda: obj.get(args[0], args[1] if len(args) > 1 else None),
            }
            if node.method in dict_methods:
                return dict_methods[node.method]()
            raise RuntimeError(f'字典没有方法: {node.method}')

        if isinstance(obj, MingyanObject):
            method = obj.get(node.method)
            if method is not None:
                if isinstance(method, MingyanFunc):
                    bound = method.bind(obj)
                    return self._call_function(bound, args)
                elif callable(method):
                    return method(*args)
            cls = self.classes.get(obj.class_name)
            if cls:
                method = cls.find_method(node.method)
                if method is not None:
                    bound = method.bind(obj)
                    return self._call_function(bound, args)
            raise RuntimeError(f'{obj.class_name} 没有方法: {node.method}')

        if isinstance(obj, MingyanClass):
            if node.method == '新建':
                instance = MingyanObject(obj.name)
                init_method = obj.find_method('初始化')
                if init_method:
                    bound = init_method.bind(instance)
                    self._call_function(bound, args)
                else:
                    for i, param in enumerate(obj.init_params or []):
                        if i < len(args):
                            instance.properties[param] = args[i]
                return instance
            raise RuntimeError(f'类 {obj.name} 没有方法: {node.method}')

        raise RuntimeError(f'对象没有方法: {node.method}')

    def _exec_MemberAccess(self, node, env):
        obj = self.evaluate(node.obj, env)

        if isinstance(obj, MingyanObject):
            if node.member in obj.properties:
                return obj.properties[node.member]
            if node.member in obj.methods:
                return obj.methods[node.member]
            cls = self.classes.get(obj.class_name)
            if cls:
                method = cls.find_method(node.member)
                if method is not None:
                    return method.bind(obj)
            raise RuntimeError(f'{obj.class_name} 没有属性: {node.member}')

        if isinstance(obj, dict):
            if node.member in obj:
                return obj[node.member]
            dict_accessors = {
                '键列表': list(obj.keys()),
                '值列表': list(obj.values()),
                '长度': len(obj),
            }
            if node.member in dict_accessors:
                return dict_accessors[node.member]
            raise RuntimeError(f'字典没有键: {node.member}')

        if isinstance(obj, list):
            list_props = {
                '长度': len(obj),
                '首个': obj[0] if obj else None,
                '末个': obj[-1] if obj else None,
            }
            if node.member in list_props:
                return list_props[node.member]
            raise RuntimeError(f'列表没有属性: {node.member}')

        if isinstance(obj, str):
            str_props = {
                '长度': len(obj),
            }
            if node.member in str_props:
                return str_props[node.member]
            raise RuntimeError(f'字符串没有属性: {node.member}')

        raise RuntimeError(f'无法访问属性: {node.member}')

    def _exec_IndexAccess(self, node, env):
        obj = self.evaluate(node.obj, env)
        index = self.evaluate(node.index, env)
        if isinstance(obj, (list, str)):
            return obj[int(index)]
        if isinstance(obj, dict):
            return obj[index]
        raise RuntimeError(f'不可索引的类型: {type(obj).__name__}')

    def _exec_IndexAssignment(self, node, env):
        obj = self.evaluate(node.obj, env)
        index = self.evaluate(node.index, env)
        value = self.evaluate(node.value, env)

        if isinstance(obj, list):
            obj[int(index)] = value
            return value
        if isinstance(obj, dict):
            obj[index] = value
            return value
        raise RuntimeError(f'不可索引赋值的类型: {type(obj).__name__}')

    def _exec_MemberAssignment(self, node, env):
        obj = self.evaluate(node.obj, env)
        value = self.evaluate(node.value, env)

        if isinstance(obj, MingyanObject):
            obj.properties[node.member] = value
            return value
        if isinstance(obj, dict):
            obj[node.member] = value
            return value
        raise RuntimeError(f'无法设置属性: {node.member}')

    def _exec_ClassDeclaration(self, node, env):
        parent = None
        if node.parent:
            parent = self.classes.get(node.parent)
            if parent is None:
                raise RuntimeError(f'未定义的父类: {node.parent}')

        methods = {}
        init_body = None
        init_params = []

        func_env = Environment(env)
        for stmt in node.body:
            if isinstance(stmt, FuncDeclaration):
                func = MingyanFunc(stmt.name, stmt.params, stmt.body, func_env, stmt.defaults)
                methods[stmt.name] = func
                if stmt.name == '初始化':
                    init_body = stmt.body
                    init_params = stmt.params
            elif isinstance(stmt, VarDeclaration):
                func_env.define(stmt.name, self.evaluate(stmt.value, func_env))

        cls = MingyanClass(node.name, parent, methods, init_body, init_params)
        self.classes[node.name] = cls
        env.define(node.name, cls)
        return cls

    def _exec_NewExpression(self, node, env):
        cls = self.classes.get(node.class_name)
        if cls is None:
            cls = env.get(node.class_name)
        if not isinstance(cls, MingyanClass):
            raise RuntimeError(f'未定义的类: {node.class_name}')

        instance = MingyanObject(cls.name)
        args = [self.evaluate(arg, env) for arg in node.args]

        init_method = cls.find_method('初始化')
        if init_method:
            bound = init_method.bind(instance)
            self._call_function(bound, args)
        else:
            for i, param in enumerate(cls.init_params or []):
                if i < len(args):
                    instance.properties[param] = args[i]

        for method_name, method in cls.methods.items():
            if method_name != '初始化':
                instance.methods[method_name] = method

        return instance

    def _exec_ThisExpression(self, node, env):
        try:
            return env.get('这个')
        except RuntimeError:
            raise RuntimeError('"这个" 只能在类方法中使用')

    def _exec_TryCatchStatement(self, node, env):
        try:
            return self._exec_block(node.try_body, env)
        except (BreakSignal, ContinueSignal, ReturnSignal):
            raise
        except (MingyanError, RuntimeError, Exception) as e:
            if node.catch_body:
                catch_env = Environment(env)
                if node.catch_var:
                    msg = e.message if isinstance(e, (MingyanError,)) else str(e)
                    catch_env.define(node.catch_var, msg)
                try:
                    return self._exec_block(node.catch_body, catch_env)
                except (BreakSignal, ContinueSignal, ReturnSignal):
                    raise
            raise
        finally:
            if node.finally_body:
                self._exec_block(node.finally_body, env)

    def _exec_RaiseStatement(self, node, env):
        value = self.evaluate(node.value, env)
        raise MingyanError(self._format_value(value) if not isinstance(value, str) else value)

    def _exec_ImportStatement(self, node, env):
        module_name = node.module.replace('.', '/')
        possible_paths = [
            module_name + '.鸣',
            module_name + '.hy',
            module_name + '/主.鸣',
            module_name + '/主.hy',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
                from lexer import Lexer
                from parser import Parser
                tokens = Lexer(source).tokenize()
                program = Parser(tokens).parse()
                module_env = Environment(self.global_env)
                self._exec_block(program.statements, module_env)
                alias = node.alias or node.module.split('.')[-1]
                env.define(alias, module_env)
                return None
        raise RuntimeError(f'找不到模块: {node.module}')

    def _exec_FromImportStatement(self, node, env):
        module_name = node.module.replace('.', '/')
        possible_paths = [
            module_name + '.鸣',
            module_name + '.hy',
            module_name + '/主.鸣',
            module_name + '/主.hy',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
                from lexer import Lexer
                from parser import Parser
                tokens = Lexer(source).tokenize()
                program = Parser(tokens).parse()
                module_env = Environment(self.global_env)
                self._exec_block(program.statements, module_env)
                for name in node.names:
                    if module_env.has(name):
                        env.define(name, module_env.get(name))
                    else:
                        raise RuntimeError(f'模块 {node.module} 没有导出: {name}')
                return None
        raise RuntimeError(f'找不到模块: {node.module}')

    def _exec_IsExpression(self, node, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        return left is right or left == right

    def _exec_InstanceofExpression(self, node, env):
        left = self.evaluate(node.left, env)
        cls = self.classes.get(node.right)
        if cls is None:
            raise RuntimeError(f'未定义的类: {node.right}')
        if isinstance(left, MingyanObject):
            current = cls
            while current:
                if left.class_name == current.name:
                    return True
                current = current.parent
        return False

    def _exec_TernaryExpression(self, node, env):
        if self._is_truthy(self.evaluate(node.condition, env)):
            return self.evaluate(node.true_expr, env)
        return self.evaluate(node.false_expr, env)

    def _exec_LambdaExpression(self, node, env):
        return MingyanFunc('<匿名>', node.params, node.body, env)

    def _exec_SliceAccess(self, node, env):
        obj = self.evaluate(node.obj, env)
        start = int(self.evaluate(node.start, env)) if node.start else None
        end = int(self.evaluate(node.end, env)) if node.end else None
        step = int(self.evaluate(node.step, env)) if node.step else None
        return obj[start:end:step]

    def _exec_ListComprehension(self, node, env):
        iterable = self.evaluate(node.iterable, env)
        result = []
        for item in iterable:
            comp_env = Environment(env)
            comp_env.define(node.var_name, item)
            if node.condition:
                if not self._is_truthy(self.evaluate(node.condition, comp_env)):
                    continue
            result.append(self.evaluate(node.expr, comp_env))
        return result

    def _exec_block(self, statements, env):
        result = None
        block_env = Environment(env)
        for stmt in statements:
            result = self.execute(stmt, block_env)
        return result

    def evaluate(self, node, env):
        return self.execute(node, env)
