class ContentManager:
    def __init__(self, db):
        self.db = db

    def create_content(self, data):
        self.db.insert(data)

    def read_content(self, content_id):
        return self.db.get(content_id)

    def update_content(self, content_id, data):
        self.db.update(content_id, data)

    def delete_content(self, content_id):
        self.db.delete(content_id)

    def list_all_content(self):
        return self.db.get_all()