# GDPR Compliance Documentation
## AI Email Grouping Extension for Gmail

**Last Updated:** 2025  
**Version:** 1.0

### Overview

This document outlines our compliance with the General Data Protection Regulation (GDPR) and the Australian Privacy Principles (APPs).

### Legal Basis for Processing

#### 1. Consent (Article 6(1)(a) GDPR)
- Users explicitly consent to data processing when installing the Extension
- OAuth consent screen provides clear information about data access
- Users can withdraw consent at any time by disabling scanning

#### 2. Legitimate Interest (Article 6(1)(f) GDPR)
- Processing email data is necessary for the core functionality of the Extension
- AI processing improves accuracy and user experience
- Audit logging for security and compliance

### Data Controller and Processor

- **Data Controller**: Tradie GSuite (Extension provider)
- **Data Processor**: 
  - OpenAI (AI processing services)
  - Google (Gmail, Drive, Contacts APIs)
  - Cloud infrastructure providers

### Data Processing Activities

#### 1. Email Processing
- **Purpose**: Group emails by project/job
- **Legal Basis**: Consent (user-installed Extension)
- **Data Minimization**: Only processes emails user explicitly selects
- **Retention**: Until account deletion or user request

#### 2. AI Processing
- **Purpose**: Extract entities, analyze content, group emails
- **Legal Basis**: Consent (explicit AI processing consent)
- **Third-Party**: OpenAI (US-based, subject to their privacy policy)
- **Data Transfer**: Encrypted in transit, subject to standard contractual clauses

#### 3. Project Management
- **Purpose**: Organize emails by project with metadata
- **Legal Basis**: Legitimate interest (core functionality)
- **Data Types**: Project names, addresses, client information
- **Storage**: Encrypted database

### User Rights Implementation

#### 1. Right of Access (Article 15)
- **Implementation**: `GET /api/v1/data/export`
- **Response Time**: Within 30 days
- **Format**: JSON export of all user data

#### 2. Right to Rectification (Article 16)
- **Implementation**: Manual correction interface
- **User Actions**: Rename projects, reassign emails
- **Storage**: Corrections stored for learning

#### 3. Right to Erasure (Article 17)
- **Implementation**: `DELETE /api/v1/data/delete`
- **Confirmation**: Required parameter `confirm=true`
- **Process**: Complete deletion of all user data
- **Anonymization**: Option to anonymize instead of delete

#### 4. Right to Restrict Processing (Article 18)
- **Implementation**: Disable scanning in configuration
- **Options**: Pause, disable, or configure filters
- **Effect**: Stops new processing, retains existing data

#### 5. Right to Data Portability (Article 20)
- **Implementation**: `GET /api/v1/data/export?format=json`
- **Format**: Machine-readable JSON
- **Scope**: All user data (projects, emails, configurations)

#### 6. Right to Object (Article 21)
- **Implementation**: Opt-out of specific features
- **Options**: 
  - Disable Google Drive integration
  - Disable Google Contacts sync
  - Disable AI processing (manual mode only)

### Data Protection Measures

#### 1. Encryption
- **At Rest**: AES-256 encryption for sensitive data
- **In Transit**: TLS/HTTPS for all communications
- **Credentials**: OAuth tokens encrypted in database

#### 2. Access Control
- **Authentication**: Required for all operations
- **Authorization**: Role-based access control (RBAC)
- **Audit Logging**: All access logged and monitored

#### 3. Data Minimization
- **Processing**: Only necessary data for functionality
- **Storage**: Only retain data required for service
- **Retention**: Deleted upon account deletion

#### 4. Security Measures
- **Secure Storage**: Encrypted credential storage
- **API Security**: Token-based authentication
- **Error Handling**: Secure error messages (no data leakage)

### Data Breach Procedures

#### 1. Detection
- Automated monitoring for security incidents
- Audit log analysis for suspicious activity
- Regular security assessments

#### 2. Notification
- **Users**: Within 72 hours of detection
- **Authorities**: Within 72 hours (GDPR Article 33)
- **Content**: Nature of breach, data affected, remediation steps

#### 3. Response
- Immediate containment of breach
- Assessment of impact
- Remediation and prevention measures

### Data Processing Agreements

#### 1. OpenAI
- **Purpose**: AI processing of email content
- **Data Transfer**: Encrypted, subject to OpenAI's privacy policy
- **Safeguards**: Standard contractual clauses

#### 2. Google Services
- **Gmail API**: Email access and management
- **Drive API**: Optional attachment storage
- **Contacts API**: Optional contact sync
- **Consent**: OAuth consent screen

### Data Retention Policy

- **Active Accounts**: Data retained while account is active
- **Inactive Accounts**: 12 months after last activity
- **Account Deletion**: 30 days to complete deletion
- **Audit Logs**: 2 years for compliance

### International Data Transfers

#### 1. Transfers to Third Countries
- **OpenAI (US)**: Standard contractual clauses
- **Cloud Infrastructure**: EU-US Privacy Shield or equivalent

#### 2. Safeguards
- Encryption in transit and at rest
- Data processing agreements
- Regular security assessments

### Privacy by Design

- **Minimal Data Collection**: Only necessary data
- **Default Privacy**: Secure defaults, opt-in for sensitive features
- **Data Minimization**: Process only required data
- **Transparency**: Clear privacy policy and documentation

### Record Keeping

- **Processing Activities**: Documented in this file
- **Data Breaches**: Logged and reported
- **User Requests**: Tracked and fulfilled within 30 days
- **Audit Logs**: Retained for 2 years

### Data Protection Impact Assessment (DPIA)

#### High-Risk Processing
- **Email Content Processing**: AI analysis of personal emails
- **Third-Party AI**: OpenAI processing
- **Mitigation**: Encryption, access controls, audit logging

#### Risk Assessment
- **Low Risk**: Configuration settings, project metadata
- **Medium Risk**: Email metadata, client information
- **High Risk**: Email content, OAuth tokens

### Compliance Monitoring

- **Regular Audits**: Annual compliance reviews
- **Security Assessments**: Regular penetration testing
- **Privacy Reviews**: Quarterly privacy policy reviews
- **User Feedback**: Continuous improvement based on feedback

### Contact Information

**Data Protection Officer**: dpo@tradie-gsuite.com  
**Privacy Inquiries**: privacy@tradie-gsuite.com  
**Data Requests**: Use API endpoints or contact support

---

**Compliance Status**: ✅ Compliant with GDPR and APPs as of 2025

