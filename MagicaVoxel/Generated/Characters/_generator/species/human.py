"""Humans: every skin and hair, the game's classes and everyday folk."""
from .common import Set, designs, person, SKIN, HAIR
from core import shade
import outfits as O
import extras as X

SPECS = [
    ('Officer', dict(skin='fair', hair='brown', hair_style='short', iris='blue', outfit='tactician', mouth='smile')),
    ('Sharpshooter', dict(skin='tan', hair='black', hair_style='crop', iris='brown', eyes='angry', beard='stubble',
                          beard_color=(90, 70, 60), outfit='sharpshooter')),
    ('Gunslinger', dict(skin='umber', hair='black', hair_style='short', iris='brown', beard='moustache', outfit='gunslinger')),
    ('Bruiser', dict(skin='ruddy', hair='ginger', hair_style='curly', iris='green', freckles=(190, 110, 80),
                     outfit='assault', hat=False, brows='angry')),
    ('Ranger', dict(skin='light', hair='blonde', hair_style='long', iris='green', eyes='pupil', outfit='ranger')),
    ('Monk', dict(skin='brown', hair='black', hair_style='bald', iris='brown', eyes='closed', mouth='smile', outfit='monk')),
    ('Ironclad', dict(skin='olive', hair='darkbrown', hair_style='short', outfit='heavy')),
    ('Barbarian', dict(skin='tan', hair='auburn', hair_style='long', iris='hazel', beard='full', outfit='barbarian',
                       hat=False, brows='bushy', eyes='angry')),
    ('Shieldbearer', dict(skin='deep', hair='black', hair_style='crop', iris='amber', outfit='guardian')),
    ('FieldMedic', dict(skin='peach', hair='chestnut', hair_style='ponytail', iris='blue', blush=(236, 150, 140),
                        outfit='support', eyes='big', eye_h=3)),
    ('Psychic', dict(skin='porcelain', hair='platinum', hair_style='bob', iris='violet', eyes='glow', outfit='psychic',
                     outfit_kw=dict(main=(70, 50, 120)))),
    ('WhiteMage', dict(skin='golden', hair='white', hair_style='long', iris='teal', outfit='white_mage', eyes='big', eye_h=3)),
    ('Necromancer', dict(skin='ashen', hair='raven', hair_style='long', iris=(120, 255, 140), eyes='glow', mouth='frown',
                         outfit='necromancer')),
    ('Apothecary', dict(skin='fair', hair='copper', hair_style='bun', iris='green', freckles=(200, 140, 110),
                        outfit='apothecary')),
    ('Pyromancer', dict(skin='umber', hair='black', hair_style='short', iris='amber', beard='goatee', outfit='fire_mage')),
    ('Captain', dict(skin='light', hair='grey', hair_style='side', iris='grey', beard='full', beard_color=(190, 190, 190),
                     outfit='pirate')),
    ('Noble', dict(skin='porcelain', hair='blonde', hair_style='swept', iris='blue', outfit='noble',
                   outfit_kw=dict(royal=True, cape=True))),
    ('Farmer', dict(skin='ruddy', hair='sandy', hair_style='short', iris='blue', mouth='grin', outfit='peasant')),
    ('Bard', dict(skin='olive', hair='chestnut', hair_style='curly', iris='hazel', mouth='smile', outfit='bard')),
    ('Scholar', dict(skin='brown', hair='grey', hair_style='bald', iris='brown', beard='goatee', beard_color=(200, 200, 200),
                     outfit='scholar')),
]

SETS = [Set('Human', 'Human', designs(person, SPECS),
            treatments=[(1, 'Cartoon'), (5, 'TwoColor'), (10, 'CratePalette')])]
