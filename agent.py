from tools import extract_quote_data, check_budget, get_supplier_status, check_company_policy, compare_suppliers
from schemas import PurchaseRequest
from ingestion import process_document

from langchain_core.tools import tool



def run_agent(request: PurchaseRequest):
    
    process_document()
    
    # Extract supplier quotations
    quotes = extract_quote_data()
    
    budget_results = []
    supplier_statuses = []
    policy_results = []
    
    # Run checks for every supplier
    for quote in quotes:
        budget_res = check_budget(request, quote)
        supplier_res = get_supplier_status(quote)
        policy_res = check_company_policy(request, quote)
        
        budget_results.append(budget_res)
        supplier_statuses.append(supplier_res)
        policy_results.append(policy_res)
        
    comparison = compare_suppliers(request, quotes, budget_results, supplier_statuses, policy_results)
    
    for supplier in comparison:
        print("\n" + "=" * 50)
        print(f"Supplier: {supplier['supplier']}")
        print(f"Price: €{supplier['price']}")
        print(f"Delivery: {supplier['delivery_days']} days")
        print(f"Warranty: {supplier['warranty_months']} months")
        print(f"Within budget: {supplier['within_budget']}")
        print(f"Approved: {supplier['approved']}")
        print(f"Meets delivery: {supplier['meets_delivery']}")

        print("Issues:")
        if supplier["issues"]:
            for issue in supplier["issues"]:
                print(f"  - {issue}")
        else:
            print("  - None")

        print(f"Policy source: {supplier['policy_source']}")
    
    return comparison
    
    
if __name__ == "__main__":
    
    request = PurchaseRequest(
        department="IT",
        item="Lenovo ThinkPad",
        quantity=30,
        max_budget=35000,
        required_delivery_days=14
    )
    
    run_agent(request)