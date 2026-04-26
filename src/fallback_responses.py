"""
Fallback response system when OpenAI API is unavailable
"""

def get_fallback_response(query: str, retrieved_docs: list = None) -> str:
    """
    Provide a simple fallback response when OpenAI API is unavailable
    Uses basic keyword matching and retrieved document context
    """
    query_lower = query.lower()
    
    # Common medical keywords and basic responses
    medical_keywords = {
        'fever': "For fever, rest, stay hydrated, and consider fever-reducing medication if needed. Consult a doctor if fever persists or is very high.",
        'headache': "For headaches, try rest, hydration, and over-the-counter pain relievers. If severe or persistent, consult a healthcare provider.",
        'head': "For headaches, try rest, hydration, and over-the-counter pain relievers. If severe or persistent, consult a healthcare provider.",
        'cough': "For cough, stay hydrated, use throat lozenges, and consider honey. If persistent or with other symptoms, see a doctor.",
        'cold': "For cold symptoms, rest, drink fluids, and use appropriate over-the-counter medications. Most colds resolve in 7-10 days.",
        'pain': "For pain management, consider appropriate pain relievers and rest. For severe or persistent pain, consult a healthcare professional.",
        'stomach': "For stomach issues, try bland foods, stay hydrated, and rest. If symptoms persist or worsen, see a doctor.",
        'nausea': "For nausea, try small sips of clear fluids, ginger, or bland foods. If persistent, consult a healthcare provider.",
        'diarrhea': "For diarrhea, stay hydrated with clear fluids and electrolytes. If severe or persistent, see a doctor.",
        'allergy': "For allergies, avoid triggers and consider antihistamines. For severe reactions, seek immediate medical attention.",
        'blood pressure': "Monitor blood pressure regularly, maintain a healthy diet, exercise, and follow your doctor's recommendations.",
        'diabetes': "For diabetes management, monitor blood sugar, follow your diet plan, take medications as prescribed, and see your doctor regularly.",
        'heart': "For heart health, maintain a healthy lifestyle, exercise regularly, eat well, and follow your cardiologist's advice.",
        'breathing': "For breathing difficulties, sit upright, stay calm, and seek immediate medical attention if severe.",
        'chest': "For chest discomfort, avoid strenuous activity and consult a healthcare provider. Seek immediate help for severe chest pain.",
        'infection': "For infections, follow your doctor's treatment plan, take antibiotics as prescribed if given, and maintain good hygiene.",
        'vitamin': "For vitamin deficiencies, eat a balanced diet and consider supplements as recommended by your healthcare provider."
    }
    
    # Check for keywords in the query
    for keyword, response in medical_keywords.items():
        if keyword in query_lower:
            disclaimer = "\n\n⚠️ Note: This is general information only. Always consult with a healthcare professional for proper medical advice."
            return response + disclaimer
    
    # If we have retrieved documents, try to extract relevant information
    if retrieved_docs:
        # Simple text matching approach
        relevant_text = ""
        for doc in retrieved_docs[:2]:  # Use first 2 documents
            if hasattr(doc, 'page_content'):
                doc_content = doc.page_content.lower()
                query_words = query_lower.split()
                # Check if any query words appear in the document
                if any(word in doc_content for word in query_words if len(word) > 3):
                    relevant_text = doc.page_content[:400] + "..."
                    break
        
        if relevant_text:
            return f"Based on available medical information:\n\n{relevant_text}\n\n⚠️ Note: This is general information only. Always consult with a healthcare professional for proper medical advice."
    
    # Default response
    return ("I apologize, but I'm currently unable to process your medical question due to service limitations. "
            "Please consult with a qualified healthcare professional for proper medical advice. "
            "You can also try rephrasing your question or contact your doctor directly.")