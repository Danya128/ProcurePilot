from schemas import SupplierQuote

import streamlit as st
import json
import os


st.set_page_config(
    page_title="Manager Approval | ProcurePilot",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background: #f5f7fb;
    color-scheme: light;
}

.block-container {
    max-width: 1040px;
    padding-top: 1.75rem;
    padding-bottom: 3rem;
}

div[data-testid="stHeadingWithActionElements"] h1,
div[data-testid="stHeadingWithActionElements"] h2,
div[data-testid="stHeadingWithActionElements"] h3,
h1, h2, h3,
h1 span, h2 span, h3 span,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stWidgetLabel"] p {
    color: #172033 !important;
}

div[data-testid="stHeadingWithActionElements"] h1 {
    letter-spacing: -0.04em;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #dde3ec;
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(23, 32, 51, 0.05);
}

.st-key-request_summary {
    background: #eef4ff !important;
    border-color: #9fb7dc !important;
    border-top: 4px solid #173b73 !important;
    box-shadow: 0 6px 20px rgba(23, 59, 115, 0.08) !important;
}

div[data-baseweb="textarea"],
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border-color: #cbd3df !important;
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
}

div[data-testid="stButton"] button {
    background: #173b73 !important;
    color: #ffffff !important;
    border: 1px solid #173b73 !important;
    min-height: 2.75rem;
    border-radius: 8px;
}

div[data-testid="stButton"] button * {
    color: #ffffff !important;
}

div[data-testid="stButton"] button:hover {
    background: #102d59 !important;
    border-color: #102d59 !important;
}

div[data-testid="stAlert"] p {
    color: #273449 !important;
}
</style>
""", unsafe_allow_html=True)


st.title("Manager Approval")


@st.fragment(run_every="2s")
def show_manager_request():

    if not os.path.exists("pending_approval.json"):
        st.info("No purchase request is waiting for approval.")
        return

    with open("pending_approval.json", "r") as file:
        data = json.load(file)

    request = data["request"]
    comparison = data["comparison"]
    recommendation = data["recommendation"]
    status = data.get("approval_status")

    with st.container(border=True, key="request_summary"):
        request_col, recommendation_col = st.columns(
            [1, 1.4],
            gap="large"
        )

        with request_col:
            st.subheader("Purchase Request")

            st.write(f"Department: {request['department']}")
            st.write(f"Item: {request['item']}")
            st.write(f"Quantity: {request['quantity']}")
            st.write(f"Maximum Budget: €{request['max_budget']}")
            st.write(
                f"Required Delivery: "
                f"{request['required_delivery_days']} days"
            )

        with recommendation_col:
            st.subheader("Agent Recommendation")
            st.write(recommendation)

    st.write("")
    st.subheader("Supplier Comparison")

    supplier_columns = st.columns(2, gap="large")

    for index, supplier in enumerate(comparison):
        with supplier_columns[index % 2]:
            with st.container(border=True):
                st.write(f"### {supplier['supplier']}")
                st.write(f"Price: €{supplier['price']}")
                st.write(
                    f"Delivery: {supplier['delivery_days']} days"
                )
                st.write(
                    f"Warranty: {supplier['warranty_months']} months"
                )
                st.write(f"Approved: {supplier['approved']}")
                st.write(
                    f"Within Budget: {supplier['within_budget']}"
                )

                if supplier["issues"]:
                    st.write("Issues:")

                    for issue in supplier["issues"]:
                        st.write(f"- {issue}")

    if status == "pending":
        
        st.warning("Manager approval required")

        with st.container(border=True):
            manager_note = st.text_area(
                "Manager note",
                placeholder="Leave an optional note..."
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Approve", use_container_width=True):

                    data["approval_status"] = "approved"
                    data["manager_note"] = manager_note.strip()

                    with open("pending_approval.json", "w") as file:
                        json.dump(data, file, indent=4)

                    st.success("Purchase approved")
                    st.rerun()

            with col2:
                if st.button("Reject", use_container_width=True):

                    data["approval_status"] = "rejected"
                    data["manager_note"] = manager_note.strip()

                    with open("pending_approval.json", "w") as file:
                        json.dump(data, file, indent=4)

                    st.error("Purchase rejected")
                    st.rerun()

    elif status == "approved":
        st.success("This request has been approved.")

    elif status == "rejected":
        st.error("This request has been rejected.")

    manager_note = data.get("manager_note", "")

    if status != "pending" and manager_note:
        st.info(f"Manager note: {manager_note}")


show_manager_request()
