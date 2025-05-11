"""
Simple English to Spanish translator using a dictionary of common words.
This is used as a fallback when the ML model is not available.
"""

class SimpleTranslator:
    def __init__(self):
        # Dictionary of common English to Spanish translations
        self.dictionary = {
            # Common greetings and phrases
            "hello": "hola",
            "hi": "hola",
            "goodbye": "adiós",
            "bye": "adiós",
            "thank you": "gracias",
            "thanks": "gracias",
            "please": "por favor",
            "sorry": "lo siento",
            "excuse me": "disculpe",
            "good morning": "buenos días",
            "good afternoon": "buenas tardes",
            "good evening": "buenas noches",
            "good night": "buenas noches",
            "how are you": "¿cómo estás?",
            "i'm fine": "estoy bien",
            "nice to meet you": "encantado de conocerte",
            
            # Common verbs
            "to be": "ser/estar",
            "to have": "tener",
            "to do": "hacer",
            "to say": "decir",
            "to go": "ir",
            "to come": "venir",
            "to see": "ver",
            "to know": "saber/conocer",
            "to want": "querer",
            "to need": "necesitar",
            "to find": "encontrar",
            "to give": "dar",
            "to tell": "decir",
            "to work": "trabajar",
            "to call": "llamar",
            "to try": "intentar",
            "to ask": "preguntar",
            "to help": "ayudar",
            "to love": "amar",
            "to live": "vivir",
            
            # Common adjectives
            "good": "bueno",
            "bad": "malo",
            "big": "grande",
            "small": "pequeño",
            "new": "nuevo",
            "old": "viejo",
            "happy": "feliz",
            "sad": "triste",
            "beautiful": "hermoso",
            "ugly": "feo",
            "easy": "fácil",
            "difficult": "difícil",
            "important": "importante",
            "interesting": "interesante",
            
            # Conjunctions
            "and": "y",
            "or": "o",
            "but": "pero",
            "because": "porque",
            "if": "si",
            "then": "entonces",
            
            # Articles
            "the": "el/la/los/las",
            "a": "un/una",
            "an": "un/una",
        }
    
    def translate(self, text):
        """
        Translate English text to Spanish using the dictionary.
        For words not in the dictionary, keep the original word.
        """
        if not text:
            return ""
        
        # Convert to lowercase for dictionary lookup
        text_lower = text.lower()
        
        # Check if the entire phrase is in the dictionary
        if text_lower in self.dictionary:
            return self.dictionary[text_lower]
        
        # Split the text into words
        words = text.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = word.lower().strip(".,;:!?\"'()[]{}")
            
            # Check if the word is in the dictionary
            if clean_word in self.dictionary:
                # Preserve original capitalization
                if word[0].isupper():
                    translated = self.dictionary[clean_word].capitalize()
                else:
                    translated = self.dictionary[clean_word]
                
                # Add back any punctuation
                if word[-1] in ".,;:!?\"'()[]{}":
                    translated += word[-1]
                
                translated_words.append(translated)
            else:
                # Keep the original word if not found
                translated_words.append(word)
        
        # Join the translated words back into a sentence
        return " ".join(translated_words)

# Singleton instance
simple_translator = None

def get_simple_translator():
    """Get or create the simple translator singleton"""
    global simple_translator
    if simple_translator is None:
        simple_translator = SimpleTranslator()
    return simple_translator
