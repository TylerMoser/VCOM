"""Manually inspected source locations. Crop boxes are context, not masks."""
FAMILIES=[]
COLORS={'slate':(83,91,100),'river':(114,128,128),'gray':(143,142,126),'pale':(151,172,147),'brown':(139,100,66),'sand':(175,145,91),'tan':(169,129,90),'wet':(87,139,150),'purple':(85,81,112),'cyan':(114,188,183)}
SOURCES={'mario':'mario.jpg','pixelwood_a':'pixelwood_a.jpg','pixelwood_b':'pixelwood_b.gif','pixelwood_c':'pixelwood_c.jpg'}
def add(src,name,shape,size,crop,color='gray',scale=1,note='',seed=1):
 source=SOURCES.get(src,src+('.jpg' if src in ['poke_a','poke_i','poke_j','poke_k','poke_s','poke_u'] else '.png'))
 prefix='Mario' if src=='mario' else (''.join(w.capitalize() for w in src.split('_')))
 FAMILIES.append(dict(source=source,name=prefix+'_'+name,shape=shape,size=size,crop=crop,color=color,scale=scale,note=note,seed=seed))

add('mario','TallStoneStack','stack',[24,20,48],[20,5,94,138],'purple',1/3,'Two broad stones with shallow pitted marks; lower edge partly hidden. Depth inferred from the side-view artwork.')
add('mario','ShortStoneStack','stack',[16,16,32],[119,49,176,143],'purple',1/3,'Narrow three-section stack; shallow face-like pits retained as carvings.',2)
for src,scale,crops in [('pixelwood_a',1/3,[[139,220,189,278],[585,384,719,499],[279,597,345,689]]),('pixelwood_b',.2,[[606,184,680,236],[944,1039,1130,1202],[247,245,327,416]]),('pixelwood_c',1/3.067,[[423,258,472,300],[483,0,605,69],[267,203,326,310]])]:
 add(src,'FlatPebble','pebble',[16,14,8],crops[0],'slate',scale,'Low dark-gray loose stone; repeated copies represented once.',4)
 add(src,'SplitBoulder','cluster',[36,30,28],crops[1],'slate',scale,'Broad faceted rock with attached smaller shoulder at its foot. Same Pixelwood rock vocabulary across all three images.',5)
 add(src,'MossyStandingStone' if src=='pixelwood_b' else 'FracturedStandingStone','moss_pillar' if src=='pixelwood_b' else 'pillar',[16,16,32],crops[2],'slate',scale,'Upright fractured slab; chipped top and transverse seams. Moss cap only where evidenced in pixelwood_b.',6)
