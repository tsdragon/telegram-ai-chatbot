import tiktoken
import logging
import textwrap
from .messagehandler import MessageHandler
from lib import load_template

# Centralize default values
DEFAULT_MODEL = 'gpt-4o'
DEFAULT_TEMPERATURE = 0.4
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 16384

class Memory:
    def __init__(self, ai_name, llm=None, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, top_p=DEFAULT_TOP_P, max_tokens=DEFAULT_MAX_TOKENS):
        self._initialize(ai_name, llm, model, temperature, top_p, max_tokens)
        self.message_history = []
        self.summary = None

    def reinit(self, ai_name, llm, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, top_p=DEFAULT_TOP_P, max_tokens=DEFAULT_MAX_TOKENS):
        self._initialize(ai_name, llm, model, temperature, top_p, max_tokens)

    def _initialize(self, ai_name, llm, model, temperature, top_p, max_tokens):
        self.log = logging.getLogger(__name__)
        self.ai_name = ai_name
        self.client = llm
        self.default_params = {
            'model': model,
            'temperature': temperature,
            'top_p': top_p
        }
        self.max_tokens = max_tokens
        self.messages = MessageHandler()
        self.max_history = self.max_tokens // 2

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['log']
        del state['ai_name']
        del state['client']
        del state['default_params']
        del state['max_tokens']
        del state['messages']
        del state['max_history']
        return state

    def update(self, messages, user):
        self.log.debug(f"Updating memory with messages: {messages}")
        self.message_history.extend(messages)
        messages_token_count = self.messages_token_counts(self.message_history)
        self.log.info(f"Updated memory for user {user}, messages token count: {messages_token_count}")
        if self.summary or messages_token_count > self.max_history:
            self.update_summary(user)

    def update_summary(self, user):
        (user_id, user_name), = user.items()
        self.log.debug(f"Updating summary with message history.")
        new_lines = self.message_history[:2]
        self.message_history = self.message_history[2:]
        self.log.debug(f"New lines: {new_lines}")
        prompt = self.construct_summary_prompt(new_lines, user_name)
        params = {'messages': prompt}
        params.update(self.default_params)
        
        try:
            response = self.client.chat.completions.create(**params)
            self.log.debug(f"Response: {response}")
            self.summary = response.choices[0].message.content
            self.log.debug(f"New summary: {self.summary}")
            self.log.info(f"Updated summary for user {user_id}, summary token count: {self.token_count(self.summary)}")
        except Exception as e:
            self.log.error(f"Error getting response: {e}")

    def construct_summary_prompt(self, new_lines, user_name):
        self.log.debug(f"Constructing summary prompt with new lines: {new_lines}")
        formatted_new_lines = ""
        for line in new_lines:
            line['role'] = user_name if line['role'] == 'user' else self.ai_name
            formatted_new_lines += f"{line['role']}: {line['content']}\n"
        
        prompt_template = load_template("summary_prompt")
        prompt = prompt_template.format(summary=self.summary, formatted_new_lines=formatted_new_lines)
        prompt_message = self.messages.create_message(prompt, role="system")
        self.log.debug(f"Constructed summary prompt: {prompt_message}")
        return prompt_message

    def messages_token_counts(self, messages):
        self.log.debug("Aggregating text from messages to calculate tokens.")
        text = "".join(f"{message['role']}: {message['content']}\n" for message in messages)
        self.log.debug(f"Aggregated text: {text}")
        total_tokens = self.token_count(text)
        self.log.debug(f"Total token count: {total_tokens}")
        return total_tokens

    def token_count(self, text):
        self.log.debug(f"Counting tokens for text: {text}")
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(text))
        except Exception as e:
            self.log.error(f"Failed to count tokens: {e}")
            num_tokens = 0
        self.log.debug(f"Token count: {num_tokens}")
        return num_tokens