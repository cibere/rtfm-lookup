class Filler:
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __getattribute__(self, name: str) -> str:
        if name == "msg":
            return super().__getattribute__(name)

        err = RuntimeError(self.msg)
        setattr(err, "__rtfm_lookup_force_raise__", True)
        raise err
