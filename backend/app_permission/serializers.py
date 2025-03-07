from django.contrib.auth.models import Group

from app_permission.models import ModuleConfiguration
from app_system.models import CustomUser
from python_files.techno_generic import TechnoListSerializer, TechnoSelectSerializer, TechnoModelSerializer


class ModuleConfigSerializer(TechnoListSerializer):
    class Meta:
        model = ModuleConfiguration
        fields = ['name', 'module_type']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = data.pop('rec_id')
        data['label'] = data.pop('name')
        data['children'] = ModuleConfigSerializer(instance.children.all(), many=True).data
        return data


class CustomUserSelectSerializer(TechnoSelectSerializer):
    class Meta:
        model = CustomUser
        fields = []


class GroupWithUsersSelectSerializer(TechnoSelectSerializer):
    class Meta:
        model = Group
        fields = ['user_set']


class ModuleConfigurationSerializer(TechnoModelSerializer):
    class Meta:
        model = ModuleConfiguration
        fields = ['name', 'codename', 'menu_type', 'is_root_menu',
                  'is_global_menu', 'page_url', 'sequence', 'react_box_icon',
                  'permissions', 'children']
