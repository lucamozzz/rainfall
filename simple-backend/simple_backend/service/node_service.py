"""
 Copyright (C) 2023 Università degli Studi di Camerino.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta, Luca Mozzoni, Vincenzo Nucci

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

import ast
import re
import sys
import os
from typing import List, Optional
import requests
from errors import CustomNodeConfigurationError, NodesRetrievalError
from schemas.nodes import CustomNode, NodeStructure, CustomNodeIOParams

RAIN_STRUCTURE_URL=os.getenv('RAIN_STRUCTURE_URL', 'https://firebasestorage.googleapis.com/v0/b/rainfall-e8e57.appspot.com/o/rain_structure.json?alt=media')

try:
    nodes_request = requests.get(url=RAIN_STRUCTURE_URL)
    if nodes_request.status_code != 200:
        raise NodesRetrievalError(f"Nodes request failed: {nodes_request.reason}")
    rain_structure = nodes_request.json()
except:
    print('Download of rain_structure.json failed!')
    sys.exit(1)


def determine_value_type(v: any):
    t = type(v).__name__
    if type(v) == list:
        if len(v) == 0:
            t = 'list[str]'
        else:
            t = 'list['+type(v[0]).__name__+']'
    return t


def get_node_param_value_and_type(clazz: str, param: str, value: str):
    v = ast.literal_eval(value)
    if clazz == 'CustomNode':
        return v, determine_value_type(v)
    n = [x for x in rain_structure["nodes"] if x["clazz"] == clazz][0]
    ps = n["parameter"]
    p = [x for x in ps if x["name"] == param][0]
    t = None
    if p["type"].lower() == 'any':
        t = determine_value_type(v)
    return v, t


def parse_custom_node_code(code: str, function_name: str):
    parsed = ast.parse(code)
    funcs = parsed.body
    main_func = [x for x in funcs if hasattr(x, 'name') and x.name == function_name][0]
    funcs.remove(main_func)
    main_func.body.insert(0, funcs)
    return main_func


def parse_custom_node_requirements(code: str):
    parsed = ast.parse(code)
    requirements = set([])
    for statement in ast.walk(parsed):
        if isinstance(statement, ast.Import):
            for name in statement.names:
                requirements.add(name.name.split('.')[0])
        elif isinstance(statement, ast.ImportFrom):
            requirements.add(statement.module.split('.')[0])
    return requirements


def find_custom_node_params(code, main_func: str) -> CustomNodeIOParams:
    """
    Method that retrieves all the parameters of a custom nodes
    """
    params = [x.arg for x in code.args.args]
    if len(params) < 2:
        raise CustomNodeConfigurationError(
            f"The signature of the function {main_func} should be: {main_func}(input, output, ...kwargs)")

    body = ast.unparse(code.body)

    inputs = get_variables_matches(
        body, r"{}(\[|\.get\()(\"|\')(?P<param>[a-zA-Z_\d-]+)(\"|\')(\]|\))".format(params[0])
    )

    outputs = get_variables_matches(
        body, r"{}\[(\"|\')(?P<param>[a-zA-Z_\d-]+)(\"|\')\]".format(params[1])
    )

    return CustomNodeIOParams(inputs=inputs, outputs=outputs, params=params[2:])


def get_variables_matches(code, regex):
    """
    Returns the matches given a string and a regex
    """
    return [x.group("param") for x in re.finditer(regex, code, re.MULTILINE)]


def check_custom_node_code(custom_nodes: List[CustomNode]):
    """
    Method that checks the correctness of the Custom Nodes
    """
    functions = []
    nodes = []
    for node in custom_nodes:
        if node.function_name not in functions:
            functions.append(node.function_name)
            nodes.append(node.code)
        else:
            # TODO consider two custom nodes different by node.class_name or node.node
            # as of now they are all CustomNode and rain.nodes.custom.custom.CustomNode
            if node.code not in nodes:
                raise CustomNodeConfigurationError(f"Duplicated function name in node {node.node_id}!")


def get_nodes_structure() -> list[NodeStructure]:
    """
    Returns the available Rain nodes
    """
    return rain_structure["nodes"]


def get_node(clazz) -> Optional[NodeStructure]:
    """
    Returns the node with the specified clazz
    """
    for node in rain_structure["nodes"]:
        if node["clazz"] == clazz:
            return node
    return None
