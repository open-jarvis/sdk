"""
Copyright (c) 2021 Philipp Scheer
"""


import random
import traceback
from .Entity import Entity, IEntity


class IntentSlotsContainer:
    """Internal class to simplify slot value extraction.  
    You should not call this class"""
    def __init__(self, slots: list) -> None:
        self._slots = slots
    
    def __getattr__(self, key: str):
        try:
            for slot in self._slots:
                if slot.get("slotName", None) == key:
                    if slot.get("resolved", None) is not None:
                        return slot.get("resolved", None)
                    AnyEntity: IEntity = Entity._entities.get(slot.get("entity", None), None)
                    if AnyEntity is None:
                        return slot.get("value", {}).get("value", None)
                    entity = AnyEntity()
                    entity._set_slot_data(slot)
                    return entity.resolve()
            return None
        except Exception:
            for slot in self._slots:
                if slot.get("slotName", None) == key:
                    return slot.get("value", {}).get("value", None)
            return None

    def __list__(self):
        return self._slots

    def __iter__(self):
        return iter(self._slots)


class CapturedIntentData:
    """A wrapper around Intents classified by Jarvis NLU.  
    Exposes some useful functions"""
    def __init__(self, data) -> None:
        """Initialize with the data object obtained by Jarvis NLU.  
        Looks like:  
        ```json
        {
            "input": "How's the weather in New York?",
            "skill": "Weather",
            "intent": "getWeather",
            "probability": 0.963054744983951
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
                    "resolved": "New York"
                }
            ]
        }
        ```
        """
        self.data = data
        assert isinstance(self.data, dict), "Data does not have required format: dict"
        for k in ["input", "skill", "intent", "probability", "slots"]:
            assert k in self.data, f"Data does not have required format: '{k}' missing"

    def __dict__(self):
        return self.data

    def to_json(self):
        """Export CapturedIntentData to json object"""
        return self.data

    def get_slot_value(self, slot_name, default=None):
        """Get the slot value for a given `slot_name`, if `slot_name` could not be found, return the `default` value
        Example:
        ```python
        from jarvis_sdk import Intent, CapturedIntentData

        @Intent.on("Weather", "getWeather")
        def Weather_getWeather(captured_intent_data: CapturedIntentData):
            city = captured_intent_data.get_slot_value("city_name") # city == "New York"
            # or shorter
            city = captured_intent_data.slots.city_name # str or None
        ```
        """
        for slot in self.slots:
            if slot.get("slotName", None) == slot_name:
                return slot.get("resolved", slot.get("value", {}).get("value", None))
        return default
  
    @property
    def skill(self) -> str:
        """Get the skill of the parsed intent, else `None`  
        Example: `"Weather"`"""
        return self.data.get("skill", None)

    @property
    def intent(self) -> str:
        """Get the skill of the parsed intent, else `None`  
        Example: `"getWeather"`"""
        return self.data.get("intent", None)

    @property
    def slots(self) -> IntentSlotsContainer:
        """Get a list of slots of the parsed intent, else `[]`  
        Example:
        ```json
        [{
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
            "resolved": "New York"
        }]
        ```
        """
        return IntentSlotsContainer(self.data.get("slots", []))
    
    @property
    def input(self) -> str:
        """Get a list of slots of the parsed intent, else `""`  
        Example: `"How's the weather in New York?"`
        """
        return self.data.get("input", "")

    @classmethod
    def from_json(cls, data):
        """Load a CapturedIntentData from JSON object
        Example:
        {
            'input': 'wie wild das wetter morgen', 
            'intent': {
                'intentName': 'Wetter$Wetterbericht', 
                'probability': 0.7764818831383247
            }, 'slots': [
                {
                    'range': {
                        'start': 20, 
                        'end': 26
                    }, 
                    'rawValue': 'morgen', 
                    'value': {
                        'kind': 'Custom', 
                        'value': 'morgen'
                    }, 
                    'entity': 'zeiteinheit', 
                    'slotName': 'zeit'
                }
            ]
        }
        """
        if data.get("intent", {}).get("intentName") is None:
            return CapturedIntentData({
                "input": data.get("input"),
                "skill": None,
                "intent": None,
                "probability": data.get("intent", {}).get("probability"),
                "slots": {
                    slot.get("slotName"): {
                        "value": slot.get("value", {}).get("value"),
                        "raw": slot.get("rawValue"),
                        "entity": slot.get("entity")
                    } for slot in data.get("slots", [])
                },
            })
        return CapturedIntentData({
            "input": data.get("input"),
            "skill": data.get("intent", {}).get("intentName").split("$")[0],
            "intent": data.get("intent", {}).get("intentName").split("$")[1],
            "probability": data.get("intent", {}).get("probability"),
            "slots": {
                slot.get("slotName"): {
                    "value": slot.get("value", {}).get("value"),
                    "raw": slot.get("rawValue"),
                    "entity": slot.get("entity")
                } for slot in data.get("slots", [])
            },
        })



