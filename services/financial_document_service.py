import re


class FinancialDocumentProcessor:
    _instance = None

    @staticmethod
    def get_instance():
        """החזרת אובייקט סינגלטון"""
        if FinancialDocumentProcessor._instance is None:
            FinancialDocumentProcessor._instance = FinancialDocumentProcessor()
        return FinancialDocumentProcessor._instance

    def __init__(self):
        """יוצרים את המילון עם המילים הרלוונטיות לשפות"""
        if FinancialDocumentProcessor._instance is not None:
            raise Exception(
                "This is a singleton class, use get_instance() to get the instance")

        # מילים מפתח עבור מסמכים כספיים בשפות שונות
        self.keywords = {
            'he': [r"\b(חשבונית|הוצאה|סכום לתשלום|החזר|תשלום|חשבונית מס|קבלה)\b", r"\b(מעמ|מע״מ|מס ערך מוסף|שיעור מע״מ|לא כולל מע״מ)\b"],
            'en': [r"\b(invoice|receipt|payment|total|amount|tax|vat)\b", r"\b(Total|Amount|Invoice|Receipt|Tax|VAT)\b"],
            'es': [r"\b(factura|recibo|pago|total|cantidad|impuesto|iva)\b", r"\b(total|cantidad|factura|recibo|impuesto|iva)\b"],
            'fr': [r"\b(facture|reçu|paiement|total|montant|taxe|tva)\b", r"\b(total|montant|facture|reçu|taxe|tva)\b"],
            'de': [r"\b(Rechnung|Quittung|Zahlung|Gesamt|Betrag|Steuer|MwSt)\b", r"\b(Gesamt|Betrag|Rechnung|Quittung|Steuer|MwSt)\b"],
            'it': [r"\b(fattura|ricevuta|pagamento|totale|importo|tassa|iva)\b", r"\b(totale|importo|fattura|ricevuta|tassa|iva)\b"]
        }

        # ביטוי רגולרי לזיהוי תאריכים
        self.date_pattern = r"\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})\b"

        # ביטוי רגולרי לזיהוי סכומים כספיים
        self.currency_pattern = r"\b(?:₪|\$|€|£)?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b"

    def detect_language(self, text):
        """
        פונקציה לזיהוי שפה על בסיס מילים מפתח.

        פרמטרים:
        text (str): הטקסט לבדיקה

        מחזירה:
        str: קוד השפה (לדוגמה, 'en' לאנגלית, 'he' לעברית, וכו')
        """
        for lang, lang_keywords in self.keywords.items():
            for keyword in lang_keywords:
                if re.search(keyword, text, re.IGNORECASE):
                    return lang
        return "unknown"

    def is_financial_document(self, text):
        """
        פונקציה לבדוק אם הטקסט מכיל תוכן כספי.

        פרמטרים:
        text (str): הטקסט לבדיקה

        מחזירה:
        tuple: (bool, str, list) - טופל שמציין אם מדובר במסמך כספי, שפה שהתגלתה ורשימה של מילות מפתח שנמצאו
        """
        try:
            # זיהוי השפה של הטקסט
            detected_lang = self.detect_language(text)

            # אם השפה נמצאת ברשימה של מילים מפתח
            if detected_lang in self.keywords:
                detected_keywords = set()

                # בדיקת מילים מפתח הקשורות למסמכים כספיים בטקסט
                for keyword in self.keywords[detected_lang]:
                    if re.search(keyword, text, re.IGNORECASE):
                        detected_keywords.add("Invoice/Expense")

                # בדיקת תאריכים בטקסט (עשוי להעיד על רשומה כספית)
                if re.search(self.date_pattern, text):
                    detected_keywords.add("Date")

                # בדיקת סכומים כספיים בטקסט
                if re.search(self.currency_pattern, text):
                    detected_keywords.add("Monetary Amount")

                # אם נמצאו מילים מפתח או סכומים כספיים, נחשב את זה למסמך כספי
                if detected_keywords:
                    return True, detected_lang, detected_keywords
                else:
                    return False, detected_lang, []
            else:
                return False, detected_lang, []

        except Exception as e:
            # במקרה של שגיאה, מחזירים False
            return False, "", set()
