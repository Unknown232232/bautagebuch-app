"""
Tests für Models
"""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.material import Material
from app.models.aufmass import AufmassEntry, AufmassDocument


@pytest.fixture
def app():
    """Create test app."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create sample user."""
    user = User(
        username='testuser',
        email='test@example.com',
        role='mitarbeiter'
    )
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_material(app):
    """Create sample material."""
    material = Material(
        name='Test Material',
        einheit='m²',
        kategorie='Test'
    )
    db.session.add(material)
    db.session.commit()
    return material


class TestUser:
    """Test User model."""
    
    def test_user_creation(self, app):
        """Test user creation."""
        user = User(
            username='newuser',
            email='new@example.com',
            role='admin'
        )
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.role == 'admin'
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')
    
    def test_password_hashing(self, app):
        """Test password hashing."""
        user = User(username='test', email='test@test.com')
        user.set_password('secret')
        
        assert user.password_hash != 'secret'
        assert user.check_password('secret')
        assert not user.check_password('wrong')
    
    def test_role_hierarchy(self, app):
        """Test role hierarchy."""
        admin = User(username='admin', email='admin@test.com', role='admin')
        bauleiter = User(username='bauleiter', email='bl@test.com', role='bauleiter')
        mitarbeiter = User(username='ma', email='ma@test.com', role='mitarbeiter')
        
        # Admin has all permissions
        assert admin.is_admin()
        assert admin.is_bauleiter()
        assert admin.is_mitarbeiter()
        assert admin.has_role('admin')
        assert admin.has_role('bauleiter')
        assert admin.has_role('mitarbeiter')
        
        # Bauleiter has bauleiter and mitarbeiter permissions
        assert not bauleiter.is_admin()
        assert bauleiter.is_bauleiter()
        assert bauleiter.is_mitarbeiter()
        assert not bauleiter.has_role('admin')
        assert bauleiter.has_role('bauleiter')
        assert bauleiter.has_role('mitarbeiter')
        
        # Mitarbeiter has only mitarbeiter permissions
        assert not mitarbeiter.is_admin()
        assert not mitarbeiter.is_bauleiter()
        assert mitarbeiter.is_mitarbeiter()
        assert not mitarbeiter.has_role('admin')
        assert not mitarbeiter.has_role('bauleiter')
        assert mitarbeiter.has_role('mitarbeiter')
    
    def test_user_serialization(self, sample_user):
        """Test user serialization."""
        data = sample_user.to_dict()
        
        assert data['id'] == sample_user.id
        assert data['username'] == sample_user.username
        assert data['email'] == sample_user.email
        assert data['role'] == sample_user.role
        assert 'password_hash' not in data
    
    def test_full_name(self, app):
        """Test full name generation."""
        user = User(
            username='test',
            email='test@test.com',
            vorname='Max',
            nachname='Mustermann'
        )
        
        assert user.get_full_name() == 'Max Mustermann'
        
        user.nachname = None
        assert user.get_full_name() == 'Max'
        
        user.vorname = None
        assert user.get_full_name() == 'test'


class TestMaterial:
    """Test Material model."""
    
    def test_material_creation(self, app):
        """Test material creation."""
        material = Material(
            name='Beton',
            einheit='m³',
            kategorie='Rohbau',
            beschreibung='Standard Beton C25/30'
        )
        
        db.session.add(material)
        db.session.commit()
        
        assert material.id is not None
        assert material.name == 'Beton'
        assert material.einheit == 'm³'
        assert material.kategorie == 'Rohbau'
        assert material.ist_aktiv is True
    
    def test_material_deactivation(self, sample_material):
        """Test material deactivation."""
        assert sample_material.ist_aktiv is True
        
        sample_material.deactivate()
        assert sample_material.ist_aktiv is False
        
        sample_material.activate()
        assert sample_material.ist_aktiv is True
    
    def test_material_serialization(self, sample_material):
        """Test material serialization."""
        data = sample_material.to_dict()
        
        assert data['id'] == sample_material.id
        assert data['name'] == sample_material.name
        assert data['einheit'] == sample_material.einheit
        assert data['kategorie'] == sample_material.kategorie


