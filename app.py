from ingestion import process_document

import streamlit as st
import os
import glob


def main():
    process_document()
    
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

        equired_delivery_days = st.number_input(
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
            pass
    
    with col3:
        st.text_area(
            "",
            value = output,
            height = 400,
            disabled = True
        )
        
if __name__ == "__main__":
    main()