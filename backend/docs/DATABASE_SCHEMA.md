# Database Schema Documentation
## TASK-037: Complete Database Schema Design

### Overview

The database schema is designed to support AI-powered email grouping with project management, learning capabilities, and comprehensive configuration options.

### Database Technology
- **Engine**: SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Encryption**: AES-256 for sensitive fields

### Schema Tables

#### 1. Users Table (`users`)
**Purpose**: Store user authentication and profile information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique user ID |
| email | String | Unique, Indexed | User email address |
| name | String | Nullable | User's full name |
| picture | String | Nullable | Google profile picture URL |
| google_id | String | Unique, Indexed | Google account ID |
| access_token | String | Nullable, Encrypted | OAuth access token (encrypted) |
| refresh_token | String | Nullable, Encrypted | OAuth refresh token (encrypted) |
| token_expires_at | DateTime | Nullable | Token expiration timestamp |
| role | Enum | Default: USER | User role (admin, user, viewer) |
| is_active | Boolean | Default: True | Account active status |
| created_at | DateTime | Not Null | Account creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |
| last_login | DateTime | Nullable | Last login timestamp |

**Relationships**:
- One-to-Many: Projects, EmailProjectMappings, ScanConfigurations, etc.

#### 2. Projects Table (`projects`)
**Purpose**: Store project/job metadata

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique project record ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| project_id | String | Unique, Indexed | Unique project identifier |
| project_name | String | Not Null, Indexed | Project name |
| project_name_aliases | JSON | Nullable | Alternative names for project |
| address | Text | Nullable | Full property address |
| street | String | Nullable | Street address |
| suburb | String | Nullable | Suburb/Locality |
| state | String | Nullable | State/Province |
| postcode | String | Nullable | Postal code |
| client_name | String | Nullable, Indexed | Client name |
| client_email | String | Nullable | Client email |
| client_phone | String | Nullable | Client phone |
| client_company | String | Nullable | Client company |
| project_type | String | Nullable | Type (renovation, new_build, etc.) |
| job_numbers | JSON | Nullable | List of job numbers |
| status | String | Default: active | Status (active, completed, on_hold, archived) |
| email_count | Integer | Default: 0 | Total emails in project |
| last_email_at | DateTime | Nullable | Last email timestamp |
| created_from_email_id | String | Nullable | First email that created project |
| confidence_score | String | Nullable | Initial confidence score |
| needs_review | Boolean | Default: False, Indexed | Review flag |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

**Indexes**:
- `user_id` (for user filtering)
- `project_id` (for unique lookups)
- `project_name` (for search)
- `client_name` (for client filtering)
- `needs_review` (for review queue)

#### 3. Email Project Mappings Table (`email_project_mappings`)
**Purpose**: Associate emails with projects

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique mapping ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| project_id | Integer | Foreign Key, Indexed | Project ID |
| email_id | String | Not Null, Indexed | Gmail message ID |
| thread_id | String | Nullable, Indexed | Gmail thread ID |
| confidence | String | Nullable | Association confidence |
| association_method | String | Nullable | Method (auto, manual, ai, similarity) |
| is_primary | Boolean | Default: True | Primary association flag |
| is_active | Boolean | Default: True, Indexed | Active mapping flag |
| created_at | DateTime | Not Null, Indexed | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

**Indexes**:
- `user_id` + `project_id` (composite, for project queries)
- `email_id` (for email lookups)
- `thread_id` (for thread grouping)
- `is_active` (for active filtering)

#### 4. Email Attachments Table (`email_attachments`)
**Purpose**: Store attachment metadata

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique attachment ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| email_id | String | Not Null, Indexed | Gmail email ID |
| thread_id | String | Nullable, Indexed | Gmail thread ID |
| attachment_id | String | Not Null | Gmail attachment ID |
| filename | String | Not Null | Attachment filename |
| mime_type | String | Nullable | MIME type |
| size | BigInteger | Not Null | File size in bytes |
| project_id | String | Nullable, Indexed | Associated project |
| file_extension | String | Nullable | File extension |
| file_type_category | String | Nullable | Category (document, image, etc.) |
| project_indicators | JSON | Nullable | Extracted project indicators |
| drive_file_id | String | Nullable, Indexed | Google Drive file ID |
| drive_url | String | Nullable | Google Drive URL |
| is_uploaded_to_drive | Boolean | Default: False | Upload status |
| additional_metadata | JSON | Nullable | Additional metadata |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

