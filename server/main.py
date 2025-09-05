from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import glob

from .utils import load_config, save_config

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Mount static files
import os
web_assets_path = os.path.join(os.path.dirname(__file__), "..", "web", "dist", "assets")
static_assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")

app.mount("/assets", StaticFiles(directory=web_assets_path), name="assets")
app.mount("/static", StaticFiles(directory=static_assets_path), name="static_assets")

@app.get("/config")
def get_config():
  return load_config()

@app.post("/config")
def update_config(new_config: dict):
  save_config(new_config)
  # Trigger config reload in the bot if it's running
  try:
    import core.state as state
    state.reload_config()
    print("[SERVER] Config reloaded after web update")
  except Exception as e:
    print(f"[SERVER] Could not reload config: {e}")
  return {"status": "success", "data": new_config}

@app.get("/support-cards")
def get_support_cards():
  """Get list of all available support cards"""
  try:
    with open("assets/support/support_urls.json", 'r', encoding='utf-8') as f:
      support_data = json.load(f)

    support_cards = []
    for card in support_data:
      # Extract ID from slug (format: "ID-name")
      slug = card.get("slug", "")
      if "-" in slug:
        card_id = slug.split("-")[0]
        card_name = card.get("name", slug)

        support_cards.append({
          "id": card_id,
          "name": card_name,
          "slug": slug,
          "url": card.get("url", ""),
          "imageUrl": f"/static/support/image/{slug}.jpg",
          "jsonUrl": f"/static/support/combined/{slug}.json"
        })

    print(f"[DEBUG] Returning {len(support_cards)} support cards from support_urls.json")
    return {"support_cards": support_cards}

  except Exception as e:
    print(f"Error loading support_urls.json: {e}")
    # Fallback to old method if new file doesn't exist
    support_cards = []
    json_files = glob.glob("assets/support/combined/*.json")

    for json_file in json_files:
      try:
        card_id = os.path.basename(json_file).split('-')[0]
        card_name = '-'.join(os.path.basename(json_file).split('-')[1:]).replace('.json', '')
        display_name = ' '.join(word.capitalize() for word in card_name.split('-'))

        support_cards.append({
          "id": card_id,
          "name": display_name,
          "imageUrl": f"/static/support/image/{card_id}-{card_name}.jpg",
          "jsonUrl": f"/static/support/combined/{card_id}-{card_name}.json"
        })
      except Exception as e:
        print(f"Error loading {json_file}: {e}")
        continue

    return {"support_cards": support_cards}

@app.get("/support-cards/{card_id}")
def get_support_card_data(card_id: str):
  """Get the JSON data for a specific support card"""
  from .scraper_service import scrape_support_card_on_demand

  json_files = glob.glob(f"assets/support/combined/{card_id}-*.json")

  if not json_files:
    # Try to scrape the support card data
    print(f"[API] Support card {card_id} not found locally, attempting to scrape...")
    success = scrape_support_card_on_demand(card_id, "combined")
    if success:
      # Try again after scraping
      json_files = glob.glob(f"assets/support/combined/{card_id}-*.json")
    else:
      return {"error": f"Support card {card_id} not found and failed to scrape"}

  if not json_files:
    return {"error": "Card not found"}

  try:
    with open(json_files[0], 'r', encoding='utf-8') as f:
      data = json.load(f)
    return data
  except Exception as e:
    return {"error": str(e)}

