import os
import sys

# Add the 'api' directory to sys.path so helper modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    from api.index import app
    print("\nStarting local development gateway on http://localhost:5000 ...")
    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True)