class TestAufmassEntry:
    """Test AufmassEntry model."""
    
    def test_aufmass_creation(self, app, sample_user, sample_material):
        """Test aufmass entry creation."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Erdgeschoss',
            raumnummer='R001',
            menge=25.5,
            einheit='m²',
            bemerkungen='Test Eintrag'
        )
        
        db.session.add(entry)
        db.session.commit()
        
        assert entry.id is not None
        assert entry.material_id == sample_material.id
        assert entry.mitarbeiter_id == sample_user.id
        assert entry.ort == 'Erdgeschoss'
        assert entry.menge == 25.5
        assert entry.is_approved is True
        assert entry.is_deleted is False
    
    def test_aufmass_validation(self, app, sample_user, sample_material):
        """Test aufmass validation."""
        # Valid entry
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test Ort',
            menge=10.0
        )
        errors = entry.validate()
        assert len(errors) == 0
        
        # Invalid entry - missing material
        entry.material_id = None
        errors = entry.validate()
        assert 'Material ist erforderlich' in errors
        
        # Invalid entry - empty location
        entry.material_id = sample_material.id
        entry.ort = ''
        errors = entry.validate()
        assert 'Ort muss mindestens 2 Zeichen lang sein' in errors
        
        # Invalid entry - negative quantity
        entry.ort = 'Test'
        entry.menge = -5.0
        errors = entry.validate()
        assert 'Menge muss größer als 0 sein' in errors
    
    def test_soft_delete(self, app, sample_user, sample_material):
        """Test soft delete functionality."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        assert entry.is_deleted is False
        assert entry.deleted_at is None
        
        entry.soft_delete(sample_user.id)
        
        assert entry.is_deleted is True
        assert entry.deleted_at is not None
        assert entry.deleted_by == sample_user.id
        
        # Test restore
        entry.restore()
        assert entry.is_deleted is False
        assert entry.deleted_at is None
        assert entry.deleted_by is None
    
    def test_active_query(self, app, sample_user, sample_material):
        """Test active query method."""
        # Create two entries
        entry1 = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test1',
            menge=10.0
        )
        entry2 = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test2',
            menge=20.0
        )
        
        db.session.add_all([entry1, entry2])
        db.session.commit()
        
        # Both should be active
        active_entries = AufmassEntry.active().all()
        assert len(active_entries) == 2
        
        # Delete one
        entry1.soft_delete()
        
        # Only one should be active
        active_entries = AufmassEntry.active().all()
        assert len(active_entries) == 1
        assert active_entries[0].id == entry2.id
    
    def test_bautagebuch_text_generation(self, app, sample_user, sample_material):
        """Test bautagebuch text generation."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Erdgeschoss',
            raumnummer='R001',
            menge=25.5,
            einheit='m²',
            bemerkungen='Wichtiger Hinweis',
            datum=datetime(2024, 1, 15)
        )
        
        # Beziehungen manuell setzen für den Test
        entry.mitarbeiter = sample_user
        entry.material = sample_material
        
        text = entry.to_bautagebuch_text()
        
        assert '15.01.2024' in text
        assert sample_user.username in text
        assert 'Erdgeschoss' in text
        assert 'R001' in text
        assert sample_material.name in text
        assert '25.5' in text
        assert 'Wichtiger Hinweis' in text
    
    def test_serialization(self, app, sample_user, sample_material):
        """Test entry serialization."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        data = entry.to_dict()
        
        assert data['id'] == entry.id
        assert data['material'] == sample_material.name
        assert data['mitarbeiter'] == sample_user.username
        assert data['ort'] == 'Test'
        assert data['menge'] == 10.0


class TestAufmassDocument:
    """Test AufmassDocument model."""
    
    def test_document_creation(self, app, sample_user, sample_material):
        """Test document creation."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        document = AufmassDocument(
            aufmass_entry_id=entry.id,
            filename='test_123.jpg',
            original_filename='test.jpg',
            file_type='image/jpeg',
            file_size=1024,
            uploaded_by=sample_user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        assert document.id is not None
        assert document.aufmass_entry_id == entry.id
        assert document.original_filename == 'test.jpg'
        assert document.file_size == 1024
        assert document.is_deleted is False
    
    def test_document_soft_delete(self, app, sample_user, sample_material):
        """Test document soft delete."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        document = AufmassDocument(
            aufmass_entry_id=entry.id,
            filename='test.jpg',
            original_filename='test.jpg',
            file_type='image/jpeg',
            file_size=1024
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.is_deleted is False
        
        document.soft_delete(sample_user.id)
        
        assert document.is_deleted is True
        assert document.deleted_by == sample_user.id
    
    def test_document_serialization(self, app, sample_user, sample_material):
        """Test document serialization."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        document = AufmassDocument(
            aufmass_entry_id=entry.id,
            filename='test.jpg',
            original_filename='test.jpg',
            file_type='image/jpeg',
            file_size=1024,
            uploaded_by=sample_user.id
        )
        db.session.add(document)
        db.session.commit()
        
        data = document.to_dict()
        
        assert data['id'] == document.id
        assert data['original_filename'] == 'test.jpg'
        assert data['file_type'] == 'image/jpeg'
        assert data['file_size'] == 1024
        assert data['uploaded_by'] == sample_user.username


class TestRelationships:
    """Test model relationships."""
    
    def test_user_aufmass_relationship(self, app, sample_user, sample_material):
        """Test user-aufmass relationship."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        # Test forward relationship
        assert entry.mitarbeiter == sample_user
        
        # Test backward relationship
        assert len(sample_user.aufmass_entries) == 1
        assert sample_user.aufmass_entries[0] == entry
    
    def test_material_aufmass_relationship(self, app, sample_user, sample_material):
        """Test material-aufmass relationship."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        # Test forward relationship
        assert entry.material == sample_material
        
        # Test backward relationship
        assert sample_material.aufmass_entries.count() == 1
        assert sample_material.aufmass_entries.first() == entry
    
    def test_aufmass_document_relationship(self, app, sample_user, sample_material):
        """Test aufmass-document relationship."""
        entry = AufmassEntry(
            material_id=sample_material.id,
            mitarbeiter_id=sample_user.id,
            ort='Test',
            menge=10.0
        )
        db.session.add(entry)
        db.session.commit()
        
        document = AufmassDocument(
            aufmass_entry_id=entry.id,
            filename='test.jpg',
            original_filename='test.jpg',
            file_type='image/jpeg',
            file_size=1024
        )
        db.session.add(document)
        db.session.commit()
        
        # Test forward relationship
        assert document.aufmass_entry == entry
        
        # Test backward relationship
        assert len(entry.documents) == 1
        assert entry.documents[0] == document