@app.get("/characters")
def get_characters():
  """Get list of all available characters"""
  try:
    with open("assets/character/character_urls.json", 'r', encoding='utf-8') as f:
      character_data = json.load(f)

    characters = []
    for char in character_data:
      # Skip the profile entry if it exists
      if char.get("slug") == "profiles":
        continue

      # Extract ID from slug (format: "ID-name")
      slug = char.get("slug", "")
      if "-" in slug:
        char_id = slug.split("-")[0]
        raw_name = char.get("name", slug)

        # If name contains the slug format, extract readable name from slug
        if raw_name == slug or "-" in raw_name:
          # Extract name part from slug (everything after first hyphen)
          name_parts = slug.split("-")[1:]
          display_name = ' '.join(word.capitalize() for word in name_parts)
        else:
          display_name = raw_name

        characters.append({
          "id": char_id,
          "name": display_name,
          "slug": slug,
          "url": char.get("url", ""),
          "imageUrl": f"/static/character/image/{slug}.jpg",
          "jsonUrl": f"/static/character/combined/{slug}.json"
        })

    print(f"[DEBUG] Returning {len(characters)} characters from character_urls.json")
    return {"characters": characters}

  except Exception as e:
    print(f"Error loading character_urls.json: {e}")
    # Fallback to old method if new file doesn't exist
    characters = []
    json_files = glob.glob("assets/character/combined/*.json")

    for json_file in json_files:
      try:
        char_id = os.path.basename(json_file).split('-')[0]
        char_name = '-'.join(os.path.basename(json_file).split('-')[1:]).replace('.json', '')
        display_name = ' '.join(word.capitalize() for word in char_name.split('-'))

        characters.append({
          "id": char_id,
          "name": display_name,
          "imageUrl": f"/static/character/image/{char_id}-{char_name}.jpg",
          "jsonUrl": f"/static/character/combined/{char_id}-{char_name}.json"
        })
      except Exception as e:
        print(f"Error loading {json_file}: {e}")
        continue

    return {"characters": characters}

@app.get("/characters/{char_id}")
def get_character_data(char_id: str):
  """Get the JSON data for a specific character"""
  from .scraper_service import scrape_character_on_demand

  json_files = glob.glob(f"assets/character/combined/{char_id}-*.json")

  if not json_files:
    # Try to scrape the character data
    print(f"[API] Character {char_id} not found locally, attempting to scrape...")
    success = scrape_character_on_demand(char_id, "combined")
    if success:
      # Try again after scraping
      json_files = glob.glob(f"assets/character/combined/{char_id}-*.json")
    else:
      return {"error": f"Character {char_id} not found and failed to scrape"}

  if not json_files:
    return {"error": "Character not found"}

  try:
    with open(json_files[0], 'r', encoding='utf-8') as f:
      data = json.load(f)
    return data
  except Exception as e:
    return {"error": str(e)}

@app.get("/debug")
def debug():
  """Debug endpoint to check file paths"""
  import os
  cwd = os.getcwd()
  files = glob.glob("assets/character/combined/*.json")
  return {
    "cwd": cwd,
    "files_found": len(files),
    "first_5_files": files[:5] if files else [],
    "assets_exists": os.path.exists("assets"),
    "character_exists": os.path.exists("assets/character"),
    "combined_exists": os.path.exists("assets/character/combined")
  }

@app.get("/scenarios")
def get_scenarios():
  """Get list of all available scenarios"""
  try:
    with open("assets/scenario/scenario_images.json", 'r', encoding='utf-8') as f:
      scenarios_data = json.load(f)
    
    scenarios = []
    for scenario in scenarios_data:
      scenarios.append({
        "id": scenario["scenario_id"],
        "name": scenario["name"],
        "imageUrl": f"/static/scenario/image/{scenario['image_file']}",
        "jsonUrl": f"/static/scenario/{scenario['scenario_id']}.json"
      })
    
    return {"scenarios": scenarios}
  except Exception as e:
    print(f"Error loading scenarios: {e}")
    return {"scenarios": []}

PATH = "web/dist"

@app.get("/")
async def root_index():
  return FileResponse(os.path.join(PATH, "index.html"), headers={
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
  })

@app.get("/{path:path}")
async def fallback(path: str):
  # Don't handle API routes
  if path.startswith(("config", "support-cards", "characters", "scenarios", "debug")):
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "Not found"}, status_code=404)
  
  file_path = os.path.join(PATH, path)
  headers = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
  }

  if os.path.isfile(file_path):
    media_type = "application/javascript" if file_path.endswith((".js", ".mjs")) else None
    return FileResponse(file_path, media_type=media_type, headers=headers)

  return FileResponse(os.path.join(PATH, "index.html"), headers=headers)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="127.0.0.1", port=8001)