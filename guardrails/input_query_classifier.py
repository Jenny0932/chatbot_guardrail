from openai import OpenAI
import os
import json
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
import torch
from transformers import pipeline
from dotenv import load_dotenv
load_dotenv('.env', override=True)  

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)


class InputQueryClassifier:
    def __init__(self, class_type=[], class_detail = '', custom_model_path = "model/query_classifier_model"):
        # A guardrail is a combination of multiple policies configured for prompts \
        # and response including; content filters, denied topics, sensitive information filters, 
        # word filters, and image content filters.
        self.class_type = class_type
        self.class_detail = class_detail
        self.custom_model_path = custom_model_path

    def filter_sensitive_words(self, query):
        # convert the query to lowercase for case-insensitive matching
        query = query.lower()
        # Define a list of sensitive words to filter out
        sensitive_words = ["investment", "money"]
        
        # Replace sensitive words with asterisks
        for word in sensitive_words:
            query = query.replace(word, '*' * len(word))
        
        return query

    def llm_input_classification(self, query, model="gpt-4o-mini"):
 
        # filter sensitive words from the query
        query = self.filter_sensitive_words(query)       
        prompt = f"""
        Classify the User query into one of the class list.\n\
        ##Class list##: {self.class_type}
        \n\n\
        ##Detail of the class list##: \n\
        {self.class_detail}\n\
        ##User query##: "{query}"

        ##Objective##: Classify the user query into one of the Class list. \n\
        Based on the different class, the chatbot can make decision to 
         - answer user query using relevant knowledge base, \
         - block user query and return general response 'Sorry, I can not answer your question.'\
         
        ##Detailed Instructions##: 
        1. Read the user query carefully.\n\
        2. Classify the user query into one of the class list.\n\
        3. If the user query does not match any of the class list, return "None".\n\
        ##Response format##: {{"input_class": "class_name"}}\n\
        """
        tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": "input_classification",
                            "description": "Function to classify user query into different class.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    # input class is one of the class list
                                    "input_class": {
                                        "type": "string",
                                        "enum": self.class_type,
                                        "description": "The class name of the user query."
                                    }
                                },
                                "required": ["input_class"]
                            }
                        }
                    }
                ]
        tool_choices = {"type": "function", "function": {"name": "input_classification"}}
        res = client.chat.completions.create(
            model= model,
            messages=[{"role": "user", "content": prompt}],
            tools = tools,
            tool_choice= tool_choices
        )
        return json.loads(res.choices[0].message.tool_calls[0].function.arguments)['input_class']
    



    # test the model with a sample text
    def bert_query_classifier(self, text):
        # Load the tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(self.custom_model_path)
        model = AutoModelForSequenceClassification.from_pretrained(self.custom_model_path)

        # Tokenize the input text
        inputs = tokenizer(text, return_tensors="pt")

        # Perform inference
        with torch.no_grad():
            logits = model(**inputs).logits

        # Get the predicted class from the logits
        predicted_class_id = logits.argmax().item()
        return model.config.id2label[predicted_class_id]
    

    def bart_query_classifier(self, text):
        """
        Classify the input text using BART zero-shot-classification pipeline.
        """
        # Initialize the zero-shot-classification pipeline with BART
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

        # Use the class_type as candidate labels
        candidate_labels = self.class_type

        # Perform classification
        result = classifier(text, candidate_labels)

        # Return the label with the highest score
        return result['labels'][0]