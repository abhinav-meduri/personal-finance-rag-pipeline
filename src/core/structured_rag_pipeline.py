#!/usr/bin/env python3
"""
Structured RAG Pipeline
Uses structured Q&A data to avoid context confusion in RAG systems.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import argparse

from langchain_community.llms import LlamaCpp
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class StructuredRAGPipeline:
    def __init__(self, 
                 model_path: str = "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                 qa_data_path: str = "structured_qa_data.json",
                 vector_db_path: str = "structured_vector_db"):
        self.model_path = model_path
        self.qa_data_path = qa_data_path
        self.vector_db_path = vector_db_path
        self.qa_data = None
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        
    def load_qa_data(self) -> Dict:
        """Load structured Q&A data."""
        if not os.path.exists(self.qa_data_path):
            raise FileNotFoundError(f"Q&A data file not found: {self.qa_data_path}")
            
        with open(self.qa_data_path, 'r', encoding='utf-8') as f:
            self.qa_data = json.load(f)
            
        print(f"Loaded {self.qa_data['metadata']['total_qa_pairs']} Q&A pairs")
        print(f"Categories: {', '.join(self.qa_data['metadata']['categories'])}")
        return self.qa_data
    
    def create_documents_from_qa(self) -> List[Document]:
        """Convert Q&A pairs to LangChain documents with proper context."""
        documents = []
        
        for qa_pair in self.qa_data['qa_pairs']:
            # Create a document with clear context
            content = f"Context: {qa_pair['context']}\n\nQuestion: {qa_pair['question']}\n\nAnswer: {qa_pair['answer']}"
            
            metadata = {
                'source': qa_pair['source'],
                'category': qa_pair['category'],
                'context': qa_pair['context'],
                'question': qa_pair['question'],
                'doc_id': qa_pair['doc_id']
            }
            
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc)
            
        print(f"Created {len(documents)} documents from Q&A pairs")
        return documents
    
    def setup_vector_store(self, documents: List[Document], recreate: bool = False):
        """Set up vector store with structured Q&A documents."""
        if recreate and os.path.exists(self.vector_db_path):
            import shutil
            shutil.rmtree(self.vector_db_path)
            print(f"Removed existing vector store: {self.vector_db_path}")
        
        if os.path.exists(self.vector_db_path) and not recreate:
            print(f"Loading existing vector store from: {self.vector_db_path}")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            self.vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=embeddings
            )
        else:
            print("Creating new vector store...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=self.vector_db_path
            )
            self.vector_store.persist()
            print(f"Vector store created and saved to: {self.vector_db_path}")
    
    def setup_llm(self):
        """Set up the language model."""
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        self.llm = LlamaCpp(
            model_path=self.model_path,
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            callback_manager=callback_manager,
            verbose=True,
            n_ctx=4096
        )
    
    def setup_qa_chain(self):
        """Set up the Q&A chain."""
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": self.create_prompt_template()
            }
        )
    
    def create_prompt_template(self):
        """Create a prompt template that emphasizes context awareness."""
        from langchain.prompts import PromptTemplate
        
        template = """You are a helpful financial advisor assistant. Use the following context to answer the question at the end.

Context information:
{context}

Question: {question}

Instructions:
1. Pay careful attention to the context labels (e.g., "Traditional IRA rules" vs "Roth IRA rules")
2. Only provide information that matches the specific context requested
3. If the context doesn't contain enough information, say so
4. Be precise and accurate in your response

Answer:"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(self, question: str) -> Dict:
        """Query the RAG system with a question."""
        if not self.qa_chain:
            raise RuntimeError("Q&A chain not set up. Call setup_pipeline() first.")
        
        print(f"\n🤔 Question: {question}")
        print("🔍 Searching structured Q&A database...")
        
        result = self.qa_chain({"query": question})
        
        print(f"\n📝 Answer: {result['result']}")
        
        # Show sources with context
        if result.get('source_documents'):
            print("\n📚 Sources:")
            for i, doc in enumerate(result['source_documents'], 1):
                context = doc.metadata.get('context', 'Unknown context')
                source = doc.metadata.get('source', 'Unknown source')
                category = doc.metadata.get('category', 'Unknown category')
                print(f"  {i}. {context} ({category}) - {source}")
        
        return result
    
    def setup_pipeline(self, recreate_vector_store: bool = False):
        """Set up the complete RAG pipeline."""
        print("🚀 Setting up Structured RAG Pipeline...")
        
        # Load Q&A data
        self.load_qa_data()
        
        # Create documents
        documents = self.create_documents_from_qa()
        
        # Setup vector store
        self.setup_vector_store(documents, recreate=recreate_vector_store)
        
        # Setup LLM
        self.setup_llm()
        
        # Setup Q&A chain
        self.setup_qa_chain()
        
        print("✅ Structured RAG Pipeline ready!")
    
    def interactive_mode(self):
        """Run interactive Q&A mode."""
        print("\n🎯 Interactive Structured RAG Mode")
        print("Type 'quit' to exit")
        print("Type 'sources' to see available categories")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() == 'quit':
                    break
                elif question.lower() == 'sources':
                    self.show_available_categories()
                    continue
                elif not question:
                    continue
                
                self.query(question)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_available_categories(self):
        """Show available Q&A categories."""
        if not self.qa_data:
            print("No Q&A data loaded")
            return
            
        categories = self.qa_data['metadata']['categories']
        print("\n📂 Available categories:")
        for category in categories:
            count = sum(1 for qa in self.qa_data['qa_pairs'] if qa['category'] == category)
            print(f"  • {category}: {count} Q&A pairs")
        
        print("\n💡 Example questions by category:")
        for category in categories:
            examples = [qa['question'] for qa in self.qa_data['qa_pairs'] if qa['category'] == category][:2]
            print(f"\n  {category}:")
            for example in examples:
                print(f"    - {example}")

def main():
    parser = argparse.ArgumentParser(description='Structured RAG Pipeline')
    parser.add_argument('--model', default='mistral-7b-instruct-v0.1.Q4_K_M.gguf',
                       help='Path to the language model')
    parser.add_argument('--qa-data', default='structured_qa_data.json',
                       help='Path to structured Q&A data file')
    parser.add_argument('--vector-db', default='structured_vector_db',
                       help='Path to vector database')
    parser.add_argument('--recreate', action='store_true',
                       help='Recreate vector database')
    parser.add_argument('--question', type=str,
                       help='Ask a single question')
    
    args = parser.parse_args()
    
    pipeline = StructuredRAGPipeline(
        model_path=args.model,
        qa_data_path=args.qa_data,
        vector_db_path=args.vector_db
    )
    
    try:
        pipeline.setup_pipeline(recreate_vector_store=args.recreate)
        
        if args.question:
            pipeline.query(args.question)
        else:
            pipeline.interactive_mode()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have generated structured Q&A data first using structured_qa_generator.py")

if __name__ == "__main__":
    main() 