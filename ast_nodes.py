from dataclasses import dataclass, field
from typing import List, Optional, Any


class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


@dataclass
class NumberLiteral(ASTNode):
    value: float


@dataclass
class StringLiteral(ASTNode):
    value: str


@dataclass
class BooleanLiteral(ASTNode):
    value: bool


@dataclass
class NullLiteral(ASTNode):
    pass


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]


@dataclass
class DictLiteral(ASTNode):
    pairs: List[tuple]


@dataclass
class BinaryOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class CompoundAssignment(ASTNode):
    name: str
    op: str
    value: ASTNode


@dataclass
class VarDeclaration(ASTNode):
    name: str
    value: ASTNode
    is_const: bool = False


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]
    elif_clauses: List[tuple] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ForStatement(ASTNode):
    var_name: str
    iterable: ASTNode
    body: List[ASTNode]


@dataclass
class FuncDeclaration(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]
    defaults: List[Optional[ASTNode]] = field(default_factory=list)


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode] = None


@dataclass
class BreakStatement(ASTNode):
    pass


@dataclass
class ContinueStatement(ASTNode):
    pass


@dataclass
class FuncCall(ASTNode):
    callee: ASTNode
    args: List[ASTNode]


@dataclass
class MemberAccess(ASTNode):
    obj: ASTNode
    member: str


@dataclass
class MemberAssignment(ASTNode):
    obj: ASTNode
    member: str
    value: ASTNode


@dataclass
class IndexAccess(ASTNode):
    obj: ASTNode
    index: ASTNode


@dataclass
class IndexAssignment(ASTNode):
    obj: ASTNode
    index: ASTNode
    value: ASTNode


@dataclass
class ClassDeclaration(ASTNode):
    name: str
    parent: Optional[str]
    body: List[ASTNode]


@dataclass
class NewExpression(ASTNode):
    class_name: str
    args: List[ASTNode]


@dataclass
class ThisExpression(ASTNode):
    pass


@dataclass
class TryCatchStatement(ASTNode):
    try_body: List[ASTNode]
    catch_var: Optional[str]
    catch_body: Optional[List[ASTNode]]
    finally_body: Optional[List[ASTNode]]


@dataclass
class RaiseStatement(ASTNode):
    value: ASTNode


@dataclass
class ImportStatement(ASTNode):
    module: str
    alias: Optional[str] = None


@dataclass
class FromImportStatement(ASTNode):
    module: str
    names: List[str]


@dataclass
class IsExpression(ASTNode):
    left: ASTNode
    right: ASTNode


@dataclass
class InstanceofExpression(ASTNode):
    left: ASTNode
    right: str


@dataclass
class TernaryExpression(ASTNode):
    condition: ASTNode
    true_expr: ASTNode
    false_expr: ASTNode


@dataclass
class LambdaExpression(ASTNode):
    params: List[str]
    body: List[ASTNode]


@dataclass
class MethodCall(ASTNode):
    obj: ASTNode
    method: str
    args: List[ASTNode]


@dataclass
class SliceAccess(ASTNode):
    obj: ASTNode
    start: Optional[ASTNode]
    end: Optional[ASTNode]
    step: Optional[ASTNode]


@dataclass
class ListComprehension(ASTNode):
    var_name: str
    iterable: ASTNode
    expr: ASTNode
    condition: Optional[ASTNode] = None
