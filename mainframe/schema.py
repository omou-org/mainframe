import graphene
import graphql_jwt
import graphql_social_auth

from account import schema as account_schema, mutations as account_mutations
from comms import schema as comms_schema, mutations as comms_mutations
from course import schema as course_schema, mutations as course_mutations
from onboarding import schema as onboarding_schema, mutations as onboarding_mutations
from invoice import schema as invoice_schema, mutations as invoice_mutations
from scheduler import schema as scheduler_schema, mutations as scheduler_mutations
from search import schema as search_schema
from pricing import schema as pricing_schema, mutations as pricing_mutations
from log import schema as log_schema


class Query(account_schema.Query, comms_schema.Query, course_schema.Query,
            invoice_schema.Query, scheduler_schema.Query, search_schema.Query,
            pricing_schema.Query, log_schema.Query, onboarding_schema.Query,
            graphene.ObjectType):
    pass


class Mutation(account_mutations.Mutation, comms_mutations.Mutation,
               course_mutations.Mutation, pricing_mutations.Mutation,
               scheduler_mutations.Mutation, invoice_mutations.Mutation,
               onboarding_mutations.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
