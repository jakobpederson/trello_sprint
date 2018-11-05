from unittest import TestCase
import datetime

from build import build_board, add_lists, add_meta_cards, TEAM


class BuildTests(TestCase):

    def setUp(self):
        self.board = build_board(TrelloClient(), 3)

    def test_board_is_named_correctly(self):
        today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        expected = 'Sprint 3 - {}'.format(today)
        self.assertEqual(self.board.name, expected)

    def test_lists_are_added(self):
        add_lists(self.board)
        self.assertEqual([x.name for x in self.board.open_lists()], ['Backlog', 'In Progress', 'Done', 'Meta'])

    def test_randomly_selected_pr_person_and_webhelp_are_added_as_cards(self):
        result = add_meta_cards(TrelloList('Meta'))
        cards = [x.name.replace(' ', '').split(':')[1] for x in result.list_cards()]
        self.assertEqual(len(cards), 2)
        self.assertTrue(cards[0] in TEAM)
        self.assertTrue(cards[1] in TEAM)
        self.assertTrue(cards[0] != cards[1])


class TrelloList():

    def __init__(self, name):
        self.name = name
        self.cards = []

    def add_card(self, name):
        card = TrelloCard(name)
        self.cards.append(card)
        return card

    def list_cards(self):
        return self.cards


class TrelloCard():

    def __init__(self, name):
        self.name = name


class TrelloClient():

    def __init__(self):
        self.name = 'client'
        self.boards = []

    def add_board(self, name, organization_id=None):
        board = TrelloBoard(name, organization_id=organization_id)
        self.boards.append(board)
        return board

    def list_boards(self):
        return self.boards


class TrelloBoard():

    def __init__(self, name, organization_id=None):
        self.name = name
        self.organization_id = organization_id
        self.trello_lists = []
        self.closed = False

    def add_list(self, name):
        trello_list = TrelloList(name)
        self.trello_lists.append(trello_list)
        return trello_list

    def open_lists(self):
        return self.trello_lists

    def close(self):
        self.closed = True
