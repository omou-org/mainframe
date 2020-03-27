from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mainframe.permissions import ReadOnly, IsDev
from course.models import Course, Enrollment
from course.serializers import EnrollmentSerializer
from payment.models import Payment
from payment.serializers import PaymentSerializer
from pricing.views import price_quote_total


class PaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data.update(price_quote_total(data))
        
        discounts = data.pop("discounts")
        data["deductions"] = []
        for discount in discounts:
            data["deductions"].append(
                {
                    "discount":discount["id"],
                    "amount":discount["amount"]
                }
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UnpaidSessionsView(APIView):
    """
    Lists all enrollments with zero or negative sessions left.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def get(self, request):
        enrollments = Enrollment.objects.all()
        final_enrollments = []
        for enrollment in enrollments:
            if enrollment.course.course_type == Course.CLASS and enrollment.sessions_left < 0:
                final_enrollments.append(enrollment)
            elif enrollment.sessions_left <= 0:
                final_enrollments.append(enrollment)

        serializer = EnrollmentSerializer(final_enrollments, many=True)
        return Response(serializer.data)
