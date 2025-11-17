"""
Context Compression Node
Retrieved dokümanları sıkıştırarak token kullanımını azaltır
"""

from state_schema import ChatState
from typing import List, Tuple
import re


def compress_chunk(content: str, max_sentences: int = 3) -> str:
    """
    Bir chunk'ı sıkıştırır - en önemli 2-3 cümleyi tutar.
    
    Strategy:
    1. Cümlelere ayır
    2. İlk cümle (genelde özet) + son 1-2 cümle (detay)
    3. Gereksiz ifadeleri temizle
    
    Args:
        content: Orijinal chunk içeriği
        max_sentences: Maksimum cümle sayısı
    
    Returns:
        Sıkıştırılmış içerik
    """
    # Cümlelere ayır (. ! ? ile biten)
    sentences = re.split(r'[.!?]\s+', content.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return content
    
    # İlk cümle + son 2 cümle al (genelde en önemli bilgiler)
    compressed = [sentences[0]]  # İlk cümle (özet)
    
    if len(sentences) > 2:
        compressed.extend(sentences[-(max_sentences-1):])  # Son N-1 cümle
    
    # Birleştir
    result = ". ".join(compressed)
    if not result.endswith('.'):
        result += "."
    
    return result


def semantic_reduce_context(context: str, max_chunks: int = 3) -> str:
    """
    Context'i semantik olarak sıkıştırır.
    
    Strategy:
    1. Her dokümanı ayrı chunk olarak işle
    2. Her chunk'tan en önemli 2-3 cümleyi al
    3. Maksimum 3 chunk tut (en yüksek score'lular)
    
    Args:
        context: Retrieve node'dan gelen full context
        max_chunks: Maksimum chunk sayısı
    
    Returns:
        Sıkıştırılmış context
    """
    if not context or "Bilgi bulunamadı" in context:
        return context
    
    # Context'i chunk'lara ayır (--- separator)
    chunks = context.split("\n\n---\n\n")
    
    if len(chunks) <= max_chunks:
        # Zaten az, sadece her chunk'ı sıkıştır
        compressed_chunks = []
        for chunk in chunks:
            # Başlığı ayır
            lines = chunk.split("\n", 1)
            if len(lines) == 2:
                header, content = lines
                compressed_content = compress_chunk(content, max_sentences=3)
                compressed_chunks.append(f"{header}\n{compressed_content}")
            else:
                compressed_chunks.append(chunk)
        
        return "\n\n---\n\n".join(compressed_chunks)
    
    # Çok fazla chunk var - sadece ilk N'i al (FAISS zaten score'a göre sıralamış)
    selected_chunks = chunks[:max_chunks]
    
    compressed_chunks = []
    for chunk in selected_chunks:
        lines = chunk.split("\n", 1)
        if len(lines) == 2:
            header, content = lines
            compressed_content = compress_chunk(content, max_sentences=3)
            compressed_chunks.append(f"{header}\n{compressed_content}")
        else:
            compressed_chunks.append(chunk)
    
    return "\n\n---\n\n".join(compressed_chunks)


def context_compression_node(state: ChatState) -> ChatState:
    """
    Context compression node - retrieved context'i sıkıştırır.
    
    Token Reduction Strategy:
    1. Her chunk'tan maksimum 3 cümle tut
    2. Maksimum 3 chunk kullan
    3. ~70% token reduction (2000 token → 600 token)
    
    Args:
        state: Current conversation state
    
    Returns:
        Updated state with compressed context
    """
    original_context = state.get("retrieved_context", "")
    
    if not original_context or "Bilgi bulunamadı" in original_context:
        print(f"\n🗜️  [COMPRESSION NODE] Context yok, compression skip")
        return state
    
    # Original stats
    original_words = len(original_context.split())
    original_chars = len(original_context)
    
    print(f"\n🗜️  [COMPRESSION NODE] Context sıkıştırılıyor...")
    print(f"   Orijinal: {original_words} kelime, {original_chars} karakter")
    
    # Compress
    compressed_context = semantic_reduce_context(original_context, max_chunks=3)
    
    # New stats
    compressed_words = len(compressed_context.split())
    compressed_chars = len(compressed_context)
    reduction_pct = ((original_chars - compressed_chars) / original_chars * 100) if original_chars > 0 else 0
    
    print(f"   Sıkıştırılmış: {compressed_words} kelime, {compressed_chars} karakter")
    print(f"   📉 Reduction: {reduction_pct:.1f}%")
    
    # Update state
    state["retrieved_context"] = compressed_context
    
    return state


# Test
if __name__ == "__main__":
    """Test context compression"""
    
    # Mock context (4 chunks)
    test_context = """**[ANAOKULU] İngilizce Eğitimi**
Anaokulumuzda İngilizce eğitimi Cambridge programı ile verilmektedir. Haftada 12 saat Main Course ve 2 saat Think&Talk dersi bulunmaktadır. Native speaker öğretmenler eşliğinde eğitim verilir. BookR dijital platform kullanılmaktadır. Dil duşu yöntemi uygulanmaktadır.

---

**[ANAOKULU] Spor Faaliyetleri**
Anaokulumuzda çocukların fiziksel gelişimini desteklemek amacıyla çeşitli spor aktiviteleri düzenlenmektedir. Hareket oyunları, koordinasyon çalışmaları, ritim aktiviteleri yapılmaktadır. Haftada 3 saat beden eğitimi dersi vardır. Profesyonel spor eğitmenleri görev almaktadır.

---

**[ANAOKULU] Sanat Atölyeleri**
Görsel sanatlar eğitimi kapsamında resim, heykel, kolaj çalışmaları yapılmaktadır. Çocukların yaratıcılığını geliştiren projeler uygulanır. Müzik atölyeleri mevcuttur. Orff çalgıları kullanılmaktadır.

---

**[ANAOKULU] EDUxLab Programı**
EDUxLab atölyeleri haftada 2 saat olarak uygulanmaktadır. Proje tabanlı öğrenme yaklaşımı benimsenir. STEM eğitimi verilir. Robotik kodlama dersleri mevcuttur."""
    
    # Create mock state
    mock_state = ChatState(
        messages=[],
        user_query="Anaokulu programı nedir?",
        intent="education",
        intent_confidence=0.95,
        intent_reasoning="Test",
        active_levels=["anaokulu"],
        retrieved_context=test_context,
        final_answer=None,
        error=None
    )
    
    print("="*80)
    print("🧪 CONTEXT COMPRESSION TEST")
    print("="*80)
    
    # Compress
    result_state = context_compression_node(mock_state)
    
    print("\n📄 COMPRESSED CONTEXT:")
    print("="*80)
    print(result_state["retrieved_context"])
    print("="*80)
