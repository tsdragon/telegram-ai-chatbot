### Keys and tokens for the bot ###
api_key = 'your-api-key-here'
telegram_token = 'your-telegram-token-here'
pyrogram_api_id = 'your-pyrogram-api-id-here'
pyrogram_api_hash = 'your-pyrogram-api-hash-here'

### LLM configurations ###
#assistant_id = 'your-openai-assistant-id-here' #if using the openai assistants api
model='gpt-3.5-turbo' # Required if not using assistants api. Model to use, can be any model available in the API, check api documentation for more details
#max_tokens=512 # Maximum tokens to generate, can be any number between 1 and 4096, default is 512
#temperature=1 # Temperature for sampling, can be any number between 0 and 1, default is 1
#top_p=1 # Top P value for nucleus sampling, can be any number between 0 and 1, default is 1
#memory_max_tokens=16384 # Maximum tokens to use for memory, can be any number between 1 and and your model's max contecxt length, default is 16384
#memory_model='gpt-4o' # Model to use for memory, defaults to the same model as the main model

allowed_users = { # Dictionary of allowed users and their respective user ids, user IDs can be found by messaging https://t.me/userinfobot
    'SampleUser': 123456789,
    'SampleUser2': 987654321
}

### Naming and logging configurations ###
ai_name = 'SampleBot' # Name of the AI
#user_threads_file = 'sample_user_threads_filename.json' # file to store user threads in, required when using the assistant handler
log_directory = './logs/SampleBot/'
template = 'sample_template'

### Handler class ###
handler_class = 'GPTChatHandler'
#handler_class = 'GPTAssistantHandler'
#handler_class = 'GroqHandler'