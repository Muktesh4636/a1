"""
Utility functions for automatic player distribution among admins
"""
from django.db.models import Count, Q
from .models import User


def get_admins_for_distribution():
    """
    Get all active admins (excluding superusers) for player distribution
    Superusers are excluded from automatic distribution
    """
    return User.objects.filter(is_staff=True, is_superuser=False, is_active=True)


def get_admin_with_fewest_clients():
    """
    Get the admin with the fewest assigned clients
    Returns None if no admins exist
    """
    admins = get_admins_for_distribution()
    if not admins.exists():
        return None
    
    # Annotate each admin with their client count
    admins_with_counts = admins.annotate(
        client_count=Count('clients', filter=Q(clients__is_staff=False))
    ).order_by('client_count', 'id')
    
    return admins_with_counts.first()


def assign_player_to_admin(player):
    """
    Assign a player to the admin with the fewest clients
    """
    admin = get_admin_with_fewest_clients()
    if admin:
        player.worker = admin
        player.save(update_fields=['worker'])
        return admin
    return None


def redistribute_players_from_deleted_admin(deleted_admin_id):
    """
    Redistribute players from a deleted admin equally among remaining admins
    """
    # Get all players that were assigned to the deleted admin
    orphaned_players = User.objects.filter(
        worker_id=deleted_admin_id,
        is_staff=False
    )
    
    if not orphaned_players.exists():
        return 0
    
    # Get remaining active admins (excluding superusers)
    remaining_admins = list(get_admins_for_distribution())
    
    if not remaining_admins:
        # No admins left, unassign all players
        orphaned_players.update(worker=None)
        return orphaned_players.count()
    
    # Distribute players equally
    players_list = list(orphaned_players)
    total_players = len(players_list)
    total_admins = len(remaining_admins)
    
    # Calculate distribution: each admin gets base_count, some get one extra
    base_count = total_players // total_admins
    extra_count = total_players % total_admins
    
    player_index = 0
    
    for i, admin in enumerate(remaining_admins):
        # First 'extra_count' admins get one extra player
        count_for_this_admin = base_count + (1 if i < extra_count else 0)
        
        # Assign players to this admin
        for _ in range(count_for_this_admin):
            if player_index < total_players:
                players_list[player_index].worker = admin
                players_list[player_index].save(update_fields=['worker'])
                player_index += 1
    
    return total_players


def redistribute_all_players():
    """
    Redistribute all unassigned players (or those assigned to superadmins) equally among all workers
    """
    admins = list(get_admins_for_distribution())
    if not admins:
        return 0
    
    # Get all unassigned players OR players assigned to superusers
    unassigned_players = User.objects.filter(
        is_staff=False
    ).filter(
        Q(worker__isnull=True) | Q(worker__is_superuser=True)
    )
    
    if not unassigned_players.exists():
        return 0
    
    players_list = list(unassigned_players)
    total_players = len(players_list)
    total_admins = len(admins)
    
    # Calculate distribution
    base_count = total_players // total_admins
    extra_count = total_players % total_admins
    
    player_index = 0
    
    for i, admin in enumerate(admins):
        count_for_this_admin = base_count + (1 if i < extra_count else 0)
        
        for _ in range(count_for_this_admin):
            if player_index < total_players:
                players_list[player_index].worker = admin
                players_list[player_index].save(update_fields=['worker'])
                player_index += 1
    
    return total_players


def balance_player_distribution():
    """
    Balance player distribution so all admins have roughly equal numbers
    This is called when a new admin joins to ensure fair distribution.
    It will also take players away from superusers and reassign them to workers.
    """
    # First, handle any unassigned players or players with superusers
    redistribute_all_players()
    
    admins = list(get_admins_for_distribution())
    if not admins:
        return 0
    
    # Get all players currently assigned to these admins
    # (Other players are already handled by redistribute_all_players)
    all_players = User.objects.filter(is_staff=False, worker__in=admins)
    
    # Count current distribution
    admin_counts = {}
    for admin in admins:
        admin_counts[admin.id] = User.objects.filter(worker=admin, is_staff=False).count()
    
    total_players = all_players.count()
    total_admins = len(admins)
    
    if total_players == 0 or total_admins == 0:
        return 0
    
    target_per_admin = total_players / total_admins
    
    players_to_reassign = []
    
    # Collect excess players from admins who have more than target
    for admin in admins:
        current_count = admin_counts[admin.id]
        if current_count > target_per_admin + 0.5:
            excess = int(current_count - target_per_admin)
            # Take the newest players to reassign
            excess_players = User.objects.filter(worker=admin, is_staff=False).order_by('-date_joined')[:excess]
            players_to_reassign.extend(list(excess_players))
    
    # Assign excess players to admins who are below target
    reassigned_count = 0
    for player in players_to_reassign:
        # Re-fetch admin with fewest clients each time to keep it balanced
        target_admin = get_admin_with_fewest_clients()
        if target_admin and target_admin.id != player.worker_id:
            player.worker = target_admin
            player.save(update_fields=['worker'])
            reassigned_count += 1
    
    return reassigned_count
