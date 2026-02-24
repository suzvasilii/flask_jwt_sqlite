import operator as op

def filter_posts(author, title, posts):
    filtered = [post for post in posts if (op.contains(post.title, title) and op.contains(post.user.email, author))]
    return filtered

def filter_my_posts(title, posts):
    filtered = [post for post in posts if op.contains(post.title, title)]
    return filtered