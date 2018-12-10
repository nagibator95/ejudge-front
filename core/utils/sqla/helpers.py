from typing import Type

from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Query


def compile_sql(query: Type[Query]) -> str:
    """Print raw SQL statement for the given query.

    >>> query = db.session.query(Run) \
    >>>     .filter(Run.status_id == 98)
    >>>
    >>> from core.utils.sqla import compile_sql
    >>> compile_sql(query)
    'SELECT courses.id, courses.author_id, courses.status...
    """
    compiled = query.statement.compile(
        dialect=mysql.dialect(),
        compile_kwargs={
            'literal_binds': True
        }
    )
    return str(compiled)
