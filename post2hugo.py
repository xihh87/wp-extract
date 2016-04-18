#!/usr/bin/python3
"""Script to extract the post from a wordpress webpage.
"""
import argparse
import bs4
from pprint import pprint
from bs4 import BeautifulSoup as bs

def unwanted_tags(tag):
    return tag.name in ['script', 'noscript', 'form', 'br'] or \
        ('class' in tag.attrs and
            [ x for x in tag.attrs['class']
                if x in ['wpcnt', 'jp-relatedposts']] ) or \
        ('id' in tag.attrs and
            tag.attrs['id'] in ['jp-post-flair'])

def get_content(tag):
    return tag.get('content')

def post_html(filename):
    return bs(open(filename), "html.parser")

def post_info(post, author=None):
    data = {
             'author': '',
             'tags': [],
             'categories': []
    }

    if author:
        data['author'] = author

    head = post.find('head')
    head_tags = head.findChildren()
    func = {
        'article:published_time': get_content,
        'og:title': get_content,
    }
    name = {
        'article:published_time': 'date',
        'og:title': 'title',
    }

    for tag in head_tags:
        prop = tag.get('property')
        if prop in func:
            data[name[prop]] = func[prop](tag)

    meta_types = {
        'Categorías ': 'categories',
        'Etiquetas ': 'tags',
    }

    meta = post.find_all('div', attrs = {'class': 'post-meta-data'})
    for tag in meta:
        content = tag.find('span')
        content.extract()
        name = meta_types[tag.text]
        data[name] = [t.text for t in content.find_all('a')]

    return data

def test_info():
    failed = False
    filename = './tests/index.html'
    author = 'Joshua Haase'
    post = post_html(filename)
    result = post_info(post, author)
    data = {
            'date': '2014-01-27T06:26:01+00:00',
            'author': 'Joshua Haase',
            'title': 'Redshift: contra el insomnio computacional',
            'tags': ["how-to", "manual"],
            'categories': ['Software Libre'],
    }
    for key in data:
        if key not in result:
            print("{} not in result".format(key))

        if not data[key] == result[key]:
            if not type(data[key]) == type(result[key]):
                print("Datatype differs: {}, {}". format(
                    type(data[key]), type(result[key])
                ))
            print("key in result «{}» differs from «{}»".format(
                    result[key], data[key] ))
            if  hasattr(data[key], '__iter__'):
                for i in range(len(data[key])):
                    if not data[key][i] == result[key][i]:
                        print("\t{} index differs in key {}: {},     {}".format(
                            i, key, data[key][i], result[key][i]
                            ))
    if not failed:
        print("TESTS OK")
    exit(0)

def print_post(post):
    content = post.find('div', attrs = {'class': 'post-content'})
    for tag in content.find_all(unwanted_tags):
        type(tag) == bs4.element.Tag and tag.decompose()

    content.attrs = {}
    content.name = 'body'
    if content.find('div'):
        content.find('div').decompose()

    for tag in content:
        tag.attrs = {}

    print(content)

def print_info(post_info):
    print('+++\ntitle = "{}"\ndate = "{}"\nauthor = "{}"\ntags = {}\ncategories = {}\n+++\n'.format(
        post_info['title'],
        post_info['date'],
        post_info['author'],
        post_info['tags'],
        post_info['categories'],
    ))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', help="What should we print.", choices=['post', 'info'])
    parser.add_argument('file', help='The filename containing the post.')
    parser.add_argument('--author', help='The name of the author.')
    args = parser.parse_args()

    if args.file == 'test':
        test_info()

    if args.author:
        author = args.author
    else:
        author = None

    post = post_html(args.file)

    if args.action == 'post':
        print_post(post)
    elif args.action == 'info':
        info = post_info(post, author)
        print_info(info)
