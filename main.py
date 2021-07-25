import json
import random
import time

import requests as req

from pprint import pprint
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

    def __lt__(self, other):
        return self.subject < other.subject \
               or (self.subject == other.subject and self.follower < other.follower)


class User:
    def __init__(self, uid, name, **kargs):
        self.uid = uid
        self.name = name
        for key, val in kargs.items():
            setattr(self, key, val)

    def get_posts(self):
        pass

    @staticmethod
    def construct_user(uid: int):
        resp = get_user_info(uid)
        name = resp.pop('screen_name')
        return User(uid, name, **resp)

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


# 只关注与根用户互相关注的好友圈
def accept(people: User, depth):
    return depth or people.follow_me
    # return True


class Network:
    logger = None

    def __init__(self, relations: list[RelationShip], users: list[User], name=None):
        self.relations = sorted(relations)
        self.users = {user.uid: user for user in users}
        self.name = name
        # 保存关系列表中相同subject的关系在列表中的最小索引
        self.head = dict()
        # 保存关系列表中相同subject的关系数目
        self.length = dict()
        self.construct_lookup()

    def construct_lookup(self):
        """根据关系列表构造head与length字典
        """
        for idx, r in enumerate(self.relations):
            _from = r.subject
            _to = r.follower
            item = self.head.setdefault(_from, idx)
            if item != idx:
                self.head[_from] = min(item, idx)
            item = self.length.setdefault(_from, 1)
            if item != 1:
                self.length[_from] += 1

    def get_user(self, uid):
        return self.users.get(uid)

    def add_user(self, user: User):
        self.users[user.uid] = user

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
        self.users.update(net.users)
        self.relations.extend(net.relations)
        self.relations.sort()

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    def from_json(self, fp):
        return json.load(self, fp)

    def dump(self, filename):
        with open(filename, 'w') as fp:
            fp.write(self.to_json())

    @staticmethod
    def construct(uid: int, max_depth=1, depth=0, callback=None):
        if depth >= max_depth:
            return
        # 获取当前uid所关注的用户列表
        users = list(filter(lambda x: accept(x, depth), get_followers(uid)))
        relations = [RelationShip(uid, user.uid) for user in users]
        net = Network(relations, users)
        container = net.users.keys() if depth else tqdm(net.users.keys())
        # 递归获取关注用户所关注的用户
        for id in container:
            out_net = Network.construct(id, max_depth, depth + 1)
            if out_net:
                net.merge(out_net)
            if callback:
                callback(net)
        # 将当前uid对应的用户加入社交网络
        current = User.construct_user(uid)
        net.add_user(current)
        return net

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


class Spider:
    def __init__(self):
        pass

    def start(self):
        pass


def get_user_info(uid) -> dict:
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
    resp = req.get(url,
                   headers=headers,
                   cookies=cookies,
                   params={
                       "page": page_id
                   },
                   proxies=None).json()

    assert resp.get('data'), f'response of {url}: {resp}'
    return resp['data']


def get_followers(uid: int) -> list[User]:
    time.sleep(random.random() * 7)
    # print(f"{uid}'s followers:")
    users = []
    url = follower_url.replace('{id}', str(uid))
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


def get_logger():
    pass


if __name__ == "__main__":
    # 由于api限制, 该方法获取的followers不超过200个
    uid = 6126303533
    net = Network.construct(uid, max_depth=1)
    print(f'net contains {net.size} people, {net.edges} relations')
    # pprint(net.relations)
    net.dump(f'{uid}.txt')
