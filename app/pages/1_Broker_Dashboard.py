import streamlit as st
import pandas as pd
import plotly.express as px
from app.api_client import InsureFlowApiClient

st.set_page_config(layout="wide")

# Function to load and inject CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/styles.css")

st.title("Broker Dashboard - Ark Insurance")

# --- Data Fetching ---
# This would be replaced with a call to the API client
# broker_data = api_client.get_broker_dashboard_data()
# For now, using mock data.
outstanding_premiums_data = [
    {'id': 1, 'Policy Namer': 'PL-8874380', 'Customer Name': 'James Adevemi', 'Due Date': '10/05/2025', 'Amount': 3600000},
    {'id': 2, 'Policy Namer': 'PL-678001', 'Customer Name': 'Grace Ibexwe', 'Due Date': '20/05/2025', 'Amount': 4500000},
    {'id': 3, 'Policy Namer': 'PL-769012', 'Customer Name': 'David Osondu', 'Due Date': '06/06/2025', 'Amount': 2250000}
]
outstanding_premiums_df = pd.DataFrame(outstanding_premiums_data)
outstanding_premiums_df['Select'] = False

commissions_data = {
    'Month': ['March', 'April'],
    'Amount': ['N548,000', 'N628,800']
}
commissions_df = pd.DataFrame(commissions_data)

donut_chart_data = {'Status': ['30+ Days', '600 days'], 'Value': [29, 16]}
donut_df = pd.DataFrame(donut_chart_data)

# --- Layout ---
st.header("Outstanding Premiums")
editable_df = st.data_editor(
    outstanding_premiums_df,
    column_config={
        "Select": st.column_config.CheckboxColumn(required=True),
        "Amount": st.column_config.NumberColumn(format="N %d"),
    },
    disabled=["Policy Namer", "Customer Name", "Due Date", "Amount"],
    hide_index=True,
    use_container_width=True
)

selected_premiums = editable_df[editable_df.Select]
selected_ids = selected_premiums['id'].tolist()

# --- Actions and Summary ---
col1, col2 = st.columns([0.7, 0.3])
with col1:
    if not selected_premiums.empty:
        total_selected = selected_premiums['Amount'].sum()
        st.subheader(f"Total Selected: N {total_selected:,.2f}")
        
        if st.button("Pay Selected Premiums (Bulk Payment)", use_container_width=True):
            api_client = InsureFlowApiClient()
            payment_info, error = api_client.initiate_bulk_payment(selected_ids)
            if error:
                st.error(f"Failed to initiate bulk payment: {error}")
            else:
                st.toast(f"✅ Bulk payment for {len(selected_ids)} premiums initiated!", icon="🚀")
                payment_url = payment_info.get("payment_url")
                st.success("Redirecting to payment gateway...")
                st.markdown(f'<meta http-equiv="refresh" content="0; url={payment_url}">', unsafe_allow_html=True)
    else:
        st.info("Select one or more premiums to make a bulk payment.")

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