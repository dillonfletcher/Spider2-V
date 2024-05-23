#coding=utf8
import io
import nbformat
from typing import Dict, Any
import json


def is_jupyter_cell_executed(result: str, expected: Dict[str, Any], **options) -> float:
    """ Determine whether all cells in a Jupyter notebook are executed.
    @args:
        result: str - the path to the Jupyter notebook file.
        expected: Dict[str, Any] - the expected result.
            key: expected, value: List[int] - the expected unexecuted cell indices.
        options: Dict[str, Any] - the options.
    """
    try:
        with io.open(result, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=options.get('version', 4))
        cell_type = options.get('cell_type', 'code')
        
        unexecuted = []
        for idx, cell in enumerate(nb.cells):
            if cell.cell_type == cell_type:
                if not cell.get('execution_count'):
                    unexecuted.append(idx)
        print(unexecuted)
        if unexecuted != expected['expected']:
            return 0.0
        return 1.0
    except Exception as e:
        print(e)
        return 0.0
    
def compare_ipynb_files(result: str, expected: str, **options) -> float:
    """ Compare two Jupyter notebook files.
    @args:
        result: str - the path to the Jupyter notebook file.
        expected: str - the path to the expected Jupyter notebook file.
        options: Dict[str, Any] - the options.
    """
    try:
        with io.open(result, 'r', encoding='utf-8') as f:
            ipynb_file1 = json.load(f)
        with io.open(expected, 'r', encoding='utf-8') as f:
            ipynb_file2 = json.load(f)
        
        for (k1, v1), (k2, v2) in zip(ipynb_file1.items(), ipynb_file2.items()):
            if k1 != k2:
                return 0.0
            if k1 != 'metadata' and v1 != v2:
                return 0.0
        return 1.0
    except Exception as e:
        print(e)
        return 0.0
    

def compare_notebook_cells(result: str, expected: str) -> float:
    """ Compare two Jupyter notebook cells.
    @args:
        result: str - the path to the Jupyter notebook file.
        expected: str - the path to the expected Jupyter notebook file.
        options: Dict[str, Any] - the options.
    """
    with open(result, 'r', encoding='utf-8') as result_file:
        result_nb = nbformat.read(result_file, as_version=4)
    with open(expected, 'r', encoding='utf-8') as expected_file:
        expected_nb = nbformat.read(expected_file, as_version=4)
    
    result_cells = result_nb['cells']
    expected_cells = expected_nb['cells']
    
    if len(result_cells) != len(expected_cells):
        return 0.0
    
    for result_cell, expected_cell in zip(result_cells, expected_cells):
        if result_cell['cell_type'] != expected_cell['cell_type']:
            return 0.0
        if result_cell['source'] != expected_cell['source']:
            return 0.0
    
    return 1.0

def compare_notebook_outputs(result: str, expected: str) -> float:
    """ Compare two Jupyter notebook outputs.
    @args:
        result: str - the path to the Jupyter notebook file.
        expected: str - the path to the expected Jupyter notebook file.
        options: Dict[str, Any] - the options.
    """
    with open(result, 'r', encoding='utf-8') as result_file:
        result_nb = nbformat.read(result_file, as_version=4)
    with open(expected, 'r', encoding='utf-8') as expected_file:
        expected_nb = nbformat.read(expected_file, as_version=4)
    
    result_cells = result_nb['cells']
    expected_cells = expected_nb['cells']
    
    if len(result_cells) != len(expected_cells):
        print("Num of cells mismatch!")
        return 0.0
    
    for result_cell, expected_cell in zip(result_cells, expected_cells):
        if result_cell['cell_type'] != expected_cell['cell_type']:
            print("Cell type mismatch!")
            return 0.0
        if result_cell['cell_type'] == "code":
            for result_output, expected_output in zip(result_cell['outputs'], expected_cell['outputs']):
                if result_output != expected_output:
                    print(result_output)
                    print(expected_output)
                    return 0.0
    
    return 1.0