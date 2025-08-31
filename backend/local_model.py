from transformers import pipeline
import sys
import json

def main():
    # Load the question-answering pipeline
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

    # Read input from stdin
    input_data = json.loads(sys.stdin.read())
    document_text = input_data.get("documentText", "")
    user_query = input_data.get("userQuery", "")

    # Perform question answering
    try:
        result = qa_pipeline(question=user_query, context=document_text)
        print(result['answer'])
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
