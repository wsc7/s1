from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app1.models import Person


class Command(BaseCommand):
    help = 'Link existing users to persons by username/name matching'

    def handle(self, *args, **options):
        users = User.objects.all()
        linked_count = 0

        for user in users:
            # Try to find a person with the same name as the username
            try:
                person = Person.objects.get(name=user.username)
                if not hasattr(person, 'user'):
                    person.user = user
                    person.save()
                    linked_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully linked user {user.username} to person {person.name}'
                        )
                    )
            except Person.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'No person found for user {user.username}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error linking user {user.username}: {e}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully linked {linked_count} users to persons'
            )
        )