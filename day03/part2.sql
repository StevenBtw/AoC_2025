WITH RECURSIVE greedy_pick AS (
    SELECT
        line_number,
        line_data,
        0 as pick_num,
        ''::VARCHAR as result_value,
        1 as search_start
    FROM banks
    WHERE LENGTH(line_data) >= 12

    UNION ALL

    SELECT
        line_number,
        line_data,
        pick_num + 1,
        result_value || best_char,
        best_pos + 1
    FROM (
        SELECT
            g.line_number,
            g.line_data,
            g.pick_num,
            g.result_value,
            g.search_start,
            (
                SELECT MAX(SUBSTR(g.line_data, pos, 1))
                FROM generate_series(g.search_start, LENGTH(g.line_data) - (11 - g.pick_num)) as t(pos)
            ) as best_char,
            (
                SELECT MIN(pos)
                FROM generate_series(g.search_start, LENGTH(g.line_data) - (11 - g.pick_num)) as t(pos)
                WHERE SUBSTR(g.line_data, pos, 1) = (
                    SELECT MAX(SUBSTR(g.line_data, pos2, 1))
                    FROM generate_series(g.search_start, LENGTH(g.line_data) - (11 - g.pick_num)) as t2(pos2)
                )
            ) as best_pos
        FROM greedy_pick g
        WHERE g.pick_num < 12
    )
),

line_results AS (
    SELECT
        line_number,
        MAX(CAST(result_value AS BIGINT)) as max_joltage
    FROM greedy_pick
    WHERE pick_num = 12
    GROUP BY line_number
)

SELECT SUM(max_joltage) as total_joltage
FROM line_results;
