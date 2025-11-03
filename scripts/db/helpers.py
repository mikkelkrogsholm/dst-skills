"""Helper functions for DST data queries."""


def filter_suppressed(sql: str, value_column: str = "INDHOLD") -> str:
    """Add WHERE clause to filter suppressed values."""
    if "WHERE" in sql.upper():
        return sql.replace("WHERE", f"WHERE {value_column} != '..' AND")
    else:
        # Add WHERE before ORDER BY or GROUP BY or at end
        for clause in ["ORDER BY", "GROUP BY", "LIMIT"]:
            if clause in sql.upper():
                return sql.replace(clause, f"WHERE {value_column} != '..' {clause}")
        return sql + f" WHERE {value_column} != '..'"


def safe_numeric_cast(column: str, cast_type: str = "INTEGER") -> str:
    """Generate CASE statement for safe numeric casting."""
    return f"CASE WHEN {column} != '..' THEN CAST({column} AS {cast_type}) ELSE NULL END"


def get_aggregate_filter(exclude_totals: bool = True) -> str:
    """Get common filter for excluding aggregate rows."""
    if exclude_totals:
        return "AND column NOT IN ('TOT', 'I alt', 'Drivmidler i alt', 'IALT')"
    return ""
