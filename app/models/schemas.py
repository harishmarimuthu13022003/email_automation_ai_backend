from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class InvoiceBase(BaseModel):
    client_name: str
    client_email: EmailStr
    amount: float
    description: str
    due_date: datetime

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    status: str

class Invoice(InvoiceBase):
    id: str = Field(alias="_id")
    status: str = "Pending"
    created_at: datetime = datetime.now()
    invoice_id: str
    pdf_path: Optional[str] = None

class Lead(BaseModel):
    name: str
    email: str
    source: str
    created_at: datetime = datetime.now()

class EmailLog(BaseModel):
    subject: str
    sender: str
    status: str
    timestamp: datetime = datetime.now()
    type: str  # incoming/outgoing
