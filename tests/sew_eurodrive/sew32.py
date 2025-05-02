from pathlib import Path

from msl.loadlib import Server32


class SEWEuroDrive32(Server32):
    def __init__(self, host: str, port: int) -> None:
        path = Path(__file__).parent / "FirstDll.dll"
        super().__init__(path, "clr", host, port)
        self.first_class = self.lib.FirstDll.FirstClass()  # pyright: ignore[reportUnannotatedClassAttribute]

    def do_something(self, value: float) -> float:
        # returns "value/3/2"
        result: float = self.first_class.DoSometing(value)  # cSpell: ignore Someting
        return result
