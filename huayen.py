#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, ReturnSignal, BreakSignal, ContinueSignal, MingyanError
from repl import REPL


def run_file(filename):
    if not os.path.exists(filename):
        print(f'错误: 找不到文件 "{filename}"')
        sys.exit(1)

    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        interpreter = Interpreter()
        interpreter.run(program)
    except LexerError as e:
        print(f'{e}')
        sys.exit(1)
    except ParseError as e:
        print(f'{e}')
        sys.exit(1)
    except MingyanError as e:
        print(f'运行错误: {e}')
        sys.exit(1)
    except ReturnSignal:
        pass
    except BreakSignal:
        print('运行错误: "中断" 只能在循环中使用')
        sys.exit(1)
    except ContinueSignal:
        print('运行错误: "继续" 只能在循环中使用')
        sys.exit(1)
    except RuntimeError as e:
        print(f'运行错误: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)


def run_source(source):
    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        interpreter = Interpreter()
        interpreter.run(program)
    except LexerError as e:
        print(f'{e}')
    except ParseError as e:
        print(f'{e}')
    except MingyanError as e:
        print(f'运行错误: {e}')
    except RuntimeError as e:
        print(f'运行错误: {e}')
    except Exception as e:
        print(f'错误: {e}')


def main():
    args = sys.argv[1:]

    if not args:
        repl = REPL()
        repl.run()
        return

    if args[0] in ('-h', '--help', '帮助'):
        print("""
鸣言 (Mingyan) - 中文编程语言 v1.0

用法:
  python huayen.py              启动交互式环境 (REPL)
  python huayen.py <文件.鸣>    执行鸣言源文件
  python huayen.py -e "代码"    直接执行一行代码
  python huayen.py -h           显示帮助信息

文件扩展名: .鸣 或 .hy
""")
        return

    if args[0] in ('-e', '--eval', '--execute'):
        if len(args) < 2:
            print('错误: 请提供要执行的代码')
            sys.exit(1)
        run_source(args[1])
        return

    filename = args[0]
    if not (filename.endswith('.鸣') or filename.endswith('.hy')):
        pass

    run_file(filename)


if __name__ == '__main__':
    main()
