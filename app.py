import streamlit as st
from chat import ChatSession, initialize_chat_model
from langgraph.checkpoint.memory import InMemorySaver

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Çözüm Koleji Veli Asistanı",
    page_icon="🎓",
    layout="centered"
)

# Başlık
st.title("🎓 Çözüm Koleji Veli Asistanı")
st.caption("Okul programları, etkinlikler ve eğitim hakkında sorularınızı yanıtlıyorum.")

# Session state başlangıcı
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
    st.session_state.messages = []
    st.session_state.levels = []
    st.session_state.onboarding_done = False
    # LLM ve checkpointer'ı da cache'leyelim
    st.session_state.llm = None
    st.session_state.checkpointer = None

# Sidebar - Kademe seçimi
with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    # Kademe seçimi
    selected_levels = st.multiselect(
        "Hangi kademe(ler) hakkında soru sormak istersiniz?",
        options=["anaokulu", "ilkokul", "ortaokul", "lise"],
        default=st.session_state.levels,
        help="Birden fazla kademe seçebilirsiniz"
    )
    
    st.divider()
    
    # 🆕 Context Compression Toggle (A/B Test)
    st.subheader("🧪 Deney Modu")
    compress_enabled = st.checkbox(
        "Context Compression",
        value=False,  # Default: OFF (full context for better quality)
        help="ON: Dokümanlar sıkıştırılır (60-70% daha az token)\nOFF: Tam dokümanlar kullanılır (daha uzun cevaplar)"
    )
    
    # Compression değişikliği kontrolü
    if st.session_state.chat_session and compress_enabled != st.session_state.chat_session.compress_context:
        st.session_state.chat_session.compress_context = compress_enabled
        st.info(f"🗜️  Compression: {'ON' if compress_enabled else 'OFF'}")
    
    st.divider()
    
    # Kademe değişikliği kontrolü
    if selected_levels != st.session_state.levels and selected_levels:
        st.session_state.levels = selected_levels
        if st.session_state.chat_session is None:
            # İlk başlatma - LLM ve checkpointer oluştur
            if st.session_state.llm is None:
                st.session_state.llm = initialize_chat_model()
                st.session_state.checkpointer = InMemorySaver()
            
            st.session_state.chat_session = ChatSession(
                st.session_state.llm, 
                st.session_state.checkpointer,
                compress_context=compress_enabled  # Kullanıcı seçimine göre
            )
            st.session_state.chat_session.set_levels(selected_levels)
            st.session_state.onboarding_done = True
            # ❌ Onboarding mesajı kaldırıldı - kullanıcı direkt soru sorsun
        else:
            # Kademe değişikliği
            old_levels = st.session_state.chat_session.levels
            st.session_state.chat_session.set_levels(selected_levels)
            
            # Kademe değişikliği bilgilendirmesi (isteğe bağlı)
            if old_levels != selected_levels:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ Kademe güncellendi: {', '.join(selected_levels).title()}"
                })
        st.rerun()
    
    st.divider()
    
    # Yeni sohbet butonu
    if st.button("🔄 Yeni Sohbet", use_container_width=True):
        # Checkpointer'ı temizle (yeni thread ID)
        if st.session_state.chat_session:
            st.session_state.chat_session.clear_history()
        
        # UI state'i sıfırla
        st.session_state.messages = []
        st.session_state.onboarding_done = False if not st.session_state.levels else True
        
        # NOT: chat_session ve levels'ı KORUYORUZ (kullanıcı aynı kademe ile devam edebilir)
        st.rerun()
    
    st.divider()
    st.caption("💡 İpucu: Birden fazla kademe seçerek karşılaştırmalı bilgi alabilirsiniz.")

# Ana chat alanı
if not st.session_state.onboarding_done:
    # Onboarding mesajı
    st.info("👈 Lütfen sol menüden en az bir kademe seçin.")
    st.markdown("""
    ### 🎓 Çözüm Koleji Veli Asistanı'na Hoş Geldiniz!
    
    #### Nasıl Kullanılır?
    
    1. **Kademe Seçin** 👈 Sol menüden ilgilendiğiniz kademe(leri) seçin
    2. **Soru Sorun** 💬 Doğal bir şekilde sorularınızı yazın
    3. **Cevap Alın** ✅ Yapay zeka asistanınız size yardımcı olacak
    
    #### 📝 Örnek Sorular:
    - *"Anaokulu programı nasıl?"*
    - *"İlkokulda kaç saat İngilizce var?"*
    - *"Lisede sınava hazırlık programı var mı?"*
    - *"Spor faaliyetleri neler?"*
    
    #### 💡 İpuçları:
    - Birden fazla kademe seçerek karşılaştırmalı bilgi alabilirsiniz
    - Takip soruları sorabilirsiniz
    - İstediğiniz zaman kademe değiştirebilirsiniz
    """)
else:
    # Chat mesajlarını göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Kullanıcı input
    if prompt := st.chat_input("Sorunuzu yazın..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Bot yanıtını al
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyorum..."):
                response = st.session_state.chat_session.chat(prompt)
                st.markdown(response)
        
        # Bot mesajını kaydet
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
