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
                st.session_state.checkpointer
            )
            st.session_state.chat_session.set_levels(selected_levels)
            st.session_state.onboarding_done = True
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✨ Merhaba! {', '.join(selected_levels).title()} kademesi hakkında size yardımcı olabilirim. Sorularınızı sorabilirsiniz."
            })
        else:
            # Kademe değişikliği
            st.session_state.chat_session.set_levels(selected_levels)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Kademe güncellendi: {', '.join(selected_levels).title()}"
            })
        st.rerun()
    
    st.divider()
    
    # Yeni sohbet butonu
    if st.button("🔄 Yeni Sohbet", use_container_width=True):
        st.session_state.chat_session = None
        st.session_state.messages = []
        st.session_state.levels = []
        st.session_state.onboarding_done = False
        # LLM ve checkpointer'ı koru, sadece session'ı sıfırla
        st.rerun()
    
    st.divider()
    st.caption("💡 İpucu: Birden fazla kademe seçerek karşılaştırmalı bilgi alabilirsiniz.")

# Ana chat alanı
if not st.session_state.onboarding_done:
    # Onboarding mesajı
    st.info("👈 Lütfen sol menüden en az bir kademe seçin.")
    st.markdown("""
    ### Nasıl Kullanılır?
    
    1. **Sol menüden** ilgilendiğiniz kademe(leri) seçin
    2. **Soru sorun**: "Anaokulu programı nedir?", "Lise biyoloji kaç saat?"
    3. **Sohbet edin**: Doğal bir şekilde sorularınızı sorun
    
    ### Örnek Sorular:
    - Anaokulu programı nasıl?
    - İlkokulda kaç saat İngilizce var?
    - Lise ve ortaokul matematik saatlerini karşılaştır
    - Hangi kademelerde robotik kodlama var?
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
