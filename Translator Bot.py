import os
from google.cloud import translate_v2 as translate

# Set up the Translation API client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/credentials.json'
translate_client = translate.Client()

# Define a function to translate text
def translate_text(text, target_language):
    # Use the Translation API to translate the text
    result = translate_client.translate(text, target_language=target_language)

    # Return the translated text
    return result['translatedText']

# Example usage
text = 'Hello, how are you?'
target_language = 'es'
translated_text = translate_text(text, target_language)
print(translated_text)
