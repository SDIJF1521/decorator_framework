"""
装饰器框架生产环境配置
基于 production_final.py 和 production_ready.py 的最佳实践
"""

import os
import logging
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.absolute()
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = BASE_DIR / "logs" / "app.log"
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# 创建日志目录
LOG_FILE.parent.mkdir(exist_ok=True)

# 日志配置字典
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_FILE),
            'maxBytes': LOG_MAX_BYTES,
            'backupCount': LOG_BACKUP_COUNT,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'nucleus': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# 框架配置
FRAMEWORK_CONFIG = {
    # 定时任务配置
    'scheduler': {
        'enabled': os.getenv("SCHEDULER_ENABLED", "true").lower() == "true",
        'max_workers': int(os.getenv("SCHEDULER_MAX_WORKERS", "10")),
        'default_interval': int(os.getenv("SCHEDULER_DEFAULT_INTERVAL", "60"))
    },
    
    # 事件系统配置
    'events': {
        'max_concurrent_handlers': int(os.getenv("EVENT_MAX_CONCURRENT", "100")),
        'timeout': int(os.getenv("EVENT_TIMEOUT", "30"))
    },
    
    # 命令系统配置
    'commands': {
        'prefix': os.getenv("COMMAND_PREFIX", "/"),
        'timeout': int(os.getenv("COMMAND_TIMEOUT", "10"))
    },
    
    # 正则表达式配置
    'regex': {
        'timeout': int(os.getenv("REGEX_TIMEOUT", "5"))
    }
}

# 监控配置
MONITORING_CONFIG = {
    'enabled': os.getenv("MONITORING_ENABLED", "true").lower() == "true",
    'metrics_port': int(os.getenv("METRICS_PORT", "8080")),
    'health_check_interval': int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
    'metrics_endpoint': os.getenv("METRICS_ENDPOINT", "/metrics")
}

# 安全配置
SECURITY_CONFIG = {
    'rate_limit': {
        'enabled': os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
        'default_limit': int(os.getenv("RATE_LIMIT_DEFAULT", "100")),
        'window': int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 秒
    },
    'input_validation': {
        'enabled': os.getenv("INPUT_VALIDATION_ENABLED", "true").lower() == "true",
        'max_input_length': int(os.getenv("MAX_INPUT_LENGTH", "1000"))
    }
}

# 数据库配置（可选）
DATABASE_CONFIG = {
    'type': os.getenv("DB_TYPE", "sqlite"),  # sqlite, mysql, postgresql
    'host': os.getenv("DB_HOST", "localhost"),
    'port': int(os.getenv("DB_PORT", "5432")),
    'name': os.getenv("DB_NAME", "decorator_framework"),
    'user': os.getenv("DB_USER", "app"),
    'password': os.getenv("DB_PASSWORD", ""),
    'pool_size': int(os.getenv("DB_POOL_SIZE", "10")),
    'max_overflow': int(os.getenv("DB_MAX_OVERFLOW", "20"))
}

# Redis配置（可选）
REDIS_CONFIG = {
    'host': os.getenv("REDIS_HOST", "localhost"),
    'port': int(os.getenv("REDIS_PORT", "6379")),
    'db': int(os.getenv("REDIS_DB", "0")),
    'password': os.getenv("REDIS_PASSWORD", ""),
    'max_connections': int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
}

# 外部API配置
EXTERNAL_API_CONFIG = {
    'timeout': int(os.getenv("API_TIMEOUT", "30")),
    'max_retries': int(os.getenv("API_MAX_RETRIES", "3")),
    'retry_delay': float(os.getenv("API_RETRY_DELAY", "1.0"))
}

# 环境特定配置
if ENVIRONMENT == "production":
    LOG_LEVEL = "WARNING"
    FRAMEWORK_CONFIG['scheduler']['max_workers'] = 50
    SECURITY_CONFIG['rate_limit']['default_limit'] = 1000
    
elif ENVIRONMENT == "staging":
    LOG_LEVEL = "INFO"
    FRAMEWORK_CONFIG['scheduler']['max_workers'] = 20
    SECURITY_CONFIG['rate_limit']['default_limit'] = 200
    
else:  # development
    LOG_LEVEL = "DEBUG"
    FRAMEWORK_CONFIG['scheduler']['max_workers'] = 5
    SECURITY_CONFIG['rate_limit']['default_limit'] = 50

# 配置验证
def validate_config():
    """验证配置有效性"""
    errors = []
    
    # 验证日志目录
    if not LOG_FILE.parent.exists():
        try:
            LOG_FILE.parent.mkdir(parents=True)
        except Exception as e:
            errors.append(f"无法创建日志目录: {e}")
    
    # 验证端口范围
    if not (1 <= MONITORING_CONFIG['metrics_port'] <= 65535):
        errors.append("监控端口必须在1-65535之间")
    
    # 验证时间间隔
    if FRAMEWORK_CONFIG['scheduler']['default_interval'] <= 0:
        errors.append("定时任务默认间隔必须大于0")
    
    if errors:
        raise ValueError("配置错误: " + "; ".join(errors))

# 自动验证配置
validate_config()

# 导出配置
__all__ = [
    'ENVIRONMENT',
    'LOG_LEVEL',
    'LOGGING_CONFIG',
    'FRAMEWORK_CONFIG',
    'MONITORING_CONFIG',
    'SECURITY_CONFIG',
    'DATABASE_CONFIG',
    'REDIS_CONFIG',
    'EXTERNAL_API_CONFIG'
]

# 使用示例
if __name__ == "__main__":
    import logging.config
    logging.config.dictConfig(LOGGING_CONFIG)
    
    logger = logging.getLogger(__name__)
    logger.info(f"环境: {ENVIRONMENT}")
    logger.info(f"日志级别: {LOG_LEVEL}")
    logger.info(f"框架配置: {FRAMEWORK_CONFIG}")