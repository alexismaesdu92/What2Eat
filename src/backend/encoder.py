from sentence_transformers import SentenceTransformer

class Encoder:
    def __init__(self, model_name: str = "intfloat/e5-base-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str):
        return self.model.encode(text, convert_to_tensor=True)
    



