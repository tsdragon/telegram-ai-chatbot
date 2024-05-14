from groq import Groq
from .basechathandler import BaseChatHandler

class GroqHandler(BaseChatHandler):
    def initialize_client(self):
        return Groq(api_key=self.api_key)