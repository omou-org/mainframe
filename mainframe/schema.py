import graphene

from account import schema, mutations


class Query(schema.Query, graphene.ObjectType):
    pass


class Mutation(mutations.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
