from dataclasses import dataclass
import os

@dataclass
class Config:
    account_id: str
    app_secret: str
    verify_token: str
    encryption_key: str
    hash_salt: str
    db_path: str = 'data/direct.sqlite'
    ig_token: str = ''
    openai_key: str = ''
    model: str = ''
    graph_version: str = 'v22.0'
    enabled: bool = False
    audio_input: bool = False
    hourly_limit: int = 3
    daily_limit: int = 10
    global_daily_limit: int = 100
    context_ttl: int = 86400
    max_chars: int = 1800

    @classmethod
    def env(cls):
        required=['IG_ACCOUNT_ID','META_APP_SECRET','IG_VERIFY_TOKEN','DATA_ENCRYPTION_KEY','USER_HASH_SALT']
        if any(not os.getenv(k) for k in required):
            raise RuntimeError('Configuração incompleta. Consulte direct_guru/.env.example; valores não são exibidos.')
        return cls(account_id=os.environ['IG_ACCOUNT_ID'],app_secret=os.environ['META_APP_SECRET'],
                   verify_token=os.environ['IG_VERIFY_TOKEN'],encryption_key=os.environ['DATA_ENCRYPTION_KEY'],
                   hash_salt=os.environ['USER_HASH_SALT'],db_path=os.getenv('DB_PATH','data/direct.sqlite'),
                   ig_token=os.getenv('IG_ACCESS_TOKEN',''),openai_key=os.getenv('OPENAI_API_KEY',''),
                   model=os.getenv('OPENAI_MODEL',''),graph_version=os.getenv('META_GRAPH_VERSION','v22.0'),
                   enabled=os.getenv('DIRECT_ENABLED')=='true',audio_input=os.getenv('AUDIO_INPUT_ENABLED')=='true')
