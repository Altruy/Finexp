from fastapi import FastAPI, File, UploadFile, Request
import os, time
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from expenses_agent import expenses_agent
from db import save_transaction, get_transactions, update_transaction, delete_transaction, reset_transaction

app = FastAPI()

class Request_(BaseModel):
    text: str
    who: str

class Transaction(BaseModel):
    Date: str
    Description: str
    Amount: float
    Category: str

class Transaction_(BaseModel):
    Date: str
    Description: str
    Amount: float
    Category: str
    id: str

class TransactionUpdate(BaseModel):
    Date: str = None
    Description: str = None
    Amount: float = None
    Category: str = None

class TranscriptionResponse(BaseModel):
    transactions: list[Transaction_]

@app.get("/")
async def status(req: Request):

    date = time.strftime("%d-%m-%Y-%H-%M-%S")
    with open(f"log.txt", "a") as f:
        f.write(date + "  " + (req.client.host) + "\n")
    return JSONResponse(content={"status": "true"})

@app.post("/text", response_model=TranscriptionResponse)
async def upload_text(req: Request_):
    try:
        os.mkdir(f"texts/{req.who}")
    except FileExistsError:
        pass
    date = time.strftime("%d-%m-%Y-%H-%M-%S")
    with open(f"texts/{req.who}/t-{date}.txt", "w") as f:
        f.write(req.text)
    a = time.time()
    transactions = expenses_agent.invoke(req.text)
    saved_transactions = [save_transaction(req.who, transaction) for transaction in transactions]
    print(f'inference in {time.time() - a}s')
    return JSONResponse(content={"transactions": saved_transactions})

@app.post("/audio", response_model=TranscriptionResponse)
async def upload_audio(file: UploadFile = File(...)):
    try:
        who, filename = file.filename.split("_")
    except Exception as e:
        print("invalid name",file.filename)
        return JSONResponse(status_code=404, content={"message": e})
    try:
        os.mkdir(f"audios/{who}")
    except FileExistsError:
        pass
    file_location = f"./audios/{who}/{filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    a = time.time()
    transactions = expenses_agent.invoke(file_location)
    saved_transactions = [save_transaction(who, transaction) for transaction in transactions]
    print(f'inference in {time.time() - a}s')
    return JSONResponse(content={"transactions": saved_transactions})

@app.post("/image", response_model=TranscriptionResponse)
async def upload_image(file: UploadFile = File(...)):
    try:
        who, filename = file.filename.split("_")
    except Exception as e:
        print("invalid name",file.filename)
        return JSONResponse(status_code=404, content={"message": e})
    try:
        os.mkdir(f"images/{who}")
    except FileExistsError:
        pass
    file_location = f"./images/{who}/{filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    a = time.time()
    transactions = expenses_agent.invoke(file_location)
    saved_transactions = [save_transaction(who, transaction) for transaction in transactions]
    print(f'inference in {time.time() - a}s')
    return JSONResponse(content={"transactions": saved_transactions})

@app.get("/transactions/{who}", response_model=TranscriptionResponse)
async def get_user_transactions(who: str):
    transactions = get_transactions(who)
    return JSONResponse(content={"transactions": transactions})

@app.put("/transactions/{who}/{transaction_id}", response_model=Transaction)
async def update_user_transaction(who: str, transaction_id: str, transaction: TransactionUpdate):
    updated_transaction = update_transaction(who, transaction_id, transaction.model_dump(exclude_unset=True))
    if updated_transaction:
        return updated_transaction
    return JSONResponse(status_code=404, content={"message": "Transaction not found"})


@app.post("/transactions/{who}", response_model=Transaction)
async def add_user_transactions(who: str, transactions:TranscriptionResponse):
    print("backup on server",transactions.model_dump(exclude_unset=True)["transactions"])
    suc = reset_transaction(who, transactions.model_dump(exclude_unset=True)["transactions"])
    if suc:
        return JSONResponse(status_code=200, content={"message": "Success"})
    return JSONResponse(status_code=404, content={"message": "Backup not made"})
    

@app.delete("/transactions/{who}/{transaction_id}", response_model=dict)
async def delete_user_transaction(who: str, transaction_id: str):
    success = delete_transaction(who, transaction_id)
    if success:
        return {"message": "Transaction deleted"}
    return JSONResponse(status_code=404, content={"message": "Transaction not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
