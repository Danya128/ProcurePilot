from schemas import SupplierQuote, BudgetResult, PurchaseRequest, SupplierStatus, PolicyResult
from company_data import DEPARTMENT_BUDGETS, APPROVED_SUPPLIERS
from typing import List

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import glob
import os

load_dotenv(override = True)

llm = ChatOpenAI(model = "gpt-4.1-nano", temperature = 0)
DB_NAME = "vector_db"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


#Create structured Supplier Quotations 
def extract_quote_data():
    quotes = []
    
    for file_path in glob.glob("quotations/*pdf"):
        loader = PyPDFLoader(file_path)
        pages = loader.load()
    
        text = "\n".join(page.page_content for page in pages)
        
        structured_llm = llm.with_structured_output(SupplierQuote)
    
        quote = structured_llm.invoke(
            f"""
            Extract the supplier quotation information from the text below
            Quotation:
            {text}
            """
        )
        quotes.append(quote)
    
    return quotes


# Check the department budget
def check_budget(request:PurchaseRequest, quote:SupplierQuote) -> BudgetResult:
    """
    Check whether a supplier quotation is within both the department's
    available budget and the maximum budget specified in the purchase request
    """
    department_budget = DEPARTMENT_BUDGETS.get(request.department)
    
    if department_budget is None:
        raise ValueError(f"Department '{request.department}' does not exist.")
    
    within_budget = (quote.total_price <= department_budget and
                     quote.total_price <= request.max_budget)
    remaining_budget = department_budget - quote.total_price
    
    return BudgetResult(
        department = request.department,
        remaining_budget = remaining_budget,
        requested_budget =  quote.total_price,
        within_budget = within_budget
    )
    
    
# Check whether a supplier is approved my company
def get_supplier_status(quote:SupplierQuote) -> SupplierStatus:
    """
    Check whether a supplier is approved by the company
    """
    supplier_name = quote.supplier
    supplier_status = APPROVED_SUPPLIERS.get(supplier_name, False)
        
    return SupplierStatus(
        supplier = supplier_name,
        status = supplier_status
    )
    

# Check the company policy
def check_company_policy(request: PurchaseRequest, quote: SupplierQuote) -> PolicyResult:
    """
    Find relevant company policies and explain how they apply
    to the purchase request and supplier quotation.
    """
    vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)

    retriever = vectorstore.as_retriever()

    documents = retriever.invoke(
        f"""
        Find company procurement policies relevant to this situation.

        Purchase request:
        Department: {request.department}
        Item: {request.item}
        Quantity: {request.quantity}
        Maximum budget: {request.max_budget}
        Required delivery: {request.required_delivery_days} days

        Supplier quotation:
        Supplier: {quote.supplier}
        Total price: {quote.total_price}
        Delivery: {quote.delivery_days} days
        Warranty: {quote.warranty_months} months
        """
    )

    policy_context = "\n\n".join(document.page_content for document in documents)

    response = llm.invoke(
        f"""
        Analyse this supplier quotation using ONLY the company policies below.

        Purchase request:
        {request}

        Supplier quotation:
        {quote}

        Relevant company policies:
        {policy_context}

        Explain which policy rules apply to this quotation
        and whether any special requirement, such as manager approval,
        is triggered.

        Do not invent company policies.
        """
    )

    sources = []
    for document in documents:
        source = os.path.basename(document.metadata.get("source", "Unknown"))
        if source not in sources:
            sources.append(source)

    return PolicyResult(
        content=response.content,
        source=", ".join(sources)
    )

# Compare the suppliers
def compare_suppliers(request: PurchaseRequest, quotes: List[SupplierQuote],
    budget_results: List[BudgetResult],supplier_statuses: List[SupplierStatus],
    policy_results: List[PolicyResult]):
    comparisons = []

    for quote, budget, status, policy in zip(
        quotes,
        budget_results,
        supplier_statuses,
        policy_results
    ):
        issues = []
        if not budget.within_budget:
            department_budget = budget.remaining_budget + budget.requested_budget
            if quote.total_price > department_budget:
                issues.append(f"Exceeds department budget by {quote.total_price - department_budget}")
            if quote.total_price > request.max_budget:
                issues.append(f"Exceeds requested max budget by {quote.total_price - request.max_budget}")
        if not status.status:
            issues.append("Supplier is not approved")
        if quote.delivery_days > request.required_delivery_days:
            issues.append(
                f"Delivery is {quote.delivery_days - request.required_delivery_days} days late"
            )

        comparisons.append({
            "supplier": quote.supplier,
            "price": quote.total_price,
            "delivery_days": quote.delivery_days,
            "warranty_months": quote.warranty_months,
            "within_budget": budget.within_budget,
            "approved": status.status,
            "meets_delivery": (
                quote.delivery_days <= request.required_delivery_days
            ),
            "policy_result": policy.content,
            "policy_source": policy.source,
            "issues": issues
        })
        
    return comparisons