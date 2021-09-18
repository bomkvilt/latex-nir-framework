import os

class PathWorks:
    @staticmethod
    def FixPath(path: str) -> str:
        return path.replace('\\', '/')

    @staticmethod
    def JoinPath(*parts: str) -> str:
        if (len(parts) == 0):
            return ''
        return PathWorks.FixPath(os.path.join(*parts))

    # \return true if exists
    # \throws if the path exists and it's not a file
    @staticmethod
    def CheckIfFileOrNotExists(path: str, *rest: str) -> bool:
        if (len(rest) > 0):
            path = os.path.join(path, *rest)
        if (os.path.exists(path)):
            if (os.path.isfile(path)):
                return True
            raise RuntimeError(f'Path "{path}" is not a file name')
        return False
    
    # \return true if exists
    # \throws if the path exists and it's not a directory
    @staticmethod
    def CheckIfDirOrNotExists(path: str, *rest: str) -> bool:
        if (len(rest) > 0):
            path = os.path.join(path, *rest)
        if (os.path.exists(path)):
            if (os.path.isdir(path)):
                return True
            raise RuntimeError(f'Path "{path}" is not a file name')
        return False
