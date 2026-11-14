from typing import List

from base.myCode.ch8 import MemoryConfig, MemoryItem


class WorkingMemory:

    def __init__(self, config: MemoryConfig):
        self.max_capacity = config.working_memory_capacity or 50
        self.max_age_minutes = config.working_memory_ttl or 60
        self.memories = []

    def add(self, memory_item: MemoryItem) -> str:
        self._expire_old_memories()  # 过期清理

        if len(self.memories) >= self.max_capacity:
            self._remove_lowest_priority_memory()  # 容量管理

        self.memories.append(memory_item)

        return memory_item.id

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        """
            组合词法检索：TF-IDF 词项权重相似度 + 关键词匹配
        """
        self._expire_old_memories()

        # 计算 TF-IDF 词项权重相似度
        vector_scores = self._try_tfidf_search(query)

        # 计算综合分数
        scored_memories = []

        for memory in self.memories:
            # 词项分数
            vector_score = vector_scores.get(memory.id, 0.0)
            # 关键词分数
            keyword_score = self._calculate_keyword_score(query, memory.content)

            # 计算权重分数
            base_relevance = (vector_score * 0.7 + keyword_score * 0.3 
                              if vector_score > 0 else keyword_score)
            time_decay = self._calculate_time_decay(memory.timestamp)
            importance_weight = 0.8 + (memory.importance * 0.4)
            
            final_score = base_relevance * time_decay * importance_weight
            if final_score > 0:
                scored_memories.append((final_score, memory))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:limit]]
