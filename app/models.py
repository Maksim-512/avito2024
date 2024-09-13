from .extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM

# ENUM для статусов тендера
tender_status_enum = ENUM('Created', 'Published', 'Closed', name='tender_status', create_type=True)
tender_service_type_enum = ENUM('Delivery', 'Construction', 'Manufacture', name='tender_service_type', create_type=True)

# ENUM для статусов предложения
bid_status_enum = ENUM('Created', 'Published', 'Canceled', name='bid_status', create_type=True)
bid_decision_enum = ENUM('Approved', 'Rejected', name='bid_decision', create_type=True)
bid_author_type_enum = ENUM('User', 'Organization', name='bid_author_type', create_type=True)


class Employee(db.Model):
    __tablename__ = 'employee'
    __table_args__ = {'extend_existing': True}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(51), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    emp_responsibles = db.relationship('OrganizationResponsible', back_populates='user')


class Organization(db.Model):
    __tablename__ = 'organization'
    __table_args__ = {'extend_existing': True}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(ENUM('IE', 'LLC', 'JSC', name='organization_type', create_type=False))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    org_responsibles = db.relationship('OrganizationResponsible', back_populates='organization')


class OrganizationResponsible(db.Model):
    __tablename__ = 'organization_responsible'
    __table_args__ = {'extend_existing': True}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organization.id', ondelete='CASCADE'))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('employee.id', ondelete='CASCADE'))

    organization = db.relationship('Organization', back_populates='org_responsibles')
    user = db.relationship('Employee', back_populates='emp_responsibles')


# Модель тендера
class Tender(db.Model):
    __tablename__ = 'tender'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    service_type = db.Column(tender_service_type_enum, nullable=False)
    status = db.Column(tender_status_enum, nullable=False)
    organization_id = db.Column(UUID(as_uuid=True), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


# Модель предложения (Bid)
class Bid(db.Model):
    __tablename__ = 'bid'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(bid_decision_enum, nullable=False)
    status = db.Column(bid_status_enum, nullable=False)
    tender_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tender.id'), nullable=False)
    author_type = db.Column(bid_author_type_enum, nullable=False)
    author_id = db.Column(UUID(as_uuid=True), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Модель отзыва на предложение (BidReview)


class BidReview(db.Model):
    __tablename__ = 'bid_review'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Уникальный идентификатор отзыва
    description = db.Column(db.String(1000), nullable=False)
