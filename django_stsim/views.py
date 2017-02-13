from django.shortcuts import render

from stsimpy import STSimConsole
import json
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, GenericAPIView 
from rest_framework.response import Response
from rest_framework.decorators import detail_route
# Create your views here.

from django_stsim.models import Library, Project, Scenario
from django_stsim.serializers import LibrarySerializer, ProjectSerializer, ScenarioSerializer


class LibraryViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer


class ProjectViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ScenarioViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    @detail_route(methods=['get'])
    def project(self, *args, **kwargs):
        return Response({'pid':self.get_object().project.pid})

