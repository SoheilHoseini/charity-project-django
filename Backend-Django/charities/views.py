from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task
from charities.serializers import (
    TaskSerializer, CharitySerializer, BenefactorSerializer
)


class BenefactorRegistration(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        benefactor_serializer = BenefactorSerializer(data=request.data)
        if benefactor_serializer.is_valid():
            benefactor_serializer.save(user=request.user)
            return Response(status=200,
                            data={"message": "Benefactor created!"})
        return Response(data={"message": benefactor_serializer.errors})


class CharityRegistration(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        charity_serializer = CharitySerializer(data=request.data)
        if charity_serializer.is_valid():
            charity_serializer.save(user=request.user)
            return Response(status=200,
                            data={"message": "Charity created!"})
        return Response(data={"message": charity_serializer.errors})


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    permission_classes = [IsBenefactor, ]

    def get(self, request, task_id):

        task = get_object_or_404(Task, id=task_id)
        if task.state != Task.TaskStatus.PENDING:
            return Response(
                status=404,
                data={'detail': 'This task is not pending.'})

        task.assign_to_benefactor(request.user.benefactor)
        return Response(
            status=200,
            data={'detail': 'Request sent.'})

        return Response(status=404)


class TaskResponse(APIView):
    permission_classes = [IsCharityOwner,]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if request.data["response"] not in ["A","R"]:
            return Response(
                status=400,
                data={'detail': 'Required field ("A" for accepted / "R" for rejected)'}
            )
        if task.state != Task.TaskStatus.WAITING:
            return Response(
                status=404,
                data={'detail': 'This task is not waiting.'}
            )

        if request.data["response"] == "A":
            task.state = Task.TaskStatus.ASSIGNED
            task.save()
            return Response(
                status=200,
                data={'detail': 'Response sent.'}
            )

        if request.data["response"] == "R":
            task.state = Task.TaskStatus.PENDING
            task.assigned_benefactor = None
            task.save()
            return Response(
                status=200,
                data={'detail': 'Response sent.'}
            )


class DoneTask(APIView):
    pass
