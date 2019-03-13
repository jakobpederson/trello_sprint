import datetime
import os
import requests
from trello import TrelloClient, exceptions
from argparse import ArgumentParser
import random

import settings


def add_board(client, board_name, organization_id):
    post_args = {
        'name': board_name,
        'prefs_cardCovers': False,
        'idOrganization': organization_id,
        'defaultLists': False
    }
    response = client.fetch_json('/boards', http_method='POST', post_args=post_args,)
    board = client.get_board(response['id'])
    return board


def build_board(client, number, organization_id=None):
    name = 'Sprint {}'.format(number)
    board = add_board(client, name, organization_id)
    labels = client.get_board('NWjn990R').get_labels()
    for label in labels:
        board.add_label(label.name, label.color)
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
            print('{}: cannot add {}'.format(e, member.full_name))
    return 'success'


def do_meta_cards(board, jobs=None):
    meta_list = [x for x in board.open_lists() if x.name.lower() == 'meta'][0]
    job_types = ['PRs', 'WebHelp', 'Retro']
    for job in job_types:
        card = meta_list.add_card('{}: '.format(job))
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
    board = add_lists(board)
    meta = [x for x in board.open_lists() if x.name.lower() == 'meta'][0]
    print(add_members(organization, board))
    do_meta_cards(board)
