USE TimesheetDB;
GO

BEGIN TRY
    BEGIN TRANSACTION;

    -- Step 1: Delete from child tables first
    DELETE FROM core.timeentry;
    DELETE FROM logs.auditlog;
    DELETE FROM core.timesheet;

    -- Step 2: Delete from mid-level dependencies
    DELETE FROM core.projects;
    DELETE FROM core.client;
    DELETE FROM core.employee;

    -- Step 3: Delete from lookup tables
    DELETE FROM core.roles;
    DELETE FROM core.department;

    -- Step 4: Reset identity seeds
    DBCC CHECKIDENT ('logs.auditlog', RESEED, 0);
    DBCC CHECKIDENT ('core.timeentry', RESEED, 0);
    DBCC CHECKIDENT ('core.timesheet', RESEED, 0);
    DBCC CHECKIDENT ('core.projects', RESEED, 0);
    DBCC CHECKIDENT ('core.client', RESEED, 0);
    DBCC CHECKIDENT ('core.employee', RESEED, 0);
    DBCC CHECKIDENT ('core.roles', RESEED, 0);
    DBCC CHECKIDENT ('core.department', RESEED, 0);

    COMMIT TRANSACTION;

    PRINT 'All data deleted and identity values reset successfully.';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;

    PRINT 'An error occurred. Transaction has been rolled back.';
    PRINT ERROR_MESSAGE();
END CATCH;
GO
