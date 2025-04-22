# guardrails/utils.py

import json

def load_knowledge_base(path):
    with open(path, 'r') as f:
        return json.load(f)
    

# convert input_class_info into markdown
def convert_to_markdown(input_class_info):
    # Convert the dictionary to a markdown string
    markdown_str = ""
    for key, value in input_class_info.items():
        if isinstance(value, list):
            value = ", ".join(value)
        markdown_str += f"**{key}**: {value}\n"
    return markdown_str


# ===============================
# Define a Simple Retrieval Function
# ===============================

def retrieve_context(query, vector_store, top_k=3, source_filter=None):
    """
    Retrieve the most relevant contexts for a given query.

    Args:
        query (str): The query string.
        top_k (int): Number of top results to retrieve.
        source_filter (dict): Optional metadata filter (e.g., {"source": "news"}).

    Returns:
        list: List of retrieved contexts with their similarity scores.
    """
    results = vector_store.similarity_search_with_relevance_scores(query, k=top_k, filter=source_filter)
    contexts = []
    for res, score in results:
        contexts.append({"content": res.page_content, "metadata": res.metadata, "score": score})

    # sort contexts by score in descending order
    contexts.sort(key=lambda x: x['score'], reverse=True)
    
    # convert contexts to string format
    contexts_string = [f"Content: {c['content']}, Metadata: {c['metadata']}, Score: {c['score']}" for c in contexts]

    return contexts, contexts_string

