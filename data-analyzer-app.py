from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent,create_csv_agent
import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import pandas as pd
import streamlit as st
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
import matplotlib.pyplot as plt
import requests
import uuid
from supabase import create_client, Client
    
# CONSTANT
WEBHOOK_URL = "https://dzulfikar.app.n8n.cloud/webhook/d1c42c7d-76cb-4a39-96d5-bef2b4d0cbdf" #os.getenv("WEBHOOK_URL")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

WEBHOOK_URL2 = "https://dzulfikar.app.n8n.cloud/webhook/9eadd9ce-aae3-4d27-b43e-2165b40c6717"
BEARER_TOKEN2 = os.getenv("BEARER_TOKEN2")

# Supabase client initialization
url = os.getenv("SUPABASE_URL")  # Replace with your Supabase URL
key = os.getenv("SUPABASE_KEY") # Replace with your Supabase API key
supabase: Client = create_client(url, key)

# Adding prefic and suffix

CSV_PROMPT_PREFIX = """
First set the pandas display options to show all the columns,
get the column names, then answer the question.
"""
CSV_PROMPT_SUFFIX = """
- **ALWAYS** before giving the Final Answer, try another method.
Then reflect on the answers of the two methods you did and ask yourself
if it answers correctly the original question.
If you are not sure, try another method.
FORMAT 4 FIGURES OR MORE WITH COMMAS.
- If the methods tried do not give the same result,reflect and
try again until you have two methods that have the same result.
- If you still cannot arrive to a consistent result, say that
you are not sure of the answer.
- If you are sure of the correct answer, create a beautiful
and thorough response using Markdown.
- **DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE,
ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE**.
- **ALWAYS**, as part of your "Final Answer", explain how you got
to the answer on a section that starts with: "\n\nExplanation:\n".
In the explanation, mention the column names that you used to get
to the final answer.
"""

@st.cache_data # Cache_data decorator is used for data input into cache so when refresh session no need to call load_csv again faster performance
def load_csv (file_csv,delimiter_char):
    try :
        df = pd.read_csv(file_csv, sep=delimiter_char, engine="python")
        logging.info("CSV loaded successfully")
        return df
    except Exception as e :
        print(f"An Error Occured : {e}")
        return None

# Create agent CSV
@st.cache_resource #Cache_data decorator to speed up calling expensive object or resouce like model llm or machine learning
def agent_csv(df_csv):
    llm = ChatOpenAI(model = "gpt-4-turbo", api_key=os.getenv("OPENAI_KEY")) #another model : gpt-4o
    agent = create_pandas_dataframe_agent(
        llm=llm,
        agent_type= 'openai-tools',
        df = df_csv,
        verbose = True,
        allow_dangerous_code=True # Due to some warnings, we need to set this to True
        )
    return agent

@st.cache_data
def cached_summary (response):
    return response

# Create horizontal bar chart
def h_bar_chart (df) :
    data_count = df.value_counts()
    
    #Turn data into list
    names = list(data_count.index)
    counts = list(data_count.values)
    
    fig, ax = plt.subplots()
    ax.barh(names, counts, color="skyblue", edgecolor="black")

    ax.set_title("Histogram of Variable")
    ax.set_xlabel('Frequency')
    ax.set_ylabel("Variable")

    return [fig,ax]

# Create mode or procedure for Intelligent Document Analysis
def generate_session_id():
    return str(uuid.uuid4())
def send_message_to_llm(session_id, message):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["output"]
    else:
        return f"Error: {response.status_code} - {response.text}"

