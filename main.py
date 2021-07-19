import json
import random
import time

import requests as req
from tqdm import tqdm

from config import headers, cookies, info_url, follower_url


class NetworkEncoder(json.JSONEncoder):
    def default(self, o) -> dict:
        if isinstance(o, User):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


class RelationShip:
    def __init__(self, subject, follower):
        self.subject = subject
        self.follower = follower

    def __str__(self):
        return f'({self.subject} -> {self.follower})'

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.subject, self.follower))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.subject == other.subject and self.follower == other.follower


class User:
    def __init__(self, uid, name, **kargs):
        self.uid = uid
        self.name = name
        for key, val in kargs.items():
            setattr(self, key, val)

    def get_posts(self):
        pass

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.uid == other.uid and self.name == other.name

    def __str__(self):
        return f"(id: {self.uid}, name: {self.name})"

    def __repr__(self):
        return str(self)

    @staticmethod
    def deserialize(data: dict):
        uid = data.pop('id')
        name = data.pop('screen_name')
        return User(uid, name, **data)


class Network:
    def __init__(self, relations: list[RelationShip], users: list[User]):
        self.relations = relations
        self.users = users

    def add_user(self, user: User):
        self.users.append(user)

    def remove_user(self, uid):
        self.remove_relation(uid)
        target = None
        for user in self.users[:]:
            if user.uid == uid:
                self.users.remove(user)
                target = user
                break
        return target

    def add_relation(self, relation: RelationShip):
        self.relations.append(relation)

    def remove_relation(self, uid):
        for relation in self.relations[:]:
            if relation.subject == uid or relation.follower == uid:
                self.relations.remove(relation)

    def merge(self, net):
        """
        merge a subnet to form a bigger network
        :param net: subnet
        """
        self.relations.extend(net.relations)
        self.users.extend(net.users)
        self.users = list(set(self.users))

    @property
    def size(self):
        return len(self.users)

    @property
    def edges(self):
        return len(self.relations)

    def __str__(self):
        rs = '\n'.join(map(str, self.relations))
        us = '\n'.join(map(str, self.users))
        repr = '{' + f'\nrelations:\n{rs},\nusers:\n{us}\n' + '}'
        return repr

    def __repr__(self):
        return str(self)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    def from_json(self, fp):
        return json.load(self, fp)


class Spider:
    def __init__(self):
        pass

    def start(self):
        pass


def get_user_info(uid):
    url = info_url.replace('{id}', str(uid))
    resp = req.get(url, headers=headers, cookies=cookies).json()
    assert resp.get('data') and resp['data'].get('user'), f'response of get {url}: {resp}'
    return resp['data']['user']


def get_page_followers(url, page_id=None):
    """get one page's user data, one page contains 20 users
    :param url:
    :param page_id:
    :return:
    """
    # print(f"page: {page_id}")
    time.sleep(random.random() * 4)
    resp = req.get(url,
                   headers=headers,
                   cookies=cookies,
                   params={
                       "page": page_id
                   },
                   proxies=None).json()

    assert resp['data'], f'response of {url}: {resp}'
    return resp['data']


def get_followers(url_tmplate: str, uid: int) -> list[User]:
    # print(f"{uid}'s followers:")
    users = []
    url = url_tmplate.replace('{id}', str(uid))
    page = 1
    while True:
        data = get_page_followers(url, page)
        # 无数据
        if not data['cards']:
            break
        page_user = [item['user'] for item in data['cards'][-1]['card_group']]
        users.extend(page_user)
        page += 1
    users = map(User.deserialize, users)
    return list(users)


def get_social_network(uid, depth=1, cur=0) -> Network:
    if cur >= depth:
        return

    # 只关注与根用户互相关注的好友圈
    def accept(people: User):
        return cur or people.follow_me

    users = list(filter(accept, get_followers(follower_url, uid)))
    relations = [RelationShip(uid, user.uid) for user in users]
    net = Network(relations, users)

    for user in tqdm(net.users[:]):
        out_net = get_social_network(user.uid, depth, cur + 1)
        if out_net:
            print(f'old net size: {net.size}')
            net.merge(out_net)
            print(f'new net size: {net.size}')
    return net


if __name__ == "__main__":
    # 由于api限制, 该方法获取的followers不超过200个
    net = get_social_network(6126303533, 2)
    print(f'net contains {net.size} people, {net.edges} relations')
    file = '6126303533-2.txt'
    with open(file, 'w') as fp:
        fp.write(net.to_json())
