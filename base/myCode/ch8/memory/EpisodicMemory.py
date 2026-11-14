

from typing import List

from base.myCode.ch8 import Episode, MemoryConfig, MemoryItem, QdrantVectorStore
from base.myCode.ch8 import SQLiteDocumentStore


class EpisodicMemory:
    """
        情境记忆：
            SQLite：结构化数据的存储和复杂查询
            Qdrant：高效的向量检索
    """

    def __init__(self, config: MemoryConfig):
        self.doc_store = SQLiteDocumentStore(config.database_path)
        self.vector_store = QdrantVectorStore(config.qdrant_url, config.qdrant_api_key)
        self.embedder = create_embedding_model_with_fallback()
        self.sessions = {}  # 会话索引

    def add(self, memory_item: MemoryItem):
        episode = Episode(
            episode_id=memory_item.id,
            session_id=memory_item.metadata.get("session_id", "default"),
            timestamp=memory_item.timestamp,
            content=memory_item.content,
            context=memory_item.metadata
        )

        session_id = episode.session_id
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(episode.episode_id)

        # 持久化存储（SQLite + Qdrant）
        self._persist_episode(episode)
        return memory_item.id

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        # 结构化查询
        candidate_ids = self._structured_filter(**kwargs)

        # 向量检索
        hits = self._vector_search(query, limit * 5, kwargs.get("user_id"))

        # 将向量检索出的数据，通过结构化查询的数据过滤，只保留结构化数据中有的数据
        # 并对数据进行评分和排序
        results = []
        for hit in hits:
            if self._should_include(hit, candidate_ids, kwargs):
                score = self._calculate_episode_score(hit)
                memory_item = self._create_memory_item(hit)
                results.append((score, memory_item))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:limit]]

    def _calculate_episode_score(self, hit) -> float:
        vec_score = float(hit.get("score", 0.0))
        recency_score = self._calculate_recency(hit["metadata"]["timestamp"])
        importance = hit["metadata"].get("importance", 0.5)
        
        # 评分公式：(向量相似度 × 0.8 + 时间近因性 × 0.2) × 重要性权重
        base_relevance = vec_score * 0.8 + recency_score * 0.2
        importance_weight = 0.8 + (importance * 0.4)
        
        return base_relevance * importance_weight