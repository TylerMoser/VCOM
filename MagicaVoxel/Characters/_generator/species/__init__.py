"""Every species' sets, in Brainstorming/Species.txt's order."""
import importlib

MODULES = ['human', 'dwarf', 'elf', 'lizards', 'reptiles', 'mammals', 'beasts', 'birds', 'aquatic', 'bugs', 'plants', 'dinos']

ALL_SETS = []
for _name in MODULES:
    ALL_SETS += importlib.import_module('.' + _name, __name__).SETS
