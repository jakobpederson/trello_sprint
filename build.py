import datetime
import os
import requests
from trello import TrelloClient, exceptions
from argparse import ArgumentParser
import random

import settings


def add_board(client, board_name, organization_id):
    post_args = {'name': board_name, 'prefs_cardCovers': False, 'idOrganization': organization_id}
    response = client.fetch_json('/boards', http_method='POST', post_args=post_args,)
    board = client.get_board(response['id'])
    return board


def build_board(client, number, organization_id=None):
    name = 'Sprint {}'.format(number)
    board = add_board(client, name, organization_id)
    return board


def purge_lists(board):
    for trello_list in board.open_lists():
        trello_list.close()
    return board


def add_lists(board):
    trello_lists = ['Later', 'Meta', 'Done', 'In Progress', 'Backlog']
    for trello_list in trello_lists:
        board.add_list(trello_list)
    return board

def add_members(organization, board):
    members = organization.get_members()
    for member in members:
        try:
            if member.full_name not in settings.EXCLUDE:
                board.add_member(member)
        except exceptions.ResourceUnavailable as e:
            print('exception: cannot add {}'.format(member.full_name))
    return 'success'



def get_viable_candidates(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
    data_list = [x for x in data.split(',') if x and x != '\n']
    if data_list:
        return data_list
    return settings.TEAM


def add_meta_cards(job, trello_list, previous=None):
    path = os.path.abspath(settings.META_JOBS[job])
    available_candidates = get_viable_candidates(settings.META_JOBS[job])
    selected = random.choice(available_candidates)
    n = 0
    while selected == previous and n < 2:
        selected = random.choice(available_candidates)
        n = n + 1
    if selected in available_candidates:
        available_candidates.remove(selected)
    update_file(settings.META_JOBS[job], available_candidates)
    card = trello_list.add_card('{}: '.format(job))
    return card


def do_meta_cards(board, jobs=None):
    cards = []
    previous = None
    meta_list = [x for x in board.open_lists() if x.name.lower() == 'meta'][0]
    job_types = jobs if jobs else settings.META_JOBS
    for key, item in job_types.items():
        selected = add_meta_cards(key, meta_list, previous)
        cards.append(selected)
        previous = selected.name.lower().replace(' ', '').split(':')[1]
    result = [x.name.replace(' ', '').split(':')[1] for x in cards]
    return result


def update_file(file_path, updated):
    with open(file_path, 'w') as f:
        for name in updated:
            f.write(name)
            f.write(',')
    return None


def get_number_of_sprint_boards(organization):
    return len([x for x in organization.get_boards('open') if x.name.lower().startswith('sprint ')])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--number', required=False)
    args = parser.parse_args()

    client = TrelloClient(api_key=settings.API_KEY, token=settings.TOKEN)
    organization = client.get_organization(settings.ORGANIZATION_ID)
    number_of_boards = get_number_of_sprint_boards(organization)
    count = args.number if args.number else number_of_boards
    board = build_board(client, count, organization_id=settings.ORGANIZATION_ID)
    board = purge_lists(board)
    board = add_lists(board)
    meta = [x for x in board.open_lists() if x.name.lower() == 'meta'][0]
    do_meta_cards(board)
    print(add_members(organization, board))
