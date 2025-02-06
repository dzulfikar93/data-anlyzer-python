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
    
# CONSTANT
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


def load_csv (file_csv):
    try :
        df = pd.read_csv(file_csv)
        logging.info("CSV loaded successfully")
        return df
    except Exception as e :
        print(f"An Error Occured : {e}")
        return None

#Create llm model
def create_llm ():
    try :
        llm = ChatOpenAI(model = "gpt-4-turbo", api_key=os.getenv("OPENAI_KEY")) #another model : gpt-4o
        return llm
    except Exception as e :
        print(f"An Error Occurred : {e}")
        return None

# Create agent CSV
def agent_csv(df_csv):
    llm = create_llm()
    agent = create_pandas_dataframe_agent(
        llm=llm,
        agent_type= 'openai-tools',
        df = df_csv,
        verbose = True,
        allow_dangerous_code=True # Due to some warnings, we need to set this to True
        )
    return agent

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



def main():
    # Streamlit UI
    st.set_page_config(layout="wide")
    st.title("📊 CSV Query Agent AI")
    st.caption("By : Dzulfikar S")

    # Sidebar dropdown menu
    with st.sidebar: # Create hideable sidebar
        option = st.sidebar.selectbox("Choose Mode:", ["Chat With Data", "Data Visualization"])
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

        st.caption("Develop by Dzulfikar Shubhy")

    # File uploader for CSV
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    # Load CSV
    try:
        df = pd.read_csv(uploaded_file, sep=delimiter, engine="python")
    except Exception as e:
        st.error(f"Error reading file: {e}")

    # Display the DataFrame preview
    if uploaded_file :
    # Question input
        st.write('🖹 **DATA PREVIEW** : ')
        st.dataframe(df.head())
        if option == "Chat With Data" :
            st.subheader("🤖 Chat with Your CSV Data")
            question = st.text_area("Enter your question about the data:")        
            if  st.button("Generate Response"):
                try :
                    # Calling agent
                    agent = agent_csv(df)
                    with st.spinner("Processing your question...") :
                        response = agent.run(CSV_PROMPT_PREFIX + question + CSV_PROMPT_SUFFIX)
                        st.success("✅ Response:")
                        st.write(response)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        elif option == "Data Visualization":
            st.subheader("📊 Data Visualization")
            
            pyg_app = StreamlitRenderer(df)
            pyg_app.explorer()
        


    else:
        st.warning("Please upload a CSV file")

if __name__ == "__main__":
    main()