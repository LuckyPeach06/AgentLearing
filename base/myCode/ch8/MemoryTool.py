from datetime import datetime

"""
    仅作为读教程时跟敲代码使用，依赖补全，代码不全，无法运行
"""
class MemoryTool:

    # def _search_memory(
    #         self,

    # )



    def execute(self, action: str, **kwargs) -> str:
        """执行记忆操作

            支持的操作：
            - add: 添加记忆（支持4种类型: working/episodic/semantic/perceptual）
            - search: 搜索记忆
            - summary: 获取记忆摘要
            - stats: 获取统计信息
            - update: 更新记忆
            - remove: 删除记忆
            - forget: 遗忘记忆（多种策略）
            - consolidate: 整合记忆（短期→长期）
            - clear_all: 清空所有记忆
        """
        if action == "add":
            return self._add_memory(**kwargs)
        elif action == "search":
            return self._search_memory(**kwargs)
        elif action == "summary":
            return self._get_summary()
        elif action == "forget":
            return self._forget_memory(**kwargs)
        elif action == "consolidate":
            return self._consolidate_memory(**kwargs)
        else:
            raise ValueError(f"未知的操作: {action}")


    def _add_memory(self, 
                    content: str = "", 
                    memory_type: str = "working", 
                    importance: float = 0.5, 
                    file_path: str = None,
                    modality: str = None,
                    **metadata
    ) -> str:
        """添加记忆"""

        try:
            # 生成唯一的记忆ID
            if self.current_session_id is None:
                self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # 多模态数据处理
            if memory_type == "perceptual" and file_path:
                inferred = modality or self._infer_modality(file_path)
                metadata.setdefault("modality", inferred)
                metadata.setdefault("file_path", file_path)

            # 添加会话信息到元数据
            metadata.update({
                "session_id": self.current_session_id,
                "timestamp": datetime.now().isoformat(),
            })

            memory_id = self.memory_manager.add_memory(
                content = content, 
                memory_type = memory_type, 
                importance = importance, 
                metadata = metadata,
                auto_classify = False
            )
            return f"记忆已添加 (ID: {memory_id[:8]}...)"

        except Exception as e:
            return f"添加记忆失败: {str(e)}"


    def _infer_modality(self, path: str) -> str:
        """根据扩展名推断模态（默认image/audio/text）"""
        try:
            ext = (path.rsplit('.', 1)[-1] or '').lower()
            if ext in {"png", "jpg", "jpeg", "bmp", "gif", "webp"}:
                return "image"
            if ext in {"mp3", "wav", "flac", "m4a", "ogg"}:
                return "audio"
            return "text"
        except Exception:
            return "text"
        
    def setdefault(self, key, default=None):
        'D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D'
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default