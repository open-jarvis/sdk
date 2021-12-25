"""
Copyright (c) 2021 Philipp Scheer
"""


import os
import json
import random
import shutil


DOCUMENT_IDENTIFIER = "$id"
REVISION_IDENTIFIER = "$rev"


class LocalDatabase:
    PATH = None
    def __init__(self, path) -> None:
        if path is None:
            path = LocalDatabase.PATH
        assertType(path, "directory")
        self.path = path

    def table(self, name):
        """Either generate a new table or retrieve the existing one"""
        assertType(f"{self.path}/{name}", "directory")
        return LocalTable(f"{self.path}/{name}")


class LocalTable:
    def __init__(self, path):
        assertType(path, "directory")
        self.path = path
    
    def get(self, docId):
        assertType(f"{self.path}/{docId}", "file")
        return json.load(open(f"{self.path}/{docId}", "r"))
        
    def all(self):
        l = []
        for f in os.listdir(self.path):
            if os.path.isfile(f"{self.path}/{f}"):
                l.append(json.load(open(f"{self.path}/{f}", "r")))
        return l

    def insert(self, newDocument):
        assert isinstance(newDocument, dict)

        if DOCUMENT_IDENTIFIER not in newDocument:
            newDocument[DOCUMENT_IDENTIFIER] = self._unique_id()

        if REVISION_IDENTIFIER not in newDocument:
            newDocument[REVISION_IDENTIFIER] = 0

        fname = f"{self.path}/{newDocument.get(DOCUMENT_IDENTIFIER)}"
        assertType(fname, "file")

        oldDocument = self.get(newDocument.get(DOCUMENT_IDENTIFIER))
        if oldDocument.get(REVISION_IDENTIFIER, -1) > newDocument[REVISION_IDENTIFIER]:
            raise LocalDatabaseException(f"Revision number is not newer, old={oldDocument[REVISION_IDENTIFIER]}, new={newDocument[REVISION_IDENTIFIER]}")
        if oldDocument.get(REVISION_IDENTIFIER, -1) == newDocument[REVISION_IDENTIFIER]:
            newDocument[REVISION_IDENTIFIER] += 1
        json.dump(newDocument, open(fname, "w"))

    def find(self, mangoQuery: dict):
        a = self.all()
        r = []
        for el in a:
            for key, val in mangoQuery.items():
                if key in el:
                    if isinstance(val, dict):
                        for k2, v2 in val.items():
                            if k2 in ["$eq", "$lt", "$gt"]:
                                try:
                                    if k2 == "$eq":
                                        if v2 == el.get(key):
                                            r.append(el)
                                    elif k2 == "$lt":
                                        if el.get(key) < v2:
                                            r.append(el)
                                    elif k2 == "$gt":
                                        if el.get(key) > v2:
                                            r.append(el)
                                except TypeError:
                                    pass
                            else:
                                if v2 == el.get(key):
                                    r.append(el)
                    else:
                        if val == el.get(key):
                            r.append(el)
        return r

    def delete(self, documentOrId):
        if isinstance(documentOrId, dict):
            documentOrId = documentOrId.get("$id")
        if os.path.isfile(f"{self.path}/{documentOrId}"):
            os.unlink(f"{self.path}/{documentOrId}")

    def drop(self):
        shutil.rmtree(self.path)

    def _unique_id(self):
        id = ''.join(random.choices("0123456789abcdef", k=32))
        while os.path.exists(f"{self.path}/{id}"):
            id = ''.join(random.choices("0123456789abcdef", k=32))
        return id


class LocalDatabaseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def assertType(path, file_or_directory, default_value="{}"):
    try:
        if file_or_directory == "file":
            if os.path.exists(path):
                if os.path.isfile(path):
                    pass
                else:
                    raise Exception("Path cannot be directory")
            else:
                with open(path, "w") as f:
                    if default_value:
                        f.write(default_value)
        if file_or_directory == "directory":
            assert not os.path.isfile(path), "Path cannot be a file"
            if not os.path.exists(path):
                os.makedirs(path)
    except Exception as e:
        raise LocalDatabaseException(str(e))

