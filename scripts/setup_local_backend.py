"""Initialise/verify the local SQLite evidence service. No network or extra server."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.api.local_service import handle
if __name__=='__main__':
    if '--daily' in sys.argv:
        from src.api.storage import connect,seed
        from src.api.daily_index import install
        db=connect()
        try:
            seed(db)
            print(json.dumps(install(db,progress=lambda year,rows:print(f'Indexed {year}: {rows} selected daily rows',flush=True)),indent=2))
            from src.api.recent_index import install_recent
            print(json.dumps(install_recent(db),indent=2))
        finally:db.close()
    result=handle({'operation':'health'})
    print(json.dumps(result['body'],ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['http_status']==200 else 1)
