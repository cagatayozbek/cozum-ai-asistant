"""
Output Format - Yanıt Format Şablonları
Agent'in yanıtlarını nasıl formatlaması gerektiğini tanımlar
"""

OUTPUT_FORMAT = """FORMAT:
- Markdown kullan: **kalın**, *italik*, bullet points
- Kısa paragraflar (max 3-4 cümle)
- Liste şeklinde detay ver
- Detay vermekten çekinme
- **ÖNEMLİ:** Etkinlik/haber cevaplarında:
  * Görseller varsa ![alt](url) formatında MUTLAKA ekle
  * Kaynak linkleri [metin](url) formatında MUTLAKA ekle
  * Bu bilgileri ATLAMAYIN - kullanıcıya gösterin!
"""


def get_output_format() -> str:
    """Output format kurallarını döndürür."""
    return OUTPUT_FORMAT


def build_minimal_system_prompt(
    role_prompt: str,
    style_guide: str,
    context_rules: str,
    output_format: str,
    active_levels: str
) -> str:
    """
    Minimal system prompt (CONTEXT OLMADAN) - Multi-turn conversation için.
    
    Context ayrı bir SystemMessage olarak son mesajdan önce eklenir.
    Bu sayede eski soruların context'i conversation history'de görünmez.
    
    Args:
        role_prompt: Rol tanımı
        style_guide: Üslup kuralları
        context_rules: Bağlam kuralları
        output_format: Çıktı formatı
        active_levels: Aktif eğitim kademeleri
    
    Returns:
        Context OLMADAN system prompt
    """
    return f"""{role_prompt}

{context_rules}

{style_guide}

{output_format}

**Aktif Kademeler:** {active_levels}

🚨 KRİTİK: Sohbet geçmişini GÖREBİLİRSİNİZ ama SADECE EN SON KULLANICI SORUSUNU yanıtlayın!
- Eski soruları ASLA tekrar yanıtlamayın
- Sadece son mesaja odaklanın
- Bağlam SADECE son soru içindir"""


def build_answer_prompt(
    role_prompt: str,
    style_guide: str, 
    context_rules: str,
    output_format: str,
    active_levels: str,
    context: str
) -> str:
    """
    Final answer için tüm promptları birleştirir - ULTRA KOMpakt versiyon.
    
    Args:
        role_prompt: Rol tanımı
        style_guide: Üslup kuralları
        context_rules: Bağlam kuralları
        output_format: Çıktı formatı
        active_levels: Aktif eğitim kademeleri
        context: Retrieve edilen dokümanlar
    
    Returns:
        Birleştirilmiş final answer prompt
    """
    return f"""{role_prompt}

{context_rules}

{style_guide}

**Aktif Kademeler:** {active_levels}

**Bağlam:**
{context}

⚠️ SADECE EN SON KULLANICI SORUSUNU YANITLA (önceki soruları tekrarlama)
"""
