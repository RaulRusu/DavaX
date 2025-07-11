CREATE OR REPLACE FUNCTION categorize_absence(absence_type IN VARCHAR2)
    RETURN VARCHAR2
    IS
        v_category VARCHAR2(50);
    BEGIN
        CASE
            -- Exam-related
            WHEN LOWER(absence_type) LIKE '%exam%' OR
                LOWER(absence_type) LIKE '%colocviu%' OR
                LOWER(absence_type) LIKE '%thesis%' OR
                LOWER(absence_type) LIKE '%presentation%' OR
                LOWER(absence_type) LIKE '%project%' OR
                LOWER(absence_type) LIKE '%licenta%' OR
                LOWER(absence_type) LIKE '%graduation%' OR
                LOWER(absence_type) LIKE '%university%' OR
                LOWER(absence_type) LIKE '%faculty%' OR
                LOWER(absence_type) LIKE '%dissertation%' OR
                LOWER(absence_type) LIKE '%curs%' OR
                LOWER(absence_type) LIKE '%labs%' OR
                LOWER(absence_type) LIKE '%lab%' OR
                LOWER(absence_type) LIKE '%seminar%' OR
                LOWER(absence_type) LIKE '%course%' OR
                LOWER(absence_type) LIKE '%final%' OR
                LOWER(absence_type) LIKE '%test%' OR
                LOWER(absence_type) LIKE '%online university%'
                THEN v_category := 'exam';

            -- Medical-related
            WHEN LOWER(absence_type) LIKE '%medical%' OR
                LOWER(absence_type) LIKE '%doctor%' OR
                LOWER(absence_type) LIKE '%consultation%' 
                THEN v_category := 'medical';

            -- Annual Leave
            WHEN LOWER(absence_type) LIKE '%annual leave%' OR
                LOWER(absence_type) LIKE '%vacation%' OR
                LOWER(absence_type) LIKE '%vacantion%' OR
                LOWER(absence_type) LIKE '%concediu planificat%' OR
                LOWER(absence_type) LIKE '%concediu%' OR
                LOWER(absence_type) LIKE '%holiday%'
                THEN v_category := 'annual leave';

            -- Training
            WHEN LOWER(absence_type) LIKE '%training%' OR
                LOWER(absence_type) LIKE '%school%' OR
                LOWER(absence_type) LIKE '%event%' OR
                LOWER(absence_type) LIKE '%conference%'
                THEN v_category := 'training';

            -- Parental Leave
            WHEN LOWER(absence_type) LIKE '%maternity%' OR
                LOWER(absence_type) LIKE '%paternity%' OR
                LOWER(absence_type) LIKE '%parental%'
                THEN v_category := 'parental leave';

            -- Fallback
            ELSE
                v_category := 'unknown';
        END CASE;

        RETURN v_category;
    END;