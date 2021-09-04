"""
## List of modules:

* [Intent](jarvis_sdk/Intent.html)
    * [IntentResponse](jarvis_sdk/Intent.html#IntentResponse)
    * [IIntentResponse](jarvis_sdk/Intent.html#IIntentResponse)
    * [ResolvedIntentResponse](jarvis_sdk/Intent.html#ResolvedIntentResponse)
    * [IntentTextResponse](jarvis_sdk/Intent.html#IntentTextResponse)
    * [IntentSpeechResponse](jarvis_sdk/Intent.html#IntentSpeechResponse)
    * [IntentCardResponse](jarvis_sdk/Intent.html#IntentCardResponse)
    * [CapturedIntentData](jarvis_sdk/Intent.html#CapturedIntentData)
    * [IntentSlotsContainer](jarvis_sdk/Intent.html#IntentSlotsContainer)
* [Entity](jarvis_sdk/Entity.html)
    * [IEntity](jarvis_sdk/Entity.html#IEntity)
* [TestSuite](jarvis_sdk/TestSuite.html)
* [Session](jarvis_sdk/Session.html)
* [Api](jarvis_sdk/Api.html)
"""


from .Intent import Intent, IntentResponse, ResolvedIntentResponse, IIntentResponse, IntentTextResponse, IntentSpeechResponse, IntentCardResponse, CapturedIntentData, IntentSlotsContainer
from .Entity import Entity, IEntity
from .TestSuite import TestSuite
from .Session import Session
from .Api import Api

# TODO: add more sessions
session = Session()
