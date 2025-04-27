"""This is a template for a custom chain.

Edit this file to implement your chain logic.
"""

from langchain.chat_models.openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from typing import Dict, Any

joke_func = {
    "name": "joke",
    "description": "A joke",
    "parameters": {
        "type": "object",
        "properties": {
            "setup": {"type": "string", "description": "The setup for the joke"},
            "punchline": {
                "type": "string",
                "description": "The punchline for the joke",
            },
        },
        "required": ["setup", "punchline"],
    },
}

def get_chain() -> Runnable:
    """Return a chain that generates jokes based on a topic."""
    prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
    model = ChatOpenAI().bind(functions=[joke_func], function_call={"name": "joke"})
    parser = JsonOutputFunctionsParser()
    return prompt | model | parser
