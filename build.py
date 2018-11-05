import datetime
from trello import TrelloClient
from argparse import ArgumentParser
import random

TEAM = ['caleb', 'jake', 'matt', 'kyle', 'taylor', 'braxton', 'jessica', 'mike']


def build_board(client, number, organization_id=None):
    today = datetime.datetime.now().date()
    name = 'Sprint {} - {}'.format(number, today.strftime('%Y-%m-%d'))
    board = client.add_board(name, organization_id=organization_id)
    return board


def purge_lists(board):
    for trello_list in board.open_lists():
        trello_list.close()
    return board


def add_lists(board):
    trello_lists = ['Meta', 'Done', 'In Progress', 'Backlog']
    for trello_list in trello_lists:
        board.add_list(trello_list)
    return board

def add_members():
    # TODO
    pass


def add_meta_cards(trello_list):
    team = list(TEAM)
    prs = random.choice(team)
    team.remove(prs)
    trello_list.add_card('PRs: {}'.format(prs))
    web_help = random.choice(team)
    trello_list.add_card('WebHelp: {}'.format(web_help))
    return trello_list


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--token', required=True)
    parser.add_argument('--organization_id', required=True)
    args = parser.parse_args()

    client = TrelloClient(api_key=args.api_key, token=args.token)
    organization = client.get_organization(args.organization_id)
    count = len(organization.get_boards('open')) + 1
    board = build_board(client, count, organization_id=args.organization_id)
    board = purge_lists(board)
    board = add_lists(board)
    meta = [x for x in board.open_lists() if x.name.lower() == 'meta'][0]
    add_meta_cards(meta)
