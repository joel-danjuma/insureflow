import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Function to load and inject CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/styles.css")

st.title("Broker Dashboard - Ark Insurance")

# --- Mock Data ---
outstanding_premiums_data = {
    'Policy Namer': ['PL-8874380', 'PL-678001', 'PL-769012'],
    'Customer Name': ['James Adevemi', 'Grace Ibexwe', 'David Osondu'],
    'Due Date': ['10/05/2025', '20/05/2025', '06/06/2025'],
    'Amount': ['N 3,600,000', 'N 4,500,000', 'N 2,250,000']
}
outstanding_premiums_df = pd.DataFrame(outstanding_premiums_data)

commissions_data = {
    'Month': ['March', 'April'],
    'Amount': ['N548,000', 'N628,800']
}
commissions_df = pd.DataFrame(commissions_data)

donut_chart_data = {'Status': ['30+ Days', '600 days'], 'Value': [29, 16]}
donut_df = pd.DataFrame(donut_chart_data)

# --- Layout ---
st.header("Outstanding Premiums")
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.dataframe(outstanding_premiums_df, use_container_width=True)
with col2:
    st.button("FILTER", use_container_width=True)
    st.button("IMPORT", use_container_width=True)


col3, col4 = st.columns(2)

with col3:
    st.subheader("Reminders")
    st.info("✉️ Automated Renewal Reminder (10/04/2925)")
    st.info("✉️ Send Payment Reminder (15/04/2025)")

    st.subheader("Total: 6,600.00")
    
    c1, c2 = st.columns(2)
    with c1:
        st.button("Custom Account", use_container_width=True)
    with c2:
        st.button("Bulk Payment", use_container_width=True)


with col4:
    st.subheader("My Commissions")
    st.dataframe(commissions_df, use_container_width=True)

    fig = px.pie(donut_df, names='Status', values='Value', hole=0.6, title="60%<br>38+ days")
    fig.update_layout(showlegend=False)
    fig.update_traces(textinfo='none')
    st.plotly_chart(fig, use_container_width=True) 