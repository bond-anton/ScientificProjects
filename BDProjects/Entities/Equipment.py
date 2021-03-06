from __future__ import division, print_function

from sqlalchemy import Table, Column, UniqueConstraint, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from BDProjects import Base, default_date_time_format
from BDProjects.Entities import Session
from BDProjects.Entities import Parameter
from BDProjects.Entities import MeasurementType


equipment_assembly_table = Table('assembly_parts', Base.metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('assembly_id', Integer, ForeignKey('equipment_assembly.id')),
                                 Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                 UniqueConstraint('assembly_id', 'equipment_id', name='assembly_equipment'))

equipment_parameters_table = Table('equipment_parameters', Base.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                   Column('parameter_id', Integer, ForeignKey('parameter.id')),
                                   UniqueConstraint('equipment_id', 'parameter_id', name='equipment_parameter'))

equipment_measurement_table = Table('equipment_measurement', Base.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                    Column('measurement_type_id', Integer, ForeignKey('measurement_type.id')),
                                    UniqueConstraint('equipment_id', 'measurement_type_id',
                                                     name='equipment_measurement_type'))


class Manufacturer(Base):

    __tablename__ = 'manufacturer'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    name_short = Column(String, unique=True)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('manufacturers', uselist=True, cascade='all, delete-orphan'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        description = 'Manufacturer: %s (%s)' % (self.name, self.name_short)
        if self.description is not None:
            description += '\n %s' % self.description
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.session.user.login
        return description


class EquipmentCategory(Base):

    __tablename__ = 'equipment_category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('equipment_category.id'))
    subcategories = relationship('EquipmentCategory', backref=backref('parent', remote_side=[id],
                                                                      cascade='all, delete'))
    name = Column(String)
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('equipment_categories', uselist=True,
                                                    cascade='all, delete-orphan'))
    created = Column(DateTime, default=func.now())
    __table_args__ = (UniqueConstraint('name', 'parent_id', name='name_parent'),)

    def __str__(self):
        description = 'Equipment category: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.session.user.login
        if self.parent is not None:
            description += '\n Parent: %s' % self.parent.name
        else:
            description += '\n Parent: %s' % self.parent
        description += '\n Subcategories number: %i' % len(self.subcategories)
        return description


class Equipment(Base):

    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    serial_number = Column(String)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    manufacturer = relationship('Manufacturer', backref=backref('equipment', uselist=True,
                                                                cascade='all, delete-orphan'))
    category_id = Column(Integer, ForeignKey('equipment_category.id'))
    category = relationship(EquipmentCategory, backref=backref('equipment', uselist=True,
                                                               cascade='all, delete-orphan'))
    assembly_id = Column(Integer, ForeignKey('equipment_assembly.id'))
    assembly = relationship('EquipmentAssembly', backref=backref('equipment', uselist=True,
                                                                 cascade='all, delete-orphan'))
    description = Column(Text)
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('equipment', uselist=True, cascade='all, delete-orphan'))
    parameters = relationship(Parameter, secondary=equipment_parameters_table, backref='equipment')
    measurement_types = relationship(MeasurementType, secondary=equipment_measurement_table, backref='equipment')
    created = Column(DateTime, default=func.now())
    __table_args__ = (UniqueConstraint('name', 'serial_number', name='_name_serial_number'),)

    def __str__(self):
        description = 'Equipment: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        if self.manufacturer is not None:
            description += '\n Manufacturer: %s' % self.manufacturer.name
        if self.category is not None:
            description += '\n Category: %s' % self.category.name
        else:
            description += '\n Category: %s' % self.category
        if self.assembly is not None:
            description += '\n Assembly: %s' % self.assembly.name
        else:
            description += '\n Assembly: %s' % self.assembly
        description += '\n Parameters number: %i' % len(self.parameters)
        description += '\n Measurement types number: %i' % len(self.measurement_types)
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.session.user.login
        return description


class EquipmentAssembly(Base):

    __tablename__ = 'equipment_assembly'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    parts = relationship(Equipment, secondary=equipment_assembly_table, backref='assemblies',
                         cascade='all, delete')
    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship(Session, backref=backref('assemblies', uselist=True, cascade='all, delete-orphan'))
    created = Column(DateTime, default=func.now())

    def __str__(self):
        description = 'Equipment assembly: %s' % self.name
        if self.description is not None:
            description += '\n %s' % self.description
        description += '\n Parts number: %i' % len(self.parts)
        created = self.created.strftime(default_date_time_format)
        description += '\n Created: %s' % created
        description += '\n Created by: @%s' % self.session.user.login
        return description
