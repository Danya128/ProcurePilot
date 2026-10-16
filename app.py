from ingestion import process_document
from schemas import PurchaseRequest
from tools import extract_quote_data
from agent import run_agent

import streamlit as st
import os
import glob
import json


@st.fragment(run_every="2s")
def show_approval_status():

    if not os.path.exists("pending_approval.json"):
        return

    with open("pending_approval.json", "r") as file:
        data = json.load(file)

    status = data.get("approval_status")
    manager_note = data.get("manager_note", "")

    if status == "pending":
        st.warning("🟡 Waiting for manager approval")

    elif status == "rejected":
        st.error("🔴 Rejected")

    elif status == "approved":
        st.success("🟢 Approved")

    if manager_note:
        st.info(f"📝 Manager note: {manager_note}")


def main():
    process_document()
    
    st.title("ProcurePilot")
    
    if st.button("New Request"):
        if os.path.exists("pending_approval.json"):
            os.remove("pending_approval.json")

        st.session_state.output = ""

        st.rerun()
    
    st.subheader("Purchase Request")

    col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.3, 2.5, 0.3, 4])
    if "output" not in st.session_state:
        st.session_state.output = ""

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
            min_value=1.0,
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
    
        # upload files into "quotations" folder
        if uploaded_files:
            for file in uploaded_files:
                save_path = os.path.join("quotations", file.name)
            
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
        
        # clean "uploaded_files" folder if user wish so
        if not uploaded_files:
            for file in glob.glob("quotations/*pdf"):
                os.remove(file)

        if st.button("Analyse"):
            # Item request
            request = PurchaseRequest(
                department = department,
                item = item, 
                quantity = quantity,
                max_budget = max_budget,
                required_delivery_days = required_delivery_days
            )
            result = run_agent(request)
            
            result["approval_status"] = "pending"
            result["manager_note"] = ""
            
            with open("pending_approval.json", "w") as file:
                json.dump(result, file, indent=4)
                
            st.session_state.output = result["recommendation"]
            
    
    with col3:
        
        show_approval_status()
            
        st.text_area(
                    "",
                    value=st.session_state.output,
                    height = 400,
                    disabled = True
                )
        
if __name__ == "__main__":
    main()