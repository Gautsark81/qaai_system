# create the writer script
@'
content = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "qaai_system"
version = "0.1.0"
description = "QA AI System"
authors = [{ name = "Gautam Sarkar" }]
readme = "README.md"
license = { text = "MIT" }
dependencies = [
  "requests",
]

[tool.setuptools]
packages = { find = { where = ["."], exclude = ["tests", "venv", "htmlcov", "docs"] } }
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
exclude = ["tests", "venv", "htmlcov", "docs"]
"""
with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write(content)
print("pyproject.toml overwritten (utf-8).")
'@ > write_pyproject.py
