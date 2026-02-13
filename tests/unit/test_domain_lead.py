"""
🎯 Tests para Lead Domain Entity

Tests unitarios puros para la entidad Lead.
"""

import pytest
from datetime import datetime

from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Phone, Email


class TestLead:
    """Suite de tests para la entidad Lead"""
    
    @pytest.fixture
    def valid_phone(self):
        """Teléfono válido para tests"""
        result = Phone.parse("77712345", country="BO")
        return result.unwrap()
    
    @pytest.fixture
    def valid_email(self):
        """Email válido para tests"""
        result = Email.parse("test@example.com")
        return result.unwrap()
    
    def test_create_lead_with_minimal_data(self, valid_phone):
        """Test: Crear lead solo con teléfono"""
        lead = Lead.create(phone=valid_phone)
        
        assert lead.phone == valid_phone
        assert lead.status == LeadStatus.NEW
        assert lead.score == 50  # Score default
        assert lead.name is None
        assert lead.email is None
        assert isinstance(lead.created_at, datetime)
    
    def test_create_lead_with_full_data(self, valid_phone, valid_email):
        """Test: Crear lead con todos los datos"""
        lead = Lead.create(
            phone=valid_phone,
            name="John Doe",
            email=valid_email,
            service_interest="Web Development"
        )
        
        assert lead.phone == valid_phone
        assert lead.name == "John Doe"
        assert lead.email == valid_email
        assert lead.service_interest == "Web Development"
        assert lead.status == LeadStatus.NEW
    
    def test_lead_status_transitions(self, valid_phone):
        """Test: Transiciones de estado del lead usando update_status"""
        lead = Lead.create(phone=valid_phone)
        
        # Estado inicial
        assert lead.status == LeadStatus.NEW
        
        # Transición: NEW -> INTERESTED
        lead.update_status(LeadStatus.INTERESTED)
        assert lead.status == LeadStatus.INTERESTED
        
        # Transición: INTERESTED -> NURTURING
        lead.update_status(LeadStatus.NURTURING)
        assert lead.status == LeadStatus.NURTURING
        
        # Transición: NURTURING -> BOOKED (aumenta score)
        previous_score = lead.score
        lead.update_status(LeadStatus.BOOKED)
        assert lead.status == LeadStatus.BOOKED
        assert lead.score > previous_score  # Score aumenta al hacer booked
    
    def test_update_contact_info(self, valid_phone, valid_email):
        """Test: Actualizar información de contacto"""
        lead = Lead.create(phone=valid_phone, name="Old Name")
        
        # Actualizar solo nombre
        lead.update_contact_info(name="New Name")
        assert lead.name == "New Name"
        
        # Actualizar email
        new_email = Email.parse("new@example.com").unwrap()
        lead.update_contact_info(email=new_email)
        assert lead.email == new_email
        assert lead.name == "New Name"  # Nombre preservado
    
    def test_qualify_lead(self, valid_phone):
        """Test: Calificar lead con pain_point y service_interest"""
        lead = Lead.create(phone=valid_phone)
        
        lead.qualify(
            pain_point="Necesita más clientes",
            service_interest="Marketing Digital"
        )
        
        assert lead.pain_point == "Necesita más clientes"
        assert lead.service_interest == "Marketing Digital"
    
    def test_mark_as_sent_to_meta(self, valid_phone):
        """Test: Marcar lead como enviado a Meta CAPI"""
        lead = Lead.create(phone=valid_phone)
        
        assert lead.sent_to_meta is False
        
        lead.mark_as_sent_to_meta()
        
        assert lead.sent_to_meta is True
    
    def test_is_qualified_property(self, valid_phone, valid_email):
        """Test: Propiedad is_qualified"""
        # Solo teléfono - calificado (tiene phone)
        lead_phone_only = Lead.create(phone=valid_phone)
        assert lead_phone_only.is_qualified is False  # Necesita nombre también
        
        # Con nombre y teléfono - calificado
        lead_with_name = Lead.create(phone=valid_phone, name="John")
        assert lead_with_name.is_qualified is True
        
        # Con email también
        lead_complete = Lead.create(phone=valid_phone, name="John", email=valid_email)
        assert lead_complete.is_qualified is True
    
    def test_is_hot_property(self, valid_phone):
        """Test: Propiedad is_hot para leads prioritarios"""
        # Lead nuevo con score bajo - no es hot
        lead = Lead.create(phone=valid_phone)
        assert lead.is_hot is False
        
        # Lead con score alto - es hot
        lead.score = 75
        assert lead.is_hot is True
        
        # Lead con score alto pero ghost - no es hot
        lead.update_status(LeadStatus.GHOST)
        assert lead.is_hot is False
    
    def test_to_meta_custom_data(self, valid_phone):
        """Test: Generar datos para Meta CAPI"""
        lead = Lead.create(
            phone=valid_phone,
            service_interest="SEO"
        )
        lead.utm_source = "facebook"
        
        data = lead.to_meta_custom_data()
        
        assert data["content_name"] == "SEO"
        assert data["content_category"] == "lead"
        assert data["lead_source"] == "facebook"
        assert data["currency"] == "BOB"
        assert "value" in data
    
    def test_lead_equality(self, valid_phone):
        """Test: Igualdad de leads basada en ID"""
        lead1 = Lead.create(phone=valid_phone)
        lead2 = Lead.create(phone=valid_phone)
        
        # Dos leads diferentes
        assert lead1 != lead2
        
        # Mismo lead
        assert lead1 == lead1
    
    def test_lead_repr(self, valid_phone):
        """Test: Representación string del lead"""
        lead = Lead.create(phone=valid_phone, name="John Doe")
        
        lead_repr = repr(lead)
        assert "Lead(" in lead_repr
        assert lead.id[:8] in lead_repr
        assert str(valid_phone) in lead_repr
        assert "new" in lead_repr
    
    def test_lead_hash(self, valid_phone):
        """Test: Lead puede usarse en sets y como key de dict"""
        lead = Lead.create(phone=valid_phone)
        
        # Usar como key en dict
        lead_dict = {lead: "value"}
        assert lead_dict[lead] == "value"
        
        # Usar en set
        lead_set = {lead}
        assert lead in lead_set
