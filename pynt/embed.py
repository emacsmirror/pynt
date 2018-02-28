"""Embed a IPython kernel into a function

Script for embedding a IPython kernel into a function so we can open a jupyter
notebook and talk to it.

"""

import ast
import shutil
import subprocess
import tempfile

import astor
import jupyter_core
import plac

from node_transformers import IPythonEmbedder


@plac.annotations(
        namespace=('function to embed a kernel in', 'option', None, str),
        cmd=('command which invokes the function', 'option', None, str),
)
def main(namespace, cmd):
    """Embed a kernel in `fname` in `namespace`

    Args:
        namespace (str): function to embed a kernel in
        cmd (str): command which invokes `namespace`

    Returns:
        None

    `namespace` is of the form module.(class.)?[method|func]

    Examples:
        - my_module.my_func
        - my_module.MyClass.my_func

    """
    module = namespace.split('.')[0]
    path = '.'.join([module, 'py'])

    # Read in Input File
    with open(path) as f:
        lines = f.readlines()
    code = ''.join(lines)

    # Embed an IPython Kernel into the Function
    tree = ast.parse(code)
    t = IPythonEmbedder(namespace).visit(tree)
    code_ = astor.to_source(t)

    # Copy the Old File to a Temporary File
    t = tempfile.NamedTemporaryFile(delete=False)
    shutil.copyfile(path, t.name)

    # Dump New Code to `path`
    with open(path, 'w') as f:
        f.write(code_)

    # Run `cmd`
    p = subprocess.run(cmd.split())
    print(f'p.returncode = {p.returncode}')

    # Move Original File Back
    shutil.copyfile(t.name, path)

    # Write .pynt to runtime dir so a kernel (re)start will attach to this
    # kernel
    runtime_dir = jupyter_core.paths.jupyter_runtime_dir()
    open(f'{runtime_dir}/.pynt', 'a').close()


if __name__ == '__main__':
    plac.call(main)
