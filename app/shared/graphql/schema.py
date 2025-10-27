"""Module de definición del schema de GraphQL"""
import strawberry

from app.menu.infrastructure.graphql.menu_mutations import MenuMutations
from app.menu.infrastructure.graphql.menu_queries import MenuQueries
from app.users.infrastructure.graphql.queries import UserQueries
from app.attendance.infrastructure.graphql.work_schedule_queries import WorkScheduleQueries
from app.users.infrastructure.graphql.mutations import UserMutations
from app.users.infrastructure.graphql.auth.auth_queries import AuthQueries
from app.users.infrastructure.graphql.auth.auth_mutations import AuthMutations
from app.attendance.infrastructure.graphql.attendance_mutations import AttendanceMutations
from app.attendance.infrastructure.graphql.work_schedule_mutations import WorkScheduleMutations

@strawberry.type
class Query(UserQueries, AuthQueries, WorkScheduleQueries, MenuQueries):
    """Query raíz de GraphQL"""

    @strawberry.field
    def hello(self) -> str:
        """ Un simple campo de ejemplo"""
        return "Hello from Catering System API!"


@strawberry.type
class Mutation(UserMutations, AuthMutations, AttendanceMutations, WorkScheduleMutations, MenuMutations):
    """Mutation raíz de GraphQL"""


# Crear schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
