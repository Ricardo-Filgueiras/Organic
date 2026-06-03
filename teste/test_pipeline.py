import sys
import os

# Ensure the root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph.graph_name import app
from langchain_core.messages import HumanMessage

def main():
    print("Iniciando teste do pipeline...")
    
    initial_state = {
        "messages": [HumanMessage(content="Um sofá modular, minimalista, tecido cinza, foco em conforto")]
    }
    
    try:
        final_state = app.invoke(initial_state)
        print("\n=== SUCESSO ===")
        print(f"Normalized Input: {final_state.get('normalized_input')}")
        print(f"Name: {final_state.get('name')}")
        print(f"Subname: {final_state.get('subname')}")
        print(f"Description: {final_state.get('Description')}")
    except Exception as e:
        print("\n=== ERRO ===")
        print(e)

if __name__ == "__main__":
    main()
