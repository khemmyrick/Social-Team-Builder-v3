import json
from os import environ
from os import path
import sys

import django


BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

PROJ_DIR = path.dirname(BASE_DIR)

sys.path.insert(0, PROJ_DIR)


def load_data():
    # Load models?
    from accounts.models import User
    from projects.models import Project, Position, Skill

    # Load User Serializer.
    try:
        from accounts.serializers import UserSerializer
    except ImportError:
        raise ImportError(
            'serializers.py must contain a properly '
            'implemented UserSerializer class for this import to work.'
        )

    filepath = path.join(PROJ_DIR, 'assets', 'user_details.json')

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        itera = 1
        for item in data:
            print(str(itera) + ': ' + item['display_name'])
            itera += 1

        serializer = UserSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Users loaded.')
        else:
            print(serializer.errors)
            print('load_data unsuccessful.')
        # Users generated. Passwords unhashed.
        # Has passwords before moving on.
        usernames = []
        for item in data:
            usernames.append(item['username'])
        all_users = User.objects.all()
        for user in all_users:
            if user.username in usernames:
                user.set_password(user.password)
                user.save()

    # Load Skill Serializer.
    try:
        from projects.serializers import SkillSerializer
    except ImportError:
        raise ImportError(
            'serializers.py must contain a properly '
            'implemented SkillSerializer class for this import to work.'
        )

    filepath = path.join(PROJ_DIR, 'assets', 'skills.json')

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        itera = 1
        for item in data:
            print(str(itera) + ': ' + item['name'])
            itera += 1

        serializer = SkillSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Skills loaded.')
        else:
            print(serializer.errors)
            print('load_data unsuccessful.')

    # Add skills to users.
    connie = User.objects.get(username="ConnieRolek")
    print("Arming Connie.")
    connie.save()
    djangoskill = Skill.objects.get(name="Django")
    pyskill = Skill.objects.get(name="Python")
    htmlskill = Skill.objects.get(name="HTML")
    cssskill = Skill.objects.get(name="CSS")
    javaskill = Skill.objects.get(name="JavaScript")
    connie.skills.add(djangoskill, pyskill, htmlskill, cssskill, javaskill)
    connie.save()

    perry = User.objects.get(username="PerryKinder")
    print("Arming Perry.")
    perry.save()
    sqlskill = Skill.objects.get(name="SQL")
    perry.skills.add(djangoskill, pyskill, sqlskill)
    perry.save()

    garnet = User.objects.get(username="GarnetDarling")
    print("Arming Garnet.")
    cpp = Skill.objects.get(name="C++")
    java = Skill.objects.get(name="Java")
    xcode = Skill.objects.get(name="Xcode")
    obj_c = Skill.objects.get(name="Objective-C")
    garnet.skills.add(cpp, java, xcode, obj_c)
    garnet.save()

    amy = User.objects.get(username="AmyDietz")
    print("Arming Amy")
    amy.save()
    jqskill = Skill.objects.get(name="jQuery")
    amy.skills.add(jqskill, htmlskill, xcode, sqlskill)
    amy.save()

    bob = User.objects.get(username="RobertLazuli")
    print("Arming Bob")
    bob.save()
    flaskskill = Skill.objects.get(name="Flask")
    phpskill = Skill.objects.get(name="PHP")
    bob.skills.add(phpskill, flaskskill, pyskill, sqlskill)
    bob.save()

    # Load Project Serializer.
    try:
        from projects.serializers import ProjectSerializer
    except ImportError:
        raise ImportError(
            'serializers.py must contain a properly '
            'implemented ProjectSerializer class for this import to work.'
        )

    filepath = path.join(PROJ_DIR, 'assets', 'project_details.json')

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        itera = 1
        for item in data:
            print(str(itera) + ': ' + item['name'])
            item['creator'] = User.objects.get(
                username=item['creator']
            ).id
            print('Created by {}.'.format(
                User.objects.get(
                    id=item['creator']
                ).display_name)
            )
            itera += 1

        serializer = ProjectSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Projects loaded.')
        else:
            print(serializer.errors)
            print('load_data unsuccessful.')

    # Load Position Serializer.
    try:
        from projects.serializers import PositionSerializer
    except ImportError:
        raise ImportError(
            'serializers.py must contain a properly '
            'implemented PositionSerializer class for this import to work.'
        )

    filepath = path.join(PROJ_DIR, 'assets', 'position_details.json')

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        itera = 1
        for item in data:
            print(str(itera) + ': ' + item['name'])

            if item['filled'] == 'True':
                item['filled'] = True
            else:
                item['filled'] = False
            item['project'] = Project.objects.get(
                name=item['project']
            ).id

            itera += 1

        serializer = PositionSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Positions loaded.')
        else:
            print(serializer.errors)
            print('load_data unsuccessful.')

    # Add skills/users to positions.
    fsds = Position.objects.filter(
        project__name="Socializer"
    ).get(
        name="Full Stack Django Specialist"
    )
    print("Getting Socializer's Full Stack Django Specialist.")
    fsds.save()
    fsds.skills.add(djangoskill, pyskill, htmlskill, cssskill, javaskill)
    fsds.user = connie
    fsds.save()
    beds = Position.objects.get(name="Backend Django Specialist")
    print("Getting Backend Django Specialist.")
    beds.save()
    beds.skills.add(djangoskill, pyskill, sqlskill)
    beds.user = perry
    beds.save()
    feds = Position.objects.get(name="Frontend Django Specialist")
    print("Getting Front End Django Specialist.")
    feds.save()
    feds.skills.add(htmlskill, cssskill, javaskill)

    # Load Applicant Serializer.
    try:
        from projects.serializers import ApplicantSerializer
    except ImportError:
        raise ImportError(
            'serializers.py must contain a properly '
            'implemented ApplicantSerializer class for this import to work.'
        )

    filepath = path.join(PROJ_DIR, 'assets', 'applicant_details.json')

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        itera = 1
        for item in data:
            print(str(itera) + ' Applicant: ' + item['user'])
            item['user'] = User.objects.get(
                username=item['user']
            ).id
            item['position'] = Position.objects.get(
                name=item['position']
            ).id
            # if item['status'] == 'True':
            #    item['status'] = True
            # else:
            #    item['status'] = False
            itera += 1

        serializer = ApplicantSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Applicants loaded.')
            print("""
!@#$%^&*()_+_)(*&^%$#@!
!!!!!!!!!!!!!!!!!!ALL DATA SHOULD BE LOADED SUCCESSFULLY!!!!!!!!!!!!!!!!!!!!!!
!@#$%^&*()_+_)(*&^%$#@!
""")
        else:
            print(serializer.errors)
            print('load_data unsuccessful.')


if __name__ == '__main__':
    # sys.path.append(PROJ_DIR) ##### MIGHT HAVE TO KEEP THIS FOR DJANGO 2+
    environ.setdefault("DJANGO_SETTINGS_MODULE", "circle.settings")
    django.setup()
    load_data()
