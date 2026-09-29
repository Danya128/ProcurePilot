from schemas import SupplierQuote

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


