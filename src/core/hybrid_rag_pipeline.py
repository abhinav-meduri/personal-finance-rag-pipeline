#!/usr/bin/env python3
"""
Hybrid RAG Pipeline - Best Practice Implementation
Tiered approach: QA data first, then document fallback, then base LLM knowledge.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from langchain_community.llms import LlamaCpp
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

class HybridRAGPipeline:
    """
    Hybrid RAG Pipeline implementing best practices:
    1. QA Data Search (fast, accurate, context-aware)
    2. Document Search (comprehensive, detailed)
    3. Base LLM Knowledge (fallback)
    """
    
    def __init__(self, 
                 model_path: str = "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                 qa_data_path: str = "comprehensive_qa_data.json",
                 qa_vector_db: str = "qa_vector_db",
                 doc_vector_db: str = "vector_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 verbose: bool = False):
        
        self.model_path = Path(model_path)
        self.qa_data_path = Path(qa_data_path)
        self.qa_vector_db = Path(qa_vector_db)
        self.doc_vector_db = Path(doc_vector_db)
        self.embedding_model = embedding_model
        self.verbose = verbose
        
        # Set up logging based on verbosity
        if verbose:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.llm = None
        self.qa_vector_store = None
        self.doc_vector_store = None
        self.qa_data = None
        
        # Load components
        self._load_llm()
        self._load_qa_data()
        self._load_vector_stores()
    
    def _load_llm(self):
        """Load the Mistral-7b model"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        if self.verbose:
            self.logger.info(f"Loading LLM from {self.model_path}")
        
        # Set up callback manager based on verbosity
        if self.verbose:
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        else:
            callback_manager = CallbackManager([])
        
        self.llm = LlamaCpp(
            model_path=str(self.model_path),
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            callback_manager=callback_manager,
            verbose=self.verbose,
            n_ctx=4096,
            n_gpu_layers=0,
        )
        
        if self.verbose:
            self.logger.info("LLM loaded successfully")
    
    def _load_qa_data(self):
        """Load structured Q&A data"""
        if self.qa_data_path.exists():
            with open(self.qa_data_path, 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)
            if self.verbose:
                self.logger.info(f"Loaded {self.qa_data['metadata']['total_qa_pairs']} Q&A pairs")
        else:
            self.logger.warning(f"QA data file not found: {self.qa_data_path}")
            self.qa_data = None
    
    def _load_vector_stores(self):
        """Load both QA and document vector stores"""
        embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load QA vector store if it exists
        if self.qa_vector_db.exists():
            self.qa_vector_store = Chroma(
                persist_directory=str(self.qa_vector_db),
                embedding_function=embeddings
            )
            if self.verbose:
                self.logger.info("QA vector store loaded")
        else:
            self.logger.warning(f"QA vector store not found: {self.qa_vector_db}")
            self.qa_vector_store = None
        
        # Load document vector store if it exists
        if self.doc_vector_db.exists():
            self.doc_vector_store = Chroma(
                persist_directory=str(self.doc_vector_db),
                embedding_function=embeddings
            )
            if self.verbose:
                self.logger.info("Document vector store loaded")
        else:
            self.logger.warning(f"Document vector store not found: {self.doc_vector_db}")
            self.doc_vector_store = None
    
    def search_qa_data(self, question: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search Q&A data for relevant answers"""
        if not self.qa_vector_store:
            return []
        
        try:
            docs = self.qa_vector_store.similarity_search_with_score(question, k=k)
            results = []
            
            for doc, score in docs:
                # Parse Q&A content from document
                content = doc.page_content
                metadata = doc.metadata
                
                # Extract question and answer from content
                lines = content.split('\n')
                qa_context = ""
                qa_question = ""
                qa_answer = ""
                
                for line in lines:
                    if line.startswith("Context:"):
                        qa_context = line.replace("Context:", "").strip()
                    elif line.startswith("Question:"):
                        qa_question = line.replace("Question:", "").strip()
                    elif line.startswith("Answer:"):
                        qa_answer = line.replace("Answer:", "").strip()
                
                results.append({
                    'type': 'qa_pair',
                    'question': qa_question,
                    'answer': qa_answer,
                    'context': qa_context,
                    'category': metadata.get('category', 'Unknown'),
                    'source': metadata.get('source', 'Unknown'),
                    'similarity_score': float(score),
                    'content': content
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching QA data: {e}")
            return []
    
    def search_documents(self, question: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search document chunks for relevant information"""
        if not self.doc_vector_store:
            return []
        
        try:
            docs = self.doc_vector_store.similarity_search_with_score(question, k=k)
            results = []
            
            for doc, score in docs:
                results.append({
                    'type': 'document_chunk',
                    'title': doc.metadata.get('title', 'Unknown'),
                    'url': doc.metadata.get('url', ''),
                    'content': doc.page_content,
                    'similarity_score': float(score),
                    'metadata': doc.metadata
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    def get_base_llm_answer(self, question: str) -> str:
        """Get answer from base LLM knowledge (fallback)"""
        prompt = f"""<s>[INST] You are a helpful financial advisor assistant. Answer the following question based on your general knowledge of financial planning and investing principles. If you're not confident about the answer, say so.

Question: {question}

Provide a helpful, accurate response based on general financial knowledge. [/INST]"""
        
        return self.llm(prompt)
    
    def ask_question(self, question: str, use_hybrid: bool = True) -> Dict[str, Any]:
        """Ask a question using the hybrid RAG approach"""
        if self.verbose:
            self.logger.info(f"Processing question: {question}")
        
        result = {
            'question': question,
            'timestamp': datetime.now().isoformat(),
            'sources_used': [],
            'answer': '',
            'confidence': 'low',
            'method': 'base_llm'
        }
        
        # Tier 1: Search Q&A data (fastest, most accurate)
        if self.qa_vector_store and use_hybrid:
            if self.verbose:
                self.logger.info("Tier 1: Searching Q&A data...")
            qa_results = self.search_qa_data(question, k=2)
            
            if qa_results and qa_results[0]['similarity_score'] > 0.7:
                best_qa = qa_results[0]
                result['answer'] = best_qa['answer']
                result['confidence'] = 'high'
                result['method'] = 'qa_data'
                result['sources_used'] = [{
                    'type': 'qa_pair',
                    'question': best_qa['question'],
                    'context': best_qa['context'],
                    'category': best_qa['category'],
                    'source': best_qa['source'],
                    'similarity_score': best_qa['similarity_score']
                }]
                
                if self.verbose:
                    self.logger.info(f"Found high-confidence QA answer (score: {best_qa['similarity_score']:.4f})")
                return result
        
        # Tier 2: Search document chunks (comprehensive)
        if self.doc_vector_store and use_hybrid:
            if self.verbose:
                self.logger.info("Tier 2: Searching document chunks...")
            doc_results = self.search_documents(question, k=3)
            
            if doc_results:
                # Combine document context
                context_parts = []
                sources = []
                
                for doc in doc_results:
                    context_parts.append(f"Source: {doc['title']}\n{doc['content']}")
                    sources.append({
                        'type': 'document_chunk',
                        'title': doc['title'],
                        'url': doc['url'],
                        'similarity_score': doc['similarity_score']
                    })
                
                context = "\n\n".join(context_parts)
                
                # Generate answer using document context
                prompt = f"""<s>[INST] You are a helpful financial advisor assistant. Use the following context to answer the user's question. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the context provided. [/INST]"""
                
                result['answer'] = self.llm(prompt)
                result['confidence'] = 'medium'
                result['method'] = 'document_search'
                result['sources_used'] = sources
                
                if self.verbose:
                    self.logger.info(f"Generated answer from document search")
                return result
        
        # Tier 3: Base LLM knowledge (fallback)
        if self.verbose:
            self.logger.info("Tier 3: Using base LLM knowledge...")
        result['answer'] = self.get_base_llm_answer(question)
        result['confidence'] = 'low'
        result['method'] = 'base_llm'
        result['sources_used'] = []
        
        if self.verbose:
            self.logger.info("Used base LLM knowledge as fallback")
        return result
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the system"""
        info = {
            'model_path': str(self.model_path),
            'embedding_model': self.embedding_model,
            'qa_data_available': self.qa_data is not None,
            'qa_vector_store_available': self.qa_vector_store is not None,
            'doc_vector_store_available': self.doc_vector_store is not None,
            'method': 'hybrid_rag'
        }
        
        if self.qa_data:
            info['qa_pairs_count'] = self.qa_data['metadata']['total_qa_pairs']
            info['qa_categories'] = self.qa_data['metadata']['categories']
        
        if self.qa_vector_store:
            info['qa_vector_count'] = self.qa_vector_store._collection.count()
        
        if self.doc_vector_store:
            info['doc_vector_count'] = self.doc_vector_store._collection.count()
        
        return info

def interactive_mode(verbose: bool = False):
    """Run the hybrid RAG pipeline in interactive mode"""
    try:
        # Initialize the hybrid RAG pipeline
        if verbose:
            print("Initializing Hybrid RAG Pipeline...")
        rag = HybridRAGPipeline(verbose=verbose)
        
        # Display system info
        system_info = rag.get_system_info()
        print("\n" + "="*60)
        print("HYBRID RAG PIPELINE")
        print("="*60)
        print(f"Method: {system_info['method']}")
        print(f"QA Data Available: {system_info['qa_data_available']}")
        print(f"QA Vector Store: {system_info['qa_vector_store_available']}")
        print(f"Document Vector Store: {system_info['doc_vector_store_available']}")
        
        if system_info['qa_data_available']:
            print(f"QA Pairs: {system_info['qa_pairs_count']}")
        
        print("="*60)
        print("\nType 'quit' to exit, 'info' for system info, or ask a question!")
        print("\nExample questions:")
        print("- What are the 2024 Roth IRA contribution limits?")
        print("- How should I allocate my assets?")
        print("- What is a Traditional IRA?")
        print("- How do I start investing?")
        print("\n" + "-"*60)
        
        while True:
            try:
                user_input = input("\nYour question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'info':
                    info = rag.get_system_info()
                    print(f"\nSystem Info: {info}")
                    continue
                
                if not user_input:
                    continue
                
                # Get answer using hybrid approach
                print("\nGenerating answer...")
                result = rag.ask_question(user_input)
                
                print(f"\nAnswer: {result['answer']}")
                print(f"Method: {result['method']} (confidence: {result['confidence']})")
                
                if result['sources_used']:
                    print(f"\nSources:")
                    for i, source in enumerate(result['sources_used'], 1):
                        if source['type'] == 'qa_pair':
                            print(f"{i}. Q&A: {source['question']} ({source['category']})")
                        else:
                            print(f"{i}. Document: {source['title']} (score: {source['similarity_score']:.4f})")
                
                print("\n" + "-"*60)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                if verbose:
                    print(f"Error processing question: {e}")
                else:
                    print(f"Error: {e}")
    
    except Exception as e:
        if verbose:
            print(f"Error initializing hybrid RAG pipeline: {e}")
        else:
            print(f"Error: {e}")

def main():
    """Main function"""
    import sys
    
    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    interactive_mode(verbose=verbose)

if __name__ == "__main__":
    main() 