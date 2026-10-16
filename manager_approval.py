from schemas import SupplierQuote

import streamlit as st
import json
import os


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

    st.subheader("Purchase Request")

    st.write(f"Department: {request['department']}")
    st.write(f"Item: {request['item']}")
    st.write(f"Quantity: {request['quantity']}")
    st.write(f"Maximum Budget: €{request['max_budget']}")
    st.write(
        f"Required Delivery: "
        f"{request['required_delivery_days']} days"
    )

    st.subheader("Supplier Comparison")

    for supplier in comparison:

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

        st.divider()

    st.subheader("Agent Recommendation")

    st.write(recommendation)

    if status == "pending":
        
        st.warning("Manager approval required")

        manager_note = st.text_area(
            "Manager note",
            placeholder="Leave an optional note..."
        )
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve"):

                data["approval_status"] = "approved"
                data["manager_note"] = manager_note.strip()

                with open("pending_approval.json", "w") as file:
                    json.dump(data, file, indent=4)

                st.success("Purchase approved")
                st.rerun()

        with col2:
            if st.button("Reject"):

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