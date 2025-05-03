import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from LLMClass import NvidiaChatClient
import asyncio
from bunqapifunc import BunqManager

client = NvidiaChatClient(api_key="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")



manager = BunqManager(api_key="a5a860e2667aa5354ee983ceb286f40a35c097c68e24286def450de5111bb20c")
raw_data = manager.list_all_payments()
# Setup view state
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'

def load_expenses():
    
    # categores = await client.finance_CategoryBot(raw_data)
    # print(categores)
    # Clean and convert to DataFrame
    records = []
    for item in raw_data:
        print(item)
        raw_amount = item['amount'].replace(' EUR', '').strip()
        try:
            amount = float(raw_amount.replace(',', ''))  # Keep sign as-is
        except ValueError:
            amount = 0.0
        desc = item['description'].strip() if item['description'] else "Unknown"
        print(item['description'])
        # Very basic category inference
        if 'thuisbezorgd' in desc.lower():
            category = 'Food Delivery'
        elif 'soundcloud' in desc.lower():
            category = 'Subscription'
        elif amount <= -300:
            category = 'Rent/Big Expense'
        else:
            category = 'Other'

        records.append({'Description': desc, 'Amount': amount, 'Category': category})

    df = pd.DataFrame(records)
    return df
# Function: Dashboard
async def getInsights():
    insights = await client.insights(raw_data)
    return insights
    # print(categores)

def show_dashboard():
    df = load_expenses()

    # Group by category
    st.title("Finanical Assistant")

    # Group by category
    summary_df = df.groupby('Category')['Amount'].sum().reset_index()

    # Bar chart
    st.subheader("Payments Overview")
    st.bar_chart(summary_df.set_index('Category'))

    # Insights Section
    with st.expander("🔍 Insights"):
        st.markdown("### 💡 Recommended Insights")
        insights=asyncio.run(getInsights())
        st.markdown(insights)
        st.markdown("- Entertainment is under control. Great job!")

    # Styled Chat Button
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

    if st.markdown('<a href="#" class="round-button">💬</a>', unsafe_allow_html=True):
        if st.button("Go to Chat"):  # hidden actual logic button
            st.session_state.view = 'chat'

# Function: Chatbot
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
        # Dummy reply
        reply = "I'm a simple bot. Try asking about your largest expense!"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)

# App router
if st.session_state.view == 'dashboard':
    show_dashboard()
else:
    show_chat()
