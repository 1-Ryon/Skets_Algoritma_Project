"""
WSGI configuration untuk FastAPI di PythonAnywhere
"""

import sys
import os

# GANTI 'Ryon' dengan username PythonAnywhere kamu
username = "Ryon"
project_path = f'/home/{username}/Project_Algoritma'

# Debug info
print(f"DEBUG: Starting WSGI configuration...", file=sys.stderr)
print(f"DEBUG: Project path: {project_path}", file=sys.stderr)
print(f"DEBUG: Current directory: {os.getcwd()}", file=sys.stderr)

# Add project path to sys.path
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Change to project directory
try:
    os.chdir(project_path)
    print(f"DEBUG: Changed directory to {project_path}", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Failed to change directory: {e}", file=sys.stderr)

# Try to import app
try:
    from main import app
    
    # For FastAPI on PythonAnywhere with WSGI
    try:
        from asgiref.wsgi import WsgiToAsgi
        application = WsgiToAsgi(app)
        print("DEBUG: Using ASGI adapter for FastAPI", file=sys.stderr)
    except ImportError:
        # Fallback if asgiref not available
        print("DEBUG: asgiref not found, using direct app", file=sys.stderr)
        application = app
    
    print("DEBUG: ✅ App loaded successfully!", file=sys.stderr)
    
except ImportError as e:
    print(f"DEBUG: ❌ Import Error: {e}", file=sys.stderr)
    print(f"DEBUG: Files in directory: {os.listdir('.')}", file=sys.stderr)
    
    # Create a simple fallback app
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return HTMLResponse(f"""
            <h1>Application Loading Error</h1>
            <p>Error: {str(e)}</p>
            <p>Path: {project_path}</p>
            <p>Files: {os.listdir('.')}</p>
            <p>Python: {sys.version}</p>
        """)
    
    application = app
except Exception as e:
    print(f"DEBUG: ❌ Unexpected Error: {e}", file=sys.stderr)
    
    # Emergency fallback
    def application(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        return [b'<h1>System Maintenance</h1><p>Please try again later.</p>']