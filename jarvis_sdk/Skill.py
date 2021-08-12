"""
Copyright (c) 2021 Philipp Scheer
"""


import time
import random


class Skill():
    """Whenever Jarvis captures a Skill with Intent in a spoken phrase or chat platform, 
    you can execute some code and provide an appropriate response.  
    You'll probably only need the .on method"""

    @staticmethod
    def on(skill: str, intent: str):
        """Listen to a captured Skill and Intent.  
        Use like:
        ```
        from jarvis_sdk import Skill

        @Skill.on("Weather", "getWeather")
        def Weather_getWeather(captured_data):
            # captured_data is an instance of [`CapturedIntentData`](#CapturedIntentData)
            # process the query in here and return a list of possible responses. The Jarvis AI will try to  
            # pick the best reply based on mood, talkactiveness and much more
            return [
                "It's sunny",
                "It's really sunny, temperatures reaching 34°C"
            ]

        @Skill.on("Weather", "*")
        def Weather_all(captured_data):
            # you can also attach a listener for all intents on all skill.
            # Make sure you return None or nothing, because everything else
            # is being treated as response and is presented to the user
            return None
        ```"""
        try:
            def decor(func):
                def wrap(*args, **kwargs):
                    res = func(*args, **kwargs)
                    return res
                id = ''.join(random.choice("0123456789abcdef") for _ in range(64))
                while (skill, intent, id) in Skill.handlers:
                    id = ''.join(random.choice("0123456789abcdef") for _ in range(64))
                Skill.handlers[(skill, intent, id)] = wrap
                return wrap
            return decor
        except Exception as e:
            raise e

    @staticmethod
    def get_slot_value(output: dict, slot_name: str, orElse=None, raw=False):
        for slot in output["slots"]:
            if slot["slotName"] == slot_name:
                return slot["rawValue"] if raw else slot["value"]["value"]
        return orElse


    handlers = {}
    """A dictionary containing all registered Skill$Intent handlers"""

    @staticmethod
    def _get(skillNameToGet, intentNameToGet):
        """Get matching functions for Skill$intent from handlers dict,  
        else return the default route"""
        endpoints = []
        for (skillName, intentName, id) in Skill.handlers:
            endpoint = Skill.handlers[(skillName, intentName, id)]
            if skillNameToGet == skillName or skillNameToGet == "*":
                if intentNameToGet == intentName or intentNameToGet == "*":
                    endpoints.append(endpoint)
        if len(endpoints) == 0:
            return [Skill._default_endpoint]
        return endpoints

    @staticmethod
    def _emit(skill: str, intent: str, *args, **kwargs) -> set:
        """Emit a Skill$Intent event with given arguments  
        Returns a tuple with `(True|False, object result)`"""
        try:
            endpoints = Skill._get(skill, intent)
            result = None
            for endpoint in endpoints:
                try:
                    res = endpoint(*args, **kwargs)
                except Exception as e:
                    res = e
                if res is not None:
                    result = res
            return (True, result)
        except Exception as e:
            return (False, str(e))

    @staticmethod
    def _default_endpoint(*args, **kwargs):
        """This is the default endpoint and gets handled if no function was found for Skill event"""
        raise Exception("Endpoint not found")




class CapturedIntentData:
    """A wrapper around Intents classified by Jarvis NLU.  
    Exposes some useful functions"""
    def __init__(self, data) -> None:
        """Initialize with the data object obtained by Jarvis NLU. Looks like:  
        ```json
        {
            "input": "How's the weather in New York?",
            "intent": {
                "intentName": "Weather$getCurrentWeather",
                "probability": 0.963054744983951
            },
            "slots": [
                {
                    "range": {
                        "start": 21,
                        "end": 29
                    },
                    "rawValue": "New York",
                    "value": {
                        "kind": "Custom",
                        "value": "New York"
                    },
                    "entity": "city",
                    "slotName": "city_name"
                }
            ]
        }
        ```
        """
        self.data = data
        assert isinstance(self.data, dict), "Data does not have required format: dict"
        for k in ["input", "intent", "slots"]:
            assert k in self.data, f"Data does not have required format: '{k}' missing"

    @property
    def skill(self):
        intent = self.data.get("intent", {}).get("intentName", None)
        if intent is None: return None
        return intent.split("$")[0]

    @property
    def intent(self):
        intent = self.data.get("intent", {}).get("intentName", None)
        if intent is None: return None
        return intent.split("$")[1]
    
    @property
    def slots(self):
        return self.data.get("slots", [])
    
    @property
    def input(self):
        return self.data.get("input", "")
    
    def get_slot_value(self, slot_name, default=None):
        for slot in self.slots:
            if slot.get("slotName", None) == slot_name:
                return slot.get("value", {}).get("value", default)
        return default