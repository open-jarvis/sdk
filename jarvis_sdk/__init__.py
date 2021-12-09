"""
## List of modules:

* [Intent](jarvis_sdk/Intent.html)
    * [IntentResponse](jarvis_sdk/Intent.html#IntentResponse)
    * [IIntentResponse](jarvis_sdk/Intent.html#IIntentResponse)
    * [ResolvedIntentResponse](jarvis_sdk/Intent.html#ResolvedIntentResponse)
    * [IntentTextResponse](jarvis_sdk/Intent.html#IntentTextResponse)
    * [IntentSpeechResponse](jarvis_sdk/Intent.html#IntentSpeechResponse)
    * [IntentCardResponse](jarvis_sdk/Intent.html#IntentCardResponse)
    * [Intent](jarvis_sdk/Intent.html#Intent)
    * [Slots](jarvis_sdk/Intent.html#Slots)
* [Entity](jarvis_sdk/Entity.html)
    * [IEntity](jarvis_sdk/Entity.html#IEntity)
* [TestSuite](jarvis_sdk/TestSuite.html)
* [Storage](jarvis_sdk/Storage.html)
    * [Session](jarvis_sdk/Storage.html#Session)
* [Api](jarvis_sdk/Api.html)
* [Connection](jarvis_sdk/Connection.html)
* [Router](jarvis_sdk/Routing.html)
"""


from .nlu.Intent import Intent, Slots
# from .nlu.Entity import Entity, IEntity

from .plugin.Tasks import Task

from .captures.AudioCapture import AudioCapture

from .TestSuite import TestSuite
from .Storage import Storage, Session
from .Api import Api
from .Connection import Connection
from .Logging import Logger
from .Highway import Highway
from .Ressources import Ressources

from .Webserver import Webserver, Router



# TODO: add more sessions
session = Session()