**Indexes**:
- `user_id` + `project_id` (for project attachments)
- `email_id` (for email attachments)
- `drive_file_id` (for Drive lookups)

#### 5. Scan Configurations Table (`scan_configurations`)
**Purpose**: Store user scanning preferences

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique config ID |
| user_id | Integer | Foreign Key, Unique, Indexed | Owner user ID |
| is_enabled | Boolean | Default: True | Scanning enabled |
| scan_frequency | String | Default: realtime | Frequency (realtime, hourly, daily, weekly, manual) |
| last_scan_at | DateTime | Nullable | Last scan timestamp |
| included_labels | JSON | Nullable | Label IDs to include |
| excluded_labels | JSON | Nullable | Label IDs to exclude |
| label_filter_action | String | Default: include | Filter action (include/exclude) |
| excluded_senders | JSON | Nullable | Excluded email addresses |
| excluded_domains | JSON | Nullable | Excluded domains |
| scan_retroactive | Boolean | Default: False | Enable retroactive scanning |
| retroactive_date_start | DateTime | Nullable | Retroactive start date |
| retroactive_date_end | DateTime | Nullable | Retroactive end date |
| scan_options | JSON | Nullable | Additional options |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 6. AI Processing Queue Table (`ai_processing_queue`)
**Purpose**: Queue AI processing tasks

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique queue item ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| task_type | String | Not Null, Indexed | Task type |
| email_id | String | Nullable, Indexed | Target email ID |
| thread_id | String | Nullable, Indexed | Target thread ID |
| status | String | Default: pending, Indexed | Status (pending, processing, completed, failed) |
| priority | Integer | Default: 5 | Priority (1-10) |
| retry_count | Integer | Default: 0 | Retry attempts |
| max_retries | Integer | Default: 3 | Maximum retries |
| result_data | JSON | Nullable | Processing results |
| error_message | Text | Nullable | Error message |
| processed_at | DateTime | Nullable | Processing timestamp |
| task_metadata | JSON | Nullable | Additional task parameters |
| created_at | DateTime | Not Null, Indexed | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |
| scheduled_at | DateTime | Nullable | Scheduled processing time |

#### 7. Batch Processing Jobs Table (`batch_processing_jobs`)
**Purpose**: Track batch processing operations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique job ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| job_type | String | Not Null | Job type |
| date_range_start | DateTime | Nullable | Start date |
| date_range_end | DateTime | Nullable | End date |
| status | String | Default: pending, Indexed | Status |
| total_items | Integer | Default: 0 | Total items to process |
| processed_items | Integer | Default: 0 | Items processed |
| failed_items | Integer | Default: 0 | Items failed |
| batch_size | Integer | Default: 50 | Batch size |
| processing_config | JSON | Nullable | Job configuration |
| result_summary | JSON | Nullable | Results summary |
| error_message | Text | Nullable | Error message |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |
| started_at | DateTime | Nullable | Start timestamp |
| completed_at | DateTime | Nullable | Completion timestamp |

