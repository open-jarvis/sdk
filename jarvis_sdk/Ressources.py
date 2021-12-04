"""
Copyright (c) 2021 Philipp Scheer
"""


import random


class Ressources:
    def __init__(self) -> None:
        self.items = {}

    def set(self, resId, value):
        if resId not in self.items: self.items[resId] = []
        self.items[resId].append(value)

    def get(self, resId, *args, getRandom: bool = True):
        _args = []
        for i in range(len(args)):
            if args[i] is None or isinstance(args[i], bool):
                _args.append("success" if args[i] else "failed")
            else:
                _args.append(str(args[i]))
        print(_args)
        if len(_args) > 0:
            resId += "::" + "::".join(_args)
        if getRandom: return random.choice(self.items.get(resId, [None]))
        return self.items.get(resId, None)

    @classmethod
    def load(cls, filename: str):
        res = Ressources()
        with open(filename, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith("#"): continue
                if line == "": continue
                if len(line.split(" ")) < 2: continue
                resId = line.split(" ")[0].strip()
                resVal = " ".join(line.split(" ")[1:]).strip()
                res.set(resId, resVal)
        return res

    def __str__(self) -> str:
        return f"Ressources{{items={self.items}}}"