import random
from collections import Counter
from django.utils import timezone
from django.conf import settings
from .models import GameRound, GameSettings


def generate_random_dice_values():
    """Generate six random dice values and determine the winning number."""
    dice_values = [random.randint(1, 6) for _ in range(6)]
    winning_number = determine_winning_number(dice_values)
    return dice_values, winning_number


def determine_winning_number(dice_values):
    """
    Determine the winning number for display.
    Rule: A number must appear at least 2 times to win.
    If multiple numbers win, only 1 is returned for display.
    """
    if not dice_values:
        return None
    
    counts = Counter(dice_values)
    # Find numbers that appeared 2 or more times
    winners = [num for num, count in counts.items() if count >= 2]
    
    if not winners:
        return None
        
    # Find the maximum frequency among winners
    max_freq = max(counts[num] for num in winners)
    
    # Get all numbers that have this maximum frequency
    top_winners = [num for num in winners if counts[num] == max_freq]
    
    # If there's a tie, pick only one. 
    # Since "there is no highest number rule", we'll just pick the first one 
    # that appeared in the original dice roll for consistency.
    for val in dice_values:
        if val in top_winners:
            return str(val)
            
    return str(top_winners[0])


def apply_dice_values_to_round(round_obj, dice_values):
    """Persist six dice values onto the GameRound instance and recalculate dice_result."""
    if len(dice_values) != 6:
        raise ValueError('dice_values must contain 6 entries')
    for index, value in enumerate(dice_values, start=1):
        setattr(round_obj, f'dice_{index}', value)
    # Always recalculate dice_result from the actual dice values
    round_obj.dice_result = determine_winning_number(dice_values)


def extract_dice_values(round_obj, round_data=None, fallback=None):
    """Return dice values from the round object or cached round data."""
    values = []
    for index in range(1, 7):
        value = getattr(round_obj, f'dice_{index}', None)
        if value is None and round_data:
            value = round_data.get(f'dice_{index}')
        if value is None:
            value = fallback
        values.append(value)
    return values


def sync_round_to_redis(round_obj, redis_client):
    """
    Sync a GameRound object from database to Redis.
    Calculates timer based on elapsed time since round start.
    """
    if not redis_client or not round_obj:
        return False
    
    try:
        # Get dynamic round_end_time from settings
        round_end_time = get_game_setting('ROUND_END_TIME', 80)
        
        # Calculate timer based on elapsed time (1-round_end_time, not 0-(round_end_time-1))
        elapsed = (timezone.now() - round_obj.start_time).total_seconds()
        timer_raw = int(elapsed) % round_end_time
        timer = round_end_time if timer_raw == 0 else timer_raw  # Show 1-round_end_time instead of 0-(round_end_time-1)
        
        # Build round data dict
        round_data = {
            'round_id': round_obj.round_id,
            'status': round_obj.status,
            'start_time': round_obj.start_time.isoformat(),
            'timer': timer,
        }
        
        # Add dice result if available
        if round_obj.dice_result:
            round_data['dice_result'] = round_obj.dice_result
        
        # Add individual dice values
        dice_values = extract_dice_values(round_obj)
        for i, value in enumerate(dice_values, start=1):
            if value is not None:
                round_data[f'dice_{i}'] = value
        
        # Update Redis using pipeline for efficient batch writes
        import json
        pipe = redis_client.pipeline()
        pipe.set('current_round', json.dumps(round_data))
        pipe.set('round_timer', str(timer))
        pipe.execute()  # Execute both writes in one round trip
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error syncing round to Redis: {e}")
        return False


