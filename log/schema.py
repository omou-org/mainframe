import arrow
import graphene
from graphql import GraphQLError
from graphene import DateTime, Field, ID, Int, List, String
from graphene_django.types import DjangoObjectType
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from graphql_jwt.decorators import login_required

from account.models import Admin
from account.mutations import AdminTypeEnum
from search.schema import paginate


class LogType(graphene.ObjectType):
    date=DateTime()
    user_id=ID()
    admin_type=String()
    action=String()
    object_type=String()
    object_repr=String()


class LogTypeResults(graphene.ObjectType):
    results=List(LogType, required=True)
    total=Int()


class Query(object):
    logs=Field(LogTypeResults,
                        start_date_time=String(),
                        end_date_time=String(),
                        user_id=ID(),
                        admin_type=String(),
                        action=String(),
                        object_type=String(),
                        page=Int(),
                        page_size=Int(),
                        sort=String()
                        )
    
    @login_required
    def resolve_logs(self, info, **kwargs):  
        queryset=LogEntry.objects.all()

        user_id=kwargs.get('user_id')
        if user_id:
            queryset=queryset.filter(user_id=user_id)

        admin_type=kwargs.get('admin_type')
        if admin_type:
            admin_types = ["owner", "receptionist", "assistant"]
            if admin_type not in admin_types:
                raise GraphQLError('Failed query. Invalid admin type.')

            admins=Admin.objects.filter(
                user__id__in=set([log.user.id for log in queryset]),
                admin_type=admin_type
            )
            queryset=queryset.filter(user_id__in=[admin.user.id for admin in admins])

        object_type=kwargs.get('object_type')
        if object_type:
            object_types = ['student', 'parent', 'instructor', 'admin', 'payment', 'registration', 'course', 'discount', 'pricerule']
            if object_type not in object_types:
                raise GraphQLError('Failed query. Invalid object type.')

            model_content_id=ContentType.objects.get(model=object_type)
            queryset=queryset.filter(content_type_id=model_content_id)

        action=kwargs.get('action')
        if action:
            action_types = {"add": 1, "edit": 2, "delete": 3}
            if action not in action_types:
                raise GraphQLError('Failed query. Invalid action type.')

            queryset=queryset.filter(action_flag=action_types[action])

        start_date=kwargs.get('start_date_time')
        if start_date:
            queryset=queryset.filter(action_time__gte=arrow.get(start_date).datetime)
        
        end_date=kwargs.get('end_date_time')
        if end_date:
            queryset=queryset.filter(action_time__lt=arrow.get(end_date).datetime)

        sort=kwargs.get('sort')
        if sort:
            sort_types = ["date_asc", "date_desc", "user_asc", "user_desc", "admin_asc", "admin_desc", "action_asc", "action_desc", "object_asc", "object_desc"]
            if sort not in sort_types:
                raise GraphQLError('Failed query. Invalid sort type.')

            obj, order = sort.split("_")
            # filter for obj
            if obj == "date":
                queryset=queryset.order_by("action_time")
            elif obj == "user":
                def get_admin_firstlast_name(log):
                    obj=Admin.objects.get(user__id=log.user_id)
                    return obj.user.first_name+" "+obj.user.last_name
                queryset=sorted(queryset, key=get_admin_firstlast_name)
            elif obj == "admin":
                def get_admin_type(log):
                    obj=Admin.objects.get(user__id=log.user_id)
                    return obj.admin_type
                queryset=sorted(queryset, key=get_admin_type)
            elif obj == "action":
                queryset=queryset.order_by("action_flag")
            elif obj == "object":
                def get_object_name(log):
                    obj=ContentType.objects.get(id=log.content_type_id)
                    return str(obj)
                queryset=sorted(queryset, key=get_object_name)

            # sort by order
            if order == "desc":
                # reverse list
                if isinstance(queryset, list):
                    queryset.reverse()
                # reverse queryset
                else:
                    queryset=queryset.reverse()
            
        # pagination
        total_size=len(queryset)
        page=kwargs.get('page')
        page_size=kwargs.get('page_size')
        if page and page_size:
            queryset=paginate(queryset, page, page_size)

        # convert EntryLog to LogType
        flag_to_action = {
            1: "Add",
            2: "Edit",
            3: "Delete"
        }
        formatted_logs=[]
        for log in queryset:
            formatted_logs.append(
                LogType(
                    date=log.action_time,
                    user_id=log.user_id,
                    admin_type=Admin.objects.get(user__id=log.user_id).admin_type,
                    action=flag_to_action[log.action_flag],
                    object_type=ContentType.objects.get(id=log.content_type_id),
                    object_repr=log.object_repr
                )
            )

        return LogTypeResults(
            results=formatted_logs,
            total=total_size
        )
