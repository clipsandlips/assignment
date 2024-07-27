#from fastapi import Depends, HTTPException, status
#from backend.src.util.models import user as model_user
#from backend.src.config.security import get_current_active_user

#async def get_current_admin(current_user: model_user.User = Depends(get_current_active_user)):
#    print('current_user.role : {}'.format(current_user.role))
#    if await current_user.role != "admin":
#        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
#    return current_user

#async def get_current_moderator(current_user: model_user.User = Depends(get_current_active_user)):
#    print('current_user.role : {}'.format(current_user.role))
#    if await current_user.role not in ["admin", "moderator"]:
#        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
#    return current_user


from fastapi import Depends, HTTPException, status
from backend.src.util.models import user as model_user
from backend.src.config.security import get_current_active_user
from functools import wraps, update_wrapper
from typing import Callable

def role_required(*roles: str):
    def decorator(func: Callable):
        async def wrapper(*args, current_user: model_user.User = Depends(get_current_active_user), **kwargs):
            print(f'role_require: current_user.role: {current_user.role}')
            if current_user.role not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator