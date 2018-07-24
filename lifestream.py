
def get_status_tv_users_utm(): ...


def get_status_tv_users_lifestream(): ...


def find_change_status_to_lifestream(): ...


def apply_change_status_lifestream(): ...


def main():
    utm_status_users = get_status_tv_users_utm()
    lifestream_status_user = get_status_tv_users_lifestream()
    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_user
    )
    apply_change_status_lifestream(status_change)


if __name__ == '__main__':
    main()
