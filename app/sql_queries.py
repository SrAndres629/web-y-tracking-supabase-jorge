# =================================================================
# SQL QUERIES REPOSITORY
# Jorge Aguirre Flores Web
# =================================================================

# --- DDL: Table Initialization ---
CREATE_TABLE_SITE_CONTENT = """
    CREATE TABLE IF NOT EXISTS site_content (
        key TEXT PRIMARY KEY,
        value JSONB,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
# Note: Designed to work with both PostgreSQL and SQLite (with some python-side logic for types)

CREATE_TABLE_CLIENTS = """
    CREATE TABLE IF NOT EXISTS clients (
        id {id_type_pk},
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        company TEXT,
        meta_pixel_id TEXT,
        meta_access_token TEXT,
        plan TEXT DEFAULT 'starter',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT {timestamp_default}
    )
"""

CREATE_TABLE_API_KEYS = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id {id_type_serial},
        client_id {lead_id_type} REFERENCES clients(id),
        key_hash TEXT UNIQUE NOT NULL,
        name TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT {timestamp_default}
    )
"""

CREATE_TABLE_EMQ_STATS = """
    CREATE TABLE IF NOT EXISTS emq_stats (
        id {id_type_serial},
        client_id {lead_id_type} REFERENCES clients(id),
        event_name TEXT NOT NULL,
        score FLOAT NOT NULL,
        payload_size INTEGER,
        has_pii BOOLEAN,
        created_at TIMESTAMP DEFAULT {timestamp_default}
    )
"""

CREATE_TABLE_BUSINESS_KNOWLEDGE = """
    CREATE TABLE IF NOT EXISTS business_knowledge (
        id {id_type_serial},
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL, -- 'pricing', 'bio', 'location', 'policy'
        content TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT {timestamp_default}
    );
"""

CREATE_INDEX_KNOWLEDGE_SLUG = (
    "CREATE INDEX IF NOT EXISTS idx_knowledge_slug ON business_knowledge(slug);"
)

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
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT {timestamp_default}
    );
"""

CREATE_INDEX_VISITORS_EXTERNAL_ID = (
    "CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);"
)

CREATE_TABLE_CONTACTS = """
    CREATE TABLE IF NOT EXISTS crm_leads (
        id {id_type_primary_key},
        whatsapp_phone TEXT UNIQUE NOT NULL,
        full_name TEXT,
        email TEXT, -- Agregado para paridad
        meta_lead_id TEXT, -- Agregado para paridad
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
        last_interaction TIMESTAMP DEFAULT {timestamp_default},
        created_at TIMESTAMP DEFAULT {timestamp_default},
        updated_at TIMESTAMP
    );
"""

CREATE_INDEX_CONTACTS_WHATSAPP = (
    "CREATE INDEX IF NOT EXISTS idx_contacts_whatsapp ON crm_leads(whatsapp_phone);"
)
CREATE_INDEX_CONTACTS_STATUS = (
    "CREATE INDEX IF NOT EXISTS idx_contacts_status ON crm_leads(status);"
)

CREATE_TABLE_MESSAGES = """
    CREATE TABLE IF NOT EXISTS messages (
        id {id_type_primary_key},
        contact_id INTEGER,
        role TEXT CHECK (role IN ('user', 'assistant', 'system', 'tool')),
        content TEXT,
        created_at TIMESTAMP DEFAULT {timestamp_default},
        FOREIGN KEY (contact_id) REFERENCES crm_leads(id) ON DELETE CASCADE
    );
"""

CREATE_INDEX_MESSAGES_CONTACT_ID = (
    "CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);"
)

CREATE_TABLE_APPOINTMENTS = """
    CREATE TABLE IF NOT EXISTS appointments (
        id {id_type_serial},
        contact_id INTEGER,
        appointment_date TIMESTAMP NOT NULL,
        service_type TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT {timestamp_default},
        FOREIGN KEY (contact_id) REFERENCES crm_leads(id)
    );
"""

# Note: redundant leads table definitions removed. Everything points to crm_leads.

CREATE_TABLE_INTERACTIONS = """
    CREATE TABLE IF NOT EXISTS interactions (
        id {id_type_serial},
        lead_id {lead_id_type},
        role TEXT NOT NULL, -- 'user', 'system', 'assistant'
        content TEXT,
        timestamp TIMESTAMP DEFAULT {timestamp_default},
        FOREIGN KEY (lead_id) REFERENCES crm_leads(id) ON DELETE CASCADE
    );
