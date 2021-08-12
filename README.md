## Jarvis SDK

This Jarvis Software Development Kit contains methods for various AI assistant tasks including Intent Parsing


### Documentation


#### Skill

Whenever Jarvis captures a Skill with Intent in a spoken phrase or chat platform, you can execute some code and provide an appropriate response.

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
```