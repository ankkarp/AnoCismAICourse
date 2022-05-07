import vk_requests
import random
import time
from tqdm import tqdm
import json
import os.path


class ParserVK:
    def __init__(self, token):
        self.api = vk_requests.create_api(service_token=token)
        self.groups = None
        # print(self.api.groups.search(q='цитатник', count=1))
        self.delay = [0.34, 0.44, 0.4, 0.43, 0.5]

    def parse_texts(self, *, q, count):
        try:
            self.groups = [{'name': g['name'], 'domain': g['screen_name']}
                           for g in self.api.groups.search(q=q, count=count)['items'] if g['is_closed'] == 0]
            try:
                print()
                for g in tqdm(self.groups):
                    g['textposts'] = []
                    offset = 0
                    while True:
                        posts = self.api.wall.get(domain=g['domain'], count=100, offset=offset)['items']
                        if posts:
                            offset += 100
                            time.sleep(random.choice(self.delay))
                            for p in posts:
                                if not p['marked_as_ads']:
                                    g['textposts'].append(p['text'].lower())
                        else:
                            break
                        # print('-', end='')
                os.system('cls')
            except Exception as e:
                print(e)
            path = f'{q}{count}.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.groups, f, ensure_ascii=False)
            return self.groups
        except KeyboardInterrupt:
            path = f'{q}{count}.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.groups, f, ensure_ascii=False)
            return self.groups

    def load_data(self, path):
        with open(path, 'r') as j:
            self.groups = json.loads(j.read())
        return self.groups

    def get_groups(self):
        return self.groups