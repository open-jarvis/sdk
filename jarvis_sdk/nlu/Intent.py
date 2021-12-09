"""
Copyright (c) 2021 Philipp Scheer
"""



class Slots:
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


class Intent:
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
        """Export Intent to json object"""
        return self.data

    def get_slot_value(self, slot_name, default=None):
        """Get the slot value for a given `slot_name`, if `slot_name` could not be found, return the `default` value
        Example:
        ```python
        from jarvis_sdk import Intent, Intent

        @Intent.on("Weather", "getWeather")
        def Weather_getWeather(captured_intent_data: Intent):
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
    def slots(self) -> Slots:
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
        return Slots(self.data.get("slots", []))
    
    @property
    def input(self) -> str:
        """Get a list of slots of the parsed intent, else `""`  
        Example: `"How's the weather in New York?"`
        """
        return self.data.get("input", "")

    @classmethod
    def from_json(cls, data):
        """Load a Intent from JSON object
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
            return Intent({
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
        return Intent({
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

    @classmethod
    def from_values(cls, input, skill, intent, probability, slots):
        return Intent({
            "input": input,
            "skill": skill,
            "intent": intent,
            "probability": probability,
            "slots": slots
        })