def sync_database_to_redis(redis_client):
    """
    Sync the current active round from database to Redis.
    Returns True if successful, False otherwise.
    """
    if not redis_client:
        return False
    
    try:
        # Get current active round from database
        round_obj = GameRound.objects.filter(
            status__in=['BETTING', 'CLOSED', 'RESULT']
        ).order_by('-start_time').first()
        
        if not round_obj:
            # No active round - check if we should create one
            latest_round = GameRound.objects.order_by('-start_time').first()
            if latest_round and latest_round.status == 'COMPLETED':
                # All rounds completed, create new one
                round_obj = GameRound.objects.create(
                    round_id=f"R{int(timezone.now().timestamp())}",
                    status='BETTING',
                    betting_close_seconds=get_game_setting('BETTING_CLOSE_TIME', 30),
                    dice_roll_seconds=get_game_setting('DICE_ROLL_TIME', 7),
                    dice_result_seconds=get_game_setting('DICE_RESULT_TIME', 51),
                    round_end_seconds=get_game_setting('ROUND_END_TIME', 80)
                )
            else:
                return False
        
        return sync_round_to_redis(round_obj, redis_client)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error syncing database to Redis: {e}")
        return False


def get_game_setting(key, default=None):
    """
    Get a game setting from the database, with fallback to settings.py defaults.
    Always reads fresh from database (no caching).
    
    Args:
        key: The setting key (e.g., 'BETTING_CLOSE_TIME')
        default: Default value if not found in database or settings.py
    
    Returns:
        The setting value (converted to int if it's a numeric setting)
    """
    try:
        # Query directly using values_list to bypass any ORM instance caching
        # This ensures we always get the latest value from the database
        # Using values_list avoids creating model instances, which can be cached
        result = GameSettings.objects.filter(key=key).values_list('value', flat=True).first()
        if result is None:
            raise GameSettings.DoesNotExist(f"GameSettings matching query does not exist.")
        value = result
        
        # Convert to int for numeric settings
        numeric_keys = [
            'BETTING_CLOSE_TIME', 'DICE_ROLL_TIME', 'DICE_RESULT_TIME', 'ROUND_END_TIME',
            'BETTING_DURATION', 'RESULT_SELECTION_DURATION', 
            'RESULT_DISPLAY_DURATION', 'TOTAL_ROUND_DURATION',
            'RESULT_ANNOUNCE_TIME'
        ]
        if key in numeric_keys:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        
        return value
    except GameSettings.DoesNotExist:
        # Fallback to settings.py defaults
        game_settings = getattr(settings, 'GAME_SETTINGS', {})
        return game_settings.get(key, default)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting game setting {key}: {e}")
        # Fallback to settings.py defaults
        game_settings = getattr(settings, 'GAME_SETTINGS', {})
        return game_settings.get(key, default)


def get_all_game_settings():
    """
    Get all game settings as a dictionary, with fallback to settings.py defaults.
    This is cached for performance - settings don't change frequently.
    """
    result = {}
    defaults = getattr(settings, 'GAME_SETTINGS', {})
    
    # Get all settings from database
    db_settings = GameSettings.objects.all()
    for setting in db_settings:
        result[setting.key] = setting.value
    
    # Fill in any missing settings from defaults
    for key, value in defaults.items():
        if key not in result:
            result[key] = value
    
    # Convert numeric settings to int
    numeric_keys = [
        'BETTING_CLOSE_TIME', 'DICE_ROLL_TIME', 'DICE_RESULT_TIME', 'ROUND_END_TIME',
        'BETTING_DURATION', 'RESULT_SELECTION_DURATION', 
        'RESULT_DISPLAY_DURATION', 'TOTAL_ROUND_DURATION',
        'RESULT_ANNOUNCE_TIME'
    ]
    for key in numeric_keys:
        if key in result:
            try:
                result[key] = int(result[key])
            except (ValueError, TypeError):
                pass
    
    # Handle PAYOUT_RATIOS - keep as dict from defaults (not stored in DB as JSON)
    if 'PAYOUT_RATIOS' not in result and 'PAYOUT_RATIOS' in defaults:
        result['PAYOUT_RATIOS'] = defaults['PAYOUT_RATIOS']
    
    return result
