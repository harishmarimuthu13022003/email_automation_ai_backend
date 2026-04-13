# 🤖 Antigravity AI - Backend Service

This is the AI agent power-center for the Invoice and Email Automation system. Built with FastAPI and CrewAI, it autonomously reads emails, extracts billing data, and generates professional PDF invoices.

## 🛠️ Tech Stack
- **FastAPI**: High-performance web framework.
- **CrewAI**: Autonomous multi-agent orchestration.
- **Motor (MongoDB)**: Async NoSQL database connector.
- **PDFlib (fpdf2)**: Invoice generation engine.

## 🧠 CrewAI Autonomous Agent Workflow

The system has been upgraded to a fully autonomous Multi-Agent department that manages the entire lifecycle of an inquiry.

### 👥 The 4-Agent Elite Team
1. **Intake Specialist (The Gatekeeper)**:
   - **Role**: Context Intelligence.
   - **Responsibility**: Analyzes the intent of incoming emails to classify them into high-value **Invoices** or business **Leads**.

2. **Precision Data Analyst (The Parser)**:
   - **Role**: Information Extraction.
   - **Responsibility**: Scans for specific billing data, contact info, and project descriptions with laser-like accuracy.

3. **Financial Auditor (The Verifier)**:
   - **Role**: Quality Assurance.
   - **Responsibility**: Cross-checks extracted amounts and dates to ensure the data is mathematically valid and formatted for accounting.

4. **Communications Officer (The Ghostwriter)**:
   - **Role**: Brand Voice.
   - **Responsibility**: Crafts a personalized, professional response based on the agent findings. No more robotic templates!

### 🔄 Fully Autonomous Pipeline
1. **Classification**: The **Intake Specialist** identifies the request type.
2. **Extraction**: The **Data Analyst** pulls raw information from the email body.
3. **Audit**: The **Financial Auditor** refines the data for the PDF generator.
4. **Drafting**: The **Communications Officer** writes a tailored reply.
5. **Execution**: The system automatically generates the PDF, saves records to MongoDB, and sends the threaded email reply.

## 🚀 Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file based on the following template:
   ```env
   MONGODB_URL=your_mongodb_url
   DATABASE_NAME=invoice_automation
   GROQ_API_KEY_1=your_key
   FINANCE_EMAIL=your_email
   EMAIL_PASSWORD=your_app_password
   ```

3. **Run the Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

## 📡 API Endpoints
- `GET /api/stats`: System-wide analytics (Revenue, Leads).
- `GET /api/invoices`: List of all generated invoices.
- `GET /api/leads`: List of all captured email leads.
- `POST /api/process-email`: Trigger the AI Agent to scan inbox.
