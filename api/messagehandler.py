import logging
    
class MessageHandler:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.response_type = list
        self.required_keys = ["role", "content"]
        self.valid_roles = ["system", "user", "assistant"]
        self.role_type = str,
        self.content_type = str

    def create_message(self, input_message, role=None):
        self.log.debug(f"Creating message with input: {input_message}")
        if isinstance(input_message, self.response_type):
            message = input_message
        elif role and isinstance(input_message, self.content_type):
            role_key = self.required_keys[0]
            content_key = self.required_keys[1]
            message = [{role_key: role, content_key: input_message}]

        else:
            raise ValueError("Invalid input format. Provide a list of message dicts, a single dict, or a string with a role.")
        
        self.validate_messages(message)
        return message

    def validate_messages(self, messages):
        if not isinstance(messages, self.response_type):
            raise TypeError(f"Messages must be a {self.response_type.__name__}")
        for message in messages:
            self.validate_single_message(message)

    def validate_single_message(self, message):
        if not isinstance(message, dict):
            raise TypeError("Message must be a dictionary.")
        if not all(key in message for key in self.required_keys):
            raise ValueError(f"Message must contain all of {self.required_keys}.")
        if message['role'] not in self.valid_roles:
            raise ValueError(f"Role must be one of {self.valid_roles}")
        if not isinstance(message['content'], self.content_type):
            raise TypeError(f"Content must be a {self.content_type.__name__}")
        if not isinstance(message['role'], self.role_type):
            raise TypeError(f"Role must be a {self.role_type.__name__}.")