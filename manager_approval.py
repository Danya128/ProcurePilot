import streamlit as st
import json
import os


st.title("Manager Approval")


if not os.path.exists("pending_approval.json"):
    st.info("No purchase request is waiting for approval.")
    st.stop()


with open("pending_approval.json", "r") as file:
    data = json.load(file)


request = data["request"]
comparison = data["comparison"]
recommendation = data["recommendation"]


st.subheader("Purchase Request")

st.write(f"Department: {request['department']}")
st.write(f"Item: {request['item']}")
st.write(f"Quantity: {request['quantity']}")
st.write(f"Maximum Budget: €{request['max_budget']}")
st.write(
    f"Required Delivery: {request['required_delivery_days']} days"
)


st.subheader("Supplier Comparison")

for supplier in comparison:

    st.write(f"### {supplier['supplier']}")

    st.write(f"Price: €{supplier['price']}")
    st.write(f"Delivery: {supplier['delivery_days']} days")
    st.write(f"Warranty: {supplier['warranty_months']} months")
    st.write(f"Approved: {supplier['approved']}")
    st.write(f"Within Budget: {supplier['within_budget']}")

    if supplier["issues"]:
        st.write("Issues:")
        for issue in supplier["issues"]:
            st.write(f"- {issue}")

    st.divider()


st.subheader("Agent Recommendation")

st.write(recommendation)


st.warning("Manager approval required")


col1, col2 = st.columns(2)

with col1:
    if st.button("Approve"):
        data["approval_status"] = "approved"

        with open("pending_approval.json", "w") as file:
            json.dump(data, file, indent=4)

        st.success("Purchase approved")


with col2:
    if st.button("Reject"):
        data["approval_status"] = "rejected"

        with open("pending_approval.json", "w") as file:
            json.dump(data, file, indent=4)

        st.error("Purchase rejected")