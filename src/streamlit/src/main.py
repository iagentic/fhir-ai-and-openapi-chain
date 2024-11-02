import streamlit as st

from sidebar import setup as set_sidebar
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import OpenAPIToolkit
from langchain.agents import initialize_agent, AgentType
from langchain.requests import RequestsWrapper

from utils import (
    clear_submit,
    get_spec_url,
    set_logo_and_page_config,
    check_all_config
)

set_logo_and_page_config()
set_sidebar()

st.write("OpenAI API Key added:", st.session_state.get("OPENAI_API_KEY") is not None)
st.write("FHIR Server details added:", st.session_state.get("FHIR_API_BASE_URL") is not None)

if check_all_config():
    spec_url = get_spec_url()
    os.environ["OPENAI_API_KEY"] = st.session_state.get("OPENAI_API_KEY")
    llm = ChatOpenAI(
        model="gpt-4o",
        # openai_api_key=st.session_state.get("OPENAI_API_KEY")
    )

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    }
    requests_wrapper = RequestsWrapper(headers=headers)

    openapi_toolkit = OpenAPIToolkit.from_llm_and_url(
        llm=llm,
        openapi_url=spec_url,
        requests=requests_wrapper
    )

    agent_executor = initialize_agent(
        tools=openapi_toolkit.get_tools(),
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )

    query = st.text_area(
        "Search Input",
        label_visibility="visible",
        placeholder="Ask anything...",
        on_change=clear_submit
    )

    button = st.button("Search")

    if button or st.session_state.get("submit"):
        if not st.session_state.get("is_key_configured"):
            st.error("Please configure your OpenAI API Key!", icon="🚨")
        elif not query:
            st.error("Please enter an input!", icon="🚨")
        else:
            st.session_state["submit"] = True
            with st.spinner(text="Searching..."):
                try:
                    result = agent_executor.run(query)
                    st.write("#### Answer")
                    st.write(result)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
