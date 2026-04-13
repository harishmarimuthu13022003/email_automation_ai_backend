from fastapi import APIRouter, HTTPException, Depends
from ..models.schemas import InvoiceCreate, Invoice, Lead, EmailLog
from ..core.database import get_collection
from ..services.email_service import EmailService
from ..services.agent_service import AgentService
from ..core.config import settings
from datetime import datetime
import asyncio

router = APIRouter()
agent_service = AgentService()

@router.post("/create-invoice")
async def create_invoice(invoice: InvoiceCreate):
    invoice_dict = invoice.dict()
    invoice_dict["invoice_id"] = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    invoice_dict["status"] = "Pending"
    invoice_dict["created_at"] = datetime.now()
    
    col = get_collection("invoices")
    result = await col.insert_one(invoice_dict)
    
    # Notify finance officer
    EmailService.send_email(
        "finance@company.com", 
        f"New Invoice Request: {invoice_dict['invoice_id']}",
        f"A new invoice request has been received for {invoice.client_name} (${invoice.amount})."
    )
    
    return {"id": str(result.inserted_id), **invoice_dict}

@router.get("/invoices")
async def get_invoices():
    invoices_col = get_collection("invoices")
    invoices = await invoices_col.find().sort("created_at", -1).to_list(100)
    for inv in invoices:
        inv["_id"] = str(inv["_id"])
    return invoices

@router.put("/invoices/{invoice_id}/paid")
async def mark_invoice_as_paid(invoice_id: str):
    invoices_col = get_collection("invoices")
    result = await invoices_col.update_one(
        {"invoice_id": invoice_id},
        {"$set": {"status": "Paid"}}
    )
    if result.modified_count == 0:
        return {"error": "Invoice not found or already paid"}
    return {"message": "Invoice marked as paid"}

@router.get("/leads")
async def get_leads():
    col = get_collection("leads")
    leads = await col.find().to_list(100)
    for lead in leads:
        lead["_id"] = str(lead["_id"])
    return leads

@router.post("/process-email")
async def process_emails():
    try:
        print(f"🚀 AI Agent Triggered. Looking for user: {settings.FINANCE_EMAIL or 'MISSING'}")
        if not settings.FINANCE_EMAIL or not settings.EMAIL_PASSWORD:
            print("❌ ERROR: Email Credentials missing in Environment Variables!")
            return {"status": "error", "message": "Credentials missing", "processed_count": 0}
            
        emails = EmailService.fetch_emails()
        processed = []
        for email in emails:
            # 🚀 FULLY AUTONOMOUS FLOW
            # The AI Agents now decide if it's an Invoice, Lead, or Misc.
            # They also handle their own DB saves and Replies.
            result = await agent_service.process_email_workflow(email)
            if result:
                processed.append(result)
                
        return {"status": "success", "processed_count": len(processed), "data": processed}
    except Exception as e:
        print(f"CRITICAL ERROR IN EMAIL PROCESSING: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent System Error: {str(e)}")

@router.get("/email-logs")
async def get_email_logs():
    col = get_collection("email_logs")
    logs = await col.find().sort("timestamp", -1).to_list(100)
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs

@router.get("/stats")
async def get_stats():
    try:
        inv_col = get_collection("invoices")
        leads_col = get_collection("leads")
        
        if inv_col is None or leads_col is None:
            raise Exception("Database not connected")

        # Calculate Revenue Safely
        invoices = await inv_col.find().to_list(1000)
        
        def safe_float(val):
            try:
                if val is None: return 0.0
                return float(val)
            except:
                return 0.0

        total_revenue = sum(safe_float(inv.get("amount")) for inv in invoices if str(inv.get("status", "")).strip().lower() == "paid")
        pending_amount = sum(safe_float(inv.get("amount")) for inv in invoices if str(inv.get("status", "")).strip().lower() == "pending")
        
        total_leads = await leads_col.count_documents({})
        active_invoices = await inv_col.count_documents({"status": "Pending"})
        
        return {
            "total_revenue": total_revenue,
            "pending_amount": pending_amount,
            "total_leads": total_leads,
            "active_invoices": active_invoices
        }
    except Exception as e:
        print(f"STATS ERROR: {str(e)}")
        # Still return a valid structure or raise a clear exception
        raise HTTPException(status_code=500, detail=str(e))
