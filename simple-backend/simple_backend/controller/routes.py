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

import os
from fastapi import APIRouter
from simple_backend.controller import node_api, config_api, script_api, repository_api, execution_api, standard_auth_api

def initialize_api_routes():
    """
    Initialize all the routes/names that can be used to access endpoints
    """
    router = APIRouter(prefix='/api/v1')

    # Node API
    router.include_router(node_api.router, prefix='/nodes', tags=['nodes'])

    # Config API
    router.include_router(config_api.router, prefix='/config', tags=['config'])

    # Script API
    router.include_router(script_api.router, prefix='/script', tags=['script'])

    # Repository API
    router.include_router(repository_api.router, prefix='/repositories', tags=['repository'])

    # Execution API
    router.include_router(execution_api.router, prefix="/execution", tags=['execution'])


    auth_type = os.environ.get("AUTH", "STANDARD")
    if auth_type == "STANDARD":
        # Standard Authentication API
        router.include_router(standard_auth_api.router, prefix="/auth", tags=['auth'])

    return router
