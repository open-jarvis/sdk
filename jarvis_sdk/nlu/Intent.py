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

    @property
    def probability(self) -> float:
        return self.data.get("probability", None)

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
    def from_values(cls, input: str = None, skill: str = None, intent: str = None, probability: float = None, slots: list = []):
        return Intent({
            "input": input,
            "skill": skill,
            "intent": intent,
            "probability": probability,
            "slots": slots
        })
    

    ## Jarvis Skills
    _skill_handlers = []
    
    @staticmethod
    def on(skill, intent):
        def decor(func):
            Intent._skill_handlers.append({
                "skill": skill,
                "intent": intent,
                "callback": func
            })
            def wrap(*args, **kwargs):
                res = func(*args, **kwargs)
                return res
            return wrap
        return decor

    @staticmethod
    def execute(skill, intent, audioCapture, context):
        for el in Intent._skill_handlers:
            if el.get("skill") == skill and el.get("intent") == intent:
                cb = el.get("callback")
                if callable(cb):
                    return cb(audioCapture, context)
        return None


    ## Jarvis Questions
    _question_handlers = []

    @staticmethod
    def question(skill, intent, key):
        def decor(func):
            Intent._question_handlers.append({
                "skill": skill,
                "intent": intent,
                "key": key,
                "callback": func
            })
            def wrap(*args, **kwargs):
                res = func(*args, **kwargs)
                return res
            return wrap
        return decor

    @staticmethod
    def ask(skill, intent, key, context):
        for el in Intent._question_handlers:
            if el.get("skill") == skill and el.get("intent") == intent and el.get("key") == key:
                cb = el.get("callback")
                if callable(cb):
                    return cb(context)
        return None



    @staticmethod
    def require(key: str, audioCapture, context, atTimestamp=None, contextKeys: list=[]):
        # Try to get the key directly from the AudioCapture object
        if audioCapture.intent is not None and audioCapture.intent.get_slot_value(key) is not None:
            return audioCapture.intent.get_slot_value(key)

        # Next, look into the context object, if there is a valid key
        k = context.get(key, None, atTimestamp)
        if k is None:
            for ck in contextKeys:
                k = context.get(ck, None, atTimestamp)
                if k is not None:
                    return k
        else:
            return k

        # If we cannot find the data, we need to ask the user for additional information
        if audioCapture.intent is not None:
            # If there is an intent in the AudioCapture
            return Intent.ask(audioCapture.intent.skill, audioCapture.intent.intent, key, context)
        else:
            # Else, return none. This should never be the case
            return None # TODO: what can we do here?


#########

class IEntity():
    def __init__(self) -> None:
        self.data = {}

    def _set_slot_data(self, slot_data: dict):
        self.data = slot_data

    def resolve(self):
        """Resolve an entity value to be computer readable  
        Usage:
        ```python
        from jarvis_sdk import Entity, IEntity

        class datetime(IEntity):
            def __init__(self) -> None:
                super().__init__()

            def resolve(self):
                # A new `self.data` dict is now available with these values:
                # {
                #     "range": {
                #         "start": 7,
                #         "end": 17
                #     },
                #     "rawValue": "in 2 days",
                #     "value": {
                #         "kind": "Custom",
                #         "value": "in 2 days"
                #     },
                #     "entity": "datetime",
                #     "slotName": "time"
                # }
                # Your job is to convert this input into something machine readable like a timestamp
                string = self.data.get("value", {}).get("value", "").lower()
                return time.time()
        
        Entity.register(datetime)
        # Don't forget to register your entity.
        # Intent handlers (via @Intent.on()) are now able to access your entity and resolve text values
        ```
        """
        pass


class Entity():
    """Register entities to process information generated by Jarvis NLU"""

    def __init__(self) -> None:
        pass

    _entities = {}

    @staticmethod
    def register(entity_class: IEntity):
        """Register your entity class  
        Usage:
        ```python
        from jarvis_sdk import Entity, IEntity

        class test(IEntity):
            def __init__(self) -> None:
                super().__init__()

            def resolve(self):
                return "something useful"
        
        Entity.register(test)
        ```"""
        Entity._entities[entity_class.__name__] = entity_class
