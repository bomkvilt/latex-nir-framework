

class BaseTexParser:
    def __init__(self) -> None:
        pass

    @staticmethod
    def TEXT(*strings: str):
        strings = map(lambda c: r'(?:\\text{' + c + r'}|' + c + ')', strings)
        return ''.join(strings)
    