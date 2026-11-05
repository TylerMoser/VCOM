"""Finite, explicit expansion of Items.txt approved by the user, 2026-11-05."""
CATALOG=[]
def add(category,family,names):
 for name in names.split():CATALOG.append(dict(category=category,family=family,name=name))
EFFECTS='Incendiary Frost Gas Push Smoke Shock Poison Acid Blight Glue Shredding Slow Weakness Blindness Silence Fire Water Air Earth Ice Lightning Nature Light Shadow Arcane Sand Mud Flood Steam Vacuum Gravity Quake Ash Spores Oil'.split()
add('Stims','stim','Healing Adrenaline Endurance Focus Reflex Strength Evasion Defense Mobility Painkiller Antitoxin Antidote Coagulant Regeneration Wakefulness Tranquilizer NightVision ColdResistance HeatResistance RadResistance')
add('HealingSupplies','medical','FieldBandage CompressionBandage GauzeRoll Splint SutureKit FieldMedkit SurgicalKit TraumaBag HerbalPoultice SalveTin AntisepticBottle AntidoteVial BloodBottle PlasmaBottle BurnDressing Tourniquet IcePack HotPack MedicinePouch RecoveryKit')
add('Potions','potion','MinorHealing Healing GreaterHealing Mana MaxHealth Defense Move Aim MeleeAccuracy Strength Evasion')
add('Potions','potion',' '.join(EFFECTS))
add('Rounds','ammo','Standard ArmorPiercing Tracer Buckshot Slug HighExplosive')
add('Rounds','ammo',' '.join(EFFECTS))
add('GrenadesBombs','grenade','Fragmentation StickGrenade')
add('GrenadesBombs','grenade',' '.join(EFFECTS))
add('Guns','gun','Shotgun SniperRifle LightMachineGun HeavyMachineGun Pistol Blunderbuss Rifle Flamethrower GrenadeLauncher')
add('Attachments','attachment','Scope AutoLoader Repeater Stock HairTrigger ExtendedMagazine')
add('Melee','melee','Club Dagger Mace Staff Sickle Spear Flail Glaive Halberd Lance Maul Pike')
add('Swords','sword','Rapier Scimitar Cutlass Sabre Katana Longsword Greatsword Shortsword')
add('Axes','axe','Handaxe Battleaxe GreatAxe')
add('Hammers','hammer','LightHammer Warhammer GreatHammer')
add('Bows','bow','Crossbow Shortbow LightCrossbow HandCrossbow HeavyCrossbow Longbow CompoundBow')
add('ThrownWeapons','thrown','Dart Sling')
add('WornItems','wearable','GasMask ReinforcedVest BulletproofVest')
add('Armor','armor','Padded Leather Studded Hide Chainmail Scalemail HalfPlate FullPlate RingMail Splint')
add('Boots','boots','Ankle Marching Trench Cavalry Officer Scout FurLined Desert Jungle Mountain Miner Sailor Wader Sabaton Greave Moccasin Sandal WrapBoot SpikedBoot Alchemist RuneBoot WingedBoot')
add('Helmets','helmet','Brodie Stahlhelm Adrian Pickelhaube Pith Kepi FieldCap Tanker Aviator Miner Sallet Barbute Bascinet GreatHelm NasalHelm Spangenhelm KettleHat Morion BoneHelm HornedHelm RuneHelm PlumedHelm')
add('MagicFocus','focus','Wand Scepter Orb Crystal StaffHead Grimoire RuneTablet Totem SkullFocus AntlerFocus ShellFocus FeatherFan RitualDagger PrayerBeads Astrolabe DiviningRod BellFocus ChaliceFocus MirrorFocus LanternFocus CenserFocus TuningFork SunDisk HourglassFocus')
add('Food','food','BreadRoll BreadLoaf Baguette Hardtack CheeseWheel CheeseWedge Apple Pear Carrot Mushroom Fish SmokedFish RoastMeat Drumstick Sausage MeatPie StewBowl SoupTin RationTin BiscuitTin BerryBowl HoneyJar JamJar WaterCanteen')
add('MagicScrolls','scroll','Healing Revival ManaBarrier Fireball FrostNova LightningBolt StoneSkin WindStep WaterBreathing PoisonCloud AcidSplash NatureGrowth Sunbeam ShadowVeil ArcaneMissile SummonWard Silence Slow Haste Earthquake Flood Sandstorm Mist OilSlick')
add('MagicItems','relic','SignetRing GemRing Amulet Locket Pendant Talisman Brooch Crown Circlet Bracelet Gauntlet Belt Compass PocketWatch Hourglass CrystalBall MusicBox Spellbook RuneStone EnchantedKey CharmBag MagicMirror FlyingCarpet BottomlessSatchel')
add('Torches','torch','PitchTorch ResinTorch WrappedTorch BoneTorch IronCageTorch StormTorch BlueFlameTorch GreenFlameTorch ArcaneTorch FrostTorch EmberTorch SunTorch ShadowTorch OilLantern HurricaneLantern TrenchLantern CandleLantern MiningLamp SignalLamp BrazierTorch')
WEARABLE={'armor','boots','helmet','wearable'}
VARIANTS=['Field','Veteran','Officer','Arcane']
# Explicit per-family design labels describe geometry, not only paint.
LABELS={'stim':['Syringe','AmpouleInjector','FieldAutoinjector','CasedInjector'],
 'potion':['RoundFlask','SquareFlask','Longneck','FacetedFlask'],
 'ammo':['Cartridge','Shell','StripperClip','AmmoBox'],
 'grenade':['Egg','Stick','Canister','FinBomb'],
 'scroll':['Open','Rolled','TwinRoll','Case'],
 'sword':['Field','BasketGuard','Runic','Ceremonial'],
 'axe':['Bearded','Crescent','DoubleBit','Runic'],
 'hammer':['Block','Peen','Flanged','Runic']}

if __name__=='__main__':
 from collections import Counter
 import json
 print(json.dumps(Counter(r['category'] for r in CATALOG),indent=2))
 print('Types:',len(CATALOG),'new design pairs:',len(CATALOG)*4,'wearable pairs:',sum(r['family'] in WEARABLE for r in CATALOG)*4)
