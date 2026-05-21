import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, ReturnSignal, BreakSignal, ContinueSignal, MingyanError


BANNER = r"""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║     鸣言 (Mingyan) - 中文编程语言 v1.0            ║
║     一个全中文语法的现代编程语言                    ║
║                                                   ║
║     输入表达式或语句，按回车执行                    ║
║     输入 "帮助" 查看帮助信息                       ║
║     输入 "退出" 或按 Ctrl+C 退出                   ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
"""

HELP_TEXT = """
鸣言 (Mingyan) 中文编程语言 - 帮助信息
=====================================

基本语法:
  变量 x = 10              声明变量
  常量 PI = 3.14            声明常量
  x = 20                    赋值

数据类型:
  整数: 42, 浮点: 3.14, 字符串: "你好", 布尔: 真/假, 空

运算符:
  算术: + - * / % **       比较: == != < > <= >=
  逻辑: 且 或 非           赋值: = += -= *= /=

控制流:
  如果 (条件) { ... } 否则如果 (条件) { ... } 否则 { ... }
  当 (条件) { ... }
  遍历 项 在 列表 { ... }

函数:
  函数 名称(参数) { ... }
  返回 值

类:
  类 名称 { ... }
  类 名称 继承 父类 { ... }

内置函数:
  打印(值)     长度(列表)    类型(值)     输入(提示)
  转整数(值)   转浮点(值)    转字符串(值)  范围(起始, 结束)
  绝对值(值)   最大值(...)   最小值(...)   排序(列表)
  平方根(值)   幂(底, 指)   随机整数(a,b) 随机浮点()
  文件读取(路径) 文件写入(路径,内容) 文件存在(路径)
  映射(函数,列表) 过滤(函数,列表) 归约(函数,列表)

列表方法:
  列表.追加(值)  列表.弹出()   列表.排序()   列表.反转()
  列表.包含(值)  列表.映射(函数) 列表.过滤(函数) 列表.去重()

字符串方法:
  字符串.分割(分隔符) 字符串.替换(旧,新) 字符串.大写()
  字符串.小写() 字符串.去空白() 字符串.包含(子串)
"""


class REPL:
    def __init__(self):
        self.interpreter = Interpreter()
        self.buffer = []
        self.brace_depth = 0

    def run(self):
        print(BANNER)
        while True:
            try:
                prompt = '鸣言>>> ' if not self.buffer else '  ... '
                line = input(prompt)
                line = line.strip()

                if not line:
                    if self.buffer:
                        continue
                    else:
                        continue

                if not self.buffer:
                    if line in ('退出', 'exit', 'quit'):
                        print('再见！')
                        break
                    if line in ('帮助', 'help'):
                        print(HELP_TEXT)
                        continue
                    if line in ('清屏', 'clear'):
                        import os
                        os.system('cls' if sys.platform == 'win32' else 'clear')
                        continue

                self.brace_depth += line.count('{') - line.count('}')

                if self.brace_depth > 0:
                    self.buffer.append(line)
                    continue

                self.buffer.append(line)
                source = '\n'.join(self.buffer)
                self.buffer = []
                self.brace_depth = 0

                self._execute(source)

            except KeyboardInterrupt:
                print()
                self.buffer = []
                self.brace_depth = 0
                continue
            except EOFError:
                print('\n再见！')
                break

    def _execute(self, source):
        try:
            tokens = Lexer(source).tokenize()
            program = Parser(tokens).parse()
            result = None
            for stmt in program.statements:
                result = self.interpreter.execute(stmt, self.interpreter.global_env)
            if result is not None:
                print(self.interpreter._format_value(result))
        except LexerError as e:
            print(f'词法错误: {e}')
        except ParseError as e:
            print(f'语法错误: {e}')
        except MingyanError as e:
            print(f'运行错误: {e}')
        except ReturnSignal as r:
            if r.value is not None:
                print(self.interpreter._format_value(r.value))
        except BreakSignal:
            print('错误: "中断" 只能在循环中使用')
        except ContinueSignal:
            print('错误: "继续" 只能在循环中使用')
        except RuntimeError as e:
            print(f'运行错误: {e}')
        except Exception as e:
            print(f'错误: {e}')
