# Cathon
Cathon 是一款使用 Python 编写的自制编程语言, 其语法继承自 Python 语法, 并对其进行扩展

Cathon is a programming language written in Python, which grammar is inherited from Python.


# Installing
require python >= 3.9
```sh
pip3 install cathon
```

# Usage
## Used by script
```sh
# Run in interactive mode
python -m cathon
cathon 

# Run a string cmd directly
cathon -c "print('hello world!')"

# Run a file
cathon tests/test.cat

# Run program read from stdin 
cat tests/test.cat | cathon
```

## Used in python
```python
import cathon 
# in a schedule
```