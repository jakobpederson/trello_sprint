from unittest import TestCase
import logging
import logging.config
import mock
import os
import datetime
from trello import TrelloClient

from build import build_board, add_lists, add_meta_cards, TEAM, get_viable_candidates, update_file, purge_lists, do_meta_cards, add_members, get_number_of_sprint_boards
from test import test_settings




class BuildTests(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.config.dictConfig({
            "version": 1,
            "loggers": {
                "urllib3.connectionpool": {
                    "level": "ERROR",
                },
                "requests_oauthlib.oauth1_auth": {
                    "level": "ERROR",
                },
                "oauthlib.oauth1.rfc5849": {
                    "level": "ERROR",
                }
            }
        })

    @mock.patch('trello.TrelloClient.add_board')
    def setUp(self, board):
        self.trello_client = TrelloClient(test_settings.API_KEY, test_settings.TOKEN)
        self.organization = self.trello_client.get_organization(test_settings.ORGANIZATION_ID)
        test_board = self.trello_client.get_board(test_settings.TEST_BOARD_ID)
        board.return_value = test_board
        self.board = build_board(self.trello_client, 'test_board_1')
        self.assertEqual('test_board_1', self.board.name)

    def tearDown(self):
        purge_lists(self.board)
        for member in self.board.normal_members():
            self.board.remove_member(member)

    def test_lists_are_added(self):
        add_lists(self.board)
        self.assertEqual([x.name for x in self.board.open_lists()], ['Backlog', 'In Progress', 'Done', 'Meta', 'Later'])

    def test_randomly_selected_pr_person_and_webhelp_are_added_as_cards(self):
        add_lists(self.board)
        meta_list = [x for x in self.board.open_lists() if x.name.lower() == 'meta'][0]
        result = add_meta_cards(meta_list)
        cards = [x.name.replace(' ', '').split(':')[1] for x in result.list_cards()]
        self.assertEqual(len(cards), 2)
        self.assertTrue(cards[0] in TEAM)
        self.assertTrue(cards[1] in TEAM)
        self.assertTrue(cards[0] != cards[1])

    @mock.patch('build.get_viable_candidates')
    def test_same_person_cannot_be_selected_for_both_cards(self, candidate):
        expected = ['jake', 'caleb']
        candidate.return_value = list(expected)
        add_lists(self.board)
        result = do_meta_cards(self.board)
        self.assertCountEqual(expected, result)
        self.assertTrue(result[1] != result[0])

    def test_add_members_to_board(self):
        add_members(self.organization, self.board)
        result = [x.full_name for x in self.board.normal_members()]
        expected = ['Worker 1', 'Worker 2', 'Worker 3', 'Worker 4', 'Worker 5', 'jp']
        self.assertCountEqual(expected, result)

    def test_get_number_of_sprint_boards(self):
        number_of_boards = get_number_of_sprint_boards(self.organization)
        self.assertEqual(1, number_of_boards)

    def test_get_viable_candidates_from_file(self):
        pull_requests = os.path.abspath('assignments/test.txt')
        with open(pull_requests, 'w') as f:
            for i in ['jake','braxton']:
                f.write(i)
                f.write(',')
        expected = ['jake','braxton']
        result = get_viable_candidates(pull_requests)
        self.assertCountEqual(result, expected)

    def test_update_candidate_list(self):
        pull_requests = os.path.abspath('assignments/test.txt')
        with open(pull_requests, 'w') as f:
            for i in ['jake','braxton']:
                f.write(i)
                f.write(',')
        name = ['jessica', 'jake','braxton']
        update_file(pull_requests, name)
        with open(pull_requests, 'r') as f:
            data = f.read()
        result = [x for x in data.split(',') if x != '\n' and x]
        expected = ['jake', 'braxton', 'jessica']
        self.assertCountEqual(result, expected)

    def test_resets_file_if_all_candidates_have_been_listed(self):
        pull_requests = os.path.abspath('assignments/test.txt')
        open(pull_requests, 'w').close()
        get_viable_candidates(pull_requests)
        add_lists(self.board)
        do_meta_cards(self.board, jobs=test_settings.META_JOBS)
        with open(pull_requests, 'r') as f:
            data = f.read()
        result = [x for x in data.split(',') if x != '\n' and x]
        expected = test_settings.TEAM
        self.assertCountEqual(result, expected)
