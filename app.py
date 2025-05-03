import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from LLMClass import NvidiaChatClient
import asyncio
from bunqapifunc import BunqManager
import nest_asyncio

client = NvidiaChatClient(api_key="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")



manager = BunqManager(api_key="a5a860e2667aa5354ee983ceb286f40a35c097c68e24286def450de5111bb20c")
client.load_saved_index()


def async_to_sync(awaitable):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(awaitable)
    loop.close()
    return result

def load_expenses():
    raw_data = manager.list_all_payments()
    records = []
    for item in raw_data:
        raw_amount = item['amount'].replace(' EUR', '').strip()
        try:
            amount = float(raw_amount.replace(',', ''))
        except ValueError:
            amount = 0.0
        desc = item['description'].strip() if item['description'] else "Unknown"

        # Basic rule-based category
        if 'thuisbezorgd' in desc.lower():
            category = 'Food Delivery'
        elif 'soundcloud' in desc.lower():
            category = 'Subscription'
        elif amount <= -300:
            category = 'Rent/Big Expense'
        else:
            category = 'Other'

        records.append({'Description': desc, 'Amount': amount, 'Category': category})

    return pd.DataFrame(records)

# 🧠 Call LLM for insights
async def getInsights(raw_data):
    return await client.insights(raw_data)

# 📈 Dashboard view
def show_dashboard():
    df = load_expenses()

    st.title("📊 Financial Assistant")
    summary_df = df.groupby('Category')['Amount'].sum().reset_index()

    st.subheader("Payments Overview")
    st.bar_chart(summary_df.set_index('Category'))

    with st.expander("🔍 Insights"):
        st.markdown("### 💡 Recommended Insights")
        insights = async_to_sync(getInsights(df))
        st.markdown(insights)

    st.markdown(
        """
        <style>
        .round-button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 12px 16px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin-top: 20px;
            border-radius: 50%;
            cursor: pointer;
        }
        .round-button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# 🧑‍💼 Chatbot view
def show_chat():
    st.title("🤖 BudgetBot")

    if st.button("🔙 Back to Dashboard"):
        st.session_state.view = 'dashboard'

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).markdown(msg["content"])

    prompt = st.chat_input("Ask anything about your expenses...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.chat_message("assistant"):
            response = async_to_sync(
                client.stream_chat(
                    system_prompt="You are a helpful personal finance assistant. Answer only from the context provided.",
                    user_prompt=prompt
                )
            )
            st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})



# 🔁 Routing logic
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'

if st.button("💬 Chat with BudgetBot"):
    st.session_state.view = 'chat'

if st.session_state.view == 'dashboard':
    show_dashboard()
else:
    show_chat()