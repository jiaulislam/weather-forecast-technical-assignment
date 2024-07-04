class OpenApiTags:
    TopDistricts = "top-districts"


openapi_description = r"""
## 🟢 Weather Forcaster API
"""

SETTINGS_METADATA = {
    "OAS_VERSION": "3.1.0",
    "TITLE": r"Weather API",
    "DESCRIPTION": openapi_description,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "SERVE_AUTHENTICATION": None,
    "SWAGGER_UI_SETTINGS": {
        "swagger": "2.0",
        "deepLinking": True,
        "filter": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
    "SERVERS": [
        {"url": "http://127.0.0.1:8000", "description": "LOCAL DEV"},
    ],
    "COMPONENT_SPLIT_REQUEST": True,
}
