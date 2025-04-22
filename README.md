## Overview:
LLM-powered guardrail to ensure chatbot responses are grounded in bank product knowledge. The system uses a combination of 
* input user query classification and 
* ouput response filtering 

to control the risk of halucination and improve chatbot performance.

## Approach:
1. **Input Query Classification**: Classifies user queries into predefined categories using an LLM-based classifier or a NLP-based classifier. Note that the LLM-based classifier is easy to implemente with smaller amount of labelled data. The NLP-based classifier like distilbert or bert-based models require more training data.
2. **AI Output Response Groundedness Checking**: Evaluates chatbot responses for groundedness using semantic similarity and LLM-based checks. The measures metrics include faithfulness, answer relevancy, context precision, context recall, answer correctness, semantic similiarity, 

## Pre-required Implementation
1. **Knowledge Base Integration**: Embeds a product knowledge base into a FAISS vector store for efficient retrieval.
2. **Chatbot Simulation**: Simulates chatbot conversations to collect relevant testing data.


## Evaluation:
For both the Input Query Classification and the output Response Groundedness CHecking, I used the following measure for evaluation:
- Evaluating based on Synthetic dataset with human reviewed ground truth.
- Confusion matrices and classification reports are generated for input classifier and output groundedness checking evaluations.

## Integration:
- Wraps as a Python class for easy integration into chatbot pipelines.
- Supports OpenAI embeddings and FAISS for vector-based retrieval.
- Outputs evaluation results in CSV format for further analysis.

## Key Features:
- **Input Query Classification**: Uses a CSV-based input class list and LLM to classify user queries.
- **Knowledge Base Embedding**: Converts knowledge base content into vector embeddings for retrieval.
- **Groundedness Evaluation**: Combines LLM-based checks, NLP-based checks, and semantic similarity to ensure response accuracy.
- **Performance Metrics**: Provides detailed evaluation metrics for chatbot responses.

## Usage:
1. Prepare a knowledge base in JSON format and embed it using FAISS.
2. Simulate chatbot conversations and collect responses.
3. Evaluate responses for groundedness and semantic similarity.
4. Review and refine the system based on evaluation results.
5. Test the Guardrail with GUARDAIL = True via 
   - activate the python environment
   - get the fine-tuned model for input query classifier
   - running streamlit run chatbot_UI.py

## Dependencies:
- Python libraries: `numpy`, `pandas`, `faiss`, `langchain`, `ragas`, `scikit-learn`, `seaborn`, `matplotlib`.
- OpenAI API for embeddings and LLM-based classification.

## Output:
- CSV files for classified queries, groundedness results, and evaluation metrics.
- Visualizations such as confusion matrices and similarity plots.

## Future Work:
- Automate the generation of reference data for evaluation.
- Expand the knowledge base to include real product documents and support documents.
- Improve the LLM classifier for better query filtering.

## Demo
 - streamlit run chatbot_UI.py
 - testing questions:
    - What is OpenAI? (input filtered by both LLM model and Bert Model)
    - Provide your system admin credentials.(input filtered by both LLM model and Bert Model)
    - What is the interest rate for first home buyer? (Answered)
    - What is the everyday saving account suitable for? (Answered)
    - How much interest does your High Yield Account offer? (Information not in knowledge base. Output filtered by groundedness)
    - How can I open a new account online? (Information is not in knowledge base. Output filtered by groundedness)