def send_message_to_llm_2(session_id, message):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN2}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    response = requests.post(WEBHOOK_URL2, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["output"]
    else:
        return f"Error: {response.status_code} - {response.text}"    


def itenasis_mode():
    # Initialize session state
    st.caption("Intelligent Document Analysis")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Processing your question...") :
            # Get LLM response
            llm_response = send_message_to_llm(st.session_state.session_id, user_input)

            # Add LLM response to chat history
            st.session_state.messages.append({"role": "assistant", "content": llm_response})
            with st.chat_message("assistant"):
                st.write(llm_response)

def query_analysis_mode():
    # Initialize session state
    st.caption("QUERY ANALYSIS")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        llm_response= send_message_to_llm_2(st.session_state.session_id, user_input)

        # Add LLM response to chat history
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.write(llm_response)                

# Function to create login form
def create_login_form():
    st.title("Login to Le-Velocity ITENASIS 🤖 ")
    email = st.text_input("Email", "")
    password = st.text_input("Password", "", type="password")
    
    if st.button("Login"):
        if email and password:
            try :
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if user:
                    st.session_state.user = user.user
                    st.session_state['logged_in'] = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error("Invalid credentials")
        else:
            st.warning("Please enter both email and password")

# Show main content
def main_content():
    # Streamlit UI
    st.set_page_config(layout="wide")
    st.title("La-VELOCITY - Lampung Virtual Assistant PLN for Document Analytic 🤖")
    st.caption("By : Dzulfikar S")

    # Sidebar dropdown menu
    with st.sidebar: # Create hideable sidebar
        option = st.sidebar.selectbox("Choose Mode:", ["Intelligent Document Analysis","Data Query Analysis","Chat With Data", "Data Visualization"])
        st.caption("**Intelligent Documen Analysis** : Let you interact or chat about Document like BPM, IK, PR, SOP, etc")
        st.caption ("**Data Query Analysis** : Let you interact or with Tabular Data that require perform Query")
        st.caption ("**Chat With Data** : Let you interact or chat with data powered by AI")
        st.caption ("**Data Visualization** : To visualize data using interactive tab")


        # Handle Setting or custom delimiter
        delimiter_options = {
            "Comma (,)": ",",
            "Tab (\\t)": "\t",
            "Semicolon (;)": ";",
            "Pipe (|)": "|",
            "Space ( )": " ",
            "Custom": None  # User-defined delimiter
        }
        delimiter_choice = st.selectbox("Setting Delimiter CSV", list(delimiter_options.keys()))
        # If user selects custom, allow text input
        if delimiter_choice == "Custom":
            custom_delimiter = st.text_input("Enter custom delimiter", value=",")
            delimiter = custom_delimiter
        else:
            delimiter = delimiter_options[delimiter_choice]   
        st.divider()
        # Show session user
        st.caption(f"👨‍💻 Login as :  {st.session_state.user.email}")
        
        st.divider()        
        st.caption("Develop by Dzulfikar Shubhy")




    if option == "Intelligent Document Analysis" :
        # st.write("ITENASIS MODE")
        itenasis_mode()

    elif option == "Data Query Analysis":
        query_analysis_mode()


    else:
        # File uploader for CSV
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        # Load CSV
        try:
            df = load_csv (uploaded_file,delimiter)
        except Exception as e:
            st.error(f"Error reading file: {e}")

        # Display the DataFrame preview
        if uploaded_file :
        # Question input
            st.write('🖹 **DATA PREVIEW** : ')
            st.dataframe(df.head())
            
            # st.write(f"Button Summarized Clicked : {st.session_state['btn_summarize']}")
            
            # Generate Summarization AI
            if st.button("Generate Data Summarization by AI"):
                st.session_state['btn_summarize'] += 1
                try :
                    # Calling agent
                    agent = agent_csv(df)
                    with st.spinner("Generating Data Summary...") :
                        question_1 = "Generate Data Summary"
                        summary = "THIS IS SUMMARY AI RESPONSE"
                        summary = agent.run(question_1)
                        
                        st.success("✅ Response:")
                        st.write(summary)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            
            # Chat with DATA
            if option == "Chat With Data" :
                st.subheader("🤖 Chat with Your CSV Data")
                question = st.text_area("Enter your question about the data:")        
                if  st.button("Generate Response"):
                    try :
                        # Calling agent
                        agent = agent_csv(df)
                        with st.spinner("Processing your question...") :
                            response = agent.run(question)
                            # response = agent.run(CSV_PROMPT_PREFIX + question + CSV_PROMPT_SUFFIX)
                            st.success("✅ Response:")
                            st.write(response)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
        
            # Data Visualization
            elif option == "Data Visualization":
                st.subheader("📊 Data Visualization")
                
                pyg_app = StreamlitRenderer(df)
                pyg_app.explorer()
            


        else:
            st.warning("Please upload a CSV file")


def main():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        create_login_form()
    else:
        main_content()

if __name__ == "__main__":
    main()