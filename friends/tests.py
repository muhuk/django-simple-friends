from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from friends.models import FriendshipRequest, Friendship, UserBlocks
from friends.templatetags import friends_tags


class BaseTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        for i in range(1, 5):
            setattr(self, 'user%d' % i,
                                  User.objects.get(username='testuser%d' % i))


class BlocksFilterTestCase(BaseTestCase):
    def test_blocks_filter(self):
        result = friends_tags.blocks(self.user4)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('applied' in result)
        self.assertEqual(len(result['applied']), 2)
        self.assertTrue(self.user1 in result['applied'])
        self.assertTrue(self.user3 in result['applied'])
        self.assertTrue('received' in result)
        self.assertEqual(len(result['received']), 2)
        self.assertTrue(self.user1 in result['received'])
        self.assertTrue(self.user2 in result['received'])


class FriendsFilterTestCase(BaseTestCase):
    def test_friends_filter(self):
        result = friends_tags.friends_(self.user1)
        self.assertEqual(len(result), 1)
        self.assertTrue(self.user2 in result)


class FriendshipModelsTestCase(BaseTestCase):
    def test_friendship_request(self):
        are_friends = Friendship.objects.are_friends
        for method, result in [('decline', False),
                               ('cancel', False),
                               ('accept', True)]:
            friendship_request = FriendshipRequest.objects.create(
                                     from_user=self.user3, to_user=self.user4)
            self.assertEqual(are_friends(self.user3, self.user4), False)
            getattr(friendship_request, method)()
            self.assertEqual(are_friends(self.user3, self.user4), result)

    def test_friendship_manager_query_methods(self):
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user2), True)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), False)
        self.assertEqual(Friendship.objects.are_friends(self.user2,
                                                        self.user3), False)
        friends_of_user1 = Friendship.objects.friends_of(self.user1)
        friends_of_user2 = Friendship.objects.friends_of(self.user2)
        friends_of_user3 = Friendship.objects.friends_of(self.user3)
        self.assertEqual(list(friends_of_user1), [self.user2])
        self.assertEqual(list(friends_of_user2), [self.user1])
        self.assertEqual(list(friends_of_user3), [])

    def test_friendship_manager_befriend(self):
        Friendship.objects.befriend(self.user1, self.user4)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user4), True)

    def test_friendship_manager_unfriend(self):
        Friendship.objects.unfriend(self.user1, self.user2)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user2), False)


class FriendshipRequestsFilterTestCase(BaseTestCase):
    def test_friendship_requests_filter(self):
        FriendshipRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        FriendshipRequest.objects.create(from_user=self.user4,
                                         to_user=self.user1)
        result = friends_tags.friendship_requests(self.user1)
        # result['sent'] shouldn't contain user2 because they're already friends_
        # result = {
        #     'sent': [user3],
        #     'received': [user4],
        # }
        raise AssertionError


class FriendshipViewsTestCase(BaseTestCase):
    urls = 'friends.urls'

    def test_friendship_request(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('friendship_request', args=('testuser3',)))
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), False)
        self.assertEqual(FriendshipRequest.objects.filter(from_user=self.user1,
                               to_user=self.user3, accepted=False).count(), 1)

    def test_friendship_accept(self):
        FriendshipRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        self.client.login(username='testuser3', password='testuser3')
        self.client.get(reverse('friendship_accept', args=('testuser1',)))
        self.assertEqual(FriendshipRequest.objects.filter(
                                                   accepted=True).count(), 2)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), True)

    def test_friendship_cancel(self):
        FriendshipRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('friendship_cancel', args=('testuser3',)))
        self.assertEqual(FriendshipRequest.objects.filter(
                                                   accepted=False).count(), 0)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), False)

    def test_friendship_decline(self):
        FriendshipRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        self.client.login(username='testuser3', password='testuser3')
        self.client.get(reverse('friendship_decline', args=('testuser1',)))
        self.assertEqual(FriendshipRequest.objects.filter(
                                                   accepted=False).count(), 0)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), False)

    def test_friendship_delete(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('friendship_delete', args=('testuser2',)))
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user2), False)

    def test_friendship_mutual_request(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('friendship_request', args=('testuser3',)))
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), False)
        self.client.login(username='testuser3', password='testuser3')
        self.client.get(reverse('friendship_request', args=('testuser1',)))
        self.assertEqual(FriendshipRequest.objects.filter(from_user=self.user1,
                                to_user=self.user3, accepted=True).count(), 1)
        self.assertEqual(Friendship.objects.are_friends(self.user1,
                                                        self.user3), True)


class UserBlockTestCase(BaseTestCase):
    def test_blocking_info_methods(self):
        self.user1.user_blocks.blocks.add(self.user3, self.user4)
        self.assertEqual(self.user1.user_blocks.block_count(), 2)
        summary = UserBlocks.objects.get(user=self.user1).block_summary()
        self.assertEqual(self.user3.username in summary, True)
        self.assertEqual(self.user4.username in summary, True)


class UserBlocksViewsTestCase(BaseTestCase):
    urls = 'friends.urls'

    def test_block(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('user_block', args=('testuser2',)))
        self.assertEqual(self.user2 in self.user1.user_blocks.blocks.all(),
                                                                         True)

    def test_unblock(self):
        self.user1.user_blocks.blocks.add(self.user2)
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('user_unblock', args=('testuser2',)))
        self.assertEqual(self.user2 in self.user1.user_blocks.blocks.all(),
                                                                        False)
