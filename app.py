import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialize session state for view toggle
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'

# Dummy data
categories = ['Rent', 'Food', 'Transport', 'Entertainment', 'Others']
expenses = [500, 300, 150, 100, 50]
dates = pd.date_range(start='2024-01-01', periods=6, freq='M')
monthly_expenses = np.random.randint(400, 800, size=6)

# Function: Dashboard
def show_dashboard():
    st.title("💰 Expense Dashboard")

    # Pie chart
    st.subheader("Expenses by Category")
    fig1, ax1 = plt.subplots()
    ax1.pie(expenses, labels=categories, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    # Line chart
    st.subheader("Monthly Expense Trend")
    df = pd.DataFrame({'Date': dates, 'Expense': monthly_expenses})
    df = df.set_index('Date')
    st.line_chart(df)

    # Button to go to chatbot
    if st.button("🗨️ Chat with BudgetBot"):
        st.session_state.view = 'chat'

# Function: Chatbot
def show_chat():
    st.title("🧠 BudgetBot - Your Expense Assistant")

    # Back button
    if st.button("🔙 Back to Dashboard"):
        st.session_state.view = 'dashboard'

    # Display previous messages
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Ask about your expenses...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Dummy response
        response = "I'm a demo bot. Try asking 'How much did I spend on food?'"
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)

# Render based on view
if st.session_state.view == 'dashboard':
    show_dashboard()
else:
    show_chat()
