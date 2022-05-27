

import re


__LINK_USER_TO_MANAGER = dict()

def link_user_with_manager(userId: int, managerId: int):
    __LINK_USER_TO_MANAGER.update({userId: managerId})


def check_user_to_manager(userId: int, managerId: int) -> bool:
    if __LINK_USER_TO_MANAGER.get(userId) == None:
        link_user_with_manager(userId, managerId)
    
    return __LINK_USER_TO_MANAGER.get(userId) == managerId

def stop_link(userId: int):
    __LINK_USER_TO_MANAGER.pop(userId)

def stop_by_manager_id(managerId: int):
    for key, val in __LINK_USER_TO_MANAGER.items():
        if val == managerId:
            __LINK_USER_TO_MANAGER.pop(key)

