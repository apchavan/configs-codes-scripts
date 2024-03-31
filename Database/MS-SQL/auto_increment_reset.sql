-- Reference: https://learn.microsoft.com/en-us/sql/t-sql/database-console-commands/dbcc-checkident-transact-sql

-- TRUNCATE all records in table.
TRUNCATE TABLE <TABLE_NAME>
GO

-- Reset the auto increment.
DBCC CHECKIDENT("<TABLE_NAME>", RESEED, 1)
GO

