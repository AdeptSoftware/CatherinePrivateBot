# https://cloud.google.com/dialogflow/docs/quick/api
from dialogflow_v2.proto.session_pb2 import TextInput, QueryInput, QueryParameters
from dialogflow_v2                   import SessionsClient
import os

# ======== ========= ========= ========= ========= ========= ========= =========

class DialogFlowAgent:
    def __init__(self):
        self._client = None
        self._path   = None
        self._cfg    = None

    def initialize(self, cfg):
        if self._client is not None:
            return True
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cfg["src"]

        self._cfg    = cfg
        self._client = SessionsClient()
        self._path   = self._client.session_path(cfg["project"], cfg["session"])
        return True

    def detect(self, text):
        t_input  = TextInput(text=text, language_code=self._cfg["lang"])
        q_input  = QueryInput(text=t_input)
        q_params = QueryParameters(time_zone=self._cfg["timezone"])
        res = self._client.detect_intent(self._path, q_input, q_params)
        if not res.query_result.action:
            return None
        return {
            "score":  res.query_result.intent_detection_confidence,
            "text":   res.query_result.fulfillment_text,
            "action": res.query_result.action
        }

# ======== ========= ========= ========= ========= ========= ========= =========