class Intent():
    """Whenever Jarvis captures an Intent in a spoken phrase or chat platform, 
    you can execute some code and provide an appropriate response.  
    You'll probably only need the `.on` method"""

    _handlers = {}

    @staticmethod
    def on(skill: str, intent: str):
        """Listen to a captured Intent.  
        Usage:
        ```python
        from jarvis_sdk import Intent, IntentResponse, IntentTextResponses

        @Intent.on("Weather", "getWeather")
        def Weather_getWeather(captured_data):
            # captured_data is an instance of `CapturedIntentData`
            # All you need to do is parse the captured data,
            # call some API endpoints and return a response
            return IntentResponse(
                text = IntentTextResponse([
                    "Temperatures will reach $temperature today.",
                    "It'll be really $temperature_feel outside today."
                ]).apply_values({
                    "$temperature": "89°F",
                    "$temperature_feel": "hot"
                }),
                # The text parameter is mandatory and must be an instance of IntentTextResponses
                # If you don't want to return any text, pass an empty list to the constructor

                speech = IntentSpeechResponse([
                    "Temperatures will reach $temperature today.",
                    "It'll be really $temperature_feel outside today."
                ]).apply_values({
                    "$temperature": "89°F",
                    "$temperature_feel": "hot"
                }), 
                # The speech paramter is optional but recommended.
                # If no `speech` parameter is given, the IntentTextResponse 
                #   will be used as IntentSpeechResponse. 
                # If you want to have different speech responses than text responses, 
                #   you may specify them here

                card = IntentCardResponse(
                    head="Weather Report"
                )
                # The card parameter is optional but recommended.
                # In the case of a weather app it makes sense to provide a IntentCardResponse
                #   so the UI can provide some graphical response (like a weather report) 
            )

        @Intent.on("Weather", "*")
        def Weather_all(captured_data):
            # By using the "*" operator, a listener may be attached to:
            # * all skills and all intents: @Intent.on("*", "*")
            # * all skills and given intents: @Intent.on("*", "getWeather")
            # * given skills and all intents: @Intent.on("Weather", "*")
            # You must not return a IntentResponse object
            # If a IntentResponse object is returned, the skill might not work as expected
            return True
        ```"""
        try:
            def decor(func):
                def wrap(*args, **kwargs):
                    res = func(*args, **kwargs)
                    return res
                id = ''.join(random.choice("0123456789abcdef") for _ in range(64))
                while (skill, intent, id) in Intent._handlers:
                    id = ''.join(random.choice("0123456789abcdef") for _ in range(64))
                Intent._handlers[(skill, intent, id)] = wrap
                return wrap
            return decor
        except Exception as e:
            raise e

    @staticmethod
    def handle(intent_data: CapturedIntentData):
        skill = intent_data.skill
        intent = intent_data.intent
        try:
            endpoints = Intent._get(skill, intent)
            result = (False, None)
            for endpoint in endpoints:
                try:
                    res = endpoint(intent_data)
                    if res is not None:
                        result = (True, res)
                except Exception as e:
                    traceback.print_exc()
            return result
        except Exception as e:
            traceback.print_exc()
            return (False, None)


    @staticmethod
    def _get(skillNameToGet, intentNameToGet):
        """Get matching functions for Skill$intent from handlers dict,  
        else return the default route"""
        endpoints = []
        for (skillName, intentName, id) in Intent._handlers:
            endpoint = Intent._handlers[(skillName, intentName, id)]
            if skillNameToGet == skillName or skillName == "*":
                if intentNameToGet == intentName or intentName == "*":
                    endpoints.append(endpoint)
        if len(endpoints) == 0:
            return [Intent._default_endpoint]
        return endpoints

    @staticmethod
    def _emit(skill: str, intent: str, nlu_result: dict) -> set:
        """Emit a Skill$Intent event with given arguments  
        Returns a tuple with `(True|False, object result)`"""
        raise NotImplementedError("NotImplementedError")
        try:
            endpoints = Intent._get(skill, intent)
            result = None
            captured_intent_data = CapturedIntentData(nlu_result)
            for endpoint in endpoints:
                try:
                    res = endpoint(captured_intent_data)
                except Exception as e:
                    res = e
                    print(f"Exception occured in endpoint {skill}${intent}")
                    traceback.print_exc()
                if isinstance(res, IntentResponse):
                    result = res
            return (True, result)
        except Exception as e:
            return (False, str(e))

    @staticmethod
    def _default_endpoint(*args, **kwargs):
        """This is the default endpoint and gets handled if no function was found for Intent event"""
        raise Exception("Endpoint not found")
