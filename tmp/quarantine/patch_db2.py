with open("app/infrastructure/persistence/database.py", "r") as f:
    text = f.read()

target = '            """,\n        ]\n\n        if self._backend == "sqlite":'
replacement = '''            """,
            """
            CREATE TABLE IF NOT EXISTS outbox_events (
                id TEXT PRIMARY KEY,
                aggregate_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload JSONB NOT NULL,
                status TEXT DEFAULT 'pending',
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
            """,
        ]

        if self._backend == "sqlite":'''

if target in text:
    text = text.replace(target, replacement)
    with open("app/infrastructure/persistence/database.py", "w") as f:
        f.write(text)
    print("PATCH_SUCCESS")
else:
    print("TARGET_NOT_FOUND")
