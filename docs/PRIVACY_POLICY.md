# Privacy Policy
## AI Email Grouping Extension for Gmail

**Last Updated:** 2025  
**Version:** 1.0

### 1. Introduction

This Privacy Policy describes how we collect, use, and protect your personal information when you use the AI Email Grouping Extension for Gmail ("the Extension"). We are committed to protecting your privacy and complying with applicable data protection laws, including the Australian Privacy Principles (APPs) and the General Data Protection Regulation (GDPR).

### 2. Information We Collect

#### 2.1 Email Data
- **Email Content**: We process email content to identify and group emails by project/job
- **Email Metadata**: Subject lines, sender information, dates, thread IDs
- **Attachments**: Attachment metadata (filename, size, type) for project organization
- **Labels/Folders**: Gmail labels for filtering and organization

#### 2.2 Account Information
- **Google Account**: Email address, name, profile picture (from Google OAuth)
- **Authentication Tokens**: Encrypted OAuth tokens for Gmail API access

#### 2.3 Usage Data
- **Configuration Settings**: Scanning preferences, filter settings, naming rules
- **Project Information**: Project names, addresses, client information extracted from emails
- **Corrections and Feedback**: User corrections to AI grouping decisions for model improvement

#### 2.4 Technical Data
- **IP Address**: Logged for security and audit purposes
- **User Agent**: Browser/device information for compatibility
- **Audit Logs**: Records of user actions for security and compliance

### 3. How We Use Your Information

#### 3.1 Core Functionality
- **Email Grouping**: Process emails to intelligently group them by project/job
- **Project Management**: Create and manage project associations
- **Label Management**: Automatically apply Gmail labels to organized emails
- **Attachment Organization**: Group attachments by project

#### 3.2 AI Processing
- **Entity Extraction**: Extract project names, addresses, job numbers from emails
- **Content Analysis**: Analyze email content for similarity and grouping
- **Pattern Learning**: Learn from user corrections to improve accuracy

#### 3.3 Service Improvement
- **Error Handling**: Detect and resolve technical issues
- **Performance Optimization**: Improve processing speed and accuracy
- **Feature Development**: Develop new features based on usage patterns

### 4. Data Storage and Security

#### 4.1 Data Storage
- **Location**: Data is stored securely in our database systems
- **Retention**: Data is retained until you delete your account or request deletion
- **Backup**: Regular backups are performed for data recovery purposes

#### 4.2 Security Measures
- **Encryption**: 
  - OAuth tokens encrypted using AES-256 encryption
  - TLS/HTTPS for all API communications
  - Encrypted database connections
- **Access Control**: 
  - Role-based access control (RBAC)
  - Authentication required for all operations
  - Audit logging for all data access
- **Secure Storage**:
  - Credentials stored in encrypted format
  - No plaintext storage of sensitive data

#### 4.3 Data Processing
- **AI Services**: Email content is sent to AI service providers (OpenAI) for processing
- **Third-Party Services**: 
  - Google Gmail API for email access
  - Google Drive API (optional) for attachment storage
  - Google Contacts API (optional) for contact sync

### 5. Data Sharing and Disclosure

#### 5.1 Third-Party Services
- **Google Services**: We use Google APIs with your explicit consent
- **AI Providers**: Email content is processed by OpenAI (subject to their privacy policy)
- **No Sale of Data**: We do not sell your personal information to third parties

#### 5.2 Legal Requirements
We may disclose your information if required by:
- Law enforcement agencies
- Court orders or legal processes
- Regulatory authorities
- To protect our rights or prevent harm

### 6. Your Rights (GDPR/APP Compliance)

#### 6.1 Right to Access
- You can request a copy of all your personal data
- Export your data via the API endpoint: `GET /api/v1/data/export`

#### 6.2 Right to Rectification
- You can correct inaccurate data through the Extension interface
- Manual project corrections are stored for learning

#### 6.3 Right to Erasure ("Right to be Forgotten")
- You can delete your account and all associated data
- Use the API endpoint: `DELETE /api/v1/data/delete` (with confirmation)
- Data anonymization option available for compliance

#### 6.4 Right to Data Portability
- Export your data in JSON format
- Includes all projects, emails, configurations, and history

#### 6.5 Right to Object
- You can disable email scanning at any time
- Opt out of specific features (e.g., Google Drive integration)

#### 6.6 Right to Restrict Processing
- Pause email scanning without deleting data
- Configure scanning frequency and filters

### 7. Data Retention

- **Active Accounts**: Data retained while account is active
- **Inactive Accounts**: Data retained for 12 months after last activity
- **Account Deletion**: All data deleted within 30 days of deletion request
- **Audit Logs**: Retained for 2 years for security and compliance

### 8. Children's Privacy

The Extension is not intended for users under 18 years of age. We do not knowingly collect personal information from children.

### 9. International Data Transfers

- **AI Processing**: Email content may be processed by OpenAI (US-based)
- **Data Storage**: Data stored in secure cloud infrastructure
- **Safeguards**: Standard contractual clauses and encryption in transit

### 10. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. We will notify you of significant changes via:
- Email notification
- In-app notification
- Updated version date

### 11. Contact Information

For privacy-related inquiries or to exercise your rights:
- **Email**: privacy@tradie-gsuite.com
- **Data Protection Officer**: dpo@tradie-gsuite.com

### 12. Compliance

- **Australian Privacy Principles (APPs)**: Fully compliant
- **GDPR**: Compliant with European data protection regulations
- **Industry Standards**: Following best practices for data security

### 13. Security Incident Response

In the event of a data breach:
- We will notify affected users within 72 hours
- We will notify relevant authorities as required by law
- We will provide details and remediation steps

---

**Your Consent**: By using the Extension, you consent to this Privacy Policy and our data practices.

