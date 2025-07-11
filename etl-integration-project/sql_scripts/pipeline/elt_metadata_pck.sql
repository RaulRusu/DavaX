CREATE OR REPLACE PACKAGE etl_metadata_pck AS
    -- Function to get the last load timestamp for a given table
    FUNCTION get_last_load_timestamp(p_table_name IN NVARCHAR2) RETURN TIMESTAMP;

    -- Procedure to update the last processed timestamp for a given table
    PROCEDURE update_last_load_processed_timestamp(p_table_name IN NVARCHAR2, p_timestamp IN TIMESTAMP);
END etl_metadata_pck;

CREATE or REPLACE PACKAGE BODY etl_metadata_pck AS
    MIN_TIMESTAMP CONSTANT TIMESTAMP := TIMESTAMP '1970-01-01 00:00:00';

    FUNCTION get_last_load_timestamp(p_table_name IN NVARCHAR2) RETURN TIMESTAMP IS
        v_last_processed_timestamp TIMESTAMP;
    BEGIN
        SELECT last_processed_timestamp INTO v_last_processed_timestamp
        FROM etl_metadata
        WHERE table_name = p_table_name;

        RETURN v_last_processed_timestamp;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RETURN MIN_TIMESTAMP;
    END get_last_load_timestamp;

    PROCEDURE update_last_load_processed_timestamp(p_table_name IN NVARCHAR2, p_timestamp IN TIMESTAMP) IS
    BEGIN
        MERGE INTO etl_metadata e
        USING (SELECT p_table_name AS table_name, p_timestamp AS last_processed_timestamp FROM dual) src
        ON (e.table_name = src.table_name)
        WHEN MATCHED THEN
            UPDATE SET e.last_processed_timestamp = src.last_processed_timestamp
        WHEN NOT MATCHED THEN
            INSERT (table_name, last_processed_timestamp)
            VALUES (src.table_name, src.last_processed_timestamp);
    END update_last_load_processed_timestamp;

END etl_metadata_pck;