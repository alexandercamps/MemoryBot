"""
This is a Python script that serves as a frontend for a conversational AI model built with the `langchain` and `llms` libraries.
The code creates a web application using Streamlit, a Python library for building interactive web apps.
"""

# Import necessary libraries
import streamlit as st
from PIL import Image
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import re

def is_four_digit_number(string):
    pattern = r'^\d{4}$'  # Matches exactly four digits
    return bool(re.match(pattern, string))


# Set Streamlit page configuration
im = Image.open('sricon.png')
st.set_page_config(page_title=' 🤖ChatGPT with Memory🧠', layout='wide', page_icon = im)
# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "just_sent" not in st.session_state:
    st.session_state["just_sent"] = False
if "temp" not in st.session_state:
    st.session_state["temp"] = ""
if "balance" not in st.session_state:
    st.session_state["balance"] = 0.0
if "deposit" not in st.session_state:
    st.session_state["deposit"] = 3.0

def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


# Define function to get user input
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input", 
                            placeholder="Your AI assistant is here! Ask me anything... Please type your question here", 
                            on_change=clear_text,    
                            label_visibility='hidden')
    input_text = st.session_state["temp"]
    return input_text

# Define function to start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])        
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()

# Set up sidebar with various options
#with st.sidebar.expander("🛠️ ", expanded=False):
#    # Option to preview memory store
#    if st.checkbox("Preview memory store"):
#        with st.expander("Memory-Store", expanded=False):
#            st.session_state.entity_memory.store
#    # Option to preview memory buffer
#    if st.checkbox("Preview memory buffer"):
#        with st.expander("Bufffer-Store", expanded=False):
#            st.session_state.entity_memory.buffer
#    MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo','text-davinci-003','text-davinci-002','code-davinci-002'])
#    K = st.number_input(' (#)Summary of prompts to consider',min_value=3,max_value=1000)

MODEL = "gpt-3.5-turbo"
K = 100

with st.sidebar:
    st.markdown("---")
    st.markdown("# About")
    st.markdown(
       "ChatGPTm is ChatGPT with added memory. "
       "It can do anything you ask and also remember you."
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    st.markdown("---")
    st.markdown("# Introduction")
    st.markdown(
       "ChatGPTm is ChatGPT with added memory. "
       "You can ask any question in the conversation box on the right."
            )
    st.markdown(
       "I hope to provide convenience to friends in China who can't register to use ChatGPT!"
            )
    
# Set up the Streamlit app layout
st.title("🤖 ChatGPT with Memory 🧠")
#st.subheader(" Powered by 🦜 LangChain + OpenAI + Streamlit")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Let user select version
st.write("GPT4.0 is now online! You can experience GPT4.0 that only OpenAI paid users can experience without registering!")
version = st.selectbox("Choose ChatGPT version", ("3.5", "4.0"))
if version == "3.5":
    # Use GPT-3.5 model
    MODEL = "gpt-3.5-turbo"
else:
    # Use GPT-4.0 model
    MODEL = "gpt-4"
    
# Ask the user to enter their OpenAI API key
#API_O = st.sidebar.text_input("API-KEY", type="password")
# Read API from Streamlit secrets
API_O = st.secrets["OPENAI_API_KEY"]

# Session state storage would be ideal
if API_O:
    # Create an OpenAI instance
    llm = OpenAI(temperature=0,
                openai_api_key=API_O, 
                model_name=MODEL, 
                verbose=False) 


    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K )
        
        # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
            llm=llm, 
            prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory
        )  
else:
    st.sidebar.warning('API key required to try this app. The API key is not stored in any form.')
    # st.stop()

# Add a button to start a new chat
#st.sidebar.button("New Chat", on_click = new_chat, type='primary')

# Get the user input
user_input = get_text()

# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input:
    if st.session_state["balance"] > -0.03:
        with get_openai_callback() as cb:
            output = Conversation.run(input=user_input)  
            st.session_state.past.append(user_input)  
            st.session_state.generated.append(output) 
            st.session_state["balance"] -= cb.total_cost * 4
    else:
        st.session_state.past.append(user_input)  
        if is_four_digit_number(user_input) :
            st.session_state["balance"] += st.session_state["deposit"]
            st.session_state.generated.append("Thank you for paying, you can continue to use it.") 
        else: 
            st.session_state.generated.append("Please scan the payment code below to pay ¥10 before you can continue to use it. I will give you another ¥10. Please remember the last four digits of the transfer order number and enter these four digits in the above conversation box.") 

# Allow to download as well
download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="🧐")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])
                            
    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    
    if download_str:
        st.download_button('Download',download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label= f"Conversation-Session:{i}"):
            st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:   
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
        
# Load the images
image1 = Image.open("wechatqrcode_leo.jpg")
image2 = Image.open("zhifubaoqrcode_kyle.jpg")
image3 = Image.open("paypalqrcode.png")
image4 = Image.open("drpang_shipinhao2.jpg")

# Display the image with text on top
st.write("I have to pay OpenAI API for each of your usage. Please consider donating $5 to keep this service alive! Thank you!")
st.write("Your current balance is:", round (st.session_state["balance"]*7, 2), "RMB.")
st.write("I am Dr. Pang, the Stanford Robot. My original intention of providing this application is to allow people in China to also experience and use ChatGPT with added memory. I pay for your every use of calling the OpenAI API, including version 3.5. Please use the WeChat or Alipay QR codes below to pay ¥10 to use it. I will give you another ¥10. This is a pay-as-you-go service.")
st.write("Since I don't have your registration information, if you close the browser or this web page, your balance will be reset to zero, so please do not close the browser or this page while using.")
st.write("Long-term users can pay a yearly fee of ¥1688 (the same fee as OpenAI paid users). Fill in your email, and I will send you a dedicated applet with ten times the memory. ")
st.write("OpenAI charges 20 times more for the GPT4.0 API than for 3.5, so please be aware when using.")
st.write("I have many videos about ChatGPT and how to use ChatGPT magic, and how to use this applet in my WeChat video account 'Stanford Robot Dr. Pang'. There is also a systematic course 'Zero Basic Mastery ChatGPT Magic 6 Lectures' and 'ChatGPT and LLM Application Programming 7 Lectures' for students who are willing to pay for knowledge. ")
st.write("All the already broadcasted courses are in the live replay of my video account homepage. Each lesson is 99 yuan. The first lesson is free for everyone to try. If you want to purchase the entire course, there is a 50% discount, only 299 yuan per course. You can send me a private message on the homepage of my video account to purchase, and specify ChatGPT Magic Course or Programming Course. If you take both courses, you get an additional discount of 100 yuan, only 499 yuan in total.")

#st.image(img, caption=None, width=200)

# Divide the app page into two columns
col1, col2, col3 = st.columns(3)

# Display the first image in the first column
with col1:
    st.image(image1, caption="WeChat Payment", width=200)

# Display the second image in the second column
with col2:
    st.image(image2, caption="Alipay", width=200)

# Display the third image in the third column
with col3:
    st.image(image3, caption="PayPal", width=200)

st.image(image4, caption="Stanford Robot Dr. Pang Video Account, scan with WeChat to go", width=200)
