"""
AI配置和日志表迁移
创建 qms_ai_config 和 qms_ai_log 表
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers
revision = "20260609_0003"
down_revision = "20260609_0001_quality_reagent"  # 依赖于试剂管理迁移
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 qms_ai_config 表
    op.execute("""
        CREATE TABLE IF NOT EXISTS qms.qms_ai_config (
            id SERIAL PRIMARY KEY,
            key VARCHAR(100) NOT NULL UNIQUE,
            value TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 插入默认配置
    op.execute("""
        INSERT INTO qms.qms_ai_config (key, value, description)
        VALUES (
            'ai_config',
            '{"enabled": false, "model": "MiniMax/VL-01", "max_tokens": 2048, "temperature": 0.7}',
            'AI功能全局配置'
        ) ON CONFLICT (key) DO NOTHING
    """)

    # 创建 qms_ai_log 表
    op.execute("""
        CREATE TABLE IF NOT EXISTS qms.qms_ai_log (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100),
            session_id VARCHAR(100),
            module VARCHAR(50) NOT NULL,
            action VARCHAR(50) NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT,
            model VARCHAR(100),
            tokens_used INTEGER,
            status VARCHAR(20) NOT NULL DEFAULT 'success',
            error_message TEXT,
            request_params JSONB,
            response_time INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建索引
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_log_user_id ON qms.qms_ai_log(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_log_session_id ON qms.qms_ai_log(session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_log_module ON qms.qms_ai_log(module)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_log_action ON qms.qms_ai_log(action)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_log_status ON qms.qms_ai_log(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_log_created_at ON qms.qms_ai_log(created_at)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS qms.qms_ai_log")
    op.execute("DROP TABLE IF EXISTS qms.qms_ai_config")
