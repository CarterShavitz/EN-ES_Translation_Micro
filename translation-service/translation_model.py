from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class TranslationModel:
    def __init__(self):
        self.model_name = "Helsinki-NLP/opus-mt-en-es"
        self.tokenizer = None
        self.model = None
        self.max_length = 128
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    def load_model(self):
        """Load the translation model and tokenizer"""
        print(f"Loading model {self.model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
        print("Model loaded successfully")
    
    def translate(self, text):
        """Translate English text to Spanish"""
        if not text:
            return ""
        
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            output = self.model.generate(**inputs, max_length=self.max_length)
        
        # Decode the generated tokens
        translation = self.tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        
        return translation

# Singleton instance
translation_model = None

def get_translation_model():
    """Get or create the translation model singleton"""
    global translation_model
    if translation_model is None:
        translation_model = TranslationModel()
    return translation_model
