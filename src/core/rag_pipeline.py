#!/usr/bin/env python3
"""
RAG Pipeline for Bogleheads Wiki using Mistral-7b
Combines vector database retrieval with LLM generation
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from langchain_community.llms import LlamaCpp
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.callbacks import CallbackManager
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BogleheadsRAGPipeline:
    def __init__(self, 
                 model_path: str = "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                 vector_db_dir: str = "vector_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_path = Path(model_path)
        self.vector_db_dir = Path(vector_db_dir)
        self.embedding_model = embedding_model
        
        # Initialize components
        self.llm = None
        self.vector_store = None
        self.qa_chain = None
        
        # Load components
        self._load_llm()
        self._load_vector_store()
        self._setup_qa_chain()
    
    def _load_llm(self):
        """Load the Mistral-7b model"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        logger.info(f"Loading LLM from {self.model_path}")
        
        # Set up callback manager for streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        # Initialize LlamaCpp with Mistral-7b
        self.llm = LlamaCpp(
            model_path=str(self.model_path),
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            callback_manager=callback_manager,
            verbose=True,
            n_ctx=4096,  # Context window
            n_gpu_layers=0,  # Use CPU for compatibility
        )
        
        logger.info("LLM loaded successfully")
    
    def _load_vector_store(self):
        """Load the vector store"""
        if not self.vector_db_dir.exists():
            raise FileNotFoundError(f"Vector database directory not found: {self.vector_db_dir}")
        
        logger.info(f"Loading vector store from {self.vector_db_dir}")
        
        # Load embeddings model
        embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load ChromaDB vector store
        self.vector_store = Chroma(
            persist_directory=str(self.vector_db_dir),
            embedding_function=embeddings
        )
        
        logger.info("Vector store loaded successfully")
    
    def _setup_qa_chain(self):
        """Set up the QA chain with custom prompt"""
        # Custom prompt template for finance questions
        prompt_template = """<s>[INST] You are a helpful financial advisor assistant with expertise in Bogleheads investing philosophy. 
        Use the following context to answer the user's question. If you cannot answer the question based on the context, 
        say so and provide general financial advice based on Bogleheads principles.

        Context:
        {context}

        Question: {question}

        Answer the question in a clear, helpful manner. If the context contains specific information, use it. 
        If not, provide general guidance based on Bogleheads investing principles of low-cost, diversified, 
        long-term investing. [/INST]"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        logger.info("QA chain set up successfully")
    
    def ask_question(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Ask a question and get an answer with sources"""
        logger.info(f"Processing question: {question}")
        
        # Get relevant documents
        docs = self.vector_store.similarity_search_with_score(question, k=k)
        
        # Format context from documents
        context_parts = []
        sources = []
        
        for i, (doc, score) in enumerate(docs):
            context_parts.append(f"Source {i+1} ({doc.metadata.get('title', 'Unknown')}):\n{doc.page_content}")
            sources.append({
                'title': doc.metadata.get('title', 'Unknown'),
                'url': doc.metadata.get('url', ''),
                'similarity_score': float(score),
                'content': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using the LLM
        logger.info("Generating answer...")
        
        # Create the full prompt
        full_prompt = f"""<s>[INST] You are a helpful financial advisor assistant with expertise in Bogleheads investing philosophy. 
        Use the following context to answer the user's question. If you cannot answer the question based on the context, 
        say so and provide general financial advice based on Bogleheads principles.

        Context:
        {context}

        Question: {question}

        Answer the question in a clear, helpful manner. If the context contains specific information, use it. 
        If not, provide general guidance based on Bogleheads investing principles of low-cost, diversified, 
        long-term investing. [/INST]"""
        
        # Generate response
        response = self.llm(full_prompt)
        
        # Format the result
        result = {
            'question': question,
            'answer': response,
            'sources': sources,
            'timestamp': datetime.now().isoformat(),
            'context_used': context[:500] + "..." if len(context) > 500 else context
        }
        
        return result
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents without generating an answer"""
        docs = self.vector_store.similarity_search_with_score(query, k=k)
        
        results = []
        for doc, score in docs:
            results.append({
                'title': doc.metadata.get('title', 'Unknown'),
                'url': doc.metadata.get('url', ''),
                'content': doc.page_content,
                'similarity_score': float(score),
                'metadata': doc.metadata
            })
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the system"""
        stats = self.vector_store._collection.count()
        
        return {
            'model_path': str(self.model_path),
            'vector_db_path': str(self.vector_db_dir),
            'embedding_model': self.embedding_model,
            'total_documents': stats,
            'model_type': 'Mistral-7b-Instruct',
            'context_window': 4096
        }

def interactive_mode():
    """Run the RAG pipeline in interactive mode"""
    try:
        # Initialize the RAG pipeline
        logger.info("Initializing Bogleheads RAG Pipeline...")
        rag = BogleheadsRAGPipeline()
        
        # Display system info
        system_info = rag.get_system_info()
        print("\n" + "="*60)
        print("BOGLEHEADS RAG PIPELINE")
        print("="*60)
        print(f"Model: {system_info['model_type']}")
        print(f"Total documents: {system_info['total_documents']}")
        print(f"Embedding model: {system_info['embedding_model']}")
        print("="*60)
        print("\nType 'quit' to exit, 'search' to search documents only, or ask a question!")
        print("\nExample questions:")
        print("- What are the basics of bond investing?")
        print("- How should I allocate my assets?")
        print("- What is a Roth IRA?")
        print("- How do I start investing?")
        print("\n" + "-"*60)
        
        while True:
            try:
                user_input = input("\nYour question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'search':
                    query = input("Search query: ").strip()
                    if query:
                        results = rag.search_documents(query, k=3)
                        print(f"\nFound {len(results)} relevant documents:")
                        for i, result in enumerate(results, 1):
                            print(f"\n{i}. {result['title']} (score: {result['similarity_score']:.4f})")
                            print(f"   URL: {result['url']}")
                            print(f"   Content: {result['content'][:200]}...")
                    continue
                
                if not user_input:
                    continue
                
                # Get answer
                print("\nGenerating answer...")
                result = rag.ask_question(user_input)
                
                print(f"\nAnswer: {result['answer']}")
                
                print(f"\nSources:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"{i}. {source['title']} (score: {source['similarity_score']:.4f})")
                    print(f"   URL: {source['url']}")
                
                print("\n" + "-"*60)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing question: {e}")
                print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Error initializing RAG pipeline: {e}")
        print(f"Error: {e}")

def main():
    """Main function"""
    interactive_mode()

if __name__ == "__main__":
    main() 