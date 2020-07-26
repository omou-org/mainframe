import graphene
from graphene import Field, ID, Int, List, DateTime
from graphene_django.types import DjangoObjectType
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from graphql_jwt.decorators import login_required

from account.models import Admin
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
                        admin_type=AdminTypeEnum(),
                        action=ActionEnum(),
                        object_type=ObjectEnum(),
                        page=Int(),
                        page_size=Int()
                        )
    
    @login_required
    def resolve_logs(self, info, **kwargs):  
        queryset = LogEntry.objects.all()

        user_id = kwargs.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id = user_id)

        admin_type = kwargs.get('admin_type')
        if admin_type:
            admins = Admin.objects.filter(
                user__id__in = set([log.user.id for log in queryset]),
                admin_type = admin_type
                )
            queryset = queryset.filter(user_id__in = [admin.user.id for admin in admins])

        object_type = kwargs.get('object_type')
        if object_type:
            model_content_id = ContentType.objects.get(model=object_type)
            queryset = queryset.filter(content_type_id=model_content_id)

        action = kwargs.get('action')
        if action:
            queryset = queryset.filter(action_flag = action)

        action_date = kwargs.get('date')
        if action_date:
            queryset = queryset.filter(action_time = action_date)
        
        total_size = len(queryset)
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        if page and page_size:
            queryset = paginate(queryset, page, page_size)

        return LogTypeResults(
            results=queryset,
            total=total_size
        )



