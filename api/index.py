from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder="../templates")

def parse_identifiers(identifiers):
    data = {"discord": None, "steam": None, "steam_id64": None}
    for info in identifiers:
        if info.startswith("discord:"):
            data["discord"] = info.replace("discord:", "")
        elif info.startswith("steam:"):
            steam_hex = info.replace("steam:", "")
            data["steam_id64"] = str(int(steam_hex, 16))
            data["steam"] = f"https://steamcommunity.com/profiles/{data['steam_id64']}"
    return data


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/fetch_all", methods=["POST"])
def fetch_all():
    server_ip = request.form.get("server_ip")
    url = f"http://{server_ip}/players.json"

    headers = {
        "User-Agent": "CitizenFX/1.0",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        players = response.json()

        processed_players = []

        for p in players:
            ids = parse_identifiers(p.get("identifiers", []))

            processed_players.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "ping": p.get("ping"),
                "discord": ids["discord"],
                "steam": ids["steam"],
                "steam_id64": ids["steam_id64"],
                "endpoint": p.get("endpoint", "Private")
            })

        return jsonify(processed_players)

    except Exception as e:
        return jsonify({"error": str(e)})


app.debug = False
application = app
