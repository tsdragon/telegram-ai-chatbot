import asyncio
import aiofiles
import logging
import pickle
from .memory import Memory
from .messagehandler import MessageHandler
from .promptbuilder import PromptBuilder

class BaseChatHandler:
    def __init__(self, api_key, ai_name, template, model=None, max_tokens=512, temperature=1.0, top_p=1.0, **kwargs):
        self.api_key = api_key
        self.ai_name = ai_name
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.user_threads = {}
        self.log = logging.getLogger(__name__)
        self.messages = MessageHandler()
        self.prompt_builder = PromptBuilder(ai_name, template, self.messages)
        self.client = self.initialize_client()
        self.memory_client = self.client
        self.load_user_threads()

    def initialize_client(self):
        raise NotImplementedError("Subclasses should implement this method")

    async def save_user_threads(self):
        try:
            async with aiofiles.open(f'./logs/{self.ai_name}/user_threads.pkl', 'wb') as file:
                await file.write(pickle.dumps(self.user_threads))
        except Exception as e:
            self.log.error(f"Error saving user threads: {e}")

    def load_user_threads(self):
        try:
            with open(f'./logs/{self.ai_name}/user_threads.pkl', 'rb') as file:
                loaded_user_threads = pickle.load(file)
            for user_id, state in loaded_user_threads.items():
                memory = Memory(ai_name=self.ai_name)
                memory.__setstate__(state, llm=self.memory_client)
                self.user_threads[user_id] = memory
        except FileNotFoundError:
            self.user_threads = {}
        except Exception as e:
            self.log.error(f"Error loading user threads: {e}")
            self.user_threads = {}

    def update_memory(self, user, messages):
        (user_id, user_name), = user.items()
        memory = self.get_user_thread(user_id)
        memory.update(messages, user)
        self.user_threads[user_id] = memory

    def get_user_thread(self, user_id):
        return self.user_threads.get(user_id, Memory(self.ai_name, self.memory_client))

    async def reset_thread(self, user_id):
        if user_id in self.user_threads:
            del self.user_threads[user_id]
        await self.save_user_threads()

    async def get_ai_response(self, user_input, user):
        if not self.model:
            raise ValueError("Model is not set.")
        self.log.debug(user)
        (user_id, user_name), = user.items()
        user_input = self.messages.create_message(user_input, role="user")
        prompt = self.prompt_builder.build_prompt(user, user_input, self.get_user_thread(user_id))
        
        try:
            response = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p
                )
            )
            self.log.debug(f"Response: {response}")
        except Exception as e:
            self.log.error(f"Error getting response: {e}")
            return "An error occurred."
        
        response = response.choices[0].message
        response = self.messages.create_message(response.content, response.role)
        user_input.extend(response)
        self.log.debug(f"Updating memory for user {user_id}")
        self.update_memory(user, user_input)
        self.log.debug(f"Saving memory for user {user_id}")
        await self.save_user_threads()
        self.log.debug(f"Returning response to telegram bot.")
        return str(response[0]['content'])