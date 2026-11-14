class PerceptualMemory:
    """
        感知记忆
            特点：
            - 支持多模态数据（文本、图像、音频等）
            - 跨模态相似性搜索
            - 感知数据的语义理解
            - 支持内容生成和检索
    """
    def __init__(self, config: MemoryConfig, storage_backend=None):
        super().__init__(config, storage_backend)

        # 多模态编码器
        self.text_embedder = get_text_embedder()
        self._clip_model = self._init_clip_model()  # 图像编码
        self._clap_model = self._init_clap_model()  # 音频编码

        self.vector_score = {
            "text": QdrantConnectionManager.get_instance(
                collection_name="perceptual_text",
                vector_size=self.vector_dim
            ),
            "image": QdrantConnectionManager.get_instance(
                collection_name="perceptual_image", 
                vector_size=self._image_dim
            ),
            "audio": QdrantConnectionManager.get_instance(
                collection_name="perceptual_audio",
                vector_size=self._audio_dim
            )
        }

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        user_id = kwargs.get("user_id")
        # 你想搜什么类型的数据
        target_modality = kwargs.get("target_modality")
        # 你想用什么类型的数据去搜索
        query_modality = kwargs.get("query_modality", target_modality or "text")

        try:
            # 把你的搜索词或者图片变为向量
            # 如果是文本，用文本模型转成向量；
            # 如果是图片，用 CLIP 模型转成向量；
            # 如果是音频，用 CLAP 模型转
            query_vector = self._encode_data(query, query_modality)

            # 找到对应模态的库
            # 物理隔离，因为文本向量是 1024 维，图片向量可能是 512 维，如果混在一个库里会直接报错
            # 所以代码里会去取 perceptual_image 或 perceptual_audio 的专属集合
            store = self._get_vector_store_for_modality(target_modality or query_modality)

            # where 条件：不仅限定是感知记忆，如果指定了搜图片，就过滤掉音频。
            where = {"memory_type": "perceptual"}
            if user_id:
                where["user_id"] = user_id
            if target_modality:
                where["modality"] = target_modality

            hits = store.search_similar(
                query_vector=query_vector,
                limit=max(limit * 5, 20),
                where=where
            )
        except Exception as e:
            hits = []

        # 融合排序（向量相似度 + 时间近因性 + 重要性权重）
        results = []
        for hit in hits:
            results.append((_calculate_perceptual_score(hit), self._create_memory_item(hit)))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:limit]]

    def _calculate_perceptual_score(self, hit) -> float:
        vec_score = float(hit.get("score", 0.0))
        recency_score = self._calculate_recency(hit["metadata"]["timestamp"])
        importance = hit["metadata"].get("importance", 0.5)
        
        # 评分公式：(向量相似度 × 0.8 + 时间近因性 × 0.2) × 重要性权重
        base_relevance = vec_score * 0.8 + recency_score * 0.2
        importance_weight = 0.8 + (importance * 0.4)
        
        return base_relevance * importance_weight

    def _calculate_recency_score(self, timestamp: str) -> float:
        """计算时间近因性得分"""
        try:
            memory_time = datetime.fromisoformat(timestamp)
            current_time = datetime.now()
            age_hours = (current_time - memory_time).total_seconds() / 3600
            
            # 指数衰减：24小时内保持高分，之后逐渐衰减
            decay_factor = 0.1  # 衰减系数
            recency_score = math.exp(-decay_factor * age_hours / 24)
            
            return max(0.1, recency_score)  # 最低保持0.1的基础分数
        except Exception:
            return 0.5  # 默认中等分数