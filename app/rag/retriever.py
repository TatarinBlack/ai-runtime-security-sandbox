"""
Fully local, offline TF-IDF based retrieval.
scikit-learn TF-IDF was deliberately chosen over sentence-embeddings so the
live demo never depends on internet access or downloading a model:
deterministic, instant to set up, never fails mid-talk.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app import config
from app.rag.loader import load_documents, chunk_documents, Chunk


class Retriever:
    def __init__(self):
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._chunks: list[Chunk] = []
        self.reload()

    def reload(self):
        docs = load_documents()
        self._chunks = chunk_documents(docs)
        if not self._chunks:
            self._vectorizer, self._matrix = None, None
            return
        self._vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
        self._matrix = self._vectorizer.fit_transform([c.text for c in self._chunks])

    def retrieve(self, query: str, top_k: int = config.TOP_K, allowed_classifications: set[str] | None = None):
        if not self._chunks or self._vectorizer is None:
            return []
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix)[0]
        scored = list(zip(self._chunks, sims))
        if allowed_classifications is not None:
            scored = [(c, s) for c, s in scored if c.classification in allowed_classifications]
        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for chunk, score in scored[:top_k]:
            if score < config.MIN_SCORE:
                continue
            results.append({
                "doc": chunk.doc_filename,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "classification": chunk.classification,
                "scenario": chunk.scenario,
                "score": round(float(score), 4),
            })
        return results

    def list_documents_meta(self):
        docs = load_documents()
        return [{"filename": d.filename, "classification": d.classification, "scenario": d.scenario} for d in docs]


retriever = Retriever()
