from rest_framework.request import Request


def extract_params(request: Request) -> dict[str, int]:
    return { 
        k: int(v) for k, v in request.query_params.items() 
    }