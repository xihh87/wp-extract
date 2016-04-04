#!/usr/bin/python3
"""Script to extract the post from a wordpress webpage.
"""
import argparse
import bs4
from bs4 import BeautifulSoup as bs

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='+', help='The filename containing the post.')
    return parser.parse_args()

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

def post_info(post):
    data = { 'author': 'Joshua Haase',
             'tags': [],
             'categories': []
    }

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

if __name__ == '__main__':
    args = parse_args()

    from pprint import pprint

    if args.file == ['test']:
        args.file = ['/home/joshpar/src/webdev/libertas87.wordpress.com/2014/01/27/redshift-contra-el-insomnio-computacional/index.html']
        for filename in args.file:
            post = post_html(filename)
            result = post_info(post)
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

    for fname in args.file:
        post = post_html(fname)
        result = post_info(post)
        pprint(result)
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
