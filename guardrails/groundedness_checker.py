from openai import OpenAI
import os
from difflib import SequenceMatcher
from guardrails.utils import retrieve_context
import json
from dotenv import load_dotenv
load_dotenv('.env',override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)


class GroundednessChecker:
    def __init__(self, vector_db, similarity_threshold=0.7):
        self.knowledge_base = vector_db
        self.similarity_threshold = similarity_threshold

    def check_grounding(self, query, response, context_string, model="gpt-4o-mini"):

        #context, context_string = retrieve_context(query, self.knowledge_base)


        prompt = f'''
        You are tasked with verifying whether an AI chatbot’s response is grounded in the provided product knowledge base.

        Definitions:
        - "Grounded" means that factual claims, instructions, or key information in the response are supported by the provided context.
        - "Ungrounded" means that the response introduces information that is missing, inconsistent, incorrect, or not supported by the context.

        Please be extremely strict:  
        - If **important detail** is unsupported by the context, mark the response as "False".
        - Minor paraphrasing that keeps the same meaning is acceptable.
        - Speculation, assumptions, hallucination, or information beyond the context is not allowed.

        Given:
        - User query: {query}
        - Product knowledge base context: {context_string}
        - AI chatbot response: "{response}"

        Task:
        - Carefully read the chatbot response and the context.
        - Compare the information closely.
        - Answer "True" if the response is grounded in the context; otherwise, answer "False".

        Return only one word: **True** or **False**.
        '''

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "check_groundedness",
                    "description": (
                        "Evaluate whether the AI chatbot's response is grounded in the provided context. "
                        "Mark as 'True' only if factual claim and important detail in the response is supported by the context, "
                        "without any added, missing, or incorrect information. Otherwise, mark as 'False'."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "grounded": {
                                "type": "boolean",
                                "description": (
                                    "True if the AI response is grounded in the provided context with no unsupported claims. "
                                    "False if the response is ungrounded, speculative, or inconsistent with the context."
                                )
                            }
                        },
                        "required": ["grounded"]
                    }
                }
            }
        ]

        tool_choices = {"type": "function", "function": {"name": "check_groundedness"}}
        res = client.chat.completions.create(
            model= model,
            messages=[{"role": "user", "content": prompt}],
            tools = tools,
            tool_choice= tool_choices
        )
        return json.loads(res.choices[0].message.tool_calls[0].function.arguments)['grounded']