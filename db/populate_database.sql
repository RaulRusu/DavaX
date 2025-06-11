USE TimesheetDB;
GO


-- 1. Roles
SET IDENTITY_INSERT core.roles ON;
INSERT INTO core.roles (role_id, role_name) VALUES
(1, 'Software Engineer'),
(2, 'Data Engineer'),
(3, 'QA Analyst'),
(4, 'Project Manager'),
(5, 'HR Specialist');
SET IDENTITY_INSERT core.roles OFF;

-- 2. Departments
SET IDENTITY_INSERT core.department ON;
INSERT INTO core.department (department_id, department_name) VALUES
(1, 'Engineering'),
(2, 'Quality Assurance'),
(3, 'Human Resources'),
(4, 'Project Management');
SET IDENTITY_INSERT core.department OFF;

-- 3. Clients
SET IDENTITY_INSERT core.client ON;
INSERT INTO core.client (client_id, client_name) VALUES
(1, 'Acme Corp'),
(2, 'Globex Inc'),
(3, 'Initech Solutions');
SET IDENTITY_INSERT core.client OFF;

-- 4. Employees
SET IDENTITY_INSERT core.employee ON;
INSERT INTO core.employee (employee_id, employee_name, employee_email, department_id, hire_date, role_id, experience_level, manager_id)
VALUES
(1, 'Alice Johnson', 'alice.johnson@endava.com', 1, '2022-06-01', 1, 'Mid', NULL),
(2, 'Bob Smith', 'bob.smith@endava.com', 1, '2023-01-15', 2, 'Senior', 1),
(3, 'Clara James', 'clara.james@endava.com', 2, '2021-11-03', 3, 'Junior', NULL),
(4, 'Dan Miller', 'dan.miller@endava.com', 3, '2020-03-20', 5, 'Mid', NULL);
SET IDENTITY_INSERT core.employee OFF;

-- 5. Projects
SET IDENTITY_INSERT core.projects ON;
INSERT INTO core.projects (project_id, client_id, project_name, project_status) VALUES
(1, 1, 'Payment Gateway Revamp', 'active'),
(2, 2, 'Cloud Migration', 'active'),
(3, 3, 'Legacy System Decommission', 'ended');
SET IDENTITY_INSERT core.projects OFF;

-- 6. Timesheets
SET IDENTITY_INSERT core.timesheet ON;
INSERT INTO core.timesheet (timesheet_id, employee_id, start_date, end_date, timesheet_status, metadata)
VALUES
(1, 1, '2025-06-01', '2025-06-07', 'submitted', '{"note":"Week 1 submission"}'),
(2, 2, '2025-06-01', '2025-06-07', 'approved', '{"note":"Week 1 approved"}'),
(3, 3, '2025-06-01', '2025-06-07', 'draft', NULL),
(4, 1, '2025-06-08', '2025-06-14', 'approved', '{"note":"Week 2 approved by manager"}'),
(5, 2, '2025-06-08', '2025-06-14', 'submitted', '{"note":"Week 2 submission"}'),
(6, 3, '2025-06-08', '2025-06-14', 'submitted', NULL),
(7, 4, '2025-06-01', '2025-06-07', 'approved', '{"note":"HR Timesheet approved"}'),
(8, 1, '2025-06-15', '2025-06-21', 'draft', '{"note":"Starting Week 3"}'),
(9, 2, '2025-06-15', '2025-06-21', 'draft', NULL),
(10, 3, '2025-06-15', '2025-06-21', 'draft', '{"note":"Pending entries"}'),
(11, 4, '2025-06-08', '2025-06-14', 'submitted', '{"note":"HR Week 2 submission"}'),
(12, 1, '2025-06-22', '2025-06-28', 'submitted', NULL),
(13, 2, '2025-06-22', '2025-06-28', 'approved', '{"note":"End of month timesheet"}'),
(14, 3, '2025-06-22', '2025-06-28', 'approved', '{"note":"QA activities completed"}'),
(15, 4, '2025-06-15', '2025-06-21', 'approved', '{"note":"HR Manager reviewed"}'),
(16, 1, '2025-06-29', '2025-07-05', 'draft', NULL),
(17, 2, '2025-06-29', '2025-07-05', 'draft', '{"note":"Planning next sprint"}'),
(18, 3, '2025-06-29', '2025-07-05', 'draft', NULL),
(19, 4, '2025-06-22', '2025-06-28', 'submitted', NULL),
(20, 1, '2025-07-06', '2025-07-12', 'submitted', '{"note":"Post-holiday submission"}'),
(21, 2, '2025-07-06', '2025-07-12', 'submitted', NULL),
(22, 3, '2025-07-06', '2025-07-12', 'draft', '{"note":"Catching up on entries"}'),
(23, 4, '2025-06-29', '2025-07-05', 'approved', '{"note":"HR tasks for first week of July"}');
SET IDENTITY_INSERT core.timesheet OFF;

