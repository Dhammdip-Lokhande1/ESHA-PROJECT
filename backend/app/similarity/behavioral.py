"""
similarity/behavioral.py
========================
Sandboxed behavioral similarity engine.

Public API (section 8.5 of INSTRUCTIONS.md):

    behavioral_similarity(code_a: str, code_b: str, test_inputs: list[str]) -> tuple[float | None, list[dict]]

Evaluates code dynamically by running it in a sandboxed subprocess.
Returns the proportion of matching outputs (stdout/stderr/exceptions).
If no inputs are provided and none can be auto-generated, returns `(None, [evidence])`.

Design notes:
-------------
- Uses `subprocess.run` with a timeout (config.BEHAVIORAL_TIMEOUT_SECONDS).
- On Unix, uses `preexec_fn` to set memory limits (`resource.setrlimit`). This degrades
  gracefully on Windows (where `resource` is unavailable).
- Auto-generates basic inputs (e.g. `foo(0)`, `foo(1)`) if `test_inputs` is empty
  by inspecting the AST for top-level functions.
- Evidence contains one item per test case: {input, output_a, output_b, matched}.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from typing import Any

from app.config import settings

# Graceful degradation for memory limits on Windows vs Unix
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False


# ──────────────────────────────────────────────────────────────────────────────
# Sandbox Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _set_memory_limit() -> None:
    """Pre-exec function to limit memory on Unix systems."""
    if HAS_RESOURCE and settings.BEHAVIORAL_MAX_MEMORY_BYTES is not None:
        try:
            resource.setrlimit(
                resource.RLIMIT_AS,
                (settings.BEHAVIORAL_MAX_MEMORY_BYTES, settings.BEHAVIORAL_MAX_MEMORY_BYTES),
            )
        except (ValueError, OSError):
            pass


BLOCKED_MODULES = {
    "os", "subprocess", "socket", "shutil", "sys", "ctypes", "urllib",
    "requests", "http", "ftplib", "smtplib", "webbrowser", "pathlib", "importlib", "asyncio",
    "pickle", "marshal", "shelve", "gc", "inspect"
}
BLOCKED_BUILTINS = {"eval", "exec", "open", "__import__", "compile", "breakpoint"}
BLOCKED_ATTRIBUTES = {
    "__class__", "__subclasses__", "__mro__", "__bases__", "__globals__", "__builtins__", "__import__", "__code__"
}

def _check_blocked_imports(code: str) -> str | None:
    """
    AST pre-check to block imports of system/network/process modules,
    invocation of dangerous built-in functions, and attribute-walk sandbox escapes.
    Returns error string if security violation is detected, else None.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_mod = alias.name.split(".")[0]
                if root_mod in BLOCKED_MODULES:
                    return f"ERROR: SecurityViolation (blocked import '{root_mod}')"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_mod = node.module.split(".")[0]
                if root_mod in BLOCKED_MODULES:
                    return f"ERROR: SecurityViolation (blocked import '{root_mod}')"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_BUILTINS:
                return f"ERROR: SecurityViolation (blocked function '{node.func.id}')"
            elif isinstance(node.func, ast.Name) and node.func.id in {"getattr", "setattr", "delattr"}:
                return f"ERROR: SecurityViolation (blocked dynamic reflection '{node.func.id}')"
        elif isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_ATTRIBUTES:
                return f"ERROR: SecurityViolation (blocked attribute access '{node.attr}')"
    return None


def _run_in_sandbox(code: str, test_input: str) -> str:
    """
    Run `test_input` appended to `code` in resource-limited subprocess execution.
    Returns stdout, or exception message if it fails / gets blocked.
    """
    # 1. AST Pre-check for blocked modules
    blocked_err = _check_blocked_imports(code)
    if blocked_err:
        return blocked_err

    # Create a temporary file to hold the code + test execution
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
        tf.write(code)
        tf.write("\n\n# --- TEST EXECUTION ---\n")
        try:
            parsed = ast.parse(test_input)
            if len(parsed.body) == 1 and isinstance(parsed.body[0], ast.Expr):
                tf.write(f"print(repr({test_input}))\n")
            else:
                tf.write(f"{test_input}\n")
        except SyntaxError:
            tf.write(f"{test_input}\n")
            
        script_path = tf.name

    try:
        kwargs: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "timeout": settings.BEHAVIORAL_TIMEOUT_SECONDS,
        }
        if HAS_RESOURCE and os.name != "nt":
            kwargs["preexec_fn"] = _set_memory_limit

        result = subprocess.run([sys.executable, script_path], **kwargs)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'Unknown error'}"
    except subprocess.TimeoutExpired:
        return "ERROR: TimeoutExpired"
    except Exception as e:
        return f"ERROR: {type(e).__name__}"
    finally:
        try:
            os.remove(script_path)
        except OSError:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# Input Auto-generation
# ──────────────────────────────────────────────────────────────────────────────

def _auto_generate_inputs(code_a: str, code_b: str) -> list[str]:
    """
    Attempt to find a common function signature and generate simple inputs.
    """
    def get_funcs(code: str) -> dict[str, int]:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {}
        funcs = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs[node.name] = len(node.args.args)
        return funcs

    funcs_a = get_funcs(code_a)
    funcs_b = get_funcs(code_b)

    # Find intersection of function names and arity
    common_funcs = {name: arity for name, arity in funcs_a.items() if name in funcs_b and funcs_b[name] == arity}
    
    inputs = []
    if common_funcs:
        # Pick the most likely "main" or first common function
        target = list(common_funcs.keys())[0]
        arity = common_funcs[target]
        
        # Generate some basic test cases depending on arity
        # This is a naive heuristic (assuming ints/lists), but gives us something to test.
        if arity == 0:
            inputs = [f"{target}()"]
        elif arity == 1:
            inputs = [f"{target}(0)", f"{target}(1)", f"{target}('')", f"{target}([])"]
        elif arity == 2:
            inputs = [f"{target}(0, 0)", f"{target}(1, 1)", f"{target}(10, -5)"]
        else:
            # Pass N zeros
            args = ", ".join(["0"] * arity)
            inputs = [f"{target}({args})"]
            
    return inputs


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def behavioral_similarity(
    code_a: str, code_b: str, test_inputs: list[str] | None = None
) -> tuple[float | None, list[dict[str, Any]]]:
    """
    Compute behavioral similarity by executing both scripts against test inputs.
    
    Parameters
    ----------
    code_a : str
        Submission code.
    code_b : str
        Reference code.
    test_inputs : list[str] | None
        Python statements to execute against both scripts (e.g. 'foo(1)').
        If empty or None, attempts to auto-generate based on AST function signatures.

    Returns
    -------
    score : float | None
        Proportion of matching outputs. None if no inputs could be run.
    evidence : list[dict]
        Detailed execution logs per test case.
    """
    inputs = test_inputs if test_inputs else []
    
    if not inputs:
        inputs = _auto_generate_inputs(code_a, code_b)
        
    if not inputs:
        return None, [
            {
                "note": "No test inputs available and auto-generation found no common function signatures. Behavioral signal is absent.",
                "status": "skipped",
            }
        ]

    evidence = []
    matches = 0

    for test_input in inputs:
        out_a = _run_in_sandbox(code_a, test_input)
        out_b = _run_in_sandbox(code_b, test_input)

        # They match if they produce the same exact string output OR the same exact error type
        matched = (out_a == out_b)
        if matched:
            matches += 1

        evidence.append({
            "input": test_input,
            "output_a": out_a,
            "output_b": out_b,
            "matched": matched,
        })

    score = matches / len(inputs)
    return score, evidence
