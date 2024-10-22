import whisper
import time
from typing import Type
from langchain.tools import BaseTool, Tool
from langchain_core.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import ToolException
from langchain_core.prompts import PromptTemplate
from langchain.agents import initialize_agent
from langchain_core.runnables import RunnableLambda
from langchain_community.llms import LlamaCpp

phi_3 = """<|system|>
You are a helpful assistant designed to help the User organise their finances, You are very skilled are classifying and categorising the nature of transactions. Your task is to help
extract details of a persons transactions from a transcription or a payment receipt. You have to provide a list of transactions 
mentioned in the transcript, or a single trasaction for payment receipts. For each transaction provide a json object with date, description, amount in euros, and classify 
them in three categories: 1. Personal Expenses, 2. Shared Expenses, 3. Debt. ONLY select from these catagories. money user needs to give or owes someone else are Debt
Food, Clothes, decoration pieces are all Personal  Expenses. Groceries, Cleaning supplies, furniture, utility bills are Shared Expenses.
return only a list in the JSON format "Date" : "dd/mm/yy", "Description" : "Food from ___", "Amount": "5" ,"Category": "Personal Expenses".
even if it is a single transaction still output a list. follow the category examples very strictly and only use the user input, dont add anything by yourself<|end|>
<|user|>
{input}<|end|>
<|assistant|>"""


llm = LlamaCpp(
    model_path="../model-cache/microsoft--Phi-3-mini-4k-instruct-gguf",
    temperature=0.75,
    max_tokens=54000,
    top_p=1,
    # callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
)

class WhisperInput(BaseModel):
    input: str = Field(description="path of file")


class WhisperTranscriptionTool(BaseTool):
    name = 'Whisper Audio Transcription Tool'
    description = "This Tool is used to transcribe an audio file into english text. Use this tool when the input is the path of an audio file of formats: .mp3 , .mp4 , .mpeg , .mpga , .m4a , .wav , .webm"
    args_schema: Type[BaseModel] = WhisperInput
    return_direct: bool = True
    handle_tool_error: bool = True
    model = whisper.load_model("small")

    def _run(self, input: str) -> str:
        # Load and transcribe the audio file
        try:
            date = time.strftime("%d/%m/%Y")
            options = {"task":"translate"}
            audio = whisper.load_audio(input)
            result = whisper.transcribe(self.model , audio, **options)
            return "today's date: " + date + " transcript: "+result['text']
        except Exception as e:
            raise ToolException(f"The following error comes up in trying to transcribe the file : {input}, error {e}.")

    def _arun(self, input: str) -> str:
        # Optional: Implement asynchronous transcription if needed
        raise ToolException("Async transcription not implemented.")

transcription_tool = WhisperTranscriptionTool()
#  print(transcription_tool.invoke({"input":eng}))

@tool
def image_to_text(file_name:str)->str: 
    """This is used to extract english text from an image of a payment receipt"""
    date = time.strftime("%d/%m/%Y")
    place_holder = """Today I spent 15 euros to buy clothes from Primark. yesterday i bought clothes detergent for 13 euros. and i need to give marium 5 euros"""
    return "today's date: " + date + " receipt: "+ place_holder


tools=[transcription_tool, image_to_text]


agent = initialize_agent(
    agent="zero-shot-react-description",
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=1,
)

def extract_list(input:str) -> list :
    print(len(input),":",input)
    ret = []
    i = 0
    while True:
        try:
            st = input[i:].index("{")
            en = input[i:].index("}")
            obj = eval(input[i+st:i+en+1])
            obj["Amount"] = float(obj["Amount"])
            ret.append(obj)
            i += en + 2
        except Exception as e:
            break
    return ret

def route(input):
    if len(input.split())==1:
        print('transcription needed')
        return agent
    else: 
        print('transcription not needed')
        date = time.strftime("%d/%m/%Y")
        return {"output":"today's date: " + date + " text: "+input}
    
outputParser = RunnableLambda(extract_list)
prompt = PromptTemplate.from_template(phi_3)
input__chain = RunnableLambda(route) | (lambda x : x['output']) 
expenses_agent = input__chain | prompt | llm |  outputParser

if __name__ == "__main__":
    placeholder = """Today I spent 15 euros to buy clothes from Primark. yesterday i bought clothes detergent for 13 euros. and i need to give marium 5 euros"""
    a = time.time()
    resp = expenses_agent.invoke(placeholder)
    print("############## ",time.time()-a,"s #########")
    print(resp)