add('pixelwood_a','RoundStone','boulder',[16,16,14],[72,0,129,56],'slate',1/3,'Small angular-rounded gray stone near the upper-left edge.',7)
add('pixelwood_b','EmptyFireRing','ring',[24,24,6],[540,881,680,976],'slate',.2,'Rock ring from the campfire, delivered without logs/flame. Existing complete emissive campfire is preserved.',8)
add('poke_a','PointedRiverRock','shard',[16,14,18],[244,181,269,216],'river',1,'Single pointed stream rock; source resized, approximately one tile wide.',9)
add('poke_c','BrownRiverBoulder','boulder',[32,28,24],[367,0,402,32],'brown',1,'Broad exposed river boulder, faceted upper crown.',10)
add('poke_c','BrownRiverPebble','pebble',[14,12,10],[239,77,257,97],'brown',1,'Smaller pointed angular river stone; repeated placements deduplicated.',11)
add('poke_d','FacetedGrayBoulder','boulder',[28,24,24],[239,384,274,418],'gray',1,'Irregular large warm-gray boulder on the river island.',12)
add('poke_d','SmallGrayRock','boulder',[16,14,12],[125,426,148,453],'gray',1,'Small rounded faceted rock on the west bank.',13)
add('poke_d','RiverShard','shard',[12,10,24],[207,463,225,498],'gray',1,'Tall narrow pointed stone at the waterfall foot; also on dry banks.',14)
add('poke_d','FlatRiverStone','pebble',[16,12,6],[188,477,208,497],'gray',1,'Low oval river stone and matching loose stepping stones.',15)
add('poke_g','AngularPondRock','boulder',[16,14,14],[62,77,82,100],'river',1,'Gray pointed faceted pond rock.',16)
add('poke_g','SmallPondStone','pebble',[10,10,8],[94,45,112,65],'river',1,'Small pale angular pond stone.',17)
add('poke_h','LargePondBoulder','boulder',[32,28,24],[492,381,531,420],'river',1,'Large slate-gray pond boulder with irregular shoulder.',18)
add('poke_h','SmallPondRock','boulder',[16,14,12],[525,396,546,419],'river',1,'Smaller rounded gray stones in the eastern pond.',19)
add('poke_i','GrayRiverBoulder','boulder',[16,14,16],[386,394,418,427],'river',2/3,'Resized JPEG, about 24 displayed pixels per tile; repeated river boulders.',20)
add('poke_i','RiverPebble','pebble',[8,8,6],[415,433,431,452],'river',2/3,'Tiny matching river stone.',21)
add('poke_i','BrownFieldRock','boulder',[16,14,12],[482,225,511,247],'brown',2/3,'Small rust-brown loose rock near houses and fields.',22)
add('poke_l','ThreeLobeRock','cluster',[28,24,24],[0,159,30,192],'pale',1,'Tilesheet: main angular peak with two smaller foot lobes.',23)
add('poke_l','LeaningRockPair','pair',[28,22,24],[29,158,63,192],'pale',1,'Tilesheet: elongated leaning rear slab and low front stone.',24)
add('poke_l','RoundRock','boulder',[16,14,12],[62,158,82,178],'pale',1,'Tilesheet upper round stone, distinct from the smaller angular pebble below.',25)
add('poke_l','AngularPebble','pebble',[14,12,10],[62,175,82,192],'pale',1,'Tilesheet lower angular stone.',26)
add('poke_l','TallShard','shard',[12,10,28],[80,157,98,192],'pale',1,'Tilesheet long tapered blade-like stone.',27)
add('poke_l','ShortShard','shard',[12,10,22],[96,163,113,192],'pale',1,'Tilesheet shorter broader blade-like stone.',28)
for src in ['poke_m','poke_t']:
 add(src,'BrownCrag','crag',[32,28,36],[662,118,700,164] if src=='poke_m' else [278,470,317,516],'brown',1,'Tall brown broad-shouldered angular crag, distinct from the rounded boulder.',29)
 add(src,'BrownBoulder','boulder',[32,28,28],[735,112,773,150] if src=='poke_m' else [334,247,371,291],'brown',1,'Large faceted brown boulder repeated around the rocky banks.',30)
 add(src,'BrownPebble','pebble',[16,14,12],[731,53,757,79] if src=='poke_m' else [319,490,339,516],'brown',1,'Small low brown stone, distinct from the dark gravel clusters.',31)
 add(src,'LayeredRockPile','pile',[32,26,28],[699,22,740,68] if src=='poke_m' else [202,566,242,600],'brown',1,'Stacked flattened layers with a smaller summit stone.',32)
 add(src,'SmallGravelCluster','gravel',[12,10,8],[27,25,51,53] if src=='poke_m' else [250,651,277,674],'brown',1,'Low group of three angular stones, kept connected below ground-contact level.',33)
 add(src,'SubmergedStone','boulder',[16,14,12],[198,203,222,226] if src=='poke_m' else [254,712,278,739],'wet',1,'Muted blue-green rock visible through water; authored complete and opaque, without a water plane.',34)
