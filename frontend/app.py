import streamlit as st
import requests

st.set_page_config(page_title="ai2query", layout="centered")

# ----------------------------
# Styling
# ----------------------------
st.markdown("""
<style>
    .stTextInput input {
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stChatMessage {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .stChatMessage.user {
        background-color: #e8f0ff;
    }
    .stChatMessage.assistant {
        background-color: #eafde3;
    }
    .block-container {
        padding-top: 2rem;
    }
    .status-ok {
        color: green;
        font-weight: bold;
    }
    .status-fail {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Title + Status Display
# ----------------------------
st.title("ai2query – SQL Assistant")

if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "schema_ok" not in st.session_state:
    st.session_state["schema_ok"] = False
if "history" not in st.session_state:
    st.session_state["history"] = []

# ----------------------------
# DB Connection Form
# ----------------------------
with st.expander("Connect to Database", expanded=True):
    with st.form("db_form"):
        col1, col2 = st.columns(2)
        host = col1.text_input("Host", value="postgres")
        port = col2.text_input("Port", value="5432")
        dbname = st.text_input("Database Name", value="ai2query")
        user = st.text_input("Username", value="user")
        password = st.text_input("Password", type="password", value="pass")

        submitted = st.form_submit_button("Connect to Database")

        if submitted:
            creds = {
                "host": host,
                "port": int(port),
                "dbname": dbname,
                "user": user,
                "password": password
            }
            try:
                res = requests.post("http://backend:8000/connect", json=creds)
                res.raise_for_status()
                data = res.json()

                if data.get("status") == "connected":
                    st.session_state["connected"] = True
                    st.session_state["schema_ok"] = True
                    st.success("Connected and schema loaded successfully.")
                else:
                    st.session_state["connected"] = False
                    st.session_state["schema_ok"] = False
                    st.error(f"Connection failed: {data.get('detail', 'Unknown error')}")
            except Exception as e:
                st.session_state["connected"] = False
                st.session_state["schema_ok"] = False
                st.error(f"Failed to connect: {e}")

# ----------------------------
# Connection Status Badge
# ----------------------------
col_status1, col_status2 = st.columns(2)
with col_status1:
    st.markdown("**Connection Status:** " + (
        "<span class='status-ok'>Connected</span>" if st.session_state["connected"] else "<span class='status-fail'>Not connected</span>"
    ), unsafe_allow_html=True)

with col_status2:
    st.markdown("**Schema Status:** " + (
        "<span class='status-ok'>Loaded</span>" if st.session_state["schema_ok"] else "<span class='status-fail'>Unavailable</span>"
    ), unsafe_allow_html=True)

# ----------------------------
# Chat UI
# ----------------------------
st.divider()
st.subheader("Ask your data")

for msg in st.session_state["history"]:
    st.chat_message(msg["role"]).markdown(msg["content"])

user_prompt = st.chat_input("Ask your question in natural language...")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state["history"].append({"role": "user", "content": user_prompt})

    if not st.session_state["connected"] or not st.session_state["schema_ok"]:
        st.error("Please connect to the database first.")
    else:
        try:
            payload = {"question": user_prompt}
            res = requests.post("http://backend:8000/generate", json=payload)
            res.raise_for_status()

            data = res.json()
            sql = data.get("sql", "No SQL returned.")
            preview = data.get("preview", [])
            explanation = data.get("explanation", "")
            plan = data.get("plan", "")

            response_text = f"```sql\n{sql}\n```"

            if preview:
                response_text += "\n\n**Preview:**\n"
                for row in preview:
                    response_text += f"- {row}\n"

            if explanation:
                response_text += f"\n\n**Explanation:**\n{explanation}"

            if plan:
                response_text += f"\n\n**Query Plan:**\n{plan}"

            st.chat_message("assistant").markdown(response_text)
            st.session_state["history"].append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Failed to generate SQL: {e}")

