import strawberry
from app.users.infrastructure.graphql.queries import UserQueries
from app.users.infrastructure.graphql.mutations import UserMutations
from app.users.infrastructure.graphql.auth.auth_queries import AuthQueries
from app.users.infrastructure.graphql.auth.auth_mutations import AuthMutations

@strawberry.type
class Query(UserQueries, AuthQueries):
    """Query raíz de GraphQL"""

    @strawberry.field
    def hello(self) -> str:
        return "Hello from Catering System API!"


@strawberry.type
class Mutation(UserMutations, AuthMutations):
    """Mutation raíz de GraphQL"""
    pass


# Crear schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)