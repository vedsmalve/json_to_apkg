import os
import uuid
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import genanki

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return "✅ JSON to Anki .apkg backend is live!"

@app.route('/generate', methods=['POST'])
def generate_apkg():
    try:
        data = request.get_json()

        if not data or 'questions' not in data:
            return jsonify({'error': 'Invalid input format. Expected a JSON with a "questions" key.'}), 400

        # Get deck name from JSON, default if missing
        deck_name = data.get('deckName', 'My Anki Deck')

        # Generate unique IDs for model and deck
        model_id = uuid.uuid4().int >> 96
        model = genanki.Model(
            model_id,
            'Simple Model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'}
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                },
            ])

        deck_id = uuid.uuid4().int >> 96
        deck = genanki.Deck(deck_id, deck_name)

        for item in data['questions']:
            question = item.get('question', '').strip()
            answer = item.get('answer', '').strip()
            if question and answer:
                note = genanki.Note(model=model, fields=[question, answer])
                deck.add_note(note)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.apkg') as tmp:
            genanki.Package(deck).write_to_file(tmp.name)
            tmp.flush()
            return send_file(tmp.name, as_attachment=True, download_name='anki_deck.apkg')

    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
