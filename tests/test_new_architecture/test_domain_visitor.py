from app.domain.models.visitor import Visitor, VisitorSource


class TestVisitor:
    def test_create_new_visitor(self):
        visitor = Visitor.create(ip="1.2.3.4", user_agent="Mozilla")
        assert visitor.visit_count == 1
    
    def test_record_visit_increments_count(self):
        visitor = Visitor.create(ip="1.2.3.4", user_agent="Mozilla")
        visitor.record_visit()
        assert visitor.visit_count == 2
