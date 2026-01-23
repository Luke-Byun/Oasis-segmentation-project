# rag/retriever.py
import os
from dataclasses import dataclass
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def load_docs(folder: str) -> List[Dict[str, str]]:
    docs = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.endswith(".md") or fn.endswith(".txt"):
                path = os.path.join(root, fn)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                docs.append({"doc_id": os.path.relpath(path, folder), "text": text})
    return docs

@dataclass
class TfidfRetriever:
    docs: List[Dict[str, str]]
    vectorizer: TfidfVectorizer
    matrix: Any

    @classmethod
    def build(cls, docs: List[Dict[str, str]]):
        texts = [d["text"] for d in docs]
        vectorizer = TfidfVectorizer(max_features=50000)
        matrix = vectorizer.fit_transform(texts)
        return cls(docs=docs, vectorizer=vectorizer, matrix=matrix)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        q = self.vectorizer.transform([query])
        scores = (self.matrix @ q.T).toarray().reshape(-1)
        idx = np.argsort(scores)[::-1][:k]
        out = []
        for i in idx:
            out.append({
                "doc_id": self.docs[i]["doc_id"],
                "score": float(scores[i]),
                "snippet": self.docs[i]["text"][:900]
            })
        return out