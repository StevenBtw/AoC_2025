WITH RECURSIVE position_generator AS (
    SELECT 
        line_number,
        line_data,
        1 as pos1
    FROM banks 
    WHERE LENGTH(line_data) >= 12
    
    UNION ALL
    
    SELECT 
        line_number,
        line_data,
        pos1 + 1
    FROM position_generator
    WHERE pos1 < LENGTH(line_data)
),

all_chars AS (
    SELECT 
        line_number,
        line_data,
        pos1,
        SUBSTR(line_data, pos1, 1) as char1
    FROM position_generator
),

three_picks AS (
    SELECT 
        c1.line_number,
        c1.line_data,
        c1.pos1 as exclude_pos1,
        c2.pos1 as exclude_pos2,
        c3.pos1 as exclude_pos3
    FROM all_chars c1
    JOIN all_chars c2 
        ON c1.line_number = c2.line_number 
        AND c1.pos1 < c2.pos1
    JOIN all_chars c3 
        ON c2.line_number = c3.line_number 
        AND c2.pos1 < c3.pos1
),

all_combinations AS (
    SELECT 
        t.line_number,
        CAST(STRING_AGG(c.char1, '' ORDER BY c.pos1) AS BIGINT) as result_value
    FROM three_picks t
    JOIN all_chars c 
        ON t.line_number = c.line_number
        AND c.pos1 NOT IN (t.exclude_pos1, t.exclude_pos2, t.exclude_pos3)
    GROUP BY t.line_number, t.exclude_pos1, t.exclude_pos2, t.exclude_pos3
    HAVING LENGTH(STRING_AGG(c.char1, '')) = 12
),

line_results AS (
    SELECT 
        line_number,
        MAX(result_value) as max_joltage
    FROM all_combinations
    GROUP BY line_number
)

SELECT SUM(max_joltage) as total_joltage
FROM line_results;