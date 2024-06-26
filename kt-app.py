# Import necessary libraries.
import streamlit as st
import os
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding

mistral_key = st.secrets["mistral_key"]

# Define LLM and embedding model
Settings.llm = MistralAI(model="mistral-small", api_key=mistral_key)
Settings.embed_model = MistralAIEmbedding(model_name='mistral-embed', api_key=mistral_key)

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="Store")
index = load_index_from_storage(storage_context, embed_model=MistralAIEmbedding(model_name='mistral-embed', api_key=mistral_key))
query_engine = index.as_query_engine(similarity_top_k=3)

################################################################################################################

# Set web page title, icon, and layout
st.set_page_config(
    page_title="RachelBot 💬 Kontiki",
    page_icon=":robot:",
    layout="wide"  # Set layout to wide for better organization
)

col1, col2, col3 = st.columns([5,5.5,1])

with col1:
    st.write("")

with col2:
    st.image("https://portale.arci.it/media/loghi/GIUSTIZIA_CLIMATICA_ORA_.jpg", width=100)

with col3:
    st.write("")

# Display title and description
st.markdown("<h1 style='color: #007FA4; text-align: center;'> Hey, come posso aiutarti?</h1>", unsafe_allow_html=True)
st.write("<h4 style='text-align: center;'>Sono RachelBot, l'assistente AI del Kontiki</h4>", unsafe_allow_html=True)
st.write("<h6 style='text-align: center;'>Chiedi a me tutto quello che chiederesti a Rachele, così non la disturberai! Qui sotto trovi degli esempi di domande 🌊😊</h6>", unsafe_allow_html=True)

st.markdown('#') 
st.markdown('#') 

st.write("Prova una di queste domande:   \n- Che cos'è il Kontiki?   \n- Come si fa il turno bar?   \n- Quali piatti di pasta abbiamo in menù?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# React to user input
if prompt := st.chat_input("Cosa vuoi sapere?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    prompt_italian=str(prompt + ". Rispondi sempre e solo in italiano")
    
    raw_response = query_engine.query(prompt_italian)
    
    # Display the response.
    response_text = raw_response.response
    response = f"{response_text}"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
        # Iterate over keys in the metadata dictionary
        with st.expander("Più info"):
            for key, value in raw_response.metadata.items():
                file_name = value.get('file_name')
                if "Bar" in file_name:
                    st.write("Guarda questo documento: [Kontiki Bar e Servizio](https://docs.google.com/document/d/13P4xlpopMB81XRbelK_A9eBGWO9zmiPKf_2PozQdiqY/edit)")
                elif "Ricettario" in file_name:
                    st.write("Guarda questo documento: [Kontiki Ricettario](https://docs.google.com/document/d/1lju2IPflfzaxF5x0BpCd5V6z1qZm1VB71eKTgFRmNKM/edit)")    
                elif "frighi" in file_name:
                    st.write("Guarda questo documento: [Kontiki Frighi e magazzino](https://docs.google.com/document/d/1y-k-nclI3btENprJNMok8qA6RPqFUIJGL21MtkFqsZo/edit)")
                elif "generali" in file_name:
                    st.write("Guarda il nostro sito: [Kontiki](https://kontiki.giustiziaclimaticaora.it/)")  
                    break  # Exit the loop once the file_name is found
                    
    st.session_state.messages.append({"role": "assistant", "content": response})
