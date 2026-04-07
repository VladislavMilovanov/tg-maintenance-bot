"""Mock seed data for equipment monitoring system."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260405_0003"
down_revision = "20260405_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert realistic seed data."""

    # -------------------------------------------------------------------------
    # System Actors
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO system_actors (actor_id, external_id, display_name, role, is_active, created_at, updated_at)
        VALUES
            ('actor-admin-001', 'web:admin',        'Администратор', 'admin',    true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('actor-eng-001',   'web:engineer1',    'Иванов И.И.',   'engineer', true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('actor-op-001',    'telegram:operator1','Петров П.П.',  'operator', true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('actor-user-001',  'telegram:user1',   'Сидоров С.С.', 'user',     true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Data Sources
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO data_sources (source_id, source_type, name, is_active, created_at, updated_at)
        VALUES
            ('ds-monitoring-001', 'external_monitoring', 'Vibration Monitoring System', true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('ds-manual-001',     'manual',              'Manual Inspection',           true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Locations
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO locations (location_id, name, location_type, parent_location_id, display_order, is_active, created_at, updated_at)
        VALUES
            ('loc-plant-001', 'Завод Альфа',            'plant', NULL,           1, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('loc-zone-001',  'Цех №1 - Турбинный',     'zone',  'loc-plant-001',1, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('loc-zone-002',  'Цех №2 - Компрессорный', 'zone',  'loc-plant-001',2, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Equipment
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO equipment (equipment_id, name, equipment_code, location_id, owner_actor_id, current_status,
                               maintenance_due_at, maintenance_completed_at, is_active, created_at, updated_at)
        VALUES
            ('eq-001', 'Турбина ГТ-001',          'GT-001',  'loc-zone-001', 'actor-eng-001', 'critical',
             '2026-04-10 00:00:00+03', NULL,                    true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-002', 'Турбина ГТ-002',          'GT-002',  'loc-zone-001', NULL,            'warning',
             '2026-04-15 00:00:00+03', '2026-03-01 00:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-003', 'Генератор Г-001',         'GEN-001', 'loc-zone-001', NULL,            'normal',
             '2026-05-01 00:00:00+03', '2026-03-15 00:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-004', 'Насос охлаждения НО-001', 'CP-001',  'loc-zone-001', NULL,            'normal',
             NULL,                    NULL,                    true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-005', 'Компрессор К-001',        'C-001',   'loc-zone-002', 'actor-eng-001', 'warning',
             '2026-04-08 00:00:00+03', NULL,                    true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-006', 'Компрессор К-002',        'C-002',   'loc-zone-002', NULL,            'normal',
             NULL,                    NULL,                    true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-007', 'Осушитель воздуха ОВ-001','AD-001',  'loc-zone-002', NULL,            'normal',
             NULL,                    '2026-03-20 00:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03'),
            ('eq-008', 'Ресивер Р-001',           'R-001',   'loc-zone-002', NULL,            'unknown',
             NULL,                    NULL,                    true, '2026-03-22 08:00:00+03', '2026-04-05 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Sensors  (2-3 per equipment)
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO sensors (sensor_id, equipment_id, name, sensor_type, data_source_id, is_primary_for_state,
                             last_observed_at, is_active, created_at, updated_at)
        VALUES
            -- eq-001: Турбина ГТ-001
            ('sen-001-vib-de',  'eq-001', 'Виброскорость DE',          'vibration',   'ds-monitoring-001', true,  '2026-04-05 07:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:00:00+03'),
            ('sen-001-vib-nde', 'eq-001', 'Виброскорость NDE',         'vibration',   'ds-monitoring-001', true,  '2026-04-05 07:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:00:00+03'),
            ('sen-001-temp-de', 'eq-001', 'Температура подшипника DE', 'temperature', 'ds-monitoring-001', false, '2026-04-05 07:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:00:00+03'),
            ('sen-001-temp-oil','eq-001', 'Температура масла',         'temperature', 'ds-monitoring-001', false, '2026-04-05 07:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:00:00+03'),

            -- eq-002: Турбина ГТ-002
            ('sen-002-vib-de',  'eq-002', 'Виброскорость DE',          'vibration',   'ds-monitoring-001', true,  '2026-04-05 06:30:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 06:30:00+03'),
            ('sen-002-vib-nde', 'eq-002', 'Виброскорость NDE',         'vibration',   'ds-monitoring-001', true,  '2026-04-05 06:30:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 06:30:00+03'),
            ('sen-002-temp-de', 'eq-002', 'Температура подшипника DE', 'temperature', 'ds-monitoring-001', false, '2026-04-05 06:30:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 06:30:00+03'),

            -- eq-003: Генератор Г-001
            ('sen-003-vib-de',  'eq-003', 'Виброскорость DE',          'vibration',   'ds-monitoring-001', true,  '2026-04-05 06:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 06:00:00+03'),
            ('sen-003-temp-de', 'eq-003', 'Температура подшипника DE', 'temperature', 'ds-monitoring-001', false, '2026-04-05 06:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 06:00:00+03'),

            -- eq-004: Насос охлаждения
            ('sen-004-pres',    'eq-004', 'Давление на выходе',        'pressure',    'ds-monitoring-001', true,  '2026-04-04 22:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-04 22:00:00+03'),
            ('sen-004-temp',    'eq-004', 'Температура жидкости',      'temperature', 'ds-monitoring-001', false, '2026-04-04 22:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-04 22:00:00+03'),

            -- eq-005: Компрессор К-001
            ('sen-005-pres-in', 'eq-005', 'Давление на входе',         'pressure',    'ds-monitoring-001', true,  '2026-04-05 07:15:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:15:00+03'),
            ('sen-005-pres-out','eq-005', 'Давление на выходе',        'pressure',    'ds-monitoring-001', true,  '2026-04-05 07:15:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:15:00+03'),
            ('sen-005-temp',    'eq-005', 'Температура нагнетания',    'temperature', 'ds-monitoring-001', false, '2026-04-05 07:15:00+03', true, '2026-03-22 08:00:00+03', '2026-04-05 07:15:00+03'),

            -- eq-006: Компрессор К-002
            ('sen-006-pres-in', 'eq-006', 'Давление на входе',         'pressure',    'ds-monitoring-001', true,  '2026-04-04 20:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-04 20:00:00+03'),
            ('sen-006-pres-out','eq-006', 'Давление на выходе',        'pressure',    'ds-monitoring-001', true,  '2026-04-04 20:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-04 20:00:00+03'),

            -- eq-007: Осушитель
            ('sen-007-humidity','eq-007', 'Влажность воздуха',         'humidity',    'ds-monitoring-001', true,  '2026-04-03 10:00:00+03', true, '2026-03-22 08:00:00+03', '2026-04-03 10:00:00+03'),

            -- eq-008: Ресивер
            ('sen-008-pres',    'eq-008', 'Давление в ресивере',       'pressure',    'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Sensor Groups  (~2 per equipment, 14 groups total)
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO sensor_groups (sensor_group_id, equipment_id, name, group_type, data_source_id,
                                   is_used_for_state_assessment, image_url, is_active, created_at, updated_at)
        VALUES
            -- eq-001
            ('sg-001-vib',  'eq-001', 'Вибрация подшипников',  'vibration',   'ds-monitoring-001', true,  '/images/turbine-gt001-vibration.jpg', true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('sg-001-temp', 'eq-001', 'Температура масла',     'temperature', 'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-002
            ('sg-002-vib',  'eq-002', 'Вибрация подшипников',  'vibration',   'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('sg-002-temp', 'eq-002', 'Температура подшипников','temperature','ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-003
            ('sg-003-vib',  'eq-003', 'Вибрация генератора',   'vibration',   'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('sg-003-temp', 'eq-003', 'Температура обмотки',   'temperature', 'ds-monitoring-001', false, NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-004
            ('sg-004-pres', 'eq-004', 'Давление системы охлаждения','pressure','ds-monitoring-001',true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('sg-004-temp', 'eq-004', 'Температура теплоносителя','temperature','ds-monitoring-001',false, NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-005
            ('sg-005-pres', 'eq-005', 'Давление компрессора',  'pressure',    'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),
            ('sg-005-temp', 'eq-005', 'Температура нагнетания','temperature', 'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-006
            ('sg-006-pres', 'eq-006', 'Давление компрессора',  'pressure',    'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-007
            ('sg-007-hum',  'eq-007', 'Влажность воздуха',     'humidity',    'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-008
            ('sg-008-pres', 'eq-008', 'Давление в ресивере',   'pressure',    'ds-monitoring-001', true,  NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03'),

            -- eq-001 extra: manual inspection group
            ('sg-001-insp', 'eq-001', 'Визуальная инспекция',  'inspection',  'ds-manual-001',     false, NULL, true, '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Sensor Group Members
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO sensor_group_members (sensor_group_id, sensor_id, created_at)
        VALUES
            ('sg-001-vib',  'sen-001-vib-de',  '2026-03-22 08:00:00+03'),
            ('sg-001-vib',  'sen-001-vib-nde', '2026-03-22 08:00:00+03'),
            ('sg-001-temp', 'sen-001-temp-de', '2026-03-22 08:00:00+03'),
            ('sg-001-temp', 'sen-001-temp-oil','2026-03-22 08:00:00+03'),

            ('sg-002-vib',  'sen-002-vib-de',  '2026-03-22 08:00:00+03'),
            ('sg-002-vib',  'sen-002-vib-nde', '2026-03-22 08:00:00+03'),
            ('sg-002-temp', 'sen-002-temp-de', '2026-03-22 08:00:00+03'),

            ('sg-003-vib',  'sen-003-vib-de',  '2026-03-22 08:00:00+03'),
            ('sg-003-temp', 'sen-003-temp-de', '2026-03-22 08:00:00+03'),

            ('sg-004-pres', 'sen-004-pres',    '2026-03-22 08:00:00+03'),
            ('sg-004-temp', 'sen-004-temp',    '2026-03-22 08:00:00+03'),

            ('sg-005-pres', 'sen-005-pres-in', '2026-03-22 08:00:00+03'),
            ('sg-005-pres', 'sen-005-pres-out','2026-03-22 08:00:00+03'),
            ('sg-005-temp', 'sen-005-temp',    '2026-03-22 08:00:00+03'),

            ('sg-006-pres', 'sen-006-pres-in', '2026-03-22 08:00:00+03'),
            ('sg-006-pres', 'sen-006-pres-out','2026-03-22 08:00:00+03'),

            ('sg-007-hum',  'sen-007-humidity','2026-03-22 08:00:00+03'),

            ('sg-008-pres', 'sen-008-pres',    '2026-03-22 08:00:00+03')
    """))

    # -------------------------------------------------------------------------
    # Equipment State Snapshots  (15 snapshots, 14-day coverage)
    # Normal → warning → critical progression for eq-001
    # Plus snapshots for other equipment
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO equipment_state_snapshots (snapshot_id, equipment_id, status, severity, summary,
                                               observed_at, effective_at, data_source_id, created_at)
        VALUES
            -- eq-001: escalation over 14 days
            ('snap-001-d14', 'eq-001', 'normal',   'low',      'Все параметры в норме',
             '2026-03-22 08:00:00+03', '2026-03-22 08:00:00+03', 'ds-monitoring-001', '2026-03-22 08:05:00+03'),
            ('snap-001-d13', 'eq-001', 'normal',   'low',      'Незначительное увеличение вибрации',
             '2026-03-23 08:00:00+03', '2026-03-23 08:00:00+03', 'ds-monitoring-001', '2026-03-23 08:05:00+03'),
            ('snap-001-d12', 'eq-001', 'normal',   'low',      'Параметры стабильны',
             '2026-03-24 08:00:00+03', '2026-03-24 08:00:00+03', 'ds-monitoring-001', '2026-03-24 08:05:00+03'),
            ('snap-001-d11', 'eq-001', 'warning',  'medium',   'Вибрация DE превышает допустимый уровень',
             '2026-03-25 08:00:00+03', '2026-03-25 08:00:00+03', 'ds-monitoring-001', '2026-03-25 08:05:00+03'),
            ('snap-001-d10', 'eq-001', 'warning',  'medium',   'Повышенная вибрация на подшипнике DE',
             '2026-03-26 08:00:00+03', '2026-03-26 08:00:00+03', 'ds-monitoring-001', '2026-03-26 08:05:00+03'),
            ('snap-001-d09', 'eq-001', 'warning',  'medium',   'Вибрация стабильно повышена, температура в норме',
             '2026-03-27 08:00:00+03', '2026-03-27 08:00:00+03', 'ds-monitoring-001', '2026-03-27 08:05:00+03'),
            ('snap-001-d08', 'eq-001', 'warning',  'medium',   'Признаки нарастающей неисправности подшипника',
             '2026-03-28 08:00:00+03', '2026-03-28 08:00:00+03', 'ds-monitoring-001', '2026-03-28 08:05:00+03'),
            ('snap-001-d07', 'eq-001', 'critical', 'high',     'Повышенная вибрация на опорном подшипнике, требуется вмешательство',
             '2026-03-29 08:00:00+03', '2026-03-29 08:00:00+03', 'ds-monitoring-001', '2026-03-29 08:05:00+03'),
            ('snap-001-d06', 'eq-001', 'critical', 'high',     'Критическая вибрация DE, рост температуры масла',
             '2026-03-30 08:00:00+03', '2026-03-30 08:00:00+03', 'ds-monitoring-001', '2026-03-30 08:05:00+03'),
            ('snap-001-d05', 'eq-001', 'critical', 'high',     'Превышение порога вибрации, аварийный режим работы',
             '2026-03-31 08:00:00+03', '2026-03-31 08:00:00+03', 'ds-monitoring-001', '2026-03-31 08:05:00+03'),
            ('snap-001-d04', 'eq-001', 'critical', 'high',     'Критические показания вибрации подшипника',
             '2026-04-01 08:00:00+03', '2026-04-01 08:00:00+03', 'ds-monitoring-001', '2026-04-01 08:05:00+03'),
            ('snap-001-d03', 'eq-001', 'critical', 'high',     'Аварийный уровень вибрации, запланирован аварийный ремонт',
             '2026-04-02 08:00:00+03', '2026-04-02 08:00:00+03', 'ds-monitoring-001', '2026-04-02 08:05:00+03'),
            ('snap-001-d02', 'eq-001', 'critical', 'high',     'Требуется немедленная остановка и ремонт подшипника',
             '2026-04-04 08:00:00+03', '2026-04-04 08:00:00+03', 'ds-monitoring-001', '2026-04-04 08:05:00+03'),
            ('snap-001-d01', 'eq-001', 'critical', 'high',     'Критическое состояние подшипника DE',
             '2026-04-05 08:00:00+03', '2026-04-05 08:00:00+03', 'ds-monitoring-001', '2026-04-05 08:05:00+03'),

            -- eq-002: warning snapshot
            ('snap-002-d03', 'eq-002', 'warning',  'medium',   'Повышенная вибрация NDE, мониторинг усилен',
             '2026-04-02 09:00:00+03', '2026-04-02 09:00:00+03', 'ds-monitoring-001', '2026-04-02 09:05:00+03'),
            ('snap-002-d01', 'eq-002', 'warning',  'medium',   'Вибрация NDE выше нормы, температура в порядке',
             '2026-04-05 09:00:00+03', '2026-04-05 09:00:00+03', 'ds-monitoring-001', '2026-04-05 09:05:00+03'),

            -- eq-003: normal
            ('snap-003-d01', 'eq-003', 'normal',   'low',      'Все параметры генератора в норме',
             '2026-04-05 09:30:00+03', '2026-04-05 09:30:00+03', 'ds-monitoring-001', '2026-04-05 09:35:00+03'),

            -- eq-004: normal
            ('snap-004-d01', 'eq-004', 'normal',   'low',      'Давление и температура в норме',
             '2026-04-04 22:00:00+03', '2026-04-04 22:00:00+03', 'ds-monitoring-001', '2026-04-04 22:05:00+03'),

            -- eq-005: warning
            ('snap-005-d02', 'eq-005', 'normal',   'low',      'Параметры компрессора в норме',
             '2026-04-03 10:00:00+03', '2026-04-03 10:00:00+03', 'ds-monitoring-001', '2026-04-03 10:05:00+03'),
            ('snap-005-d01', 'eq-005', 'warning',  'medium',   'Давление на выходе ниже нормы, требует внимания',
             '2026-04-05 10:00:00+03', '2026-04-05 10:00:00+03', 'ds-monitoring-001', '2026-04-05 10:05:00+03'),

            -- eq-006: normal
            ('snap-006-d01', 'eq-006', 'normal',   'low',      'Компрессор работает штатно',
             '2026-04-04 20:00:00+03', '2026-04-04 20:00:00+03', 'ds-monitoring-001', '2026-04-04 20:05:00+03'),

            -- eq-007: normal
            ('snap-007-d01', 'eq-007', 'normal',   'low',      'Влажность в норме после ТО',
             '2026-04-03 10:00:00+03', '2026-04-03 10:00:00+03', 'ds-monitoring-001', '2026-04-03 10:05:00+03')
    """))

    # -------------------------------------------------------------------------
    # Equipment State Snapshot Sensor Groups
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO equipment_state_snapshot_sensor_groups (snapshot_id, sensor_group_id, created_at)
        VALUES
            -- snap-001 series → sg-001-vib (primary culprit)
            ('snap-001-d14', 'sg-001-vib',  '2026-03-22 08:05:00+03'),
            ('snap-001-d13', 'sg-001-vib',  '2026-03-23 08:05:00+03'),
            ('snap-001-d12', 'sg-001-vib',  '2026-03-24 08:05:00+03'),
            ('snap-001-d11', 'sg-001-vib',  '2026-03-25 08:05:00+03'),
            ('snap-001-d10', 'sg-001-vib',  '2026-03-26 08:05:00+03'),
            ('snap-001-d09', 'sg-001-vib',  '2026-03-27 08:05:00+03'),
            ('snap-001-d08', 'sg-001-vib',  '2026-03-28 08:05:00+03'),
            ('snap-001-d07', 'sg-001-vib',  '2026-03-29 08:05:00+03'),
            ('snap-001-d07', 'sg-001-temp', '2026-03-29 08:05:00+03'),
            ('snap-001-d06', 'sg-001-vib',  '2026-03-30 08:05:00+03'),
            ('snap-001-d06', 'sg-001-temp', '2026-03-30 08:05:00+03'),
            ('snap-001-d05', 'sg-001-vib',  '2026-03-31 08:05:00+03'),
            ('snap-001-d05', 'sg-001-temp', '2026-03-31 08:05:00+03'),
            ('snap-001-d04', 'sg-001-vib',  '2026-04-01 08:05:00+03'),
            ('snap-001-d03', 'sg-001-vib',  '2026-04-02 08:05:00+03'),
            ('snap-001-d02', 'sg-001-vib',  '2026-04-04 08:05:00+03'),
            ('snap-001-d01', 'sg-001-vib',  '2026-04-05 08:05:00+03'),

            -- snap-002 series
            ('snap-002-d03', 'sg-002-vib',  '2026-04-02 09:05:00+03'),
            ('snap-002-d01', 'sg-002-vib',  '2026-04-05 09:05:00+03'),

            -- snap-003
            ('snap-003-d01', 'sg-003-vib',  '2026-04-05 09:35:00+03'),

            -- snap-004
            ('snap-004-d01', 'sg-004-pres', '2026-04-04 22:05:00+03'),

            -- snap-005
            ('snap-005-d02', 'sg-005-pres', '2026-04-03 10:05:00+03'),
            ('snap-005-d01', 'sg-005-pres', '2026-04-05 10:05:00+03'),

            -- snap-006
            ('snap-006-d01', 'sg-006-pres', '2026-04-04 20:05:00+03'),

            -- snap-007
            ('snap-007-d01', 'sg-007-hum',  '2026-04-03 10:05:00+03')
    """))

    # -------------------------------------------------------------------------
    # Equipment State Records  (manual entries from different actors/channels)
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO equipment_state_records (record_id, equipment_id, author_actor_id, channel, status, comment,
                                             observed_at, created_at, source_type, review_status,
                                             reviewed_by_actor_id, reviewed_at, review_comment)
        VALUES
            ('rec-001', 'eq-001', 'actor-op-001',   'telegram', 'warning',  'Замечена повышенная вибрация при обходе цеха',
             '2026-03-25 09:00:00+03', '2026-03-25 09:05:00+03', 'manual', 'reviewed',
             'actor-eng-001', '2026-03-25 10:00:00+03', 'Принято к сведению, усилен мониторинг'),

            ('rec-002', 'eq-001', 'actor-eng-001',  'web',      'critical', 'Проведена визуальная диагностика: признаки разрушения подшипника DE',
             '2026-03-29 11:00:00+03', '2026-03-29 11:10:00+03', 'manual', 'reviewed',
             'actor-admin-001', '2026-03-29 12:00:00+03', 'Запланирован ремонт подшипника'),

            ('rec-003', 'eq-001', 'actor-op-001',   'telegram', 'critical', 'Шум и вибрация значительно усилились',
             '2026-04-01 14:00:00+03', '2026-04-01 14:05:00+03', 'manual', 'resolved',
             'actor-eng-001', '2026-04-01 15:00:00+03', 'Заявка на аварийный ремонт подана'),

            ('rec-004', 'eq-001', 'actor-eng-001',  'web',      'critical', 'Запланирован ремонт подшипника на 2026-04-10',
             '2026-04-02 09:00:00+03', '2026-04-02 09:05:00+03', 'manual', 'reviewed',
             'actor-admin-001', '2026-04-02 10:00:00+03', 'Ремонт утверждён'),

            ('rec-005', 'eq-002', 'actor-op-001',   'telegram', 'warning',  'Незначительная вибрация на NDE подшипнике',
             '2026-04-02 10:00:00+03', '2026-04-02 10:05:00+03', 'manual', 'reviewed',
             'actor-eng-001', '2026-04-02 11:00:00+03', 'Занесено в журнал наблюдений'),

            ('rec-006', 'eq-005', 'actor-op-001',   'telegram', 'warning',  'Давление на выходе компрессора ниже нормы на 5%',
             '2026-04-05 08:00:00+03', '2026-04-05 08:05:00+03', 'manual', 'pending',
             NULL, NULL, NULL),

            ('rec-007', 'eq-003', 'actor-user-001', 'telegram', 'normal',   'Генератор работает штатно, замечаний нет',
             '2026-04-04 14:00:00+03', '2026-04-04 14:05:00+03', 'manual', 'reviewed',
             'actor-eng-001', '2026-04-04 15:00:00+03', 'Принято к сведению'),

            ('rec-008', 'eq-007', 'actor-eng-001',  'web',      'normal',   'Проведено плановое ТО осушителя, параметры восстановлены',
             '2026-03-20 16:00:00+03', '2026-03-20 16:05:00+03', 'manual', 'resolved',
             'actor-admin-001', '2026-03-20 17:00:00+03', 'ТО выполнено в срок'),

            ('rec-009', 'eq-002', 'actor-eng-001',  'web',      'warning',  'Выполнена диагностика вибрации, замена подшипника не требуется',
             '2026-04-05 11:00:00+03', '2026-04-05 11:05:00+03', 'manual', 'pending',
             NULL, NULL, NULL),

            ('rec-010', 'eq-001', 'actor-user-001', 'telegram', 'critical', 'Слышен нехарактерный гул со стороны турбины ГТ-001',
             '2026-04-05 07:30:00+03', '2026-04-05 07:35:00+03', 'manual', 'pending',
             NULL, NULL, NULL)
    """))

    # -------------------------------------------------------------------------
    # Equipment State Record Sensor Groups
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
        INSERT INTO equipment_state_record_sensor_groups (record_id, sensor_group_id, created_at)
        VALUES
            ('rec-001', 'sg-001-vib',  '2026-03-25 09:05:00+03'),
            ('rec-002', 'sg-001-vib',  '2026-03-29 11:10:00+03'),
            ('rec-002', 'sg-001-temp', '2026-03-29 11:10:00+03'),
            ('rec-003', 'sg-001-vib',  '2026-04-01 14:05:00+03'),
            ('rec-004', 'sg-001-vib',  '2026-04-02 09:05:00+03'),
            ('rec-005', 'sg-002-vib',  '2026-04-02 10:05:00+03'),
            ('rec-006', 'sg-005-pres', '2026-04-05 08:05:00+03'),
            ('rec-009', 'sg-002-vib',  '2026-04-05 11:05:00+03'),
            ('rec-010', 'sg-001-vib',  '2026-04-05 07:35:00+03')
    """))


def downgrade() -> None:
    """Remove all seed data inserted by this migration."""

    # Join tables first
    op.execute(sa.text("""
        DELETE FROM equipment_state_record_sensor_groups
        WHERE record_id IN (
            'rec-001','rec-002','rec-003','rec-004','rec-005',
            'rec-006','rec-007','rec-008','rec-009','rec-010'
        )
    """))

    op.execute(sa.text("""
        DELETE FROM equipment_state_snapshot_sensor_groups
        WHERE snapshot_id IN (
            'snap-001-d14','snap-001-d13','snap-001-d12','snap-001-d11',
            'snap-001-d10','snap-001-d09','snap-001-d08','snap-001-d07',
            'snap-001-d06','snap-001-d05','snap-001-d04','snap-001-d03',
            'snap-001-d02','snap-001-d01',
            'snap-002-d03','snap-002-d01',
            'snap-003-d01','snap-004-d01',
            'snap-005-d02','snap-005-d01',
            'snap-006-d01','snap-007-d01'
        )
    """))

    op.execute(sa.text("""
        DELETE FROM sensor_group_members
        WHERE sensor_group_id IN (
            'sg-001-vib','sg-001-temp','sg-001-insp',
            'sg-002-vib','sg-002-temp',
            'sg-003-vib','sg-003-temp',
            'sg-004-pres','sg-004-temp',
            'sg-005-pres','sg-005-temp',
            'sg-006-pres',
            'sg-007-hum',
            'sg-008-pres'
        )
    """))

    # Records and snapshots
    op.execute(sa.text("""
        DELETE FROM equipment_state_records
        WHERE record_id IN (
            'rec-001','rec-002','rec-003','rec-004','rec-005',
            'rec-006','rec-007','rec-008','rec-009','rec-010'
        )
    """))

    op.execute(sa.text("""
        DELETE FROM equipment_state_snapshots
        WHERE snapshot_id IN (
            'snap-001-d14','snap-001-d13','snap-001-d12','snap-001-d11',
            'snap-001-d10','snap-001-d09','snap-001-d08','snap-001-d07',
            'snap-001-d06','snap-001-d05','snap-001-d04','snap-001-d03',
            'snap-001-d02','snap-001-d01',
            'snap-002-d03','snap-002-d01',
            'snap-003-d01','snap-004-d01',
            'snap-005-d02','snap-005-d01',
            'snap-006-d01','snap-007-d01'
        )
    """))

    # Sensor groups and sensors
    op.execute(sa.text("""
        DELETE FROM sensor_groups
        WHERE sensor_group_id IN (
            'sg-001-vib','sg-001-temp','sg-001-insp',
            'sg-002-vib','sg-002-temp',
            'sg-003-vib','sg-003-temp',
            'sg-004-pres','sg-004-temp',
            'sg-005-pres','sg-005-temp',
            'sg-006-pres',
            'sg-007-hum',
            'sg-008-pres'
        )
    """))

    op.execute(sa.text("""
        DELETE FROM sensors
        WHERE sensor_id IN (
            'sen-001-vib-de','sen-001-vib-nde','sen-001-temp-de','sen-001-temp-oil',
            'sen-002-vib-de','sen-002-vib-nde','sen-002-temp-de',
            'sen-003-vib-de','sen-003-temp-de',
            'sen-004-pres','sen-004-temp',
            'sen-005-pres-in','sen-005-pres-out','sen-005-temp',
            'sen-006-pres-in','sen-006-pres-out',
            'sen-007-humidity',
            'sen-008-pres'
        )
    """))

    # Equipment
    op.execute(sa.text("""
        DELETE FROM equipment
        WHERE equipment_id IN (
            'eq-001','eq-002','eq-003','eq-004',
            'eq-005','eq-006','eq-007','eq-008'
        )
    """))

    # Locations
    op.execute(sa.text("""
        DELETE FROM locations WHERE location_id IN ('loc-zone-001','loc-zone-002')
    """))
    op.execute(sa.text("""
        DELETE FROM locations WHERE location_id = 'loc-plant-001'
    """))

    # Data sources and actors
    op.execute(sa.text("""
        DELETE FROM data_sources WHERE source_id IN ('ds-monitoring-001','ds-manual-001')
    """))

    op.execute(sa.text("""
        DELETE FROM system_actors
        WHERE actor_id IN ('actor-admin-001','actor-eng-001','actor-op-001','actor-user-001')
    """))
