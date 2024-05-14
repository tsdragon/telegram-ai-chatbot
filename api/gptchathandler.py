from openai import OpenAI
from .basechathandler import BaseChatHandler

class GPTChatHandler(BaseChatHandler):
    def initialize_client(self):
        return OpenAI(api_key=self.api_key)