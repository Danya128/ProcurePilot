from tools import extract_quote_data, check_budget, get_supplier_status, check_company_policy, compare_suppliers
from schemas import PurchaseRequest
from ingestion import process_document

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_recommendations(request:PurchaseRequest, comparison):
    llm = ChatOpenAI(
        model="gpt-4.1-nano",
        temperature=0
        )
    
    response = llm.invoke(
        f"""
        You are a procurement agent.

        Purchase request:
        {request}

        Supplier comparisons:
        {comparison}

        Recommend the best available supplier.

        Rules:
        - If exactly one supplier meets all requirements, recommend it directly.
        - If multiple suppliers meet all requirements, compare only those suppliers.
        - If none meet all requirements, recommend the best available option and
        clearly mention the unmet requirements.
        - Do not invent information.

        Keep the response concise.

        Output only:
        Recommended supplier: <name>

        Reason:
        <2-4 short sentences>

        Issues:
        <issues, or "None">
        """
    )
    
    return response.content

def run_agent(request: PurchaseRequest):
    
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
    recommendation = generate_recommendations(request, comparison)
    
    for supplier in comparison:
        print(f"Policy source: {supplier['policy_source']}")
    print("\n" + "=" * 50)
    print("RECOMMENDATION")
    print("=" * 50)
    print(recommendation)
    
    return {
    "request": request.model_dump(),
    "comparison": comparison,
    "recommendation": recommendation
    }