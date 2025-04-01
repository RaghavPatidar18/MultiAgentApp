from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langgraph.graph import StateGraph, END, START
from app.document_prep import retriever
from app.config import GROQ_API_KEY
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

# LLM setup
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

class RouteQuery(BaseModel):
    """Routes a user query to Wikipedia or Vectorstore."""
    datasource: Literal["vectorstore", "wiki_search"] = Field(..., description="Choose either Wikipedia or Vectorstore.")

structured_llm_router = llm.with_structured_output(RouteQuery)

route_prompt = ChatPromptTemplate.from_messages([
    ("system", "Route the question to either Wikipedia or Vectorstore."),
    ("human", "{question}")
])

question_router = route_prompt | structured_llm_router
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

class GraphState(TypedDict):
    question: str
    generation: str
    documents: str

def retrieve(state):
    question = state["question"]
    documents = retriever.invoke(question)
    doc_texts = "\n\n".join([doc.page_content for doc in documents])
    return {"documents": doc_texts, "question": question}

def wiki_search(state):
    question = state["question"]
    docs = wiki.invoke({"query": question})
    return {"documents": docs, "question": question}

def generate_answer(state):
    question = state["question"]
    context = state["documents"]

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", "Provide structured responses based only on retrieved documents."),
        ("human", "Question: {question}\n\nContext:\n{context}")
    ])

    structured_response = (answer_prompt | llm).invoke({"question": question, "context": context})
    return {"generation": structured_response, "question": question}

def route_question(state):
    question = state["question"]
    source = question_router.invoke({"question": question})
    return "wiki_search" if source.datasource == "wiki_search" else "retrieve"

workflow = StateGraph(GraphState)
workflow.add_node("wiki_search", wiki_search)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate_answer", generate_answer)

workflow.add_conditional_edges(START, route_question, {
    "wiki_search": "wiki_search",
    "retrieve": "retrieve",
})
workflow.add_edge("retrieve", "generate_answer")
workflow.add_edge("wiki_search", "generate_answer")
workflow.add_edge("generate_answer", END)

app = workflow.compile()
