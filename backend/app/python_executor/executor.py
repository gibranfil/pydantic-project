import ast
import builtins
from datetime import date, datetime

import numpy as np
import pandas as pd


class PythonExecutor:

    DANGEROUS_NAMES = {
        "__import__",
        "eval",
        "exec",
        "open",
        "input",
        "compile",
        "globals",
        "locals",
        "vars",
        "help",
        "exit",
        "quit",
        "setattr",
        "getattr",
        "delattr",
        "hasattr",
        "issubclass",
        "super",
        "object",
        "os",
        "sys",
        "subprocess",
        "socket",
        "pathlib",
        "shutil",
        "importlib",
    }

    DANGEROUS_ATTRS = {
        "__class__",
        "__mro__",
        "__subclasses__",
        "__globals__",
        "__builtins__",
        "__dict__",
        "__import__",
        "im_class",
        "gi_frame",
    }

    SAFE_BUILTINS = {
        "abs",
        "all",
        "any",
        "dict",
        "enumerate",
        "len",
        "list",
        "max",
        "min",
        "round",
        "set",
        "sorted",
        "sum",
        "tuple",
        "range",
    }

    def __init__(self, dataframe):
        self.df = dataframe

    def _validate_code(self, code: str) -> None:
        tree = ast.parse(code, mode="exec")

        class SafeCodeValidator(ast.NodeVisitor):
            def visit_Import(self, node):
                raise ValueError("Unsafe code: imports are not allowed")

            def visit_ImportFrom(self, node):
                raise ValueError("Unsafe code: imports are not allowed")

            def visit_FunctionDef(self, node):
                raise ValueError("Unsafe code: function definitions are not allowed")

            def visit_AsyncFunctionDef(self, node):
                raise ValueError("Unsafe code: async functions are not allowed")

            def visit_ClassDef(self, node):
                raise ValueError("Unsafe code: class definitions are not allowed")

            def visit_Lambda(self, node):
                raise ValueError("Unsafe code: lambda expressions are not allowed")

            def visit_Global(self, node):
                raise ValueError("Unsafe code: global statements are not allowed")

            def visit_Nonlocal(self, node):
                raise ValueError("Unsafe code: nonlocal statements are not allowed")

            def visit_Name(self, node):
                if node.id in PythonExecutor.DANGEROUS_NAMES:
                    raise ValueError(f"Unsafe code: {node.id} is not allowed")
                self.generic_visit(node)

            def visit_Attribute(self, node):
                if node.attr in PythonExecutor.DANGEROUS_ATTRS:
                    raise ValueError(f"Unsafe attribute: {node.attr}")
                self.generic_visit(node)

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                    if name in PythonExecutor.DANGEROUS_NAMES:
                        raise ValueError(f"Unsafe function: {name}")
                    if (
                        name not in PythonExecutor.SAFE_BUILTINS
                        and name not in {"df", "pd", "np"}
                    ):
                        raise ValueError(f"Function '{name}' is not allowed.")
                elif isinstance(node.func, ast.Attribute):
                    root = node.func
                    while isinstance(root, ast.Attribute):
                        root = root.value

                    if isinstance(root, ast.Name):
                        if root.id in PythonExecutor.DANGEROUS_NAMES:
                            raise ValueError(f"Unsafe object: {root.id}")
                        if root.id not in {"df", "pd", "np"}:
                            raise ValueError(f"Object '{root.id}' is not allowed.")

                self.generic_visit(node)

    def _normalize_result(self, value):
        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, pd.Series):
            return self._normalize_result(value.to_dict())

        if isinstance(value, pd.DataFrame):
            return self._normalize_result(value.to_dict(orient="records"))

        if isinstance(value, np.ndarray):
            return self._normalize_result(value.tolist())

        if isinstance(value, np.generic):
            return value.item()

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, dict):
            return {str(key): self._normalize_result(item) for key, item in value.items()}

        if isinstance(value, (list, tuple, set)):
            return [self._normalize_result(item) for item in value]

        return value

    def execute(self, code: str):
        self._validate_code(code)

        allowed_globals = {
            "pd": pd,
            "np": np,
            "df": self.df,
            "__builtins__": {name: getattr(builtins, name) for name in self.SAFE_BUILTINS},
        }
        locals_dict = {}

        try:
            exec(compile(code, "<python_executor>", "exec"), allowed_globals, locals_dict)
        except NameError as exc:
            raise ValueError(f"Unsafe code: {exc}") from exc

        if "result" not in locals_dict:
            raise ValueError("The executed code must assign the final answer to a variable named 'result'")

        return self._normalize_result(locals_dict["result"])