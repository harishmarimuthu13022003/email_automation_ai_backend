import os
import json
import re
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from ..core.config import settings
from .email_service import EmailService
from .pdf_service import PDFService
from ..core.database import get_collection

class AgentService:
    def __init__(self):
        self.keys = settings.groq_keys
        self.current_key_index = 0

    def get_llm_string(self):
        if not self.keys:
            raise Exception("No Groq API keys provided in .env")
        
        # Set the environment variable so CrewAI/LiteLLM picks it up
        current_key = self.keys[self.current_key_index]
        
        # Security: Mask the key in logs but show start/end for debugging
        masked_key = f"{current_key[:6]}...{current_key[-4:]}" if len(current_key) > 10 else "INVALID_KEY"
        print(f"🔑 AI AGENT: Initializing with key: {masked_key}")
        
        os.environ["GROQ_API_KEY"] = current_key
        return "groq/llama-3.3-70b-versatile" # Newer, supported model

    def rotate_key(self):
        if len(self.keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            print(f"🔄 SWITCHING API KEY: Using key {self.current_key_index + 1}")
            return True
        return False

    def create_agents(self, llm_string):
        intake_specialist = Agent(
            role='Intake Specialist',
            goal='Classify the email into one of three categories: INVOICE, LEAD, or OTHER.',
            backstory='Expert in triaging business communications. You decide if a request is a billing event or a sales opportunity.',
            llm=llm_string,
            verbose=True,
            allow_delegation=False
        )

        data_analyst = Agent(
            role='Precision Data Analyst',
            goal='Extract exact client details, amounts, and dates from the email.',
            backstory='Known for 100% accuracy in parsing unstructured billing and contact information.',
            llm=llm_string,
            verbose=True,
            allow_delegation=False
        )

        financial_auditor = Agent(
            role='Financial Auditor',
            goal='Validate extracted amounts and ensure they are formatted as clean numbers.',
            backstory='Ensures that the financial data is mathematically sound and ready for bookkeeping.',
            llm=llm_string,
            verbose=True,
            allow_delegation=False
        )

        ghostwriter = Agent(
            role='Communications Officer',
            goal='Write a specialized, professional response based on the classification.',
            backstory='Master of corporate tone. You craft personalized replies that reflect the Antigravity brand.',
            llm=llm_string,
            verbose=True,
            allow_delegation=False
        )
        return [intake_specialist, data_analyst, financial_auditor, ghostwriter]

    async def process_email_workflow(self, email_data: dict):
        max_retries = len(self.keys)
        attempts = 0
        
        while attempts < max_retries:
            try:
                llm_string = self.get_llm_string()
                agents = self.create_agents(llm_string)

                autonomous_task = Task(
                    description=(
                        f"Analyze this email:\nSubject: {email_data.get('subject')}\nBody: {email_data.get('body')}\n"
                        "1. Classify as INVOICE or LEAD.\n"
                        "2. Extract Client Name, Email, Amount (if applicable), and Description.\n"
                        "3. Write a 3-sentence personalized reply.\n"
                        "Return ONLY a JSON object with keys: type, client_name, client_email, amount, description, due_date, reply_body."
                    ),
                    agent=agents[0], # Starter agent
                    expected_output="A full JSON autonomous packet containing classification, data, and reply."
                )

                crew = Crew(
                    agents=agents,
                    tasks=[autonomous_task],
                    process=Process.sequential,
                    verbose=True
                )

                result = crew.kickoff()
                
                try:
                    clean_result = str(result.raw).strip()
                    match = re.search(r'\{.*\}', clean_result, re.DOTALL)
                    if match:
                        clean_result = match.group()
                    
                    data = json.loads(clean_result)
                    
                    # Store tracking info
                    data['original_msg_id'] = email_data.get('message_id')
                    data['invoice_id'] = f"INV-{datetime.now().strftime('%Y%j%H%M')}"
                    data['status'] = "Pending"
                    data['created_at'] = datetime.now()
                    
                    # Determine next steps based on Agent Classification
                    if data.get('type') == 'INVOICE':
                        await self._handle_invoice(data, email_data)
                    else:
                        await self._handle_lead(data, email_data)

                    return data
                except Exception as e:
                    print(f"⚠️ JSON Parsing error on attempt {attempts + 1}: {e}")
                    raise e

            except Exception as e:
                attempts += 1
                if not self.rotate_key() or attempts >= max_retries:
                    return None
                continue
        return None

    async def _handle_invoice(self, data, email_data):
        invoices_col = get_collection("invoices")
        await invoices_col.insert_one(data.copy())
        pdf_path = PDFService.generate_invoice_pdf(data)
        await invoices_col.update_one({"invoice_id": data['invoice_id']}, {"$set": {"pdf_path": pdf_path}})
        
        EmailService.send_email(
            to_email=email_data['sender'], 
            subject=email_data['subject'],
            body=data.get('reply_body', "Your invoice is attached."),
            attachment_path=pdf_path,
            reply_to_id=email_data.get('message_id')
        )
        
        await get_collection("email_logs").insert_one({
            "action": "AI Invoice Processed",
            "details": f"Agents processed invoice for {data.get('client_name')}",
            "timestamp": datetime.now()
        })

    async def _handle_lead(self, data, email_data):
        lead_data = {
            "sender": data.get('client_name', email_data['sender']),
            "email": email_data['sender'],
            "subject": email_data['subject'],
            "body": email_data['body'],
            "status": "AI Processed",
            "source": "Agent Crew",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        await get_collection("leads").insert_one(lead_data)
        
        EmailService.send_email(
            to_email=email_data['sender'], 
            subject=email_data['subject'],
            body=data.get('reply_body', "Thanks for reaching out!"),
            reply_to_id=email_data.get('message_id')
        )

        await get_collection("email_logs").insert_one({
            "action": "AI Lead Captured",
            "details": f"Agents identified a new opportunity from {lead_data['sender']}",
            "timestamp": datetime.now()
        })
