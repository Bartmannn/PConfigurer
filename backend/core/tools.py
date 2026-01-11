from rest_framework.request import Request


COMPATIBILITY_KEYS = {
    "cpu", "mobo", "ram", "gpu", "psu", "mem", "case", "chassis",
}


def extract_params(request: Request, allowed_keys: set[str] | None = None) -> dict[str, int]:
    keys = allowed_keys or COMPATIBILITY_KEYS
    params: dict[str, int] = {}
    for key, value in request.query_params.items():
        if key not in keys:
            continue
        try:
            params[key] = int(value)
        except (TypeError, ValueError):
            continue
    return params
    
def debug(**kwargs) -> None:
    print("\n\n\n")
    for key, val in kwargs.items():
        print(f"{key} | {val}\n")
    print("\n\n\n")
