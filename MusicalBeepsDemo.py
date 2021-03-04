import musicalbeeps

player = musicalbeeps.Player(volume = 0.3,
                            mute_output = False)

# To play an A on default octave n°4 for 0.2 seconds
player.play_note("A", 5)

# # To play a G flat on octave n°3 for 2.5 seconds
player.play_note("G3b", 2.5)

# # To play a F sharp on octave n°5 for the default duration of 0.5 seconds
player.play_note("F5#")
