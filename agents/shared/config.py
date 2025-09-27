"""
Configuration settings for PulseProof Enhanced Risk Engine
"""

import os
from typing import Optional

class Config:
    """Configuration class for API keys and settings"""
    
    # API Keys (set via environment variables or use defaults for testing)
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', 'YourApiKeyToken')
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', None)  # Optional
    GOPLUS_API_KEY = os.getenv('GOPLUS_API_KEY', None)  # Optional
    
    # Web3 Provider URLs
    WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL', None)
    INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID', None)
    ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY', None)
    
    # API URLs
    ETHERSCAN_API_URL = "https://api.etherscan.io/api"
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    GOPLUS_API_URL = "https://api.gopluslabs.io/api/v1"
    
    # Cache settings
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes default
    
    # Risk assessment settings
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '0.6'))
    HIGH_RISK_THRESHOLD = float(os.getenv('HIGH_RISK_THRESHOLD', '0.7'))
    CRITICAL_RISK_THRESHOLD = float(os.getenv('CRITICAL_RISK_THRESHOLD', '0.9'))
    
    # Financial thresholds (in USD)
    CRITICAL_FINANCIAL_THRESHOLD = float(os.getenv('CRITICAL_FINANCIAL_THRESHOLD', '1000000'))  # $1M
    HIGH_FINANCIAL_THRESHOLD = float(os.getenv('HIGH_FINANCIAL_THRESHOLD', '100000'))    # $100K
    MEDIUM_FINANCIAL_THRESHOLD = float(os.getenv('MEDIUM_FINANCIAL_THRESHOLD', '10000'))  # $10K
    LOW_FINANCIAL_THRESHOLD = float(os.getenv('LOW_FINANCIAL_THRESHOLD', '1000'))      # $1K
    
    # Risk weights
    RISK_WEIGHTS = {
        'financial_impact': float(os.getenv('FINANCIAL_WEIGHT', '0.35')),
        'behavioral_anomaly': float(os.getenv('BEHAVIORAL_WEIGHT', '0.25')),
        'reputation_risk': float(os.getenv('REPUTATION_WEIGHT', '0.20')),
        'historical_context': float(os.getenv('HISTORICAL_WEIGHT', '0.15')),
        'approval_risk': float(os.getenv('APPROVAL_WEIGHT', '0.05'))
    }
    
    # API rate limiting
    ETHERSCAN_RATE_LIMIT = int(os.getenv('ETHERSCAN_RATE_LIMIT', '5'))  # requests per second
    COINGECKO_RATE_LIMIT = int(os.getenv('COINGECKO_RATE_LIMIT', '10'))  # requests per second
    GOPLUS_RATE_LIMIT = int(os.getenv('GOPLUS_RATE_LIMIT', '10'))  # requests per second
    
    # Timeout settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))  # seconds
    
    # Retry and circuit breaker settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = float(os.getenv('RETRY_DELAY', '1.0'))  # seconds
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', '5'))
    CIRCUIT_BREAKER_TIMEOUT = int(os.getenv('CIRCUIT_BREAKER_TIMEOUT', '60'))  # seconds
    
    # Logging and monitoring
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))
    
    # Security settings
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '100'))
    ENABLE_CORS = os.getenv('ENABLE_CORS', 'true').lower() == 'true'
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # Database and persistence
    ENABLE_PERSISTENCE = os.getenv('ENABLE_PERSISTENCE', 'false').lower() == 'true'
    DATABASE_URL = os.getenv('DATABASE_URL', None)
    REDIS_URL = os.getenv('REDIS_URL', None)
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
    REQUEST_QUEUE_SIZE = int(os.getenv('REQUEST_QUEUE_SIZE', '100'))
    ENABLE_COMPRESSION = os.getenv('ENABLE_COMPRESSION', 'true').lower() == 'true'
    
    # Feature flags
    ENABLE_ETHERSCAN_API = os.getenv('ENABLE_ETHERSCAN_API', 'true').lower() == 'true'
    ENABLE_COINGECKO_API = os.getenv('ENABLE_COINGECKO_API', 'true').lower() == 'true'
    ENABLE_GOPLUS_API = os.getenv('ENABLE_GOPLUS_API', 'true').lower() == 'true'
    ENABLE_WEB3_INTEGRATION = os.getenv('ENABLE_WEB3_INTEGRATION', 'false').lower() == 'true'
    
    @classmethod
    def get_web3_provider_url(cls) -> Optional[str]:
        """Get the best available Web3 provider URL"""
        if cls.WEB3_PROVIDER_URL:
            return cls.WEB3_PROVIDER_URL
        
        if cls.INFURA_PROJECT_ID:
            return f"https://mainnet.infura.io/v3/{cls.INFURA_PROJECT_ID}"
        
        if cls.ALCHEMY_API_KEY:
            return f"https://eth-mainnet.alchemyapi.io/v2/{cls.ALCHEMY_API_KEY}"
        
        return None
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get appropriate log level"""
        return 'INFO' if cls.is_production() else 'DEBUG'
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """Validate configuration settings and return (is_valid, errors)"""
        errors = []
        
        # Validate risk weights sum to 1.0
        total_weight = sum(cls.RISK_WEIGHTS.values())
        if abs(total_weight - 1.0) > 0.001:
            errors.append(f"Risk weights must sum to 1.0, got {total_weight}")
        
        # Validate thresholds are in correct order
        if cls.LOW_FINANCIAL_THRESHOLD >= cls.MEDIUM_FINANCIAL_THRESHOLD:
            errors.append("LOW_FINANCIAL_THRESHOLD must be less than MEDIUM_FINANCIAL_THRESHOLD")
        if cls.MEDIUM_FINANCIAL_THRESHOLD >= cls.HIGH_FINANCIAL_THRESHOLD:
            errors.append("MEDIUM_FINANCIAL_THRESHOLD must be less than HIGH_FINANCIAL_THRESHOLD")
        if cls.HIGH_FINANCIAL_THRESHOLD >= cls.CRITICAL_FINANCIAL_THRESHOLD:
            errors.append("HIGH_FINANCIAL_THRESHOLD must be less than CRITICAL_FINANCIAL_THRESHOLD")
        
        # Validate risk thresholds
        if cls.MIN_CONFIDENCE >= cls.HIGH_RISK_THRESHOLD:
            errors.append("MIN_CONFIDENCE must be less than HIGH_RISK_THRESHOLD")
        if cls.HIGH_RISK_THRESHOLD >= cls.CRITICAL_RISK_THRESHOLD:
            errors.append("HIGH_RISK_THRESHOLD must be less than CRITICAL_RISK_THRESHOLD")
        
        # Validate numeric ranges
        if cls.CACHE_TTL <= 0:
            errors.append("CACHE_TTL must be positive")
        if cls.API_TIMEOUT <= 0:
            errors.append("API_TIMEOUT must be positive")
        if cls.MAX_RETRIES < 0:
            errors.append("MAX_RETRIES must be non-negative")
        
        # Validate API keys in production
        if cls.is_production():
            if cls.ETHERSCAN_API_KEY == 'YourApiKeyToken':
                errors.append("ETHERSCAN_API_KEY must be set in production")
            if cls.ENABLE_WEB3_INTEGRATION and not cls.get_web3_provider_url():
                errors.append("Web3 provider must be configured when ENABLE_WEB3_INTEGRATION is true")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """Get a summary of current configuration (excluding sensitive data)"""
        return {
            'environment': 'production' if cls.is_production() else 'development',
            'risk_weights': cls.RISK_WEIGHTS,
            'financial_thresholds': {
                'critical': cls.CRITICAL_FINANCIAL_THRESHOLD,
                'high': cls.HIGH_FINANCIAL_THRESHOLD,
                'medium': cls.MEDIUM_FINANCIAL_THRESHOLD,
                'low': cls.LOW_FINANCIAL_THRESHOLD
            },
            'risk_thresholds': {
                'min_confidence': cls.MIN_CONFIDENCE,
                'high_risk': cls.HIGH_RISK_THRESHOLD,
                'critical_risk': cls.CRITICAL_RISK_THRESHOLD
            },
            'cache_ttl': cls.CACHE_TTL,
            'api_timeout': cls.API_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'feature_flags': {
                'etherscan_api': cls.ENABLE_ETHERSCAN_API,
                'coingecko_api': cls.ENABLE_COINGECKO_API,
                'goplus_api': cls.ENABLE_GOPLUS_API,
                'web3_integration': cls.ENABLE_WEB3_INTEGRATION,
                'metrics': cls.ENABLE_METRICS,
                'persistence': cls.ENABLE_PERSISTENCE
            }
        }
