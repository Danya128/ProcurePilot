from schemas import SupplierQuote, BudgetResult, PurchaseRequest
from company_data import DEPARTMENT_BUDGETS

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
import glob

llm = ChatOpenAI(model = "gpt-4.1-nano", temperature = 0)


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