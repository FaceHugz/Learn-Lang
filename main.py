import sys
import requests
import json
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QListWidget, QWidget, QMessageBox)
from gtts import gTTS
import sounddevice as sd
import os
import tempfile

class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.history = []
        # Azure Translator API settings
        self.subscription_key = "92992ec1ed914232b026c03544c8dc31"  # Replace with your actual key
        self.endpoint = "https://api.cognitive.microsofttranslator.com"  # Endpoint URL
        self.location = "eastus"  # Region of your resource
        self.api_version = '3.0'

        self.init_ui()
      
    def init_ui(self):
        self.setWindowTitle("Translator")

    
        layout = QVBoxLayout()

      
        layout.addWidget(QLabel("Source Language:"))
        self.source_language_var = QComboBox()
     
        self.source_language_var.addItems(['en', 'es', 'fr'])
        layout.addWidget(self.source_language_var)

     
        layout.addWidget(QLabel("Target Language:"))
        self.language_var = QComboBox()
       
        self.language_var.addItems(['en', 'es', 'fr'])
        layout.addWidget(self.language_var)

   
        layout.addWidget(QLabel("Input Text:"))
        self.input_text = QLineEdit()
        layout.addWidget(self.input_text)


        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.on_translate)
        layout.addWidget(self.translate_button)

        layout.addWidget(QLabel("Translated Text:"))
        self.translated_text = QLineEdit()
        self.translated_text.setReadOnly(True)
        layout.addWidget(self.translated_text)

   
        self.speech_button = QPushButton("Speak")
        self.speech_button.clicked.connect(self.on_speak)
        layout.addWidget(self.speech_button)

        
        layout.addWidget(QLabel("Translation History:"))
        self.history_listbox = QListWidget()
        layout.addWidget(self.history_listbox)

      
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.on_clear_history)
        layout.addWidget(self.clear_history_button)

        self.setLayout(layout)

    def on_translate(self):
        text = self.input_text.text()
        source_lang = self.source_language_var.currentText()
        target_lang = self.language_var.currentText()

        if not text.strip():
            QMessageBox.critical(self, "Input Error", "Please enter valid text for translation.")
            return

        try:
           
            path = '/translate'
            constructed_url = self.endpoint + path

            params = {
                'api-version': self.api_version,
                'from': source_lang,
                'to': [target_lang]
            }

            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Ocp-Apim-Subscription-Region': self.location,
                'Authorization': "Bearer 141bdebcdadc451f9d9640ac60ca3bb7",
                'Content-Type': 'application/json'
            }

            body = [{'text': text}]
            print(constructed_url)
            response = requests.post(constructed_url, params=params, headers=headers, json=body)
            response_json = response.json()

            if response.status_code == 200:
                translation_text = response_json[0]['translations'][0]['text']
                self.translated_text.setText(translation_text)
                self.history.append(f"{text} -> {translation_text}")
                self.history_listbox.addItem(f"{text} -> {translation_text}")
            else:
                raise Exception(f"Translation failed: {response.status_code}, {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Translation failed: {e}")

    def on_speak(self):
        text = self.translated_text.text()
        if not text.strip():
            QMessageBox.critical(self, "Input Error", "No text to speak.")
            return

        try:
            
            tts = gTTS(text=text, lang=self.language_var.currentText())
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                tts.save(temp_audio_file.name)
                temp_audio_path = temp_audio_file.name

          
            import soundfile as sf
            audio_data, samplerate = sf.read(temp_audio_path)

          
            sd.play(audio_data, samplerate)
            sd.wait()  

           
            os.remove(temp_audio_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Speech synthesis failed: {e}")

    def on_clear_history(self):
        self.history_listbox.clear()
        self.history = []


if __name__ == "__main__":    
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())