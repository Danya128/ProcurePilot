import streamlit as st

st.title("ProcurePilot")
st.subheader("Purchase Request")

col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.3, 2.5, 0.3, 4])
output = None

with col1:
    department = st.text_input("Department")
    item = st.text_input("Item")
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        step=1
    )

    max_budget = st.number_input(
        "Maximum budget (€)",
        min_value=0.0,
        step=100.0
    )

    required_delivery_days = st.number_input(
        "Required delivery (days)",
        min_value=1,
        step=1
    )

with col2:
    st.subheader("Supplier Quotations")

    uploaded_files = st.file_uploader(
        "Upload supplier quotation PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Analyse"):
        pass
    
with col3:
    st.text_area(
        "",
        value = output,
        height = 400,
        disabled = True
    )