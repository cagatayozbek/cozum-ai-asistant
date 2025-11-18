"""
Answer Node
Final yanıtı oluşturur (LLM ile)
"""

from state_schema import ChatState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from prompts.role_prompt import get_role_prompt
from prompts.style_guide import get_style_guide
from prompts.context_rules import get_context_rules
from prompts.output_format import get_output_format, build_minimal_system_prompt


def answer_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> ChatState:
    """
    Answer node - final yanıtı oluşturur.
    
    Args:
        state: Current conversation state
        llm: LangChain LLM instance
    
    Returns:
        Updated state with final answer
    """
    intent = state.get("intent", "unknown")
    query = state["user_query"]
    context = state.get("retrieved_context", "")
    active_levels = state.get("active_levels", [])
    
    print(f"\n💬 [ANSWER NODE] Final yanıt oluşturuluyor...")
    print(f"   Intent: {intent}")
    
    # Greeting intent - direkt yanıt ver
    if intent == "greeting":
        answer = "Merhaba! Ben Çözüm Eğitim Kurumları'nın veli asistanıyım. Size nasıl yardımcı olabilirim?"
        state["final_answer"] = answer
        print(f"   ✅ Greeting yanıtı oluşturuldu")
        return state
    
    # Unknown intent - fallback
    if intent == "unknown":
        answer = "Üzgünüm, sorunuzu tam olarak anlayamadım. Eğitim programları, etkinlikler veya okul hakkında başka bir şey sormak ister misiniz?"
        state["final_answer"] = answer
        print(f"   ⚠️  Unknown intent - fallback yanıt")
        return state
    
    # Price intent - contact info
    if intent == "price":
        answer = """Ücret bilgileri için lütfen okul iletişim kanallarımızdan bizimle irtibata geçin:

📞 **Telefon:** [okul telefonu]
📧 **E-posta:** [okul email]
🌐 **Website:** [okul website]

Kayıt ve ücret konusundaki tüm detayları size aktaracaklardır."""
        state["final_answer"] = answer
        print(f"   💰 Price inquiry - contact info verildi")
        return state
    
    # Education/Event intents - LLM ile yanıt oluştur
    active_levels_str = ", ".join(active_levels).title() if active_levels else "Tüm kademeler"
    
    # Build minimal system prompt (context OLMADAN - multi-turn için)
    minimal_system_prompt = build_minimal_system_prompt(
        role_prompt=get_role_prompt(),
        style_guide=get_style_guide(),
        context_rules=get_context_rules(),
        output_format=get_output_format(),
        active_levels=active_levels_str
    )
    
    # Get conversation history (sliding window)
    messages = state.get("messages", [])
    recent_messages = messages[-10:] if len(messages) > 10 else messages  # Last 10 messages
    
    # Build messages for LLM - Context'i SON mesajdan ÖNCE ekle!
    # Bu sayede context SADECE son soruyla ilişkilendirilir
    if len(recent_messages) > 0:
        last_human_message = recent_messages[-1]
        conversation_history = recent_messages[:-1]
    else:
        last_human_message = HumanMessage(content=query)
        conversation_history = []
    
    llm_messages = [
        SystemMessage(content=minimal_system_prompt),      # Rol & kurallar (context YOK!)
        *conversation_history,                             # Eski conversation (context'ler YOK!)
        AIMessage(content=f"""İşte sorunuzla ilgili bulduğum bilgiler:

{context}"""),  # ← Context: Assistant'ın referans bilgisi (LangChain pattern)
        last_human_message                                 # Kullanıcının son sorusu
    ]
    
    print(f"   📝 LLM'e gönderilen mesaj sayısı: {len(llm_messages)} (sliding window + context injection)")
    
    # Generate answer
    response = llm.invoke(llm_messages)
    answer = response.content if isinstance(response.content, str) else str(response.content)
    
    # Update state
    state["final_answer"] = answer
    
    print(f"   ✅ Final yanıt oluşturuldu ({len(answer)} karakter)")
    
    return state


def direct_answer_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> ChatState:
    """
    Direct answer node - context olmadan direkt yanıt ver (greeting, unknown).
    
    Bu node retrieve yapmadan direkt yanıt üretir.
    """
    return answer_node(state, llm)


def search_news_node(state: ChatState) -> ChatState:
    """
    Search news node - okul haberleri ve etkinlikler (placeholder).
    
    TODO: Gerçek web scraping veya API entegrasyonu eklenecek.
    """
    print(f"\n📰 [SEARCH NEWS NODE] Haber/etkinlik arama (placeholder)")
    
    # Placeholder response
    state["retrieved_context"] = "🚧 Haber ve etkinlik arama özelliği henüz aktif değil."
    
    return state


def price_info_node(state: ChatState) -> ChatState:
    """
    Price info node - ücret bilgileri için iletişim yönlendirmesi.
    
    Ücret soruları için direkt contact info verir.
    """
    print(f"\n💰 [PRICE INFO NODE] Ücret sorgusu - contact info hazırlanıyor")
    
    # No context needed - answer_node will handle
    state["retrieved_context"] = "Price inquiry - contact info"
    
    return state
