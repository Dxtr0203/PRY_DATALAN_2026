-- DATALAN - Esquema PostgreSQL normalizado
-- Ejecutar sobre una base PostgreSQL nueva.
-- La aplicacion debe escribir fechas como timestamptz y conservar el historial.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS datalan;
SET search_path TO datalan, public;

CREATE TABLE app_user (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    full_name VARCHAR(160) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    identity_number VARCHAR(80) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE role (
    role_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_key VARCHAR(50) NOT NULL UNIQUE,
    label VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE user_role (
    user_id BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES role(role_id) ON DELETE RESTRICT,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE module (
    module_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    module_key VARCHAR(80) NOT NULL UNIQUE,
    label VARCHAR(120) NOT NULL,
    route_name VARCHAR(120) NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE role_module (
    role_id BIGINT NOT NULL REFERENCES role(role_id) ON DELETE CASCADE,
    module_id BIGINT NOT NULL REFERENCES module(module_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, module_id)
);

CREATE TABLE role_access_settings (
    role_id BIGINT PRIMARY KEY REFERENCES role(role_id) ON DELETE CASCADE,
    modules JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE client (
    client_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    legal_name VARCHAR(180) NOT NULL,
    tax_id VARCHAR(40),
    client_type VARCHAR(30) NOT NULL DEFAULT 'CLIENTE',
    email VARCHAR(254),
    phone VARCHAR(40),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT client_type_ck CHECK (client_type IN ('CLIENTE', 'ENTIDAD')),
    CONSTRAINT client_tax_id_uq UNIQUE (tax_id)
);

CREATE TABLE address (
    address_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    line_1 VARCHAR(220) NOT NULL,
    line_2 VARCHAR(220),
    city VARCHAR(100),
    region VARCHAR(100),
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    CONSTRAINT address_latitude_ck CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT address_longitude_ck CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

CREATE TABLE service_type (
    service_type_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_key VARCHAR(40) NOT NULL UNIQUE,
    label VARCHAR(120) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE priority (
    priority_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    priority_key VARCHAR(20) NOT NULL UNIQUE,
    label VARCHAR(40) NOT NULL UNIQUE,
    weight NUMERIC(8,2) NOT NULL DEFAULT 1,
    CONSTRAINT priority_weight_ck CHECK (weight > 0)
);

CREATE TABLE request_status (
    status_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status_key VARCHAR(60) NOT NULL UNIQUE,
    label VARCHAR(100) NOT NULL,
    area_key VARCHAR(40) NOT NULL,
    is_terminal BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE operational_request (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cite VARCHAR(40) NOT NULL UNIQUE,
    client_id BIGINT NOT NULL REFERENCES client(client_id) ON DELETE RESTRICT,
    service_type_id BIGINT NOT NULL REFERENCES service_type(service_type_id) ON DELETE RESTRICT,
    priority_id SMALLINT NOT NULL REFERENCES priority(priority_id) ON DELETE RESTRICT,
    current_status_id BIGINT NOT NULL REFERENCES request_status(status_id) ON DELETE RESTRICT,
    commercial_user_id BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    origin_address_id BIGINT REFERENCES address(address_id) ON DELETE RESTRICT,
    destination_address_id BIGINT REFERENCES address(address_id) ON DELETE RESTRICT,
    installation_address_id BIGINT REFERENCES address(address_id) ON DELETE RESTRICT,
    requirements TEXT NOT NULL DEFAULT '',
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    forwarded_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    concluded_at TIMESTAMPTZ,
    extra_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT request_dates_ck CHECK (concluded_at IS NULL OR concluded_at >= received_at)
);

CREATE TABLE request_status_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE CASCADE,
    from_status_id BIGINT REFERENCES request_status(status_id) ON DELETE RESTRICT,
    to_status_id BIGINT NOT NULL REFERENCES request_status(status_id) ON DELETE RESTRICT,
    changed_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    note TEXT NOT NULL DEFAULT '',
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE request_contact (
    request_id UUID PRIMARY KEY REFERENCES operational_request(request_id) ON DELETE CASCADE,
    contact_name VARCHAR(160) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(40),
    company_name VARCHAR(180)
);

CREATE TABLE technical_evaluation (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE CASCADE,
    evaluated_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    distance_km NUMERIC(10,3),
    coverage VARCHAR(40) NOT NULL,
    infrastructure VARCHAR(60) NOT NULL,
    deployment VARCHAR(30) NOT NULL,
    fiber_type VARCHAR(30) NOT NULL,
    fiber_amount INTEGER,
    difficulty VARCHAR(20) NOT NULL,
    materials TEXT NOT NULL DEFAULT '',
    observations TEXT NOT NULL DEFAULT '',
    feasibility VARCHAR(20) NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT technical_feasibility_ck CHECK (feasibility IN ('FACTIBLE', 'NO FACTIBLE')),
    CONSTRAINT technical_distance_ck CHECK (distance_km IS NULL OR distance_km >= 0),
    CONSTRAINT technical_fiber_ck CHECK (fiber_amount IS NULL OR fiber_amount > 0)
);

CREATE TABLE equipment (
    equipment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipment_key VARCHAR(60) NOT NULL UNIQUE,
    label VARCHAR(120) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE systems_verification (
    verification_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE CASCADE,
    verified_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    availability VARCHAR(30) NOT NULL,
    compatibility VARCHAR(30) NOT NULL,
    additional_requirements TEXT NOT NULL DEFAULT '',
    observations TEXT NOT NULL DEFAULT '',
    result VARCHAR(20) NOT NULL,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT systems_result_ck CHECK (result IN ('APROBADO', 'NO APROBADO'))
);

CREATE TABLE verification_equipment (
    verification_id BIGINT NOT NULL REFERENCES systems_verification(verification_id) ON DELETE CASCADE,
    equipment_id BIGINT NOT NULL REFERENCES equipment(equipment_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (verification_id, equipment_id),
    CONSTRAINT verification_quantity_ck CHECK (quantity > 0)
);

CREATE TABLE work_assignment (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE CASCADE,
    leader_user_id BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    scheduled_date DATE NOT NULL,
    assigned_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (request_id)
);

CREATE TABLE assignment_member (
    assignment_id BIGINT NOT NULL REFERENCES work_assignment(assignment_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    member_role VARCHAR(20) NOT NULL DEFAULT 'APOYO',
    PRIMARY KEY (assignment_id, user_id),
    CONSTRAINT member_role_ck CHECK (member_role IN ('LIDER', 'APOYO'))
);

CREATE TABLE work_report (
    report_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assignment_id BIGINT NOT NULL REFERENCES work_assignment(assignment_id) ON DELETE CASCADE,
    reported_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ,
    activities TEXT NOT NULL,
    materials_used TEXT NOT NULL DEFAULT '',
    problems TEXT NOT NULL DEFAULT '',
    result VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT report_dates_ck CHECK (end_at IS NULL OR end_at >= start_at),
    CONSTRAINT report_result_ck CHECK (result IN ('EN EJECUCIÓN', 'FINALIZADA', 'SUSPENDIDA'))
);

CREATE TABLE incident (
    incident_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE CASCADE,
    reported_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    incident_type VARCHAR(60) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ABIERTA',
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ,
    CONSTRAINT incident_status_ck CHECK (status IN ('ABIERTA', 'EN ATENCIÓN', 'CERRADA'))
);

CREATE TABLE genetic_run (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    population_size INTEGER NOT NULL,
    generations INTEGER NOT NULL,
    mutation_rate NUMERIC(5,4) NOT NULL,
    crossover_rate NUMERIC(5,4) NOT NULL,
    objective_weights JSONB NOT NULL DEFAULT '{}'::jsonb,
    input_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    best_fitness NUMERIC(14,6),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT genetic_run_status_ck CHECK (status IN ('PENDIENTE', 'EJECUTANDO', 'COMPLETADO', 'CANCELADO', 'ERROR')),
    CONSTRAINT genetic_population_ck CHECK (population_size > 1),
    CONSTRAINT genetic_generations_ck CHECK (generations > 0),
    CONSTRAINT genetic_rates_ck CHECK (mutation_rate BETWEEN 0 AND 1 AND crossover_rate BETWEEN 0 AND 1)
);

CREATE TABLE genetic_run_request (
    run_id UUID NOT NULL REFERENCES genetic_run(run_id) ON DELETE CASCADE,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE RESTRICT,
    position_original INTEGER NOT NULL,
    PRIMARY KEY (run_id, request_id),
    UNIQUE (run_id, position_original)
);

CREATE TABLE genetic_candidate (
    candidate_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES genetic_run(run_id) ON DELETE CASCADE,
    generation INTEGER NOT NULL,
    candidate_index INTEGER NOT NULL,
    chromosome JSONB NOT NULL,
    fitness NUMERIC(14,6) NOT NULL,
    is_best BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, generation, candidate_index),
    CONSTRAINT candidate_generation_ck CHECK (generation >= 0)
);

CREATE TABLE genetic_solution_gene (
    candidate_id BIGINT NOT NULL REFERENCES genetic_candidate(candidate_id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    request_id UUID NOT NULL REFERENCES operational_request(request_id) ON DELETE RESTRICT,
    technician_id BIGINT REFERENCES app_user(user_id) ON DELETE RESTRICT,
    scheduled_date DATE,
    local_cost NUMERIC(14,6) NOT NULL DEFAULT 0,
    PRIMARY KEY (candidate_id, position),
    UNIQUE (candidate_id, request_id),
    CONSTRAINT gene_position_ck CHECK (position >= 0)
);

CREATE TABLE genetic_solution_application (
    application_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    candidate_id BIGINT NOT NULL REFERENCES genetic_candidate(candidate_id) ON DELETE RESTRICT,
    applied_by BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE RESTRICT,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes TEXT NOT NULL DEFAULT ''
);

-- Nombres fisicos en espanol para facilitar administracion y consultas.
ALTER TABLE IF EXISTS app_user RENAME TO usuarios;
ALTER TABLE IF EXISTS role RENAME TO roles;
ALTER TABLE IF EXISTS user_role RENAME TO usuarios_roles;
ALTER TABLE IF EXISTS module RENAME TO modulos;
ALTER TABLE IF EXISTS role_module RENAME TO roles_modulos;
ALTER TABLE IF EXISTS client RENAME TO clientes;
ALTER TABLE IF EXISTS address RENAME TO direcciones;
ALTER TABLE IF EXISTS service_type RENAME TO tipos_servicio;
ALTER TABLE IF EXISTS priority RENAME TO prioridades;
ALTER TABLE IF EXISTS request_status RENAME TO estados_solicitud;
ALTER TABLE IF EXISTS operational_request RENAME TO solicitudes;
ALTER TABLE IF EXISTS request_status_history RENAME TO historial_estados_solicitud;
ALTER TABLE IF EXISTS request_contact RENAME TO contactos_solicitud;
ALTER TABLE IF EXISTS technical_evaluation RENAME TO evaluaciones_tecnicas;
ALTER TABLE IF EXISTS equipment RENAME TO equipos;
ALTER TABLE IF EXISTS systems_verification RENAME TO verificaciones_sistemas;
ALTER TABLE IF EXISTS verification_equipment RENAME TO verificaciones_equipos;
ALTER TABLE IF EXISTS work_assignment RENAME TO asignaciones_trabajo;
ALTER TABLE IF EXISTS assignment_member RENAME TO miembros_asignacion;
ALTER TABLE IF EXISTS work_report RENAME TO reportes_trabajo;
ALTER TABLE IF EXISTS incident RENAME TO incidencias;
ALTER TABLE IF EXISTS genetic_run RENAME TO ejecuciones_geneticas;
ALTER TABLE IF EXISTS genetic_run_request RENAME TO ejecuciones_solicitudes;
ALTER TABLE IF EXISTS genetic_candidate RENAME TO candidatos_geneticos;
ALTER TABLE IF EXISTS genetic_solution_gene RENAME TO genes_solucion_genetica;
ALTER TABLE IF EXISTS genetic_solution_application RENAME TO aplicaciones_solucion_genetica;

CREATE INDEX request_status_idx ON solicitudes(current_status_id);
CREATE INDEX request_received_idx ON solicitudes(received_at DESC);
CREATE INDEX history_request_idx ON historial_estados_solicitud(request_id, changed_at DESC);
CREATE INDEX assignment_date_idx ON asignaciones_trabajo(scheduled_date);
CREATE INDEX report_assignment_idx ON reportes_trabajo(assignment_id, created_at DESC);
CREATE INDEX genetic_candidate_best_idx ON candidatos_geneticos(run_id, is_best) WHERE is_best;

INSERT INTO roles (role_key, label) VALUES
    ('admin', 'Administrador'),
    ('comercial', 'Personal Comercial'),
    ('planta_encargado', 'Encargado de Planta Técnica'),
    ('tecnico', 'Técnico'),
    ('sistemas_encargado', 'Encargado de Sistemas'),
    ('soporte_sistemas', 'Soporte de Sistemas')
ON CONFLICT (role_key) DO NOTHING;

INSERT INTO tipos_servicio (service_key, label) VALUES
    ('PUNTO_A_PUNTO', 'Instalación Punto a Punto'),
    ('PUNTO_MULTIPUNTO', 'Instalación Punto Multipunto'),
    ('INTERNET', 'Internet')
ON CONFLICT (service_key) DO NOTHING;

INSERT INTO prioridades (priority_key, label, weight) VALUES
    ('ALTA', 'Alta', 3), ('MEDIA', 'Media', 2), ('BAJA', 'Baja', 1)
ON CONFLICT (priority_key) DO NOTHING;

INSERT INTO estados_solicitud (status_key, label, area_key, is_terminal) VALUES
    ('REGISTRADA', 'Registrada', 'COMERCIAL', FALSE),
    ('EN_REVISION_PLANTA', 'En revisión Planta Técnica', 'PLANTA_TECNICA', FALSE),
    ('FACTIBLE', 'Factible', 'PLANTA_TECNICA', FALSE),
    ('NO_FACTIBLE', 'No factible', 'PLANTA_TECNICA', TRUE),
    ('EN_REVISION_SISTEMAS', 'En revisión Sistemas', 'SISTEMAS', FALSE),
    ('NO_APROBADA_SISTEMAS', 'No aprobada por Sistemas', 'SISTEMAS', TRUE),
    ('RECHAZADA_COMERCIAL', 'Rechazada por Comercial', 'COMERCIAL', TRUE),
    ('APROBADA', 'Aprobada', 'SISTEMAS', FALSE),
    ('ASIGNADA', 'Asignada', 'SISTEMAS', FALSE),
    ('EN_EJECUCION', 'En ejecución', 'PLANTA_TECNICA', FALSE),
    ('SUSPENDIDA', 'Suspendida', 'PLANTA_TECNICA', FALSE),
    ('FINALIZADA', 'Finalizada', 'PLANTA_TECNICA', TRUE),
    ('CANCELADA', 'Cancelada', 'COMERCIAL', TRUE)
ON CONFLICT (status_key) DO NOTHING;

INSERT INTO equipos (equipment_key, label) VALUES
    ('MEDIA_CONVERTER', 'Media Converter'), ('SFP', 'SFP'), ('ONT', 'ONT'),
    ('ROUTER', 'Router'), ('SWITCH', 'Switch'), ('ODF', 'ODF'),
    ('PATCH_PANEL', 'Patch Panel'), ('PATCH_CORD', 'Patch Cord'),
    ('MC1500R', 'MC1500R'), ('OTROS', 'Otros')
ON CONFLICT (equipment_key) DO NOTHING;

-- Ejemplo de consultas para el dashboard:
-- SELECT rs.label, count(*) FROM operational_request r
-- JOIN request_status rs ON rs.status_id = r.current_status_id GROUP BY rs.label;
-- SELECT st.label, count(*) FROM operational_request r
-- JOIN service_type st ON st.service_type_id = r.service_type_id GROUP BY st.label;
-- SELECT scheduled_date, count(*) FROM work_assignment GROUP BY scheduled_date ORDER BY scheduled_date;
