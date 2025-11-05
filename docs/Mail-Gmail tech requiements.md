<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Create a technical requirements, our first focus should be Gmail \& Gsuite

Here are the **considerations** before defining technical requirements for an MVP AI email extension (Gmail \& G Suite first focus):

***

**Considerations Before Technical Requirements**

1. **User Workflow Integration:**
    - Must operate inside Gmail/G Suite (web client, Chrome extension, or API integration)
    - Minimize disruption: augment existing workflow, avoid requiring new platforms
2. **Inbox Data Access:**
    - Secure access to inbox, support for both individual user and delegated/shared inbox scenarios
    - Ensure robust handling of permissions and Google OAuth
3. **AI Capabilities Scope:**
    - Natural language processing for email parsing (identify project, extract quote requests, detect attachments)
    - Retrieval and matching (grouping, suggestion, auto-draft price options)
4. **Internal Approval Workflow:**
    - Must support multi-user flow (quote draft, team review, approval, auto-send)
    - Notification and tracking inside G Suite ecosystem
5. **Pricing Automation:**
    - Integration with Google Sheets (for master price list), possibly later with Xero/MYOB, etc.
    - Support complex option/variant matching
6. **Security \& Compliance:**
    - Data privacy, email encryption, Google API compliance
    - Audit log for all price and email actions
7. **Deployment \& Maintenance:**
    - Must be simple for SMEs to install (Chrome Web Store, Workspace Marketplace)
    - Admin control, updates, rollback
8. **Australian Context:**
    - default GST fields/preparation in quotes
    - customisation for Aussie builder conventions (project/job codes, etc)

***

# Technical Requirements: AI Email Extension for Builders (Gmail \& G Suite Focus)


***

## 1. Core Functionality

- **Gmail Add-on / Chrome Extension**
    - Embedded directly in Gmail web client for seamless user experience.
    - Support for G Suite (Workspace) multi-user environments.
    - Admin provisioning via Google Workspace Marketplace install.
- **Inbox Data Handling**
    - OAuth2 consent flow for secure inbox access (read, compose, send, meta, attachments).
    - Ability to process both individual and delegated/team inboxes.
    - Real-time monitoring of inbound emails for customer project queries.
- **Email Parsing \& Project Grouping**
    - AI model (LLM or custom NLP pipeline) parses email content for:
        - Project/job identification
        - Client contact extraction
        - Quotation/trade-related requests
        - Attachment scanning (plans/specs)
    - Auto-tagging/grouping by job, project, or customer using extracted keywords.
- **Quote Drafting \& Option Pricing**
    - Integration with Google Sheets:
        - Fetch, lookup, and calculate pricing options based on project specs.
        - Handle multiple project variants and custom calculations per builder/carpenter conventions.
    - Automated generation of draft quotations, itemized with per-option pricing.
    - Quote template management (editable in G Suite / Google Docs).
- **Internal Approval Workflow**
    - Assign quote drafts for builder/manager review.
    - Approval or feedback directly in Gmail (interactive cards or side-panel UI).
    - Notification flows (email, Google Chat, G Suite notification center).
    - Email scheduling: queue drafts for approval, auto-send post-approval.
- **Quote Sending \& Audit Trail**
    - Automated sending to client post-approval.
    - Store outgoing quotes in a searchable sent-folder (audit-logging).
    - Time/date/user stamped records for all quote actions.
- **Australian Compliance Features**
    - GST fields and Australian builder compliance templates.
    - Localised templates with legal/pricing/disclaimer language fit for AU market.

***

## 2. AI and Data Architecture

- **Natural Language Processing (NLP)**
    - GPT-based or specialist model for parsing and summarization.
    - Entity extraction: client name, job, specification, variation requests.
    - Confidence scoring and “human-in-the-loop” review.
- **Integration Layer**
    - Google APIs: Gmail, Google Sheets, Drive (for attachments), Calendar (meeting scheduling).
    - Webhooks for event-driven automation (new emails, sheet updates).
- **Security \& Privacy**
    - Strict adherence to Google API scopes (minimum permissions).
    - End-to-end encryption for quote data.
    - User-access level management (admin roles, team permissions).

***

## 3. User Experience

- **Contextual UI/UX**
    - In-Gmail panel: project grouping, quote dashboard, approval buttons.
    - Template selection/customization inline.
    - Smart notifications and reminders (review needed, quote sent, client reply received).
- **Onboarding \& Help**
    - Guided first-use setup (Connect Sheet, configure templates).
    - In-app tooltips, live chat support \& FAQ.
    - Easy add/remove team members via Workspace admin panel.

***

## 4. Deployment, Maintenance \& Support

- **Install \& Updates**
    - Available via Chrome Web Store and Google Workspace Marketplace.
    - Simple auto-update mechanism, rollback supported.
- **Admin \& IT Controls**
    - Org-level enable/disable, per-user permissions, logging.
    - Usage analytics/dashboard for team leaders.
- **Support \& SLA**
    - In-product feedback channel.
    - Audit logs for troubleshooting and compliance.
    - Tiered support response times for paid/business accounts.

***

## 5. Technical Stack Outline

- **Frontend:** Chrome Extension JS/React (Manifest v3), Gmail Add-on Apps Script, MaterialUI or similar
- **Backend:** Python/Node (FastAPI, Express), Google Cloud Functions
- **AI/NLP:** OpenAI GPT, Google Vertex AI, or custom fine-tuned LLM
- **Datastore:** Google Sheets for MVP, Firestore/Firebase for scale
- **Integrations:** Google APIs (Gmail, Sheets, Drive, Chat), optional Webhooks for future CRMs
- **Security:** OAuth2, Google IAM, encrypted storage (AES-256)
- **Compliance:** Designed for AU regulatory standards, GDPR-compliant

***

*End Document.*

