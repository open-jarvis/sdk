"""
Copyright (c) 2021 Philipp Scheer
"""


import json
import random
import traceback
from typing import Any
from .Entity import Entity, IEntity



class Intent():
    """Whenever Jarvis captures an Intent in a spoken phrase or chat platform, 
    you can execute some code and provide an appropriate response.  
    You'll probably only need the `.on` method"""

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

    _handlers = {}

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
        try:
            endpoints = Intent._get(skill, intent)
            result = None
            captured_intent_data = CapturedIntentData(nlu_result) # might be faster to only compute this once if there are cpu-heavy tasks inside later on
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


class IIntentResponse():
    def __init__(self) -> None:
        pass


class IntentTextResponse(IIntentResponse):
    """Class to handle and format text responses for Intent requests."""

    def __init__(self, responses: list) -> None:
        """Initalize a new instance with a list of possible responses"""
        super().__init__()
        self.responses = responses

    def apply_values(self, value_dict: dict):
        """Apply a dictionary of values to the response list.  
        Usage:
        ```python
        from jarvis_sdk import IntentTextResponse

        responses = [
            "Temperatures will reach $temperature today.",
            "It'll be really $temperature_feel outside today."
        ]
        responses_formatted = IntentTextResponse(responses).apply_values({
            "$temperature": "89°F",
            "$temperature_feel": "hot"
        })
        # Note: .apply_values() returns the `self` object to keep code short and clear

        print(responses_formatted)
        IntentTextResponse(responses=[
            "Temperatures will reach 89°F today.",
            "It'll be really hot outside today."
        ])
        ```"""
        def _apply_values(sentence: str):
            for key, value in value_dict.items():
                sentence.replace(f"${key}", value)
                # turns "$Hello Buddy", { Hello: Hi } into -> "Hi Buddy"
            return sentence
        self.responses = list(map(_apply_values, self.responses))
        return self

    @staticmethod
    def load(dict_of_responses: dict):
        """Load a dictionary of responses and convert all arrays to instances of IntentTextResponse  
        Usage:
        ```python
        from jarvis_sdk import Intent
        
        responses = {
            "getWeather": {
                "sunny": [
                    "It'll be sunny today",
                    "Cloud coverage is only $cloud_coverage"
                ],
                "rain": [
                    "You should take an umbrella with you",
                    "It'll start raining at $rain_start_time"
                ]
            }
        }
        
        IntentTextResponse.load(responses)
        # Note: the existing dict will be overwritten, so no need to assign to variable
        {
            "getWeather": {
                "sunny": IntentTextResponse(responses=[
                    "It'll be sunny today",
                    "Cloud coverage is only $cloud_coverage"
                ]),
                "rain": IntentTextResponse(responses=[
                    "You should take an umbrella with you",
                    "It'll start raining at $rain_start_time"
                ])
            }
        }
        ```"""
        def _handle_dict(d: dict):
            for k, v in d.items():
                if isinstance(v, dict):
                    d[k] = _handle_dict(v)
                elif isinstance(v, list):
                    d[k] = IntentTextResponse(v)
                else:
                    d[k] = v
            return d
        return _handle_dict(dict_of_responses)


class IntentSpeechResponse(IIntentResponse):
    def __init__(self) -> None:
        super().__init__()
        self.responses = []


class IntentCardResponse(IIntentResponse):
    def __init__(self) -> None:
        super().__init__()



class IntentResponse():
    """A container for all different response types"""
    def __init__(self, text: IntentTextResponse=None, speech: IntentSpeechResponse=None, card: IntentCardResponse=None) -> None:
        """
        Usage:
        ```python
        IntentResponse(
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
        ```
        """
        assert text is None   or isinstance(text,   IntentTextResponse),   "text has to be None or instance of IntentTextResponse"
        assert speech is None or isinstance(speech, IntentSpeechResponse), "speech has to be None or instance of IntentSpeechResponse"
        assert card is None   or isinstance(card,   IntentCardResponse),   "text has to be None or instance of IntentCardResponse"
        self.text = text
        self.speech = speech
        self.card = card
    
    def pick_results(self, function) -> dict:
        """Let a function pick results.  
        This function should pick the best response based on the user input"""
        return ResolvedIntentResponse(**{
            "text": function(self.text) if isinstance(self.text, IntentTextResponse) else None,
            "speech": function(self.speech) if isinstance(self.speech, IntentSpeechResponse) else None,
            "card": self.card,
        })
    
    @classmethod
    def single_text(cls, txt):
        return cls(text=IntentTextResponse([txt]))

    @classmethod
    def single_speech(cls, speech):
        return cls(speech=IntentSpeechResponse([speech]))

    @classmethod
    def single_card(cls, **args):
        return cls(card=IntentCardResponse(**args))

    @classmethod
    def empty(cls):
        return cls()


class ResolvedIntentResponse():
    """Resolved intent responses"""
    def __init__(self, text: IntentTextResponse=None, speech: IntentSpeechResponse=None, card: IntentCardResponse=None) -> None:
        assert text   is None or isinstance(text,   IntentTextResponse),   "text has to be None or instance of IntentTextResponse"
        assert speech is None or isinstance(speech, IntentSpeechResponse), "speech has to be None or instance of IntentSpeechResponse"
        assert card   is None or isinstance(card,   IntentCardResponse),   "text has to be None or instance of IntentCardResponse"
        self.text = text
        self.speech = speech
        self.card = card
    
    def __dict__(self):
        return {
            "text": self.text,
            "speech": self.speech,
            "card": self.card
        }

    def to_json(self):
        return json.dumps(self.__dict__())

    @classmethod
    def from_json(cls, obj):
        return cls(**obj)



class CapturedIntentData:
    """A wrapper around Intents classified by Jarvis NLU.  
    Exposes some useful functions"""
    def __init__(self, data) -> None:
        """Initialize with the data object obtained by Jarvis NLU.  
        Looks like:  
        ```json
        {
            "input": "How's the weather in New York?",
            "intent": {
                "intentName": "Weather$getWeather",
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

    def to_json(self):
        """Export CapturedIntentData to json string"""
        return json.dumps(self.data)
    
    @classmethod
    def from_json(cls, data):
        """Load a CapturedIntentData from json string"""
        return cls(data)

    @property
    def skill(self) -> str:
        """Get the skill of the parsed intent, else `None`  
        Example: `"Weather"`"""
        intent = self.data.get("intent", {}).get("intentName", None)
        if intent is None: return None
        return intent.split("$")[0]

    @property
    def intent(self) -> str:
        """Get the skill of the parsed intent, else `None`  
        Example: `"getWeather"`"""
        intent = self.data.get("intent", {}).get("intentName", None)
        if intent is None: return None
        return intent.split("$")[1]
    
    @property
    def slots(self) -> list:
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
                return slot.get("value", {}).get("value", default)
        return default


class IntentSlotsContainer:
    """Internal class to simplify slot value extraction.  
    You should not call this class"""
    def __init__(self, slots: list) -> None:
        self._slots = slots
    
    def __getattr__(self, key: str):
        for slot in self._slots:
            if slot.get("slotName", None) == key:
                AnyEntity: IEntity = Entity._entities.get(slot.get("entity", None), None)
                if AnyEntity is None:
                    return slot.get("value", {}).get("value", None)
                entity = AnyEntity()
                entity._set_slot_data(slot)
                print("entity", entity, entity.resolve)
                return entity.resolve()
        return None

    def __list__(self):
        return self._slots

    def __iter__(self):
        return iter(self._slots)

