"""
Context Rules - Bağlam Kullanım Kuralları
Agent'in doküman ve context'i nasıl kullanacağını tanımlar
"""

CONTEXT_RULES = """KURALLAR:
1. SADECE verilen BAĞLAM'daki bilgileri kullan - asla uydurma
2. Aktif kademe bilgilerini kullan

"""


def get_context_rules() -> str:
    """Context rules'u döndürür."""
    return CONTEXT_RULES
