"""
AI配置管理模块
提供全局AI配置的管理功能，支持从数据库持久化加载和保存
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session


class AIConfig:
    """AI配置类 - 单例模式"""
    _instance: Optional["AIConfig"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config: dict = {}
        self._db_session: Optional[Session] = None
        self._table_name: str = "qms.qms_ai_config"

    def init(self, db_session: Session):
        """初始化数据库会话并加载配置"""
        self._db_session = db_session
        self.load_config()

    def load_config(self):
        """从数据库加载AI配置"""
        if not self._db_session:
            return

        try:
            query = select(self._table_name).where(
                getattr(__import__("sqlalchemy").text, "__call__", lambda x: x)("key = 'ai_config'") if False else True
            )
            from sqlalchemy import text
            result = self._db_session.execute(
                text("SELECT value FROM qms.qms_ai_config WHERE key = 'ai_config' LIMIT 1")
            ).fetchone()

            if result and result[0]:
                import json
                self._config = json.loads(result[0])
        except Exception as e:
            print(f"加载AI配置失败: {e}")
            self._config = {}

    def save_config(self):
        """保存AI配置到数据库"""
        if not self._db_session:
            return

        try:
            import json
            config_json = json.dumps(self._config, ensure_ascii=False)

            from sqlalchemy import text
            exists = self._db_session.execute(
                text("SELECT COUNT(*) FROM qms.qms_ai_config WHERE key = 'ai_config'")
            ).scalar()

            if exists and exists > 0:
                self._db_session.execute(
                    text("UPDATE qms.qms_ai_config SET value = :value, updated_at = NOW() WHERE key = 'ai_config'"),
                    {"value": config_json}
                )
            else:
                self._db_session.execute(
                    text("INSERT INTO qms.qms_ai_config (key, value, created_at, updated_at) VALUES ('ai_config', :value, NOW(), NOW())"),
                    {"value": config_json}
                )
            self._db_session.commit()
        except Exception as e:
            print(f"保存AI配置失败: {e}")
            self._db_session.rollback()

    def get(self, key: str, default=None):
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key: str, value):
        """设置配置项"""
        self._config[key] = value

    def get_all(self) -> dict:
        """获取所有配置"""
        return self._config.copy()

    def update(self, config: dict):
        """批量更新配置"""
        self._config.update(config)

    def is_enabled(self) -> bool:
        """检查AI功能是否启用"""
        return self._config.get("enabled", False)

    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        return self._config.get("api_key")

    def get_base_url(self) -> Optional[str]:
        """获取API基础URL"""
        return self._config.get("base_url")

    def get_model(self) -> str:
        """获取模型名称"""
        return self._config.get("model", "MiniMax/VL-01")

    def get_max_tokens(self) -> int:
        """获取最大token数"""
        return self._config.get("max_tokens", 2048)

    def get_temperature(self) -> float:
        """获取温度参数"""
        return self._config.get("temperature", 0.7)


# 全局AI配置实例
ai_config = AIConfig()
