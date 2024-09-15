import json
import re
import math


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"\W+", " ", text)
    return text


def load_model(json_file):
    with open(json_file, "r") as f:
        model_json = json.load(f)

    return model_json


def classify_sentence(model, sentence, threshold=50):
    sentence = preprocess_text(sentence)
    words = sentence.split()
    
    # Create bigrams
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    words += bigrams
    
    # Calculate log probabilities for each class
    log_probs = {}
    for cls, prior in zip(model['classes'], model['class_log_prior']):
        log_probs[cls] = prior
    
    for word in words:
        if word in model['vocabulary']:
            index = model['vocabulary'][word]
            for cls in model['classes']:
                log_probs[cls] += model['feature_log_prob'][cls][index]
    
    # Sort log probabilities
    sorted_log_probs = sorted(log_probs.items(), key=lambda item: item[1], reverse=True)
    print(sorted_log_probs[0][1] - sorted_log_probs[1][1])
    
    return 1 if sorted_log_probs[0][1] - sorted_log_probs[1][1] > threshold else 0


class PromptLeakDetector:
    def __init__(self):
        self.model = load_model("./prompt_leak_model.json")

    def detect(self, prompt):
        return classify_sentence(self.model, prompt) == 1 or 'bazinga' in prompt.lower()
