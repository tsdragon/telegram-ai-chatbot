import json
import time
from openai import OpenAI
from .basechathandler import BaseChatHandler
from lib import load_character_sheet

class GPTAssistantHandler(BaseChatHandler):
    def __init__(self, api_key, assistant_id, ai_name, user_threads_file, **kwargs):
        self.assistant_id = assistant_id
        self.user_threads_file = user_threads_file
        super().__init__(api_key, ai_name, None, **kwargs)

    def initialize_client(self):
        return OpenAI(api_key=self.api_key)

    async def get_ai_response(self, user_input, user):
        (user_id, user_name), = user.items()
        thread_id = self.get_thread(user_id)
        try:
            self.log.info("Getting response from OpenAI API")
            response = self.get_openai_response(user_input, thread_id)
            return response
        except Exception as e:
            self.log.error("Error sending message to OpenAI: %s", str(e), exc_info=True)
            raise Exception("An error occurred sending message to OpenAI") from e

    def get_thread(self, user_id):
        user_threads = self.load_user_threads()
        if user_id not in user_threads:
            self.create_thread(user_id)
            user_threads = self.load_user_threads()
        return user_threads[user_id]

    def create_thread(self, user_id):
        self.log.info("No thread found for user %s, creating a new one.", user_id)
        thread = self.client.beta.threads.create()
        user_threads = self.load_user_threads()
        user_threads[user_id] = thread.id
        self.save_user_threads(user_threads)
        self.init_new_thread(user_id)

    def save_user_threads(self, user_threads):
        with open(self.user_threads_file, 'w') as file:
            json.dump(user_threads, file)
            self.log.info("Saved user threads to file: %s", user_threads)

    def init_new_thread(self, user_id):
        thread_id = self.get_thread(user_id)
        try:
            self.log.debug("Initializing new thread: %s", user_id)
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=load_character_sheet(self.ai_name, user_id)
            )
        except Exception as e:
            self.log.error("Error initializing new thread: %s", str(e), exc_info=True)
    
    def get_openai_response(self, user_input, thread_id):
        try:
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )
            run = self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=self.assistant_id)
            self.wait_for_run_completion(self.client, thread_id, run.id)
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            response = messages.data[0].content[0].text.value if messages.data[0].role == "assistant" else "No response."
            return response
        except Exception as e:
            self.log.error("Error getting response from OpenAI: %s", str(e), exc_info=True)
            raise Exception("An error occurred in GPT response") from e

    def wait_for_run_completion(self, client, thread_id, run_id):
        timeout = 60 * 10
        while timeout >= 0:
            timeout -= 1
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.status == "completed":
                break
            time.sleep(1)