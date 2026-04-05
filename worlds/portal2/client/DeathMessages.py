from random import choice

default_death_messages = [
    "Long fall boots could not save {player_name}",
    "{player_name} found the cake",
    "{player_name} looked at the operational end of the Aperture Science Handheld Portal Device",
    "{player_name} died of known side effects",
    "{player_name} died of unknown side effects"
]

map_specific_death_messages = {
    # Chapter 1
    "sp_a1_intro1":         ["{player_name} had a minor case of serious brain damage"],
    "sp_a1_intro2":         ["The Aperture Science Material Emancipation Grill fizzled {player_name}'s eartubes"],
    "sp_a1_intro3":         ["{player_name} found a gun that makes the wrong type of hole"],
    "sp_a1_intro4":         ["{player_name} did not remain tranquil in the face of almost certain death"],
    "sp_a1_intro5":         ["{player_name} did not avoid unsheltered testing areas"],
    "sp_a1_intro6":         ["{player_name} was irradiated in such a way that the future should not start with them"],
    "sp_a1_intro7":         ["{player_name}disengaged from their management rail"],
    "sp_a1_wakeup":         ["{player_name} found the escape pod"],
    "sp_a2_intro":          ["{player_name} was euthanized"],
    # Chapter 2
    "sp_a2_laser_intro":    ["{player_name} failed this first simple test"],
    "sp_a2_laser_stairs":   ["{player_name} got to see how the Discouragement Redirection Cubes work"],
    "sp_a2_dual_lasers":    ["{player_name} somehow managed to pack on a few pounds"],
    "sp_a2_laser_over_goo": ["{player_name} decided to go THAT slowly"],
    "sp_a2_catapult_intro": ["{player_name} was catapulted into space"],
    "sp_a2_trust_fling":    ["{player_name} landed in 15 acres of broken glass"],
    "sp_a2_pit_flings":     ['{player_name} has died. They probably wanted to say: "I love you"'],
    "sp_a2_fizzler_intro":  ["{player_name} did not understand the test"],
    # Chapter 3
    "sp_a2_sphere_peek":    ["{player_name} defeated the load-bearing capacity of the Aperture Science Aerial Faith Plate"],
    "sp_a2_ricochet":       ["{player_name} saw a deer"],
    "sp_a2_bridge_intro":   ["{player_name} rubbed their cheek on the Aperture Science Hard Light Bridge"],
    "sp_a2_bridge_the_gap": ["{player_name} did not do well enough"],
    "sp_a2_turret_intro":   ["{player_name} became a pale spherical thing full of bullets"],
    "sp_a2_laser_relays":   ["{player_name} accepted a belated birthday medical experiment"],
    "sp_a2_turret_blocker": ["{player_name}'s jumpsuit looked too stupid"],
    "sp_a2_laser_vs_turret":["{player_name} couldn't wait for the surprise"],
    "sp_a2_pull_the_rug":   ["{player_name} didn't win the Nobel Prize for being immune to neurotoxin"],
    # Chapter 4
    "sp_a2_column_blocker": ["{player_name}'s birth parents do not love them"],
    "sp_a2_laser_chaining": ["{player_name}'s death was actually pretty funny according to the old formula"],
    "sp_a2_triple_laser":   ["Something is wrong with {player_name}'s Triple Laser"],
    "sp_a2_bts1":           ["{player_name} completed the last test"],
    "sp_a2_bts2":           ["{player_name} did not get into the lift"],
    # Chapter 5
    "sp_a2_bts3":           ["{player_name} was too smelly"],
    "sp_a2_bts4":           ["{player_name} made a potato battery"],
    "sp_a2_bts5":           ["{player_name} did not look directly at the implosion"],
    "sp_a2_core":           ["{player_name} must have felt really silly for dying here"],
    # Chapter 6
    "sp_a3_01":             ["{player_name} did not heed the warning signs"],
    "sp_a3_03":             ["{player_name} found the human-mantis hybrids"],
    "sp_a3_jump_intro":     ["{player_name} was part of the control group"],
    "sp_a3_bomb_flings":    ["{player_name} died from asbestos poisoning"],
    "sp_a3_crazy_box":      ["{player_name} made eye contact with themselves on the testing track"],
    "sp_a3_transition01":   ["{player_name} was not good at murder"],
    # Chapter 7
    "sp_a3_speed_ramp":     ["{player_name} did not want the 60 bucks"],
    "sp_a3_speed_flings":   ["{player_name} let Aperture Science disassemble them"],
    "sp_a3_portal_intro":   ["Cave Johnson burned {player_name}'s house down with the lemons"],
    "sp_a3_end":            ["{player_name} died of moon rock poisoning"],
    # Chapter 8
    "sp_a4_intro":          ["{player_name} did not want to get onto the button"],
    "sp_a4_tb_intro":       ["{player_name} got stuck on the roof when trying to crouch-flight"],
    "sp_a4_tb_trust_drop":  ["{player_name} did not pull the lever"],
    "sp_a4_tb_wall_button": ["{player_name} started before Wheatley"],
    "sp_a4_tb_polarity":    ["{player_name} got called adopted"],
    "sp_a4_tb_catch":       ["{player_name} did not read Machiavellian"],
    "sp_a4_stop_the_box":   ["{player_name} found the worst way to solve the test chamber"],
    "sp_a4_laser_catapult": ["{player_name} failed to solve the test chamber ten times as fast"],
    "sp_a4_laser_platform": ["{player_name} was caught in the tremor for old times' sake"],
    "sp_a4_speed_tb_catch": ["{player_name} loved the big surprise to death"],
    "sp_a4_jump_polarity":  ["{player_name} slipped. Butterfingers!"],
    # Chapter 9
    "sp_a4_finale1":        ["{player_name} reached the part where he kills you"],
    "sp_a4_finale2":        ["{player_name} lost against mashy spike plate"],
    "sp_a4_finale3":        ["{player_name} spent ten years in the room where all the robots scream at you"],
    "sp_a4_finale4":        ["Bombs were thrown at {player_name}"],
}

def get_death_message(map_name, player_name):
    death_messages = default_death_messages
    if map_name in map_specific_death_messages:
        death_messages += map_specific_death_messages[map_name]
    return choice(death_messages).format(player_name=player_name)