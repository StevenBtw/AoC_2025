WITH RECURSIVE position_generator AS (
    SELECT 
        line_number,
        line_data,
        1 as pos1
    FROM banks 
    WHERE LENGTH(line_data) > 1
    
    UNION ALL
    
    SELECT 
        line_number,
        line_data,
        pos1 + 1
    FROM position_generator
    WHERE pos1 < LENGTH(line_data)
),

all_pairs AS (
    SELECT 
        p1.line_number,
        p1.line_data,
        p1.pos1,
        p2.pos1 as pos2,
        SUBSTR(p1.line_data, p1.pos1, 1) as char1,
        SUBSTR(p2.line_data, p2.pos1, 1) as char2
    FROM position_generator p1
    JOIN position_generator p2 
        ON p1.line_number = p2.line_number 
        AND p1.pos1 < p2.pos1
    WHERE 
        SUBSTR(p1.line_data, p1.pos1, 1) BETWEEN '0' AND '9'
        AND SUBSTR(p2.line_data, p2.pos1, 1) BETWEEN '0' AND '9'
),

line_results AS (
    SELECT 
        line_number,
        MAX(CAST(char1 || char2 AS INTEGER)) as max_joltage
    FROM all_pairs
    GROUP BY line_number
)

SELECT SUM(max_joltage) as total_joltage
FROM line_results;