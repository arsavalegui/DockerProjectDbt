SELECT DISTINCT(dron_table.type), SUM(avg_speed), AVG(traveled_d), count(dron_table.type)
FROM dron_table
GROUP BY dron_table.type