#### 8. User Corrections Table (`user_corrections`)
**Purpose**: Store user corrections for AI learning

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique correction ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| correction_type | String | Not Null, Indexed | Type (project_assignment, merge, split, rename) |
| original_result | JSON | Not Null | Original AI result |
| corrected_result | JSON | Not Null | User's correction |
| email_id | String | Nullable, Indexed | Related email ID |
| project_id | String | Nullable, Indexed | Related project ID |
| original_confidence | String | Nullable | Original confidence score |
| learning_features | JSON | Nullable | Extracted learning features |
| correction_reason | Text | Nullable | User's reason |
| is_processed | Boolean | Default: False, Indexed | Processing status |
| processed_at | DateTime | Nullable | Processing timestamp |
| created_at | DateTime | Not Null, Indexed | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 9. Model Feedback Table (`model_feedback`)
**Purpose**: Store user feedback for model improvement

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique feedback ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| feedback_type | String | Not Null | Feedback type |
| rating | Integer | Nullable | Rating (1-5) |
| comment | Text | Nullable | Feedback comment |
| context | JSON | Nullable | Feedback context |
| is_processed | Boolean | Default: False | Processing status |
| processed_at | DateTime | Nullable | Processing timestamp |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 10. Learning Patterns Table (`learning_patterns`)
**Purpose**: Store learned patterns from corrections

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique pattern ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| pattern_type | String | Not Null | Pattern type |
| pattern_data | JSON | Not Null | Pattern data |
| confidence | Float | Nullable | Pattern confidence |
| usage_count | Integer | Default: 0 | Usage frequency |
| is_active | Boolean | Default: True | Active status |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 11. Gmail Watch Table (`gmail_watches`)
**Purpose**: Store Gmail watch subscriptions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique watch ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| topic_name | String | Nullable | Pub/Sub topic |
| history_id | String | Nullable | Last history ID |
| expiration | DateTime | Nullable | Watch expiration |
| is_active | Boolean | Default: True | Active status |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 12. Notification Queue Table (`notification_queue`)
**Purpose**: Queue email notifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique queue item ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| notification_type | String | Not Null | Notification type |
| message_id | String | Nullable, Indexed | Gmail message ID |
| status | String | Default: pending, Indexed | Status |
| retry_count | Integer | Default: 0 | Retry attempts |
| max_retries | Integer | Default: 3 | Maximum retries |
| error_message | Text | Nullable | Error message |
| processed_at | DateTime | Nullable | Processing timestamp |
| created_at | DateTime | Not Null, Indexed | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 13. Scheduled Scans Table (`scheduled_scans`)
**Purpose**: Store scheduled scan configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique scan ID |
| user_id | Integer | Foreign Key, Indexed | Owner user ID |
| schedule_type | String | Not Null | Type (daily, weekly, custom) |
| schedule_time | String | Nullable | Time (HH:MM) |
| schedule_day | String | Nullable | Day of week |
| schedule_cron | String | Nullable | Cron expression |
| is_active | Boolean | Default: True, Indexed | Active status |
| last_run_at | DateTime | Nullable | Last run timestamp |
| next_run_at | DateTime | Nullable, Indexed | Next run timestamp |
| run_count | Integer | Default: 0 | Total runs |
| last_run_result | JSON | Nullable | Last run results |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

#### 14. Attachment Project Mappings Table (`attachment_project_mappings`)
**Purpose**: Map attachments to projects

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique mapping ID |
| attachment_id | Integer | Foreign Key, Indexed | Attachment ID |
| project_id | String | Not Null, Indexed | Project ID |
| confidence | String | Nullable | Association confidence |
| association_method | String | Nullable | Method (filename, email_content, manual, etc.) |
| created_at | DateTime | Not Null | Creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

### Key Relationships

```
User (1) ──< (Many) Projects
User (1) ──< (Many) EmailProjectMappings
User (1) ──< (Many) ScanConfigurations
User (1) ──< (Many) AIProcessingQueue
User (1) ──< (Many) UserCorrections

Project (1) ──< (Many) EmailProjectMappings
Project (1) ──< (Many) EmailAttachments (via project_id)
EmailAttachment (1) ──< (Many) AttachmentProjectMappings
```

### Indexing Strategy

**Performance Indexes**:
- User-based queries: `user_id` on all user-scoped tables
- Project lookups: `project_id` on projects, mappings
- Email lookups: `email_id` on mappings, attachments
- Status filtering: `status`, `is_active` on processing tables
- Time-based queries: `created_at` on queue tables

**Composite Indexes** (for common queries):
- `(user_id, project_id)` on email_project_mappings
- `(user_id, status)` on ai_processing_queue
- `(user_id, is_active)` on various tables

### Data Privacy Considerations

**Sensitive Data Encryption**:
- `access_token`, `refresh_token` in users table (AES-256)
- Future: client PII encryption option

**Data Retention**:
- User data retained until account deletion
- Correction history for learning improvement
- Audit trail for compliance

### Migration Strategy

- **Alembic** for database migrations
- Version-controlled schema changes
- Backward compatibility considerations
- Data migration scripts for schema updates

