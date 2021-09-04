"""
Copyright (c) 2021 Philipp Scheer
"""


import json
import traceback
from jarvis_sdk import IEntity, CapturedIntentData


class TestSuite():
    def __init__(self) -> None:
        pass

    @staticmethod
    def run(method_or_IEntity: IEntity, data: dict):
        if hasattr(method_or_IEntity, "resolve"):
            TestSuite.run_entity(method_or_IEntity, data)
        elif callable(method_or_IEntity):
            TestSuite.run_endpoint(method_or_IEntity, data)

    @staticmethod
    def run_endpoint(method, data: dict):
        printf(f"TESTING ENDPOINT {method.__name__}")
        printf(f"CAPTURED DATA")
        print(data)
        if not isinstance(data, CapturedIntentData):
            printf("TRANSFORMING INPUT TO CapturedIntentData")
            data = CapturedIntentData(data)
        else:
            printf("INPUT ALREADY CapturedIntentData")
        printf("DEBUG OUTPUT")
        res = method(data)
        printf("RESULT")
        print(res.__dict__() if res else None)
        printf("DONE")
        

    @staticmethod
    def run_entity(Entity: IEntity, data: dict):
        printf(f"TESTING ENTITY {Entity.__name__}")
        printf(f"CAPTURED DATA")
        print(data.get("value", {}).get("value", None))
        printf(f"DEBUG OUTPUT")
        try:
            entity = Entity()
            entity._set_slot_data(data)
            result = entity.resolve()

            printf("RESULT")
            print(json.dumps(result, indent=4, sort_keys=True))
        except Exception:
            traceback.print_exc()
        printf("DONE")


def printf(string, pre = "=", maxlen = 50):
    maxlen -= 2
    if len(string) % 2 != 0:
        string += " "
    real_pre = pre * ((maxlen - len(string)) // 2)
    print(real_pre + " " + string + " " + real_pre)