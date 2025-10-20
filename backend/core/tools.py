from rest_framework.request import Request


def extract_params(request: Request) -> dict[str, int]:
    return { 
        k: int(v) for k, v in request.query_params.items() 
    }
    
def debug(**kwargs) -> None:
    print("\n\n\n")
    for key, val in kwargs.items():
        print(f"{key} | {val}\n")
    print("\n\n\n")