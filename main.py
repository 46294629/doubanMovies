from get_movies import get_seen_movies
from insert_mysql import handle_records

if __name__ == '__main__':
    get_seen_movies()
    handle_records()