CREATE DATABASE TimesheetDB
GO

USE TimesheetDB
GO  

ALTER DATABASE CURRENT SET ANSI_NULLS ON;
GO

-- Create schemas
CREATE SCHEMA core;
GO
CREATE SCHEMA logs;
GO
CREATE SCHEMA ano;
GO

-- Create tables

CREATE TABLE core.roles (
    role_id INT IDENTITY(1,1) PRIMARY KEY,
    role_name NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE core.department (
    department_id INT IDENTITY(1,1) PRIMARY KEY,
    department_name NVARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE core.employee (
    employee_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_name NVARCHAR(100) NOT NULL,
    employee_email NVARCHAR(150) NOT NULL UNIQUE,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL CHECK (hire_date <= GETDATE()),
    role_id INT NOT NULL,
    experience_level NVARCHAR(50) NOT NULL,
    manager_id INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    is_active BIT NOT NULL DEFAULT 1,

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id) REFERENCES core.department(department_id),

    CONSTRAINT fk_employee_role
        FOREIGN KEY (role_id) REFERENCES core.roles(role_id),

    CONSTRAINT fk_employee_manager
        FOREIGN KEY (manager_id) REFERENCES core.employee(employee_id)
);

CREATE TABLE core.client (
    client_id INT IDENTITY(1,1) PRIMARY KEY,
    client_name NVARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE core.projects (
    project_id INT IDENTITY(1,1) PRIMARY KEY,
    client_id INT NOT NULL,
    project_name NVARCHAR(200) NOT NULL,
    project_status NVARCHAR(20) NOT NULL CHECK (project_status IN ('active', 'ended', 'freeze')),

    CONSTRAINT fk_projects_client
        FOREIGN KEY (client_id) REFERENCES core.client(client_id)
);

CREATE TABLE core.timesheet (
    timesheet_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    timesheet_status NVARCHAR(20) NOT NULL CHECK (timesheet_status IN ('draft', 'submitted', 'approved', 'rejected', 'edited')),
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    metadata NVARCHAR(MAX) NULL,

    CONSTRAINT fk_timesheet_employee
        FOREIGN KEY (employee_id) REFERENCES core.employee(employee_id),

    CONSTRAINT ck_check_date
        CHECK (end_date >= start_date)
);

CREATE TABLE core.timeentry (
    entry_id INT IDENTITY(1,1) PRIMARY KEY,
    timesheet_id INT NOT NULL,
    project_id INT NOT NULL,
    entry_date DATE NOT NULL,
    hours_worked DECIMAL(5,2) NOT NULL CHECK (hours_worked > 0 AND hours_worked <= 24),
    entry_description NVARCHAR(255) NULL,
    is_billable BIT NOT NULL,

    CONSTRAINT fk_timeentry_timesheet
        FOREIGN KEY (timesheet_id) REFERENCES core.timesheet(timesheet_id) ON DELETE CASCADE,

    CONSTRAINT fk_timeentry_project
        FOREIGN KEY (project_id) REFERENCES core.projects(project_id)
);

CREATE TABLE logs.auditlog (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    timesheet_id INT NOT NULL,
    action_taken NVARCHAR(30) NOT NULL CHECK (action_taken IN ('added', 'edit', 'add_timeentry', 'edit_timeentry', 'delete_timeentry', 'status_change', 'delete')),
    action_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    employee_id INT NOT NULL,
    new_value NVARCHAR(MAX) NULL,

    CONSTRAINT fk_auditlog_employee
        FOREIGN KEY (employee_id) REFERENCES core.employee(employee_id)
);
GO


-- Triggers

-- Trigger for INSERT on core.employee -> update core.employee.updated_at with current date
CREATE TRIGGER trg_employee_after_update_set_updated_at
ON core.employee
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE core.employee
    SET updated_at = GETDATE()
    FROM core.employee
    INNER JOIN inserted
        ON core.employee.employee_id = inserted.employee_id;
END
GO


-- Trigger for INSERT on core.timesheet -> update timesheet.updated_at with current date
CREATE TRIGGER trg_timesheet_after_update_set_updated_at
ON core.timesheet
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE core.timesheet
    SET updated_at = GETDATE()
    FROM core.timesheet
    INNER JOIN inserted
        ON core.timesheet.timesheet_id = inserted.timesheet_id;
END
GO

-- Helper function to create a json from a timesheet containing its timeetries
CREATE FUNCTION core.fn_timesheet_with_entries_json (@timesheet_id INT)
RETURNS NVARCHAR(MAX)
AS
BEGIN
    RETURN (
        SELECT
            ts.timesheet_id,
            ts.employee_id,
            ts.start_date,
            ts.end_date,
            ts.timesheet_status,
            ts.created_at,
            ts.updated_at,
            ts.metadata,
            (
                SELECT
                    te.entry_id,
                    te.project_id,
                    te.entry_date,
                    te.hours_worked,
                    te.entry_description,
                    te.is_billable
                FROM core.timeentry te
                WHERE te.timesheet_id = ts.timesheet_id
                FOR JSON PATH
            ) AS timeentries
        FROM core.timesheet ts
        WHERE ts.timesheet_id = @timesheet_id
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    );
END
GO


-- Trigger logic to create audit logs when interacting with timesheets/timeetries

-- SESSION_CONTEXT employee_id is expected to be set before running the insert, it will default to owner of the timesheet if its not set
-- Usually will need to be set from api when creating db_context

-- Trigger for INSERT on core.timesheet -> create entries on logs.auditlogs
CREATE TRIGGER trg_timesheet_auditlog_after_insert
ON core.timesheet
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @employee_id INT = CAST(SESSION_CONTEXT(N'employee_id') AS INT);
    INSERT INTO logs.auditlog (
        timesheet_id,
        action_taken,
        action_date,
        employee_id,
        new_value
    )
    SELECT
        i.timesheet_id,
        'added',
        GETDATE(),
        COALESCE(@employee_id, i.employee_id),
        core.fn_timesheet_with_entries_json(i.timesheet_id)
    FROM inserted i;
END
GO

-- Trigger for UPDATE on core.timesheet (state_change) -> create entries on logs.auditlogs
CREATE TRIGGER trg_timesheet_auditlog_status_change
ON core.timesheet
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @employee_id INT = CAST(SESSION_CONTEXT(N'employee_id') AS INT);

    INSERT INTO logs.auditlog (
        timesheet_id,
        action_taken,
        action_date,
        employee_id,
        new_value
    )
    SELECT
        i.timesheet_id,
        'status_change',
        GETDATE(),
        COALESCE(@employee_id, i.employee_id),
        core.fn_timesheet_with_entries_json(i.timesheet_id)
    FROM inserted i
    INNER JOIN deleted d
        ON i.timesheet_id = d.timesheet_id
    WHERE ISNULL(i.timesheet_status, '') <> ISNULL(d.timesheet_status, '');
END
GO

-- Trigger for UPDATE on core.timesheet -> create entries on logs.auditlogs
CREATE TRIGGER trg_timesheet_auditlog_after_update_otherfields
ON core.timesheet
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @employee_id INT = CAST(SESSION_CONTEXT(N'employee_id') AS INT);

    INSERT INTO logs.auditlog (
        timesheet_id,
        action_taken,
        action_date,
        employee_id,
        new_value
    )
    SELECT
        i.timesheet_id,
        'edit',
        GETDATE(),
        COALESCE(@employee_id, i.employee_id),
        core.fn_timesheet_with_entries_json(i.timesheet_id)
    FROM inserted i
    INNER JOIN deleted d
        ON i.timesheet_id = d.timesheet_id
    WHERE
        (
            ISNULL(i.start_date, '') <> ISNULL(d.start_date, '') OR
            ISNULL(i.end_date, '') <> ISNULL(d.end_date, '') OR
            ISNULL(i.metadata, '') <> ISNULL(d.metadata, '') 
        )
        AND
        ISNULL(i.timesheet_status, '') = ISNULL(d.timesheet_status, '');
END
GO

-- Trigger for INSERT on core.timeentry -> create entries on logs.auditlogs
CREATE TRIGGER trg_timeentry_auditlog_after_insert
ON core.timeentry
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @employee_id INT = CAST(SESSION_CONTEXT(N'employee_id') AS INT);

    INSERT INTO logs.auditlog (
        timesheet_id,
        action_taken,
        action_date,
        employee_id,
        new_value
    )
    SELECT
        i.timesheet_id,
        'add_timeentry',
        GETDATE(),
        COALESCE(@employee_id, (SELECT ts.employee_id FROM core.timesheet ts WHERE ts.timesheet_id = i.timesheet_id)),
        core.fn_timesheet_with_entries_json(i.timesheet_id)
    FROM inserted i;
END;
GO


-- Trigger for UPDATE on core.timeentry -> create entries on logs.auditlogs
CREATE TRIGGER trg_timeentry_auditlog_after_update
ON core.timeentry
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @employee_id INT = CAST(SESSION_CONTEXT(N'employee_id') AS INT);

    INSERT INTO logs.auditlog (
        timesheet_id,
        action_taken,
        action_date,
        employee_id,
        new_value
    )
    SELECT
        i.timesheet_id,
        'edit_timeentry',
        GETDATE(),
        COALESCE(@employee_id, (SELECT ts.employee_id FROM core.timesheet ts WHERE ts.timesheet_id = i.timesheet_id)),
        core.fn_timesheet_with_entries_json(d.timesheet_id)
    FROM inserted i
    INNER JOIN deleted d
        ON i.entry_id = d.entry_id
    WHERE
        ISNULL(i.project_id, '') <> ISNULL(d.project_id, '') OR
        ISNULL(i.entry_date, '') <> ISNULL(d.entry_date, '') OR
        ISNULL(i.hours_worked, '') <> ISNULL(d.hours_worked, '') OR
        ISNULL(i.entry_description, '') <> ISNULL(d.entry_description, '') OR
        ISNULL(i.is_billable, '') <> ISNULL(d.is_billable, '');
END;
GO


-- Trigger for DELETE on core.timeentry -> create entries on logs.auditlogs
CREATE TRIGGER trg_timeentry_auditlog_after_delete
ON core.timeentry
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @employee_id INT = CAST(SESSION_CONTEXT(N'employee_id') AS INT);

    INSERT INTO logs.auditlog (
        timesheet_id,
        action_taken,
        action_date,
        employee_id,
        new_value
    )
    SELECT
        d.timesheet_id,
        'delete_timeentry',
        GETDATE(),
        COALESCE(@employee_id, (SELECT ts.employee_id FROM core.timesheet ts WHERE ts.timesheet_id = d.timesheet_id)),
        core.fn_timesheet_with_entries_json(d.timesheet_id)
    FROM deleted d;
END;
GO


-- Views

-- Employee information pre-aggregated 
CREATE VIEW core.vw_employee_details
AS
SELECT
    e.employee_id,
    e.employee_name,
    e.employee_email,
    d.department_name,
    r.role_name,
    e.hire_date,
    e.experience_level,
    m.employee_name AS manager_name,
    e.is_active,
    e.created_at,
    e.updated_at
FROM
    core.employee AS e
INNER JOIN
    core.department AS d ON e.department_id = d.department_id
INNER JOIN
    core.roles AS r ON e.role_id = r.role_id
LEFT JOIN
    core.employee AS m ON e.manager_id = m.employee_id; -- Left join for employees without a manager
GO


-- Timesheet information pre-aggregated + worked hours associated with the timesheet
CREATE VIEW core.vw_timesheet_summary
AS
SELECT
    ts.timesheet_id,
    e.employee_name,
    e.employee_email,
    ts.start_date,
    ts.end_date,
    ts.timesheet_status,
    COALESCE(SUM(te.hours_worked), 0.00) AS total_hours_worked,
    ts.created_at AS timesheet_created_at,
    ts.updated_at AS timesheet_updated_at
FROM
    core.timesheet AS ts
INNER JOIN
    core.employee AS e ON ts.employee_id = e.employee_id
LEFT JOIN
    core.timeentry AS te ON ts.timesheet_id = te.timesheet_id
GROUP BY
    ts.timesheet_id,
    e.employee_name,
    e.employee_email,
    ts.start_date,
    ts.end_date,
    ts.timesheet_status,
    ts.created_at,
    ts.updated_at;
GO

-- Calculates the total number of hours each employee worked for recorded days
CREATE VIEW core.vw_daily_employee_hours
AS
SELECT
    ts.employee_id,
    e.employee_name,
    te.entry_date,
    SUM(te.hours_worked) AS daily_hours_worked
FROM
    core.timeentry AS te
INNER JOIN
    core.timesheet AS ts ON te.timesheet_id = ts.timesheet_id
INNER JOIN
    core.employee AS e ON ts.employee_id = e.employee_id
GROUP BY
    ts.employee_id,
    e.employee_name,
    te.entry_date;
GO

-- Daily logged hours vs hours logged on the previous recorded day 
Create VIEW core.vw_daily_hours_comparison
AS
-- Cte to get the hours worked form the previous recorded day (partition by id and order by date)
-- -> data is taken from the previeous defined view where we have each employee daily recordead hours
WITH lagged_daily_hours AS (
    SELECT
        deh.employee_id,
        deh.employee_name,
        deh.entry_date,
        deh.daily_hours_worked,
        -- Prev 1 value, 0 if it doesnt exist
        LAG(deh.daily_hours_worked, 1, 0.00) OVER (
            PARTITION BY deh.employee_id
            ORDER BY deh.entry_date
        ) AS previous_day_hours_calculated
    FROM
        core.vw_daily_employee_hours AS deh
)
SELECT
    ldh.employee_id,
    ldh.employee_name,
    ldh.entry_date,
    ldh.daily_hours_worked,
    ldh.previous_day_hours_calculated AS previous_day_hours,
    ldh.daily_hours_worked - ldh.previous_day_hours_calculated AS difference_from_previous_day
FROM
    lagged_daily_hours AS ldh;
GO


CREATE VIEW core.mv_employee_project_hours_summary
WITH SCHEMABINDING
AS
SELECT
    e.employee_id,
    e.employee_name,
    p.project_id,
    p.project_name,
    -- Total hours worked for the employee on this project
    SUM(te.hours_worked) AS total_hours_per_project,
    -- Total billable hours for the employee on this project
    SUM(CASE WHEN te.is_billable = 1 THEN te.hours_worked ELSE 0 END) AS total_billable_hours_per_project,
    -- Total unbillable hours for the employee on this project
    SUM(CASE WHEN te.is_billable = 0 THEN te.hours_worked ELSE 0 END) AS total_unbillable_hours_per_project,
    -- Count of entries for this employee on this project (using COUNT_BIG as required for indexed views)
    COUNT_BIG(*) AS number_of_entries
FROM
    core.timeentry AS te
INNER JOIN
    core.timesheet AS ts ON te.timesheet_id = ts.timesheet_id
INNER JOIN
    core.employee AS e ON ts.employee_id = e.employee_id
INNER JOIN
    core.projects AS p ON te.project_id = p.project_id
GROUP BY
    e.employee_id,
    e.employee_name,
    p.project_id,
    p.project_name;
GO

CREATE UNIQUE CLUSTERED INDEX idx_mv_employee_project_hours_summary
ON core.mv_employee_project_hours_summary (employee_id, project_id);
GO


-- View (from the index view) without personal information
CREATE VIEW ano.mv_employee_project_hours_summary_anonymized
AS
SELECT
    mv.employee_id,
    mv.project_id,
    mv.total_hours_per_project,
    mv.total_billable_hours_per_project,
    mv.total_unbillable_hours_per_project
FROM core.mv_employee_project_hours_summary mv
GO

-- Roles
CREATE ROLE db_admin;
CREATE ROLE etl_engineer;
CREATE ROLE bi_analyst;
CREATE ROLE timesheet_app_user;
CREATE ROLE auditor;

GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::core TO etl_engineer;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::logs TO etl_engineer;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::ano TO etl_engineer;
GRANT CREATE VIEW TO etl_engineer;

GRANT SELECT ON SCHEMA::core TO bi_analyst;
GRANT SELECT ON SCHEMA::ano TO bi_analyst;

GRANT SELECT, INSERT, UPDATE, DELETE ON core.timesheet TO timesheet_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON core.timeentry TO timesheet_app_user;
GRANT SELECT ON core.vw_timesheet_summary TO timesheet_app_user;
GRANT SELECT ON core.vw_employee_details TO timesheet_app_user;

GRANT SELECT ON SCHEMA::core TO auditor;
GRANT SELECT ON SCHEMA::logs TO auditor;
GRANT SELECT ON SCHEMA::ano TO auditor;

--Indexes

-- fk indexes

-- Index on employee.department_id (FK to core.department)
CREATE NONCLUSTERED INDEX idx_employee_department_id
ON core.employee (department_id);

-- Index on projects.client_id (FK to core.client)
CREATE NONCLUSTERED INDEX idx_projects_client_id
ON core.projects (client_id);

-- Index on timesheet.employee_id (FK to core.employee)
CREATE NONCLUSTERED INDEX idx_timesheet_employee_id
ON core.timesheet (employee_id);


-- fields indexes
-- Index for timesheet_status (filtering timesheets by status)
CREATE NONCLUSTERED INDEX idx_timesheet_status
ON core.timesheet (timesheet_status);

-- Index for entry_date (filtering time entries by date)
CREATE NONCLUSTERED INDEX idx_timeentry_entry_date
ON core.timeentry (entry_date);

GO