import graphene
from graphene import Field, ID, Int, List, DateTime
from graphene_django.types import DjangoObjectType
from django.contrib.admin.models import LogEntry

from account.mutations import AdminTypeEnum
from search.schema import paginate

class ActionEnum(graphene.Enum):
    ADDITION = 1
    CHANGE = 2
    DELETION = 3

class ObjectEnum(graphene.Enum):
    STUDENT = 'student'
    PARENT = 'parent'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'
    PAYMENT = 'payment'
    REGISTRATION = 'registration'
    AVAILABILITY = 'availability'
    COURSE = 'course'
    DISCOUNT = 'discount'
    PRICERULE = 'pricerule'

class LogType(DjangoObjectType):
    class Meta:
        model = LogEntry 

class LogTypeResults(graphene.ObjectType):
    results = List(LogType, required=True)
    total = Int()

class Query(object):
    logs = Field(LogTypeResults,
                        date=DateTime(),
                        user_id=ID(),
                        admin_type=AdminTypeEnum,
                        action=ActionEnum,
                        object_id=ID(),
                        object_type=ObjectEnum,
                        page=Int(),
                        page_size=Int()
                        )
    
    @login_required
    def resolve_logs(self, info, **kwargs):  
        queryset = LogEntry.objects.all()

        # user
        user_id = kwargs.get('user_id')

        # adminType
        admin_type = kwargs.get('admin_type')

        # objectType
        object_type = kwargs.set('object_type')

        # objectID
        object_id = kwargs.set('object_id')

        # action
        action = kwargs.set('action')

        # date
        action_date = kwargs.get('date')
        # check what action

        return LogTypeResults(
            results=queryset,
            total=len(queryset)
        )



