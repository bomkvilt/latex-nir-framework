import os



def FixPath(path: str) -> str:
    return path.replace('\\', '/')


def JoinPath(parts: list[str]) -> str:
    if (len(parts) > 0):
        return FixPath(os.path.join(*parts))
    return ''
