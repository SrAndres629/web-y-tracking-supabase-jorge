# =================================================================
# SQL QUERIES REPOSITORY
# Jorge Aguirre Flores Web
# =================================================================

# --- DDL: Table Initialization ---
# Note: Designed to work with both PostgreSQL and SQLite (with some python-side logic for types)

CREATE_TABLE_BUSINESS_KNOWLEDGE = """
    CREATE TABLE IF NOT EXISTS business_knowledge (
        id {id_type_serial},
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL, -- 'pricing', 'bio', 'location', 'policy'
        content TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT {timestamp_default}
    );
"""

CREATE_INDEX_KNOWLEDGE_SLUG = "CREATE INDEX IF NOT EXISTS idx_knowledge_slug ON business_knowledge(slug);"

CREATE_TABLE_VISITORS = """
    CREATE TABLE IF NOT EXISTS visitors (
        id {id_type_serial},
        external_id TEXT,
        fbclid TEXT,
        ip_address TEXT,
        user_agent TEXT,
        source TEXT,
        utm_source TEXT,
        utm_medium TEXT,
        utm_campaign TEXT,
        utm_term TEXT,
        utm_content TEXT,
        timestamp TIMESTAMP DEFAULT {timestamp_default}
    );
"""

CREATE_INDEX_VISITORS_EXTERNAL_ID = "CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);"

CREATE_TABLE_CONTACTS = """
    CREATE TABLE IF NOT EXISTS contacts (
        id {id_type_primary_key},
        whatsapp_number TEXT UNIQUE NOT NULL,
        full_name TEXT,
        profile_pic_url TEXT,
        
        fb_click_id TEXT,
        fb_browser_id TEXT,
        utm_source TEXT,
        utm_medium TEXT,
        utm_campaign TEXT,
        utm_term TEXT,
        utm_content TEXT,
        web_visit_count INTEGER DEFAULT 1,
        conversion_sent_to_meta BOOLEAN DEFAULT FALSE,
        
        status {status_type},
        lead_score INTEGER DEFAULT 50,
        pain_point TEXT,
        service_interest TEXT,
        service_booked_date TIMESTAMP,
        appointment_count INTEGER DEFAULT 0,
        
        created_at TIMESTAMP DEFAULT {timestamp_default},
        updated_at TIMESTAMP,
        last_interaction TIMESTAMP DEFAULT {timestamp_default}
    );
"""

CREATE_INDEX_CONTACTS_WHATSAPP = "CREATE INDEX IF NOT EXISTS idx_contacts_whatsapp ON contacts(whatsapp_number);"
CREATE_INDEX_CONTACTS_STATUS = "CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);"

CREATE_TABLE_MESSAGES = """
    CREATE TABLE IF NOT EXISTS messages (
        id {id_type_primary_key},
        contact_id INTEGER,
        role TEXT CHECK (role IN ('user', 'assistant', 'system', 'tool')),
        content TEXT,
        created_at TIMESTAMP DEFAULT {timestamp_default},
        FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );
"""

CREATE_INDEX_MESSAGES_CONTACT_ID = "CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);"

CREATE_TABLE_APPOINTMENTS = """
    CREATE TABLE IF NOT EXISTS appointments (
        id {id_type_serial},
        contact_id INTEGER,
        appointment_date TIMESTAMP NOT NULL,
        service_type TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT {timestamp_default},
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    );
"""

CREATE_TABLE_LEADS = """
    CREATE TABLE IF NOT EXISTS leads (
        id {id_type_primary_key},
        whatsapp_phone TEXT UNIQUE NOT NULL,
        meta_lead_id TEXT,
        click_id TEXT, -- fbclid
        email TEXT,
        name TEXT,
        conversion_status TEXT DEFAULT 'NEW',
        created_at TIMESTAMP DEFAULT {timestamp_default},
        last_interaction TIMESTAMP DEFAULT {timestamp_default}
    );
"""

CREATE_INDEX_LEADS_PHONE = "CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(whatsapp_phone);"
CREATE_INDEX_LEADS_META_ID = "CREATE INDEX IF NOT EXISTS idx_leads_meta_id ON leads(meta_lead_id);"

CREATE_TABLE_INTERACTIONS = """
    CREATE TABLE IF NOT EXISTS interactions (
        id {id_type_serial},
        lead_id {lead_id_type},
        role TEXT NOT NULL, -- 'user', 'system', 'assistant'
        content TEXT,
        timestamp TIMESTAMP DEFAULT {timestamp_default},
        FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
    );
"""

CREATE_INDEX_INTERACTIONS_LEAD_ID = "CREATE INDEX IF NOT EXISTS idx_interactions_lead_id ON interactions(lead_id);"

# --- DML: Operations ---

