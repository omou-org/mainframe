import graphene

from account import schema as account_schema, mutations as account_mutations
from course import schema as course_schema
from payment import schema as payment_schema
from search import schema as search_schema

class Query(account_schema.Query, course_schema.Query,
            payment_schema.Query,
            search_schema.Query,
            graphene.ObjectType):
    pass


class Mutation(account_mutations.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
