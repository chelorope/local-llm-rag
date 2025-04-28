from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from typing import Dict, Any
from pydantic import BaseModel, Field

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

class Joke(BaseModel):
    """Understand joke"""
    setup: str = Field(description="question to set up a joke")
    punchline: str = Field(description="answer to resolve the joke")

def get_chain() -> Runnable:
    """Return a chain that generates jokes based on a topic."""
    prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
    model = ChatOllama(model="llama3.2").bind_tools([Joke])
    parser = JsonOutputParser(pydantic_object=Joke)
    return prompt | model # | parser
