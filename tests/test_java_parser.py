import os
import pytest
from testgen.parser.java_parser import JavaParser

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "SampleService.java")


@pytest.fixture
def ctx():
    return JavaParser().parse(FIXTURE)


def test_language(ctx):
    assert ctx.language == "java"


def test_class_name(ctx):
    assert ctx.class_name == "UserService"


def test_public_methods_extracted(ctx):
    method_names = {m.name for m in ctx.methods}
    assert {"createUser", "getUserById", "getAllUsers", "updateEmail"}.issubset(method_names)


def test_get_user_by_id_throws(ctx):
    method = next(m for m in ctx.methods if m.name == "getUserById")
    assert "UserNotFoundException" in method.throws


def test_create_user_params(ctx):
    method = next(m for m in ctx.methods if m.name == "createUser")
    param_names = [p[0] for p in method.params]
    assert "name" in param_names
    assert "email" in param_names


def test_imports_extracted(ctx):
    assert any("UserRepository" in imp for imp in ctx.imports)
