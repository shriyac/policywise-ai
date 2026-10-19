"""Evidence-gated LangGraph RAG. Citation IDs must be retrieved AND approved."""
from functools import lru_cache
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from src.config import GROQ_MODEL, require_secret
from src.store import search

class EvidenceDecision(BaseModel):
    sufficient: bool = Field(description="Whether retrieved passages directly answer the question")
    approved_chunk_ids: list[str] = Field(default_factory=list)
    reason: str = ""

class AnswerPayload(BaseModel):
    answer: str
    cited_chunk_ids: list[str] = Field(default_factory=list)

class RAGState(TypedDict, total=False):
    question: str
    employment_country: str
    retrieved: list[dict[str, Any]]
    assessment: dict[str, Any]
    answer: str
    citations: list[dict[str, Any]]
    status: str

@lru_cache(maxsize=1)
def model():
    return ChatGroq(model=GROQ_MODEL, api_key=require_secret("GROQ_API_KEY"), temperature=0)

def retrieve(state: RAGState):
    docs = []
    for doc, score in search(state['question'], k=5):
        docs.append({"id": doc.metadata.get('chunk_id', ''), "text": doc.page_content,
                     "filename": doc.metadata.get('filename', ''), "page": doc.metadata.get('page_number'),
                     "similarity": float(score)})
    return {"retrieved": docs}

def context(state):
    return "\n\n".join(f"[ID={x['id']} | {x['filename']} p.{x['page']}]\n{x['text']}" for x in state.get('retrieved', []))

def assess(state: RAGState):
    if not state.get('retrieved'):
        return {"assessment": {"sufficient": False, "approved_chunk_ids": [], "reason": "No retrieved evidence"}}
    instructions = ("You are a strict policy evidence reviewer. Use ONLY the retrieved extracts. "
      "Approve IDs that directly support the complete question. For personal entitlements, country-specific "
      "eligibility, PTO balance, or cross-border work, do NOT infer facts missing from the extracts. "
      "If question is ambiguous or evidence lacks required scope, mark insufficient. "
      "Return only IDs actually in the extracts.")
    prompt = f"Question: {state['question']}\nEmployment country: {state.get('employment_country') or 'unknown'}\nEvidence:\n{context(state)}"
    result = model().with_structured_output(EvidenceDecision).invoke([SystemMessage(content=instructions), HumanMessage(content=prompt)])
    actual = {x['id'] for x in state['retrieved']}
    approved = [x for x in result.approved_chunk_ids if x in actual]
    return {"assessment": {"sufficient": bool(result.sufficient and approved), "approved_chunk_ids": approved, "reason": result.reason}}

def path(state):
    return "generate" if state['assessment']['sufficient'] else "abstain"

def abstain(state):
    return {"status": "insufficient_evidence", "answer": "The available documents do not contain sufficient information to answer this question.", "citations": []}

def generate(state: RAGState):
    allowed = set(state['assessment']['approved_chunk_ids'])
    evidence = "\n\n".join(f"[ID={x['id']}] {x['text']}" for x in state['retrieved'] if x['id'] in allowed)
    instructions = ("Answer ONLY from the provided evidence and preserve jurisdiction qualifiers. "
                    "Be concise. Cite IDs in cited_chunk_ids for claims made. Do not invent eligibility, "
                    "amounts, page numbers, or policy facts. If evidence is insufficient, say so.")
    response = model().with_structured_output(AnswerPayload).invoke([
        SystemMessage(content=instructions),
        HumanMessage(content=f"Question: {state['question']}\nApproved evidence:\n{evidence}")])
    referenced = set(response.cited_chunk_ids)
    if not referenced or not referenced.issubset(allowed):
        return {"status": "citation_validation_failed", "answer": "Answer withheld: citations failed validation.", "citations": []}
    citations = [{"chunk_id": x['id'], "filename": x['filename'], "page": x['page'], "excerpt": x['text'][:500]}
                 for x in state['retrieved'] if x['id'] in referenced]
    # ID-membership validation is not semantic claim-support verification; human/LLM evaluation remains required.
    return {"status": "success", "answer": response.answer, "citations": citations}

@lru_cache(maxsize=1)
def graph():
    builder = StateGraph(RAGState)
    builder.add_node('retrieve', retrieve)
    builder.add_node('assess', assess)
    builder.add_node('generate', generate)
    builder.add_node('abstain', abstain)
    builder.add_edge(START, 'retrieve')
    builder.add_edge('retrieve', 'assess')
    builder.add_conditional_edges('assess', path, {'generate': 'generate', 'abstain': 'abstain'})
    builder.add_edge('generate', END)
    builder.add_edge('abstain', END)
    return builder.compile()

def ask(question: str, employment_country: str = ''):
    return graph().invoke({"question": question, "employment_country": employment_country})
