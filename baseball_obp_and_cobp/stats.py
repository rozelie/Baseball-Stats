from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.player import Player


def get_player_to_game_on_base_percentage(game: Game, explain: bool = False) -> dict[str, float]:
    return {player.id: _get_on_base_percentage(player, explain) for player in game.players}


def get_player_to_game_conditional_on_base_percentage(game: Game) -> dict[str, float]:
    # TODO
    return {}


def _get_on_base_percentage(player: Player, explain: bool = False) -> float:
    explain_lines: list[str] = []
    hits = 0
    walks = 0
    hit_by_pitches = 0
    at_bats = 0
    sacrifice_flys = 0
    for play in player.plays:
        play_id = f"- {play.result.name}"
        if play.modifiers:
            modifiers = "/".join(modifier.name for modifier in play.modifiers)
            play_id = f"{play_id}/{modifiers}"

        play_id = f"{play_id} ({play.play_descriptor})"

        result = play.result
        if result.is_at_bat:
            at_bats += 1

        if result.is_hit:
            hits += 1
            if explain:
                explain_lines.append(f"{play_id} => HIT, AB")
        elif result.is_walk:
            walks += 1
            if explain:
                explain_lines.append(f"{play_id} => WALK")
        elif result.is_hit_by_pitch:
            hit_by_pitches += 1
            if explain:
                explain_lines.append(f"{play_id} => HBP")
        elif any(modifier.is_sacrifice_fly for modifier in play.modifiers):
            sacrifice_flys += 1
            if explain:
                explain_lines.append(f"{play_id} => SF, AB")
        elif result.is_at_bat:
            if explain:
                explain_lines.append(f"{play_id} => AB")
        else:
            if explain:
                explain_lines.append(f"{play_id} => Unused for OBP")

    numerator = hits + walks + hit_by_pitches
    denominator = at_bats + walks + hit_by_pitches + sacrifice_flys
    try:
        on_base_percentage = numerator / denominator
    except ZeroDivisionError:
        on_base_percentage = 0.0

    if explain:
        explain_lines.insert(0, f"{player.name}: OBP = {round(on_base_percentage, 3)}")
        explain_lines.append(f"  > {hits=} + {walks=} + {hit_by_pitches=} == {numerator}")
        explain_lines.append(f"  > {at_bats=} + {walks=} + {hit_by_pitches=} + {sacrifice_flys=} == {denominator}")
        explain_lines.append("")
        print("\n".join(explain_lines))

    return on_base_percentage
