"""Report only presence booleans. Never print credentials or account identifiers."""
import json
import os
from pathlib import Path

def main():
    report={'openai_key_present':bool(os.getenv('OPENAI_API_KEY')),
            'script_model_configured':bool(os.getenv('PABLO_SCRIPT_MODEL')),
            'instagram_token_present':bool(os.getenv('IG_ACCESS_TOKEN') or os.getenv('IG_TOKEN')),
            'instagram_account_configured':bool(os.getenv('IG_ACCOUNT_ID') or os.getenv('IG_USER_ID')),
            'instagram_publication_enabled':False}
    Path('output').mkdir(exist_ok=True)
    Path('output/integration_status.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

if __name__=='__main__':main()
