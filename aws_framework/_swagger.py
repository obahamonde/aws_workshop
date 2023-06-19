import json
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

"""Automatically generate OpenAPI documentation for your AioFauna API."""
from functools import singledispatch
from json import JSONDecoder, loads
from typing import Any, Dict, List, Union

from aiohttp.web import Request, Response
from aiohttp.web_request import FileField
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ._fmt import AWSEncoder, SwaggerEncoder
from .data import DynaModel  # pylint: disable=no-name-in-module
from .odm import NoSQLModel


def extract(params: dict, path: str):
    """
    Extracts openapi parameters from the function signature."""
    open_api_params = {}

    for name, param in params.items():
        type_ = param.annotation

        if type_ in (str, int, float, bool) and name:
            if f"{{{name}}}" in path:
                param_location = "path"
            else:
                param_location = "query"

            open_api_params[name] = {
                "in": param_location,
                "name": name,
                "required": True,
                "schema": {"type": type_, "default": param.default, "required": True},
            }

        elif type_ == FileField:
            open_api_params[name] = {
                "in": "formData",
                "name": name,
                "required": True,
                "schema": {"type": "file", "format": "binary"},
                "consumes": ["multipart/form-data"],
                "headers": {
                    "Content-Type": {"type": "string", "default": "multipart/form-data"}
                },
            }

        elif issubclass(type_, (BaseModel, DynaModel)):
            open_api_params[name] = {
                "in": "body",
                "name": name,
                "required": True,
                "schema": type_.schema(),
            }

        else:
            continue

    return open_api_params


def transform(
    open_api: Dict[str, Any],
    path: str,
    method: str,
    func: Any,
    open_api_params: Dict[str, Any],
):
    """
    Transforms the function signature into OpenAPI documentation.
        open_api (Dict[str, Any]): The OpenAPI documentation.
        path (str): The URL path of the endpoint.
        method (str): The HTTP method of the endpoint.
        func (Any): The function being documented.
        open_api_params (Dict[str, Any]): The OpenAPI parameters of the function.
    """
    if path in ["/openapi.json", "/docs"]:
        return

    _scalars = []
    _body = None
    _is_file_upload = False

    for param in open_api_params.values():
        if isinstance(param["schema"], dict):
            if "type" in param["schema"] and param["schema"]["type"] != "object":
                _scalars.append(param)
            else:
                _body = {"content": {"application/json": {"schema": param["schema"]}}}
        elif param["in"] == "formData" and param["schema"]["type"] == "file":
            _is_file_upload = True
            _scalars.append(param)
        else:
            continue

    if _body:
        open_api["paths"].setdefault(path, {})[method.lower()] = {
            "summary": func.__name__,
            "description": func.__doc__,
            "parameters": _scalars,
            "requestBody": _body
            if not _is_file_upload
            else {
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "properties": {
                                "file": {
                                    "type": "array",
                                    "items": {"type": "string", "format": "binary"},
                                }
                            }
                        }
                    }
                }
            },
            "responses": {"200": {"description": "OK"}},
        }
        open_api["components"]["schemas"].update(param["schema"])  # type: ignore
    else:
        open_api["paths"].setdefault(path, {})[method.lower()] = {
            "summary": func.__name__,
            "description": func.__doc__,
            "parameters": _scalars,
            "responses": {"200": {"description": "OK"}},
        }


async def load(request: Request, params: dict):
    """
    Loads the function parameters from the request.
        Dict[str, Any]: The updated parameters to apply to the function.
    """
    args_to_apply = {}

    for name, param in params.items():
        annotation = param.annotation
        if annotation in (str, int, float, bool) and name in request.match_info:
            args_to_apply[name] = request.match_info[name]
        elif annotation in (str, int, float, bool) and name in request.query:
            args_to_apply[name] = annotation(request.query[name])
        elif annotation == FileField:
            headers = dict(request.headers)
            new_headers = {
                "Content-Type": headers.get("Content-Type", "multipart/form-data"),
                "Content-Disposition": headers.get("Content-Disposition", "inline"),
            }
            new_request = request.clone(headers=new_headers)
            args_to_apply[name] = new_request
        elif issubclass(annotation, BaseModel):
            data = await request.json(loads=JSONDecoder().decode)
            if isinstance(data, (str, bytes)):
                data = loads(data)
            args_to_apply[name] = annotation(**data)
        else:
            args_to_apply[name] = request
    return args_to_apply


html = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>AWS WorkShop</title>
                <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.3/swagger-ui.css" >
                <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.3/favicon-32x32.png" sizes="32x32" />
                <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.3/favicon-16x16.png" sizes="16x16" />
                <style>
                html
                {
                    box-sizing: border-box;
                    overflow: -moz-scrollbars-vertical;
                    overflow-y: scroll;
                }
                
                .swagger-ui .topbar
                {
                    display: none;
                }
                    
                    
                *,
                *:before,
                *:after
                {
                    box-sizing: inherit;
                }

                body
                {
                    margin:0;
                    background: #fafafa;
                }
                </style>
            </head>

            <body>
                <div id="swagger-ui"></div>

                <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.3/swagger-ui-bundle.js"> </script>
                <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.3/swagger-ui-standalone-preset.js"> </script>
                <script>
                window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/openapi.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                    ],
                    plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                })
                window.ui = ui
                }
            </script>
            </body>
            </html>
            """


@singledispatch
def do_response(response: Any) -> Response:
    """
    Flask-esque function to make a response from a function.
    """
    return response


@do_response.register(BaseModel)
def _(response: BaseModel) -> Response:
    return Response(
        status=200,
        body=json.dumps(response.dict(), cls=AWSEncoder),
        content_type="application/json",
    )


@do_response.register(NoSQLModel)
def _(response: NoSQLModel) -> Response:
    return Response(
        status=200,
        body=json.dumps(response.dict(), cls=AWSEncoder),
        content_type="application/json",
    )


@do_response.register(dict)
def _(response: dict) -> Response:
    return Response(
        status=200,
        body=json.dumps(response, cls=AWSEncoder),
        content_type="application/json",
    )


@do_response.register(str)
def _(response: str) -> Response:
    if "<html" in response:
        return Response(status=200, text=response, content_type="text/html")
    return Response(status=200, text=response, content_type="text/plain")


@do_response.register(bytes)
def _(response: bytes) -> Response:
    return Response(status=200, body=response, content_type="application/octet-stream")


@do_response.register(int)
def _(response: int) -> Response:
    return Response(status=200, text=str(response), content_type="text/plain")


@do_response.register(float)
def _(response: float) -> Response:
    return Response(status=200, text=str(response), content_type="text/plain")


@do_response.register(bool)
def _(response: bool) -> Response:
    return Response(status=200, text=str(response), content_type="text/plain")


@do_response.register(list)
def _(response: List[Union[NoSQLModel, BaseModel, dict, str, int, float]]) -> Response:
    processed_response = []

    for item in response:
        if isinstance(item, (NoSQLModel, BaseModel)):
            processed_response.append(item.dict())
        elif isinstance(item, dict):
            processed_response.append(item)
        elif isinstance(item, str):
            processed_response.append(item)
        elif isinstance(item, (int, float, bool)):
            processed_response.append(str(item))
        else:
            raise TypeError(f"Cannot serialize type {type(item)}")
    return Response(
        status=200, body=json.dumps(processed_response), content_type="application/json"
    )
