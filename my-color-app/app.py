from flask import Flask
import os
import socket

app = Flask(__name__)

@app.route("/")
def hello():
    # 1. Container ID pata karna (Hostname hi container ID hota hai)
    container_id = socket.gethostname()

    # 2. Environment Variable se Color lena
    # Agar variable nahi mila, to default 'lightred' use karega.
    bg_color = os.environ.get("APP_COLOR","lightred")
    
    # Version tag (Optional, update dekhne ke liye)
    version_tag = os.environ.get("APP_VERSION", "v1")

    # HTML Response
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>K8s Visualizer</title>
        <style>
            body {{
                background-color: {bg_color}; 
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                transition: background-color 0.5s ease;
            }}
            .card {{
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
            }}
            h1 {{ margin: 0; color: #333; }}
            p {{ font-size: 1.5em; color: #555; }}
            .id-box {{
                background: #222;
                color: #00ff00;
                padding: 15px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                font-size: 1.2em;
                margin-top: 20px;
            }}
            .version {{ color: {bg_color}; font-weight: bold;}}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Deployment Visualizer</h1>
            <p>Version: <span class="version">{version_tag}</span></p>
            <p>Served by Container ID:</p>
            <div class="id-box">{container_id}</div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    # Flask ko 0.0.0.0 pe chalana zaruri hai container ke liye
    app.run(host='0.0.0.0', port=5000)