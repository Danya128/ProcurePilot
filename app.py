from ingestion import process_document
from schemas import PurchaseRequest
from tools import extract_quote_data
from agent import run_agent

import streamlit as st
import os
import glob
import json


st.set_page_config(
    page_title="ProcurePilot",
    layout="wide"
)


# =========================================================
# UI STYLE
# =========================================================

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
div[data-testid="stWidgetLabel"] p,
div[data-testid="stCaptionContainer"] p {
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

div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="textarea"],
[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border-color: #cbd3df !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] div {
    color: #334155 !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-baseweb="textarea"] textarea,
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    caret-color: #173b73 !important;
    cursor: text !important;
}

div[data-testid="stNumberInput"] button {
    background: #eef2f7 !important;
    color: #334155 !important;
    border-color: #cbd3df !important;
}

div[data-testid="stNumberInput"] button:disabled {
    background: #f1f5f9 !important;
    color: #94a3b8 !important;
    opacity: 1 !important;
    cursor: not-allowed !important;
}

div[data-testid="stNumberInput"] button svg,
div[data-testid="stNumberInput"] button svg path {
    color: currentColor !important;
    fill: currentColor !important;
    stroke: currentColor !important;
}

div[data-testid="stTextArea"] textarea:disabled {
    background: #f8fafc !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    opacity: 1 !important;
}

div[data-testid="stButton"] button,
[data-testid="stFileUploaderDropzone"] button {
    background: #173b73 !important;
    color: #ffffff !important;
    border: 1px solid #173b73 !important;
    min-height: 2.75rem;
    border-radius: 8px;
}

div[data-testid="stButton"] button *,
[data-testid="stFileUploaderDropzone"] button * {
    color: #ffffff !important;
}

div[data-testid="stButton"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #102d59 !important;
    border-color: #102d59 !important;
}

div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] small,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] *,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] *,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderPagination"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderPagination"] * {
    color: #334155 !important;
}

div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderPagination"] button {
    background: transparent !important;
    color: #475569 !important;
    border: 1px solid transparent !important;
    min-height: 2rem;
}

div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button:hover,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderPagination"] button:hover {
    background: #e8edf5 !important;
    border-color: #cbd3df !important;
}

div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button *,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderPagination"] button * {
    color: #475569 !important;
}

div[data-testid="stAlert"] p {
    color: #273449 !important;
}

hr {
    border-color: #dde3ec !important;
}
</style>
""", unsafe_allow_html=True)


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

    if "output" not in st.session_state:
        st.session_state.output = ""

    header_left, header_right = st.columns([6, 1])

    with header_left:
        st.title("ProcurePilot")
        st.caption(
            "AI-powered supplier evaluation and procurement approval"
        )

    with header_right:
        st.write("")

        if st.button(
            "New Request",
            use_container_width=True
        ):

            if os.path.exists("pending_approval.json"):
                os.remove("pending_approval.json")

            st.session_state.output = ""

            st.rerun()

    st.divider()

    with st.container(border=True):
        st.subheader("Purchase Request")

        request_text_col, item_text_col = st.columns(2, gap="medium")

        with request_text_col:
            department = st.text_input(
                "Department"
            )

        with item_text_col:
            item = st.text_input(
                "Item"
            )

        quantity_col, budget_col, delivery_col = st.columns(3, gap="medium")

        with quantity_col:
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1
            )

        with budget_col:
            max_budget = st.number_input(
                "Maximum budget (€)",
                min_value=1.0,
                step=100.0
            )

        with delivery_col:
            required_delivery_days = st.number_input(
                "Required delivery (days)",
                min_value=1,
                step=1
            )

    st.write("")

    with st.container(border=True):
        st.subheader("Supplier Quotations")

        uploaded_files = st.file_uploader(
            "Upload supplier quotation PDFs",
            type=["pdf"],
            accept_multiple_files=True
        )

        if uploaded_files:

            for file in uploaded_files:

                save_path = os.path.join(
                    "quotations",
                    file.name
                )

                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())

        if not uploaded_files:

            for file in glob.glob(
                "quotations/*pdf"
            ):
                os.remove(file)

        if st.button(
            "Analyse",
            use_container_width=True
        ):

            request = PurchaseRequest(
                department=department,
                item=item,
                quantity=quantity,
                max_budget=max_budget,
                required_delivery_days=required_delivery_days
            )

            result = run_agent(request)

            result["approval_status"] = "pending"
            result["manager_note"] = ""

            with open(
                "pending_approval.json",
                "w"
            ) as file:

                json.dump(
                    result,
                    file,
                    indent=4
                )

            st.session_state.output = (
                result["recommendation"]
            )

    st.write("")

    with st.container(border=True):

        st.subheader("Analysis Result")

        show_approval_status()

        st.text_area(
            "Recommendation",
            value=st.session_state.output,
            height=180,
            disabled=True
        )


if __name__ == "__main__":
    main()
