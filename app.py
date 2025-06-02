from flask import Flask, request, send_file, jsonify
import json
import uuid
import os
import genanki

app = Flask(__name__)

def safe_id():
    return int(str(uuid.uuid4().int)[:9])

@app.route("/convert", methods=["POST"])
def convert():
    if 'json_file' not in request.files:
        return jsonify({"error": "No JSON file uploaded"}), 400
    
    json_file = request.files['json_file']
    deck_name = request.form.get('deck_name', 'Default Deck')
    output_name = request.form.get('output_name', 'output.apkg')

    try:
        flashcards = json.load(json_file)

        model = genanki.Model(
            model_id=safe_id(),
            name='Universal Flashcard Model',
            fields=[{'name': 'Question'}, {'name': 'Answer'}],
            templates=[{
                'name': 'Card Template',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            }],
            css=".card { font-family: arial; font-size: 14px; text-align: left; }"
        )

        deck = genanki.Deck(deck_id=safe_id(), name=deck_name)

        for card in flashcards.get('questions', []):
            question = card.get("question", "").strip()
            answer = card.get("answer", "").strip()
            tags = card.get("tags", [])
            if question and answer:
                note = genanki.Note(model=model, fields=[question, answer], tags=tags)
                deck.add_note(note)

        output_path = f"/tmp/{output_name}"
        genanki.Package(deck).write_to_file(output_path)
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
