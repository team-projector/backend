from rest_framework import status

from apps.payroll.utils.metrics.user import User
from tests.base import BaseAPITest
from tests.test_payroll.factories import WorkBreakFactory


class WorkBreaksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(login='user')

    def get_data(self):
        return {
            "reason": "dayoff",
            "comment": "Comment text",
            "from_date": "2019-04-27T17:33:26+03:00",
            "user": self.user.id,
            "to_date": "2019-04-27T17:33:26+03:00"
        }

    def get_update_data(self):
        return {
            "reason": "vacation",
            "comment": "Comment text",
            "from_date": "2019-04-27T17:33:26+03:00",
            "user": self.user.id,
            "to_date": "2019-04-27T17:33:26+03:00"
        }

    def test_retrieve(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_not_exists(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/work-breaks/{work_break.id + 1}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        data = self.get_data()

        self.set_credentials()
        response = self.client.post('/api/work-breaks', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approve_state'], 'created')

    def test_update(self):
        work_break = WorkBreakFactory.create(user=self.user)
        update_data = self.get_update_data()

        self.set_credentials()

        response = self.client.put(f'/api/work-breaks/{work_break.id}', update_data)

        self.assertEqual(response.data['reason'], update_data['reason'])

    def test_delete(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()

        response = self.client.delete(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
