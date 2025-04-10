import re

# Keywords for financial documents in different languages
keywords = {
    'he': [r"\b(חשבונית|הוצאה|סכום לתשלום|החזר|תשלום|חשבונית מס|קבלה)\b", r"\b(מעמ|מע״מ|מס ערך מוסף|שיעור מע״מ|לא כולל מע״מ)\b"],
    'en': [r"\b(invoice|receipt|payment|total|amount|tax|vat)\b", r"\b(Total|Amount|Invoice|Receipt|Tax|VAT)\b"],
    'es': [r"\b(factura|recibo|pago|total|cantidad|impuesto|iva)\b", r"\b(total|cantidad|factura|recibo|impuesto|iva)\b"],
    'fr': [r"\b(facture|reçu|paiement|total|montant|taxe|tva)\b", r"\b(total|montant|facture|reçu|taxe|tva)\b"],
    'de': [r"\b(Rechnung|Quittung|Zahlung|Gesamt|Betrag|Steuer|MwSt)\b", r"\b(Gesamt|Betrag|Rechnung|Quittung|Steuer|MwSt)\b"],
    'it': [r"\b(fattura|ricevuta|pagamento|totale|importo|tassa|iva)\b", r"\b(totale|importo|fattura|ricevuta|tassa|iva)\b"]
}

# Regular Expression to detect dates in formats like dd/mm/yyyy or yyyy-mm-dd
date_pattern = r"\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})\b"

# Regular Expression to detect monetary amounts
currency_pattern = r"\b(?:₪|\$|€|£)?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b"

def detect_language(text):
    """
    Function to detect language based on specific keywords.
    
    Parameters:
    text (str): The input text to be analyzed.
    
    Returns:
    str: Language code (e.g., 'en' for English, 'he' for Hebrew, etc.)
    """
    for lang, lang_keywords in keywords.items():
        for keyword in lang_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                return lang
    return "unknown"

def is_financial_document(text):
    """
    Function to check if the provided text contains financial content.
    
    Parameters:
    text (str): The input text to be analyzed.
    
    Returns:
    tuple: (bool, str, list) - A tuple where:
        - bool indicates whether the document is financial or not,
        - str represents the detected language of the text,
        - list contains detected keywords related to financial content.
    """
    try:
        # Detect the language of the text using the custom function
        detected_lang = detect_language(text)
        
        # Check if the detected language is in our predefined keywords list
        if detected_lang in keywords:
            detected_keywords = []
            
            # Check for the presence of financial-related keywords in the text
            for keyword in keywords[detected_lang]:
                if re.search(keyword, text, re.IGNORECASE):
                    detected_keywords.append("Invoice/Expense")
            
            # Check if dates are mentioned in the text (could indicate a financial record)
            if re.search(date_pattern, text):
                detected_keywords.append("Date")
            
            # Check if monetary amounts are mentioned in the text
            if re.search(currency_pattern, text):
                detected_keywords.append("Monetary Amount")
            
            # If any financial keywords or amounts are detected, consider it a financial document
            if detected_keywords:
                return True, detected_lang, detected_keywords
            else:
                return False, detected_lang, []
        else:
            return False, detected_lang, []
    
    except Exception as e:
        # Return False if an error occurs during processing
        return False, "", []
