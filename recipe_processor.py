
from dataclasses import dataclass

from transformers import AutoTokenizer, AutoModel
import torch


@dataclass
class ConfigEncoder:
    model_name : str= "intfloat/e5-base-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)


    


class ReceiptProcessor:

    def process_ingredients(self, text):
        pass


if __name__ == '__main__':
    config = ConfigEncoder()