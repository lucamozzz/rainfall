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

import sys
sys.path.append('.')
import json
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from config import here
from controller.routes import initialize_api_routes
from errors import register_errors


def create_app():
    app = FastAPI(debug=os.environ.get("MODE", "DEBUG") == "DEBUG")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:7000"] if app.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization"]
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.include_router(initialize_api_routes())
    register_errors(app)

    if not app.debug:
        static_files_folder = os.path.join(os.path.dirname(__file__), 'static')
        if os.path.exists(static_files_folder) and os.path.isdir(static_files_folder):
            app.mount("/", StaticFiles(directory=static_files_folder, html=True), name="static")

    if 'generate' in sys.argv:
        with open(file=here('../openapi.json'), mode='w') as f:
            f.write(json.dumps(app.openapi(), separators=(',', ':')))
            print('openapi.json generated successfully!')
        sys.exit(0)

    return app


if __name__ == '__main__':
    uvicorn.run(create_app(), host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
