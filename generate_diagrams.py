import base64
import zlib
import urllib.request
import os

def save_diagram(input_path, output_path):
    try:
        if not os.path.exists(input_path):
            print(f"File not found: {input_path}")
            return

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        url = "https://kroki.io/mermaid/png"
        print(f"Downloading diagram from {os.path.basename(input_path)} via POST...")
        
        # POST request with raw content
        req = urllib.request.Request(url, data=content.encode('utf-8'), method='POST')
        req.add_header('Content-Type', 'text/plain')
        
        with urllib.request.urlopen(req) as response:
            data = response.read()
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"✅ Saved to {output_path}")
    except Exception as e:
        print(f"❌ Error processing {input_path}: {e}")

if __name__ == "__main__":
    # Paths to the mermaid files I created earlier
    base_artifact_path = r"C:\Users\Gabriel Guilhem\.gemini\antigravity\brain\7d807bc0-e16d-4809-b20e-c658a49e63fc"
    
    files = [
        (os.path.join(base_artifact_path, "diagrama_classes.mermaid"), "diagrama_classes.png"),
        (os.path.join(base_artifact_path, "diagrama_casos_uso.mermaid"), "diagrama_casos_uso.png")
    ]
    
    for input_p, output_p in files:
        save_diagram(input_p, output_p)