add('poke_t','DarkStalagmite','shard',[12,10,24],[348,710,371,740],'brown',1,'Narrow dark cave spire with a chipped angular crown.',35)
add('poke_n','OchreBankBoulder','boulder',[24,20,22],[465,379,497,416],'tan',1,'Warm ochre boulder east of the path, with a broad pale facet.',36)
add('poke_n','OchreRiverBoulder','boulder',[24,20,18],[222,620,252,650],'tan',1,'Lower rounded partly submerged river boulder. Whole underside inferred; no water included.',37)
add('poke_o','PaleSeaBoulder','boulder',[32,28,26],[462,0,499,34],'sand',1,'Pale sandy-gray sea boulder with polygonal upper facets.',38)
add('poke_o','BrownSeaBoulder','boulder',[32,28,26],[558,0,595,34],'brown',1,'Warm brown colorway of the large sea boulder.',38)
add('poke_o','SmallSeaRock','boulder',[16,14,12],[565,84,589,107],'sand',1,'Small faceted offshore rock.',39)
add('poke_p','TaupeBoulder','boulder',[32,28,26],[493,636,532,674],'gray',1,'Large taupe boulder at the plateau edge.',40)
add('poke_p','TaupePebble','pebble',[16,14,12],[239,332,258,352],'gray',1,'Small standalone angular stone on the north plateau.',41)
add('poke_p','BlueRiverStone','boulder',[16,14,14],[357,381,381,416],'wet',1,'Dark wet blue-gray stone in the upper pond.',42)
add('poke_p','TippedRiverPillar','tipped',[16,14,28],[397,402,421,435],'wet',1,'Narrow blue-gray river pillar with exposed brown top; flat variants merge wet/dry shades as the same stone.',43)
add('poke_q','RedCrystalOutcrop','geode',[48,40,40],[48,155,100,213],'river',1,'Gray peaked host rock with a dark open front and red crystal blades. Crystals remain opaque diffuse; no evidence that they emit light.',44)
add('poke_q','LargeCoastalRockPile','pile',[48,40,40],[628,49,677,96],'sand',1,'Large golden offshore outcrop with rounded summit and smaller surrounding rocks.',45)
add('poke_q','SmallCoastalRockPair','pair',[32,24,20],[746,289,788,323],'sand',1,'Low two-lobed golden offshore rock.',46)
add('poke_q','BrownHillBoulder','boulder',[32,28,28],[400,125,434,163],'brown',1,'Rounded brown hill rock with a faceted crown.',47)
add('poke_q','SmallHillStone','pebble',[16,14,12],[355,79,388,103],'brown',1,'Small ochre-brown hill stones beside the shrine path.',48)
add('poke_s','PaleRiverSpire','shard',[12,10,28],[124,267,140,288],'river',1.6,'Tiny pale pointed river stones; JPEG obscures fine facets. Existing estimate: ten displayed pixels per tile.',49)
add('poke_s','PaleRiverBoulder','boulder',[20,18,16],[123,49,142,72],'river',1.6,'Pale faceted boulder in the river below the upper-left waterfall.',50)
add('poke_s','DarkRiverPebble','pebble',[12,10,8],[137,292,151,304],'river',1.6,'Low dark blue-gray river stone, distinct from the tall pale spire.',51)
add('poke_s','MossyRiverColumn','moss_pillar',[16,16,20],[609,437,628,460],'gray',1.6,'Small isolated moss-topped stone pillar in the stream; no surrounding water included.',52)

# Corrections after enlarged source-crop review (not inferred from thumbnails).
CORRECTIONS={
 'PixelwoodA_FlatPebble':dict(name='PixelwoodA_SmallRoundStone',shape='boulder',size=[16,14,14],note='Small rounded gray rock beside the lantern; taller than the flat pebbles in the other Pixelwood images.'),
 'PixelwoodA_FracturedStandingStone':dict(name='PixelwoodA_FracturedStone',shape='boulder',size=[18,16,20],note='Short upright fractured boulder partly overlapped by foliage; not the tall river pillar in pixelwood_c.'),
 'PokeI_RiverPebble':dict(crop=[421,447,434,466]),
 'PokeM_BrownBoulder':dict(crop=[733,219,772,260]),
 'PokeM_BrownPebble':dict(crop=[766,43,787,69]),
 'PokeM_SubmergedStone':dict(crop=[312,271,335,293]),
 'PokeT_SmallGravelCluster':dict(crop=[252,634,277,662]),
 'PokeT_SubmergedStone':dict(crop=[480,413,499,436]),
 'PokeO_SmallSeaRock':dict(crop=[573,285,596,307]),
 'PokeP_BlueRiverStone':dict(crop=[324,380,384,428]),
}
for family in FAMILIES:family.update(CORRECTIONS.get(family['name'],{}))
add('poke_m','SubmergedBoulder','boulder',[32,26,14],[289,267,322,300],'wet',1,'Broad low submerged boulder. Color captures the water-muted appearance, but the asset contains stone only.',53)
add('poke_t','SubmergedBoulder','boulder',[32,26,14],[448,408,482,439],'wet',1,'Broad low submerged boulder with smaller stones nearby; separate small-stone family supplied.',53)

EXCLUSIONS={
 'poke_b.png':'No discrete loose rocks found; stone paving, continuous cliffs and house masonry excluded.',
 'poke_e.png':'No discrete rocks found; shoreline is continuous terrain.',
 'poke_f.png':'No discrete rocks found; central sculpted creature statue is not a natural rock.',
 'poke_j.jpg':'No discrete rocks found; cliffs, buildings and garden edging are terrain/architecture.',
 'poke_k.jpg':'No discrete rocks found; repeated cliff banks are continuous terrain.',
 'poke_r.png':'No discrete rocks found; stairs, paving and continuous cliff edges excluded.',
 'poke_u.jpg':'Rock-sided floating islands are whole terrain masses; no discrete loose rock prop identified.',
}
