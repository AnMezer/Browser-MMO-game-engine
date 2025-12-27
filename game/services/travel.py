from users.models import CustomUser
from game.constants import SECONDS_PER_UNIT_DISTANCE
from game.models import GlobalLocation, SubLocation


def calculate_travel_time(user: CustomUser,
                          target_global_location: GlobalLocation,
                          target_sublocation: SubLocation) -> int:
    if (user.current_global_location is None or
            user.current_sublocation is None):
        return 0
    else:
        if user.current_global_location == target_global_location:
            travel_time = abs(user.current_sublocation.distance_to_location_start - target_sublocation.distance_to_location_start)
        else:
            travel_time = user.current_sublocation.distance_to_location_start + abs(user.current_global_location.distance_to_the_city - target_global_location.distance_to_the_city) + target_sublocation.distance_to_location_start
    return travel_time * SECONDS_PER_UNIT_DISTANCE