-- 7. Timeentries
SET IDENTITY_INSERT core.timeentry ON;
INSERT INTO core.timeentry (entry_id, timesheet_id, project_id, entry_date, hours_worked, entry_description, is_billable)
VALUES
(1, 1, 1, '2025-06-03', 6.0, 'Implemented new endpoint', 1),
(2, 1, 1, '2025-06-04', 7.5, 'Code review and refactor', 1),
(3, 2, 2, '2025-06-05', 8.0, 'Data migration tasks', 1),
(4, 3, 3, '2025-06-06', 4.0, 'System analysis', 0),
(5, 1, 1, '2025-06-05', 5.0, 'Testing payment module', 1),
(6, 2, 2, '2025-06-06', 7.0, 'Cloud architecture review', 1),
(7, 3, 3, '2025-06-07', 3.0, 'Documentation update', 0),
(8, 4, 1, '2025-06-08', 8.0, 'Frontend development', 1),
(9, 5, 2, '2025-06-09', 6.5, 'Database optimization', 1),
(10, 6, 3, '2025-06-10', 5.0, 'Requirement gathering', 0),
(11, 7, 2, '2025-06-02', 7.0, 'HR system maintenance', 0),
(12, 8, 1, '2025-06-16', 7.5, 'Bug fixing', 1),
(13, 9, 2, '2025-06-17', 8.0, 'Security audit', 1),
(14, 10, 3, '2025-06-18', 4.0, 'User training session', 0),
(15, 11, 2, '2025-06-09', 6.0, 'Policy review', 0),
(16, 12, 1, '2025-06-23', 7.0, 'API integration', 1),
(17, 13, 2, '2025-06-24', 8.0, 'System monitoring', 1),
(18, 14, 3, '2025-06-25', 5.5, 'Regression testing', 1),
(19, 15, 2, '2025-06-19', 7.0, 'Employee onboarding documentation', 0),
(20, 16, 1, '2025-06-30', 6.0, 'New feature planning', 1),
(21, 17, 2, '2025-07-01', 7.0, 'Infrastructure setup', 1),
(22, 18, 3, '2025-07-02', 3.5, 'Support documentation', 0),
(23, 19, 1, '2025-06-26', 8.0, 'Payroll processing', 0),
(24, 20, 1, '2025-07-07', 6.0, 'Client meeting preparation', 1),
(25, 21, 2, '2025-07-08', 7.0, 'Database migration', 1),
(26, 22, 3, '2025-07-09', 4.0, 'Performance testing', 1),
(27, 23, 2, '2025-07-01', 7.0, 'Benefits administration', 0),
(28, 1, 1, '2025-06-01', 8.0, 'Initial setup and configuration', 1),
(29, 2, 2, '2025-06-02', 7.0, 'Network design', 1),
(30, 3, 3, '2025-06-03', 5.0, 'Compliance review', 0),
(31, 4, 1, '2025-06-09', 6.0, 'User interface adjustments', 1),
(32, 5, 2, '2025-06-10', 8.0, 'Server maintenance', 1),
(33, 6, 3, '2025-06-11', 4.5, 'Stakeholder communication', 0),
(34, 7, 2, '2025-06-03', 6.5, 'Recruitment process improvements', 0),
(35, 8, 1, '2025-06-19', 7.0, 'Code refactoring', 1),
(36, 9, 2, '2025-06-20', 8.0, 'Data warehousing tasks', 1),
(37, 10, 3, '2025-06-21', 3.0, 'Ad-hoc reporting', 0),
(38, 11, 2, '2025-06-12', 7.0, 'Onboarding new hires', 0),
(39, 12, 1, '2025-06-26', 7.5, 'Deployment activities', 1),
(40, 13, 2, '2025-06-27', 8.0, 'Disaster recovery planning', 1),
(41, 14, 3, '2025-06-28', 6.0, 'Final testing phase', 1),
(42, 15, 2, '2025-06-20', 7.0, 'Performance review preparation', 0),
(43, 16, 1, '2025-07-03', 5.0, 'Research and development', 1),
(44, 17, 2, '2025-07-04', 7.0, 'Cloud cost optimization', 1);
SET IDENTITY_INSERT core.timeentry OFF;

GO