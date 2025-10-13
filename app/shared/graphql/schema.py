import strawberry

from app.requests.infrastructure.graphql.requests_mutations import RequestsMutations
from app.requests.infrastructure.graphql.requests_queries import RequestsQueries
from app.users.infrastructure.graphql.queries import UserQueries
from app.attendance.infrastructure.graphql.work_schedule_queries import WorkScheduleQueries
from app.users.infrastructure.graphql.mutations import UserMutations
from app.users.infrastructure.graphql.auth.auth_queries import AuthQueries
from app.users.infrastructure.graphql.auth.auth_mutations import AuthMutations
from app.attendance.infrastructure.graphql.attendance_mutations import AttendanceMutations
from app.attendance.infrastructure.graphql.work_schedule_mutations import WorkScheduleMutations

@strawberry.type
class Query(UserQueries, AuthQueries, RequestsQueries, WorkScheduleQueries):
    """Query raíz de GraphQL"""

    @strawberry.field
    def hello(self) -> str:
        """ Un simple campo de ejemplo"""
        return "Hello from Catering System API!"


@strawberry.type
class Mutation(UserMutations, AuthMutations, AttendanceMutations, RequestsMutations, WorkScheduleMutations):
    """Mutation raíz de GraphQL"""
    pass


# Crear schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