INSERT_VISITOR = """
    INSERT INTO visitors (
        external_id, fbclid, ip_address, user_agent, source,
        utm_source, utm_medium, utm_campaign, utm_term, utm_content
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPSERT_CONTACT_SQLITE = """
    INSERT INTO contacts (whatsapp_number, full_name, utm_source, status)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT(whatsapp_number) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        utm_source = COALESCE(EXCLUDED.utm_source, contacts.utm_source),
        last_interaction = CURRENT_TIMESTAMP
"""

UPSERT_CONTACT_POSTGRES = """
    INSERT INTO contacts (
        whatsapp_number, full_name, profile_pic_url,
        fb_click_id, fb_browser_id,
        utm_source, utm_medium, utm_campaign, utm_term, utm_content,
        status, lead_score, pain_point, service_interest,
        last_interaction
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    ON CONFLICT (whatsapp_number) 
    DO UPDATE SET 
        full_name = COALESCE(EXCLUDED.full_name, contacts.full_name),
        profile_pic_url = COALESCE(EXCLUDED.profile_pic_url, contacts.profile_pic_url),
        fb_click_id = COALESCE(EXCLUDED.fb_click_id, contacts.fb_click_id),
        utm_source = COALESCE(EXCLUDED.utm_source, contacts.utm_source),
        status = COALESCE(EXCLUDED.status, contacts.status),
        lead_score = COALESCE(EXCLUDED.lead_score, contacts.lead_score),
        pain_point = COALESCE(EXCLUDED.pain_point, contacts.pain_point),
        service_interest = COALESCE(EXCLUDED.service_interest, contacts.service_interest),
        last_interaction = NOW(),
        web_visit_count = contacts.web_visit_count + 1,
        updated_at = NOW();
"""

SELECT_CONTACT_ID_BY_PHONE = "SELECT id FROM contacts WHERE whatsapp_number = %s"

INSERT_MESSAGE = "INSERT INTO messages (contact_id, role, content) VALUES (%s, %s, %s)"

SELECT_CHAT_HISTORY = """
    SELECT m.role, m.content 
    FROM messages m
    JOIN contacts c ON m.contact_id = c.id
    WHERE c.whatsapp_number = %s
    ORDER BY m.created_at DESC
    LIMIT %s
"""

SELECT_FBCLID_BY_EXTERNAL_ID = "SELECT fbclid FROM visitors WHERE external_id = %s AND fbclid IS NOT NULL ORDER BY timestamp DESC LIMIT 1"

SELECT_RECENT_VISITORS = "SELECT id, external_id, source, timestamp, ip_address FROM visitors ORDER BY timestamp DESC LIMIT %s"

SELECT_VISITOR_BY_ID = "SELECT id, external_id, fbclid, source, timestamp FROM visitors WHERE id = %s"

# --- Operations: Leads (W-003) ---

UPDATE_LEAD_SENT_FLAG = "UPDATE contacts SET conversion_sent_to_meta = TRUE WHERE whatsapp_number = %s"

COUNT_USER_MESSAGES = """
    SELECT COUNT(*) FROM messages m
    JOIN contacts c ON m.contact_id = c.id
    WHERE c.whatsapp_number = %s AND m.role = 'user'
"""

CHECK_LEAD_SENT_FLAG = "SELECT conversion_sent_to_meta FROM contacts WHERE whatsapp_number = %s"

SELECT_META_DATA_BY_REF = """
    SELECT fbclid, user_agent, ip_address, utm_source, utm_medium, utm_campaign
    FROM visitors 
    WHERE external_id LIKE %s 
    ORDER BY timestamp DESC LIMIT 1
"""

SELECT_LEAD_ID_BY_PHONE = "SELECT id FROM leads WHERE whatsapp_phone = %s"

UPDATE_LEAD_METADATA = """
    UPDATE leads SET 
        meta_lead_id = COALESCE(%s, meta_lead_id),
        click_id = COALESCE(%s, click_id),
        email = COALESCE(%s, email),
        name = COALESCE(%s, name),
        last_interaction = CURRENT_TIMESTAMP
    WHERE id = %s
"""

INSERT_LEAD_RETURNING_ID = """
    INSERT INTO leads (whatsapp_phone, meta_lead_id, click_id, email, name)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
"""

INSERT_LEAD_SQLITE = """
    INSERT INTO leads (id, whatsapp_phone, meta_lead_id, click_id, email, name)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

INSERT_INTERACTION = "INSERT INTO interactions (lead_id, role, content) VALUES (%s, %s, %s)"

# --- Knowledge Base ---

UPSERT_KNOWLEDGE_POSTGRES = """
    INSERT INTO business_knowledge (slug, category, content, updated_at)
    VALUES (%s, %s, %s, NOW())
    ON CONFLICT (slug) DO UPDATE SET
        content = EXCLUDED.content,
        category = EXCLUDED.category,
        updated_at = NOW();
"""

UPSERT_KNOWLEDGE_SQLITE = """
    INSERT INTO business_knowledge (slug, category, content)
    VALUES (%s, %s, %s)
    ON CONFLICT (slug) DO UPDATE SET
        content = EXCLUDED.content,
        category = EXCLUDED.category;
"""
