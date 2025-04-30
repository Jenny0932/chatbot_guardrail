from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
from guardrails.utils import retrieve_context, convert_to_markdown
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import json
from guardrails.input_query_classifier import InputQueryClassifier
from guardrails.groundedness_checker import GroundednessChecker
import pandas as pd
import numpy as np
import torch
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(override=True)
# fix streamlit error for torch classes
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 


# with Guardrail or not
GUARDAIL = True

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
st.title("💬 Bank Product Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI and Bank Product")

client = OpenAI(api_key=OPENAI_API_KEY)
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = FAISS.load_local("data/faiss_index", embeddings, allow_dangerous_deserialization=True)

system_prompt = {"role": "system", "content": "You are a helpful assistant that answers questions about bank products and services.\
          You have access to a knowledge base of bank products. You Must answer the questions based on the knowledge base.\
          Check the context careflully, if you did not find the information from context, say 'I don't know'."}

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        system_prompt
    ]

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"**User:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Assistant:** {message['content']}")
        else:
            pass


# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if prompt is not None:
                # RAG retrieval
                retrieved_contexts, retrieved_contexts_string = retrieve_context(prompt, vector_store=vector_store, top_k=3)
                # build the Prompt for the LLM
                query = f"Chat history: {str(st.session_state.messages)}\n\n\
                          Context: {retrieved_contexts_string}\n\n\
                          User: {prompt}\n\
                          Assistant:"

                if GUARDAIL:
                    # check user input query for Guardrail
                    # LLM input query classifier
                    # read input_class_list from csv file
                    input_class_info = pd.read_csv("data/input_class_data.csv")
                    input_class_list = input_class_info["input_class_name"].tolist()
                    input_classifier = InputQueryClassifier(class_type = input_class_list, 
                                                            class_detail = convert_to_markdown(input_class_info),
                                                            custom_model_path = "model/query_classifier_model")
                                    
                    llm_input_class = input_classifier.llm_input_classification(prompt)
                    logging.info(f"Input class from LLM for '{prompt}': {llm_input_class}")
                    # Bert text classification for Guardrail
                    bert_input_class = input_classifier.bert_query_classifier(prompt)
                    logging.info(f"BERT:Predicted class for '{prompt}': {bert_input_class}")

                     # Bart text classification for Guardrail
                    bart_input_class = input_classifier.bart_query_classifier(prompt)
                    logging.info(f"BART:Predicted class for '{prompt}': {bart_input_class}")

                    if llm_input_class not in ['service', 'product'] and bert_input_class not in ['service', 'product']:
                        st.write("Filtered Query. Sorry, I cannot answer this question. Please rephrase your question.")
                        message = {"role": "assistant", "content": "Sorry, I cannot answer this question. Please rephrase your question."}
                        st.session_state.messages.append(message)
                    else:
                        st.write("Retrieving context with Guardrail...")
                        # Use Guardrail to validate the response
                        response = client.chat.completions.create(model="gpt-4o-mini",
                                        messages=[system_prompt, 
                                                    {"role": "user", "content": query}])
                        ai_msg = response.choices[0].message.content
                        logging.info(f"AI response for '{prompt}': {ai_msg}")

                        # check AI response for Guardrail
                        # Initialize the GroundednessChecker
                        checker = GroundednessChecker(vector_db=vector_store)
                        # Check groundedness for each example
                        groundedness_result = checker.check_grounding(prompt, ai_msg, retrieved_contexts_string)
                        logging.info(f"Groundedness result for '{prompt}': {groundedness_result}")

                        # semantic similarity check for Guardrail
                        retrieved_contexts_list = [context['content'] for context in retrieved_contexts]
                        similarity = [context['score'] for context in retrieved_contexts]
                        # average similarity score
                        similarity_max = np.max(similarity) if similarity else 0.0
                        logging.info(f"Similarity score list for '{prompt}': {similarity}")
                        logging.info(f"Similarity score for '{prompt}': {similarity_max}")

                        if groundedness_result == False or similarity_max < 0.5:
                            st.write("Filtered AI Response. Sorry, I cannot find the information from the knowledge base.Please rephrase your question.")
                            message = {"role": "assistant", "content": "Sorry, I cannot find the information from the knowledge base.Please rephrase your question."}
                            st.session_state.messages.append(message)
                        else:
                            st.write(ai_msg)
                            message = {"role": "assistant", "content": ai_msg}
                            st.session_state.messages.append(message)
                
                else:
                    # no Guardrail check, just use the LLM to generate the response
                    st.write("Retrieving context without Guardrail...")
                    response = client.chat.completions.create(model="gpt-4o-mini",
                                                            messages=[system_prompt, 
                                                                        {"role": "user", "content": query}])
                    ai_msg = response.choices[0].message.content
                    st.write(ai_msg)
                    message = {"role": "assistant", "content": ai_msg}
                    st.session_state.messages.append(message)
                
                # save user and assistant messages to a dictionary json file
                with open("data/chat_history.json", "w") as f:
                    json.dump(st.session_state.messages[1:], f, indent=4) 
            else:
                st.write("Please enter a question.")

            
