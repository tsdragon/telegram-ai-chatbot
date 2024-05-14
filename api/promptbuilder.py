from lib import load_character_sheet, load_template
import logging

class PromptBuilder:
    def __init__(self, ai_name, template, formatter):
        self.log = logging.getLogger(__name__)
        self.ai_name = ai_name
        self.template = template
        self.formatter = formatter

    def build_prompt(self, user, user_input, memory):
        prompt = []
        self.log.debug("Building prompt...")
        system_message = self.construct_system_message(user, memory.summary)
        system_message = self.formatter.create_message(system_message, role="system")

        prompt.extend(system_message)

        if memory.message_history:
            prompt.extend(memory.message_history)
            
        user_input = self.formatter.create_message(user_input, role="user")
        prompt.extend(user_input)

        return prompt
    
    def construct_system_message(self, user, memory_summary):
        self.log.debug("Constructing system message...")
        self.log.debug(user)
        (user_id, user_name), = user.items()
        self.log.debug(f"User ID: {user_id}, User Name: {user_name}")
        self.log.debug(f"AI Name: {self.ai_name}, Template: {self.template}")
        template = load_template(self.template)
        ai_sheet = load_character_sheet(self.ai_name)
        user_sheet = load_character_sheet(self.ai_name, user_id)

        template = f"{template}\n{ai_sheet}\n{user_sheet}"

        self.log.debug(f"formatting template...")
        system_message = template.format(assistant=self.ai_name, user=user_name)
        self.log.debug(f"{system_message}")

        if memory_summary:
            system_message += f"\nSummary: {memory_summary}"

        self.log.debug('returning system message...')
        return system_message