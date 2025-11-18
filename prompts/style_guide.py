"""
Style Guide - Yanıt Üslubu ve Format Kuralları
Agent'in nasıl yanıt vereceğini tanımlar
"""

STYLE_GUIDE = """ÜSLUP:
- "Siz" ile hitap edin (resmi ama samimi)
- Yanıtların açıklayıcı ve bilgilendirici olmasına özen gösterin
- Bilgi yoksa: "Bu konuda bilgi bulamadım, okul iletişim kanallarını kullanın"
- Ücret soruları: "Ücret için okul iletişim kanallarına başvurun"
"""


def get_style_guide() -> str:
    """Style guide'ı döndürür."""
    return STYLE_GUIDE
