

class NameChecker():
    def __init__(self) -> None:
        self._sectionForchars = {'/', '\\', ' '}
        self._secpartForchars = {'/', '\\'}

    def CheckSectionName(self, name: str):
        self._checkName(self._sectionForchars, name)

    def CheckSecpartName(self, name: str):
        self._checkName(self._secpartForchars, name)

# private:

    def _checkName(self, forchars: set[str], name: str) -> None:
        badchars = set(name) & (forchars)
        if (len(badchars) > 0):
            raise RuntimeError(f'passed name {name} contains invalid characters "{badchars}"')
