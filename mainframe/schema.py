import graphene
import graphql_jwt

from account import schema as account_schema, mutations as account_mutations
from course import schema as course_schema
from payment import schema as payment_schema
from search import schema as search_schema
from pricing import schema as pricing_schema


class Query(account_schema.Query, course_schema.Query, payment_schema.Query,
            search_schema.Query, pricing_schema.Query, graphene.ObjectType):
    pass


class Mutation(account_mutations.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
