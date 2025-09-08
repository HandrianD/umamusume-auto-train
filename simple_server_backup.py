#!/usr/bin/env python3
"""
Simple HTTP server for serving             elif self.path == '/wanted-skills':
                self.update_wanted_skills()atic files without FastAPI dependencies
Uses only Python built-in libraries
    def serve_support_cards(self):
        """Serve support cards (simplified)"""
        self.serve_json({"support_cards": []})

    def serve_characters(self):
        """Serve characters (simplified)"""
        self.serve_json({"characters": []})

    def serve_race_positions(self):
        """Serve race positions data"""
        try:
            with open("assets/race_positions.json", 'r', encoding='utf-8') as f:
                race_positions = json.load(f)
            self.serve_json(race_positions)
        except Exception as e:
            self.serve_json({"positions": ["front", "pace", "late", "end"], "race_types": ["sprint", "mile", "medium", "long"], "error": str(e)}, 500)

    def serve_wanted_skills(self):port os
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

class SimpleAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Don't set directory to avoid conflicts
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        print(f"[DEBUG] Request path: {path}")
        
        try:
            # API endpoints
            if path == '/config':
                self.serve_config()
            elif path == '/skills':
                self.serve_skills()
            elif path.startswith('/skills/search'):
                query_params = parse_qs(parsed_path.query)
                query = query_params.get('query', [''])[0]
                self.serve_skill_search(query)
            elif path == '/support-cards':
                self.serve_support_cards()
            elif path == '/characters':
                self.serve_characters()
            elif path == '/race-positions':
                self.serve_race_positions()
            elif path == '/wanted-skills':
                self.serve_wanted_skills()
            else:
                # Serve static files (web assets, skill images, etc.)
                if path.startswith('/static/'):
                    # Remove /static prefix and serve from assets
                    file_path = path[8:]  # Remove '/static/'
                    self.serve_static_file(f"assets/{file_path}")
                elif path.startswith('/assets/'):
                    # Serve web assets
                    file_path = path[8:]  # Remove '/assets/'
                    self.serve_static_file(f"web/dist/assets/{file_path}")
                else:
                    # Serve web files
                    if path == '/' or path == '':
                        self.serve_static_file("web/dist/index.html")
                    else:
                        self.serve_static_file(f"web/dist{path}")
        except Exception as e:
            print(f"Error handling request {path}: {e}")
            self.send_error(500)

    def do_POST(self):
        try:
            if self.path == '/config':
                self.update_config()
            else:
                self.send_error(404)
        except Exception as e:
            print(f"Error handling POST {self.path}: {e}")
            self.send_error(500)

    def serve_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def serve_static_file(self, file_path):
        """Serve static file"""
        if os.path.exists(file_path):
            # Read and serve the file directly
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Set appropriate content type
            if file_path.endswith('.html'):
                content_type = 'text/html'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.json'):
                content_type = 'application/json'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

    def serve_config(self):
        """Serve configuration"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.serve_json(config)
        except Exception as e:
            self.serve_json({"error": str(e)}, 500)

    def update_config(self):
        """Update configuration"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            new_config = json.loads(post_data.decode('utf-8'))
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            
            # Reload config in bot if running
            try:
                import core.state as state
                state.reload_config()
                print("[SERVER] Config reloaded after web update")
            except Exception as e:
                print(f"[SERVER] Could not reload config: {e}")
            
            self.serve_json({"status": "success", "data": new_config})
        except Exception as e:
            self.serve_json({"error": str(e)}, 500)

    def serve_skills(self):
        """Serve skills data"""
        try:
            with open("assets/skill/nested/skill_data.json", 'r', encoding='utf-8') as f:
                skill_data = json.load(f)

            skills = skill_data.get("skills", [])
            
            # Transform skills for frontend
            enhanced_skills = []
            for skill in skills:
                enhanced_skill = {
                    "id": skill.get("id", ""),
                    "name": skill.get("name_en", ""),
                    "name_jp": skill.get("name_jp", ""),
                    "description": skill.get("description_en", ""),
                    "icon_url": skill.get("icon_url", "").replace("assets/skill/image/", "/static/skill/image/"),
                    "scraped_at": skill.get("scraped_at", ""),
                    "source": skill.get("source", "")
                }
                enhanced_skills.append(enhanced_skill)

            self.serve_json({"skills": enhanced_skills})
        except Exception as e:
            # Fallback to old format
            try:
                with open("data/skills.json", 'r', encoding='utf-8') as f:
                    old_skills = json.load(f)
                
                enhanced_skills = []
                for skill in old_skills:
                    enhanced_skill = {
                        "id": "",
                        "name": skill.get("name", ""),
                        "name_jp": "",
                        "description": skill.get("description", ""),
                        "icon_url": "",
                        "scraped_at": "",
                        "source": "fallback"
                    }
                    enhanced_skills.append(enhanced_skill)
                
                self.serve_json({"skills": enhanced_skills})
            except Exception as e2:
                self.serve_json({"skills": [], "error": str(e2)}, 500)

    def serve_skill_search(self, query):
        """Search skills"""
        try:
            with open("assets/skill/nested/skill_data.json", 'r', encoding='utf-8') as f:
                skill_data = json.load(f)

            skills = skill_data.get("skills", [])
            query_lower = query.lower()

            if not query:
                results = skills[:50]  # Return first 50 if no query
            else:
                results = []
                for skill in skills:
                    name_en = skill.get("name_en", "").lower()
                    name_jp = skill.get("name_jp", "").lower()
                    description = skill.get("description_en", "").lower()

                    if (query_lower in name_en or
                        query_lower in name_jp or
                        query_lower in description):
                        results.append(skill)
                        if len(results) >= 50:
                            break

            # Transform results
            enhanced_results = []
            for skill in results:
                enhanced_skill = {
                    "id": skill.get("id", ""),
                    "name": skill.get("name_en", ""),
                    "name_jp": skill.get("name_jp", ""),
                    "description": skill.get("description_en", ""),
                    "icon_url": skill.get("icon_url", "").replace("assets/skill/image/", "/static/skill/image/"),
                    "scraped_at": skill.get("scraped_at", ""),
                    "source": skill.get("source", "")
                }
                enhanced_results.append(enhanced_skill)

            self.serve_json({"skills": enhanced_results, "query": query, "total": len(enhanced_results)})
        except Exception as e:
            self.serve_json({"skills": [], "error": str(e)}, 500)

    def serve_support_cards(self):
        """Serve support cards (simplified)"""
        self.serve_json({"support_cards": []})

    def serve_characters(self):
        """Serve characters (simplified)"""
        self.serve_json({"characters": []})

    def serve_scenarios(self):
        """Serve scenarios (simplified)"""
        self.serve_json({"scenarios": []})

    def serve_race_positions(self):
        """Serve race positions data"""
        try:
            with open("assets/race_positions.json", 'r', encoding='utf-8') as f:
                race_positions = json.load(f)
            self.serve_json({"race_positions": race_positions})
        except Exception as e:
            self.serve_json({"race_positions": [], "error": str(e)}, 500)

    def serve_wanted_skills(self):
        """Serve wanted skills data from config"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            wanted_skills = config.get('wanted_skills', [])
            self.serve_json({"wanted_skills": wanted_skills})
        except Exception as e:
            self.serve_json({"wanted_skills": [], "error": str(e)}, 500)

    def update_wanted_skills(self):
        """Update wanted skills in config"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            new_wanted_skills_data = json.loads(post_data.decode('utf-8'))
            
            # Read current config
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update wanted skills
            config['wanted_skills'] = new_wanted_skills_data.get('wanted_skills', [])
            
            # Save updated config
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Reload config in bot if running
            try:
                import core.state as state
                state.reload_config()
                print("[SERVER] Config reloaded after wanted skills update")
            except Exception as e:
                print(f"[SERVER] Could not reload config: {e}")
            
            self.serve_json({"status": "success", "data": new_wanted_skills_data})
        except Exception as e:
            self.serve_json({"error": str(e)}, 500)

def start_server(port=8001):
    """Start the simple HTTP server"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", port), SimpleAPIHandler) as httpd:
        print(f"🚀 Simple server running on http://localhost:{port}")
        print("📁 Serving skills data without FastAPI dependencies")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n⏹️  Server stopped")

if __name__ == "__main__":
    start_server()
