# Telegram AI Chatbot

A Python-based Telegram chatbot integrated with multiple AI services including OpenAI's GPT and Groq. Just something basic I use to play around with chatbots in telegram.

## Features

- Supports OpenAI GPT models with both chat completions and assistants apis and Groq models.
- Persistent user memory using both a rolling summary and a chat history window.
- Customizable prompts and templates.


## Getting Started

### Prerequisites

- Python 3.7+
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/telegram-ai-chatbot.git
    cd telegram-ai-chatbot
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. **Create your configuration file:**

    Copy the sample configuration file and edit it with your own API keys and settings.
    !!!DO NOT PUT YOUR KEYS IN THE SAMPLE CONFIG AND ACCIDETALLY UPLOAD IT TO GIT!!!

    ```bash
    cp configs/sample_config.py configs/my_config.py
    ```

    Edit `configs/my_config.py` with your own API keys, user IDs, and other settings.

2. **Create your instruction templates:**

    Ensure your templates and prompt files are set up as per your requirements. You can use the sample templates provided in the `instructions/` directory.

### Running the Bot

Run the Telegram bot with your configuration file:

```bash
python telegram_bot.py my_config