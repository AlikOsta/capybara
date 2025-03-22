from mistralai import Mistral
from django.conf import settings

def moderate_review(text):
    client = Mistral(api_key=settings.MISTRAL_API_KEY)
    
    response = client.classifiers.moderate_chat(
        model="mistral-moderation-latest",
        inputs=[{"role": "user", "content": text}]
    )
    
    category_scores = response.results[0].category_scores
    
    has_violations = any(
        category_score > 0.5 
        for category_score in category_scores.values()
    )
    

    return not has_violations
