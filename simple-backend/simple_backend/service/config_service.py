"""
 Copyright (C) 2023 Università degli Studi di Camerino and Sigma S.p.A.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

import time
import io
import zipfile
import yaml
import uuid
import os
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
from typing import List, Union
from simple_backend.errors import DagCycleError, FileWriteError
from simple_backend.schemas.nodes import UI, CustomNode, Node, UINode, CustomNodeStructure, NodeStructure
from simple_backend.service import node_service
from simple_backend.service.dag_generator import DagCreator
from simple_backend.service.node_service import parse_custom_node_requirements
from simple_backend.service.script_generator import ScriptGenerator
from simple_backend.service.repository_service import add_dataflow_to_repo
from simple_backend import config


DATABASE_NAME='rainfall'
EXECUTIONS_COLLECTION_NAME='repositories'


def check_dag(nodes):
    """
    Method that creates and checks the dag of nodes
    """
    dag = DagCreator()
    dag.create_dag(nodes)
    if dag.has_cycles():
        raise DagCycleError("The Dataflow contains cycles!", 400)

    return dag


def generate_script(nodes: list[Union[CustomNode, Node]]):
    """
    Method that generates the final python script
    """
    dag = check_dag(nodes)

    ordered_nodes = dag.get_ordered_nodes()
    ordered_edges = dag.get_ordered_edges()

    if custom_nodes := list(filter(lambda node: isinstance(node, CustomNode), ordered_nodes)):
        node_service.check_custom_node_code(custom_nodes)

    script_generator = ScriptGenerator(ordered_nodes, ordered_edges)
    script = script_generator.generate_script()

    return script


def get_requirements(libs: List[str], ui_nodes: List[UINode],
                     ui_structures: dict[str, Union[CustomNodeStructure, NodeStructure]]) -> List[str]:
    """
    Method that returns the Python dependencies, useful to re-create the environment of a given Dataflow
    """
    libs = [lib.lower() for lib in libs]
    requirements = set(["git+ssh://git@bitbucket.org/proslabteam/rain@master#egg=rain"])

    # TODO: manage dependencies' versions and avoid duplicates
    #       e.g. pandas and pandas~=1.3.0 shouldn't be two different dependencies
    # for dep in rain_structure["dependencies"]:
    #    if any(lib in dep for lib in libs):
    #        requirements.add(dep)

    for lib in libs:
        if lib != 'base':
            requirements.add(lib)

    custom_structures = set([node.package for node in ui_nodes
                             if node.package.startswith('rain.nodes.custom.custom.CustomNode')])
    for structure in custom_structures:
        for req in parse_custom_node_requirements(ui_structures[structure].code):
            requirements.add(req)

    return requirements


def generate_artifacts(repository: str, script: str, dependencies: List[str], ui: UI) -> None:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    requirements = get_requirements(dependencies, ui.nodes.values(), ui.structures)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dataflow = {
        "_id": 'dataflow-' + str(uuid.uuid4()),
        "created_at": current_time,
        "script": script,
        "requirements": "\n".join(requirements),
        "ui": ui.json(separators=(',', ':')),
    }

    add_dataflow_to_repo(dataflow, repository)
    return dataflow