"""

CREATE_INDEX_INTERACTIONS_LEAD_ID = (
    "CREATE INDEX IF NOT EXISTS idx_interactions_lead_id ON interactions(lead_id);"
)

# --- DML: Operations ---

INSERT_VISITOR = """
    INSERT INTO visitors (
        external_id, fbclid, ip_address, user_agent, source,
        utm_source, utm_medium, utm_campaign, utm_term, utm_content, email, phone
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPSERT_CONTACT_SQLITE = """
    INSERT INTO crm_leads (whatsapp_phone, full_name, utm_source, status)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT(whatsapp_phone) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        utm_source = COALESCE(EXCLUDED.utm_source, crm_leads.utm_source),
        last_interaction = CURRENT_TIMESTAMP
"""

UPSERT_CONTACT_POSTGRES = """
    INSERT INTO crm_leads (
        whatsapp_phone, full_name, profile_pic_url,
        fb_click_id, fb_browser_id,
        utm_source, utm_medium, utm_campaign, utm_term, utm_content,
        status, lead_score, pain_point, service_interest,
        last_interaction
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    ON CONFLICT (whatsapp_phone)
    DO UPDATE SET
        full_name = COALESCE(EXCLUDED.full_name, crm_leads.full_name),
        profile_pic_url = COALESCE(EXCLUDED.profile_pic_url, crm_leads.profile_pic_url),
        fb_click_id = COALESCE(EXCLUDED.fb_click_id, crm_leads.fb_click_id),
        utm_source = COALESCE(EXCLUDED.utm_source, crm_leads.utm_source),
        status = COALESCE(EXCLUDED.status, crm_leads.status),
        lead_score = COALESCE(EXCLUDED.lead_score, crm_leads.lead_score),
        pain_point = COALESCE(EXCLUDED.pain_point, crm_leads.pain_point),
        service_interest = COALESCE(EXCLUDED.service_interest, crm_leads.service_interest),
        last_interaction = NOW(),
        web_visit_count = crm_leads.web_visit_count + 1,
        updated_at = NOW();
"""

SELECT_CONTACT_ID_BY_PHONE = "SELECT id FROM crm_leads WHERE whatsapp_phone = %s"

INSERT_MESSAGE = "INSERT INTO messages (contact_id, role, content) VALUES (%s, %s, %s)"

SELECT_CHAT_HISTORY = """
    SELECT m.role, m.content
    FROM messages m
    JOIN crm_leads c ON m.contact_id = c.id
    WHERE c.whatsapp_phone = %s
    ORDER BY m.created_at DESC
    LIMIT %s
"""

SELECT_FBCLID_BY_EXTERNAL_ID = "SELECT fbclid FROM visitors WHERE external_id = %s AND fbclid IS NOT NULL ORDER BY created_at DESC LIMIT 1"

SELECT_RECENT_VISITORS = "SELECT id, external_id, source, created_at, ip_address FROM visitors ORDER BY created_at DESC LIMIT %s"

SELECT_VISITOR_BY_ID = (
    "SELECT id, external_id, fbclid, source, created_at FROM visitors WHERE id = %s"
)

# --- Operations: Leads (W-003) ---

UPDATE_LEAD_SENT_FLAG = (
    "UPDATE crm_leads SET conversion_sent_to_meta = TRUE WHERE whatsapp_phone = %s"
)

COUNT_USER_MESSAGES = """
    SELECT COUNT(*) FROM messages m
    JOIN crm_leads c ON m.contact_id = c.id
    WHERE c.whatsapp_phone = %s AND m.role = 'user'
"""

CHECK_LEAD_SENT_FLAG = "SELECT conversion_sent_to_meta FROM crm_leads WHERE whatsapp_phone = %s"

SELECT_META_DATA_BY_REF = """
    SELECT fbclid, user_agent, ip_address, utm_source, utm_medium, utm_campaign
    FROM visitors
    WHERE external_id LIKE %s
    ORDER BY created_at DESC LIMIT 1
"""

SELECT_LEAD_ID_BY_PHONE = "SELECT id FROM crm_leads WHERE whatsapp_phone = %s"
SELECT_LEAD_BY_PHONE = "SELECT * FROM crm_leads WHERE whatsapp_phone = %s"

UPDATE_LEAD_METADATA = """
    UPDATE crm_leads SET
        meta_lead_id = COALESCE(%s, meta_lead_id),
        fb_click_id = COALESCE(%s, fb_click_id),
        email = COALESCE(%s, email),
        full_name = COALESCE(%s, full_name),
        last_interaction = CURRENT_TIMESTAMP
    WHERE id = %s
"""

INSERT_LEAD_RETURNING_ID = """
    INSERT INTO crm_leads (whatsapp_phone, meta_lead_id, fb_click_id, email, full_name)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
"""

INSERT_LEAD_SQLITE = """
    INSERT INTO crm_leads (id, whatsapp_phone, meta_lead_id, fb_click_id, email, full_name)
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
