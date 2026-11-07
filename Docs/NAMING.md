# Naming

Started 2026-11-06. This document records the naming brief, source research,
construction rules, and settlement, ruler, and territorial assignments. Names below are the first authored
pass for review, not a claim of user approval of each individual name.

## Game integration status

2026-11-07: At the user's request, all 220 existing Court resources in
`vcom/Scenes/Map.tscn` now use the assigned people below. `ruler_name` contains
the title and personal name; `display_name` is `Court of ` followed by that
value, for example `Court of King Pershaniel`. These supply the court header,
settlement tooltip, and location tab. All 2,220 settlement display names are now
also applied from the assignment registers. The Details page shows that name
as its heading, matching the settlement's map tooltip.
Earlier documentation-only statements describe the original naming passes;
this integration status supersedes them for person and settlement names.
The 273 county, duchy, and kingdom names added below remain documentation-only.

## Decisions and scope

- Every kingdom/biome should develop a recognizable naming tradition that evokes
  its environment without copying a real culture or an existing fictional world.
- Borrow and transform ordinary word roots from multiple relevant languages;
  combine those with invented vocabulary and consistent fictional sound rules.
- There are currently three name types: **settlements**, **people**, and
  **territories** (counties, duchies, and kingdoms). All three now have
  assignment registers for the desert, tundra/frozen mountains, volcanic mountains/ruins,
  evergreen temperate rainforest, tropical rainforest, swamp, temperate mountains,
  deciduous forest, and grassland biomes.
- Desert inspirations: Sahara, Sahel, Namibia, Mogollon, Pueblo, Navajo, Apache.
- Tundra inspirations: Inuit, Aleut, Nordic, Nenets (the user's Nenet), and Siberian;
  the tundra section identifies the specific languages selected within those categories.
- Volcanic inspirations: Hawaiian, Japanese, and Indonesian; this pass uses
  Bahasa Indonesia for the Indonesian lexical contribution.
- Evergreen rainforest inspirations: Pacific Northwest traditions; this pass
  selects Lushootseed, Tlingit, and Chinuk Wawa, with specific sources below.
- Tropical rainforest inspirations: Amazon, Congo, Borneo, and New Guinea;
  this pass selects Nheengatu, Lingala, Iban, and West Kewa.
- Swamp inspirations: Uros, Aztec, Cajun (interpreting the user's “Cajan”), and
  Native Louisiana; this pass selects Uru/Uchumataqu, historical Nahuatl,
  Cajun French, Tunica, and Biloxi.
- Temperate mountain inspirations: Andes (especially Incan), Himalayas, and
  Rocky Mountain peoples; this pass emphasizes Quechua alongside Sherpa, Ute,
  and Blackfoot.
- Deciduous Forest inspirations: Celtic, Slavic, Korean, and Iroquoian; this pass
  selects Irish, Polish, Korean, and Mohawk.
- Grassland inspirations: Germanic, French, Plains North American, Eurasian
  Steppe, Mongolian, and Zulu; this pass selects German, French, Lakota, Kazakh,
  Mongolian, and Zulu.
- Deciduous Forest and Grassland should feel more clearly European-inspired
  than the other kingdoms; their separate sound rules implement that direction.
- **User clarification, 2026-11-06:** use all seven across the tradition; individual
  names blend a smaller selection. Seven separate fragments per name are not required.
- Assign names to every existing desert settlement, including villages and hamlets.
  This document is the assignment register. The names have not been applied to the
  game scene in this pass.
- Territorial and personal names are authored separately from their capitals;
  their assignment registers below are authoritative. Dynasties remain a future
  naming decision.

## Desert identity

The intended impression is inhabited dry country: stone ridges, sand, protected
water, fields after rain, sheltered houses, and routes between settlements. Avoid
making every name mean sand, sun, or death. The desert contains farms and towns as
well as exposed wilderness.

This is one fictional naming tradition, not seven real peoples mapped onto seven
districts. Roots can recur across political boundaries. Differences between a
capital and a hamlet should come mostly from the name's history and length, not
from an English rank suffix such as City or Town.

### What each inspiration contributes

| Requested inspiration | Specific basis for this pass | Contribution and boundary |
| --- | --- | --- |
| Sahara | Tamasheq/Amazigh vocabulary: `aman` (water), `adrar` (mountain) | Reshaped water and ridge stems; do not reuse complete oasis names. Tamasheq spans the Sahara and Sahel, so these are not sealed cultural categories. [S1, S2] |
| Sahel | Hausa `ruwa` (water/rain), `rairayi` (sand) | Water/rain and sand fragments blended into other roots. Hausa is the selected linguistic source, not a synonym for all Sahelian cultures. [S3] |
| Namibia | Khoekhoegowab `soreb` (hot rainy summer), `saob` (cold dry winter), documented near Fransfontein | Seasonal contrasts become fictional rain-season and dry-season roots. This is a specific Namibian source, not a claim that all Namibia is desert or speaks one language. [S4] |
| Mogollon | Archaeology of the Tularosa Mogollon dwellings at Gila: sheltered construction and access to a perennial stream | Architectural inspiration for invented settlement-form endings. **No purported Mogollon word roots.** The archaeological label is not a recovered native language name. [S5] |
| Pueblo | Hopi, specifically the vocabulary documented in Milo Kalectaca's *Lessons in Hopi*: `kiihu` (house/village), `paasa` (field) | Reshaped dwelling and cultivated-ground stems. Hopi is one selected language; Pueblo is not a single language or tribe. [S6, S7] |
| Navajo | Diné Bizaad `tsé` (rock) | Reshaped stone stems, combined with African and Hopi material. The fictional `z` sound is our invention, not a Navajo pronunciation instruction. [S8] |
| Apache | Mescalero Apache `tú` (water), as supplied by the tribe's language program | Reshaped water stems, often emphasizing dependable supply in the fictional lexicon. That semantic narrowing is invented. Apache varieties are not interchangeable. [S9] |

Real-world source words are evidence for inspiration, not translations of the
finished names. Short coincident syllables do not by themselves prove derivation;
the construction ledger below records the actual design choices.

## Construction method

1. Choose an environmental image or a settlement history. Where geography is
   verified, use it; otherwise treat the image as a proposed name story.
2. Select roots from at least two of the source traditions. Use a previously
   blended stem where appropriate, rather than repeatedly joining full real words.
3. Shorten and reshape them into the fictional root inventory below. These changes
   are creative operations, not reconstructed historical sound changes.
4. Add an invented settlement-form ending when useful. Vary the length and ordering;
   a name should sound like a place people use, not a list of its inspirations.
5. Read the result aloud. Prefer two to four syllables, distinct openings, and a
   clear consonant near the end. Allow a longer capital name when it remains easy
   to say. Check neighboring names for confusion.
6. Record the spelling, components, intended sense, and stable settlement ID.
7. Check duplicates in the project, then search candidate spellings for conspicuous
   existing place, personal, and fictional names. Revise recognizable collisions.
   A search with no result cannot establish worldwide originality.

### Sound and spelling rules

- Five vowels: `a` as in father, `e` as in bed, `i` as in machine, `o` as in
  more without an added glide, `u` as in rule. `ai` is one sound as in eye.
- `k` is always hard; `s` is unvoiced; `z` is voiced; `sh` is as in ship.
  No silent final `e`. `y` is a consonant as in yes.
- Stress the penultimate syllable. Pronunciation examples below give explicit
  syllable boundaries for the principal names.
- Plain Latin spelling is a fictional orthographic choice. Do not manufacture
  clicks, tone marks, or apostrophes for decoration or imply that removing them
  preserves a source language's pronunciation.
- Typical lengths: 6–11 letters. Do not enforce equal lengths by settlement rank.
- Recurring endings indicate an imagined settlement form, not political status.
  A capital may retain a name that originally described a modest shelter.

### Source fragments and fictional blended roots

In this ledger, `am`, `ad`, `ru`, `rai`, `so`, `sa`, `ki`, `pa`, `ze`, and `tu`
are **our extracted fragments**, not a list of grammatical morphemes in the source
languages. All meanings in the last column are invented for this setting.

| Fictional root | Construction from source fragments | Fictional sense |
| --- | --- | --- |
| `amar` | `aman` → am + `ruwa` → ru; fuse and reshape to amar | stored/shared water |
| `azek` | `aman` → a + `tsé` → ze; add closing k | water held in stone |
| `aruk` | `adrar` → ar + `ruwa` → ru; overlap r and add k | ridge runoff |
| `soru` | `soreb` → so + `ruwa` → ru | seasonal rainwater |
| `sazel` | `saob` → sa + `tsé` → ze; add l | dry stone ground |
| `tumar` | `tú` → tu + `aman` → am; contract and add r | dependable well |
| `tuser` | `tú` → tu + `soreb` → ser | water kept after the rains |
| `pazek` | `paasa` → pa + `tsé` → ze; add k | stone-edged cultivated ground |
| `kirai` | `kiihu` → ki + `rairayi` → rai | dwellings among sand |
| `raitu` | `rairayi` → rai + `tú` → tu | water beneath sand |
| `kisar` | `kiihu` → ki + `saob` → sa; add r | dry-season shelter |
| `zoru` | `tsé` → zo + `ruwa` → ru | water running across rock |

The added consonants and vowel changes deliberately move the results away from
verbatim source words. `amar` and `tumar` remain different fictional words even
though their source meanings overlap. Do not call either a literal translation
of “reservoir” or “well” into any real language.

### Invented settlement-form endings

These sounds are newly coined. Their **architectural ideas**, rather than their
phonetics, are the Mogollon contribution. They also suit the broader clustered
dwelling/field vocabulary developed from the Hopi sources, without reproducing
Hopi grammar.

| Ending | Fictional meaning / name image |
| --- | --- |
| `-en` | sheltered inhabited place |
| `-esh` | joined dwellings / house cluster |
| `-or` | settlement on a ledge or raised footing |
| `-vek` | settlement around a stored supply |
| `-avel` | a spread of habitation and cultivated ground |
| `-un` | a small sheltered resting place |

When a root ends in a vowel and an ending starts in one, insert `v`: `soru + en`
becomes `Sor u v en` → **Soruven** (written without spaces). This is an invented
joining rule. A root ending in a consonant joins directly: `pazek + or` →
**Pazekor**. Do not silently make additional contractions; log exceptions.

The initial register uses these twelve mixed roots and six endings, with different
pairings rather than a complete generated grid. Recurrence is intentional, but
future additions should expand the imagery before exhausting every combination.

## Settlement register: Desert / Kingdom 4

Read from the current `vcom/Scenes/Map.tscn`, using settlement nodes with
`metadata/kingdom = 4`: **64 settlements**, in counties 73–96. There are 24 capital
nodes (1 kingdom, 3 duchy, 20 county), 24 villages, and 16 hamlets. The kingdom
capital also serves its lower administrative levels; do not invent a second
capital for Duchy 17.

Node IDs identify existing places even when their displayed names change. Paths
are relative to `Settlements/`. Capital groups are `KingdomCapitals`,
`DuchyCapitals`, and `CountyCapitals`; the other groups are `Villages` and `Hamlets`.

**Meaning versus terrain:** the glosses below are proposed fictional name stories,
not verified descriptions of built structures or terrain at each node. The source
settlement JSON supplies historical siting data for capitals only; current scene
positions and a terrain inspection must take priority before treating a story as
geographic fact. Names concerning storage can refer to built cisterns rather than
a mapped river. No new buildings, wells, farms, or lore events are implied to exist
in the game by these assignments.

### Capitals

| Node | County | Name | Components | Intended name image |
| --- | --- | --- | --- | --- |
| Kingdom4Capital | 85 | Amaravel | amar + avel | habitation and fields sustained by shared water |
| Duchy15Capital | 73 | Arukesh | aruk + esh | houses gathering ridge runoff |
| Duchy16Capital | 79 | Sazelor | sazel + or | raised settlement on dry stone |
| Duchy18Capital | 91 | Kisarvek | kisar + vek | provisioned dry-season refuge |
| County074Capital | 74 | Kiraivesh | kirai + esh | house cluster among sand |
| County075Capital | 75 | Zoruvel | zoru + avel, contracted | rock-water habitation |
| County076Capital | 76 | Sazelen | sazel + en | shelter on dry stone |
| County077Capital | 77 | Soruvek | soru + vek | settlement storing seasonal water |
| County078Capital | 78 | Raituvesh | raitu + esh | houses above a sand seep |
| County080Capital | 80 | Kisaror | kisar + or | raised dry-season shelter |
| County081Capital | 81 | Tumarvek | tumar + vek | settlement provisioned by a well |
| County082Capital | 82 | Kiraiven | kirai + en | sheltered sand dwellings |
| County083Capital | 83 | Pazekor | pazek + or | raised field settlement |
| County084Capital | 84 | Tuseren | tuser + en | shelter with water held through the dry season |
| County086Capital | 86 | Azekavel | azek + avel | cultivation around a rock cistern |
| County087Capital | 87 | Zoruvesh | zoru + esh | houses beside rock runoff |
| County088Capital | 88 | Sazelavel | sazel + avel | habitation spread across dry stone ground |
| County089Capital | 89 | Amarkiven | amar + ki + en | dwellings by a shared water store |
| County090Capital | 90 | Pazekavel | pazek + avel | settlement among stone-edged fields |
| County092Capital | 92 | Tumaror | tumar + or | well settlement on raised footing |
| County093Capital | 93 | Kisaravel | kisar + avel | dry-season dwellings and grounds |
| County094Capital | 94 | Raituvek | raitu + vek | stored supply from water beneath sand |
| County095Capital | 95 | Tuseresh | tuser + esh | houses sharing stored rainwater |
| County096Capital | 96 | Arukor | aruk + or | raised settlement gathering runoff |

Exception: **Zoruvel** = `zoru + avel`, reduced from `Zoruvavel` by losing the
unstressed middle `va`. Its meaning is habitation/grounds sustained by rock runoff.
This is a logged contraction, not the `-en` ending. The shorter form is preferred
to the repeated `vav` sequence.

Principal pronunciations: Amaravel **a-ma-RA-vel**; Arukesh **a-RU-kesh**;
Sazelor **sa-ZE-lor**; Kisarvek **ki-SAR-vek**; Kiraivesh **ki-RAI-vesh**;
Zoruvel **zo-RU-vel**; Raituvesh **rai-TU-vesh**; Pazekor **pa-ZE-kor**.

### Villages

| Node | Name | Components | Intended name image |
| --- | --- | --- | --- |
| County073Village1 | Arukisen | aruk + kisar + en, contracted | seasonal shelter gathering runoff |
| County073Village2 | Tumaresh | tumar + esh | well houses |
| County073Village3 | Pazeken | pazek + en | shelter among stone-edged fields |
| County074Village1 | Kiraivor | kirai + or | raised sand dwellings |
| County075Village1 | Zoruven | zoru + en | rock-water shelter |
| County077Village1 | Soruvesh | soru + esh | seasonal-water houses |
| County077Village2 | Amarekesh | amar + pazek + esh, contracted | shared-water field houses |
| County077Village3 | Arukavel | aruk + avel | runoff-fed habitation and grounds |
| County077Village4 | Tuseror | tuser + or | raised rainwater settlement |
| County078Village1 | Raituven | raitu + en | shelter above sand water |
| County078Village2 | Kisaren | kisar + en | dry-season refuge |
| County078Village3 | Zorupaz | zoru + pazek, contracted | fields watered across stone |
| County083Village1 | Pazekesh | pazek + esh | field houses |
| County085Village1 | Amarzekesh | amar + azek + esh, contracted | shared-water stone houses |
| County085Village2 | Tumaravel | tumar + avel | well-fed habitation and grounds |
| County085Village3 | Azekesh | azek + esh | rock-cistern houses |
| County085Village4 | Sorupaz | soru + pazek, contracted | fields after seasonal rain |
| County085Village5 | Kisorun | kisar + soru + un, contracted | seasonal refuge |
| County088Village1 | Sazelvek | sazel + vek | supply settlement on dry stone |
| County088Village2 | Azekor | azek + or | raised rock-cistern settlement |
| County090Village1 | Pazekvek | pazek + vek | stores among cultivated ground |
| County090Village2 | Aruktuser | aruk + tuser | retained runoff |
| County090Village3 | Soruven | soru + en | seasonal-water shelter |
| County090Village4 | Kisaresh | kisar + esh | dry-season house cluster |

Additional authored contractions: `amar + pazek + esh` → `amar-ek-esh`
(drop `paz`); `zoru/soru + pazek` → `zoru/soru-paz` (drop `ek`);
`kisar + soru + un` → `ki-sor-un` (retain `ki`, shorten `soru` to `sor`).
These exceptions add older-looking names without claiming genuine linguistic history.

### Hamlets

| Node | Name | Components | Intended name image |
| --- | --- | --- | --- |
| County073Hamlet1 | Arukun | aruk + un | small runoff refuge |
| County073Hamlet2 | Tumaren | tumar + en | sheltered well |
| County074Hamlet1 | Kiraivun | kirai + un | small sand refuge |
| County074Hamlet2 | Kisarun | kisar + un | small dry-season refuge |
| County074Hamlet3 | Raituvun | raitu + un | small sand-water refuge |
| County075Hamlet1 | Zoruvun | zoru + un | small rock-water refuge |
| County077Hamlet1 | Soruvun | soru + un | small seasonal-water refuge |
| County080Hamlet1 | Sazelun | sazel + un | small dry-stone refuge |
| County081Hamlet1 | Tumarun | tumar + un | small well refuge |
| County085Hamlet1 | Amarzekun | amar + azek + un, contracted | small refuge at shared stone-held water |
| County085Hamlet2 | Azekun | azek + un | small rock-cistern refuge |
| County088Hamlet1 | Pazekun | pazek + un | small field refuge |
| County088Hamlet2 | Azeken | azek + en | sheltered rock cistern |
| County088Hamlet3 | Sazelkis | sazel + kisar, contracted | dry-stone seasonal shelter |
| County088Hamlet4 | Tuserun | tuser + un | small stored-rainwater refuge |
| County095Hamlet1 | Kistumar | kisar + tumar, contracted | seasonal shelter by a well |

Final contractions: `sazel + kisar` → `sazel-kis`; `kisar + tumar` → `kis-tumar`.
Collision revisions: `aruk + kisar + en` → `aru-kis-en` (overlap k, drop ar);
`amar + azek + esh` → `amar-zek-esh` (drop initial a); `amar + azek + un` →
`amar-zek-un` (drop the second root's initial a). `Amarkiven` adds the documented
Hopi-derived `ki` fragment to `amar`, then uses the regular vowel-linking rule.
The `-un` concentration among hamlets is a first-pass tendency, not a rule that
hamlets must end in `-un` or that such a place cannot grow into a city.

## Originality and review status

No existing settlement, person, franchise, or sacred name was intentionally used
as a finished name. The construction ledger makes borrowed roots and invented
material visible. Shared short syllables with real names will be unavoidable.

The register has been checked for exact duplicate names and for complete coverage
of the current 64 desert settlement node IDs. An initial web screen submitted all
64 original spellings in grouped exact-name searches, which returned no results.
Individual follow-up searches nevertheless found collisions, demonstrating that
those grouped searches are insufficient evidence of originality:

| Rejected draft | Reason | Replacement |
| --- | --- | --- |
| Amaren | Existing [restaurant name](https://amarenbarcelona.com/en/contact/) and other uses | Amarkiven |
| Amaresh | Established [personal name](https://www.alltomnamn.se/namn/amaresh) | Amarzekesh |
| Amarun | Existing [settlement name](https://en.wikipedia.org/wiki/Amarun) | Amarzekun |
| Aruken | Existing [fictional/folktale character usage](https://repositori.kemendikdasmen.go.id/26091/1/5.%20Kumpulan%20Cerita%20Rakyat%20Papua.pdf) | Arukisen |

A further intermediate spelling, Amarzesh, was discarded after a name website
returned it as a suggested variant (not reliable linguistic evidence). The final
replacement is Amarzekesh. Individual exact-spelling searches for the four final
replacements returned no results.
Individual screening of every remaining spelling and sound-alike remains outstanding;
do not describe this pass as globally unique, linguistically authenticated, or
cleared of all media resemblance.

Review priorities: whether the repeated water roots feel too dominant; whether
the `-un` hamlets are too alike; whether adjacent settlements need more distinct
spoken forms. These are proposed refinements, not changes to the user's brief.
Do not replace an individual approved name merely to make a future generator tidy.

When applying approved names to the game, change settlement `display_name` values
while retaining node IDs, metadata, positions, and existing manual scene edits.
Inspect tooltips and settlement-menu headings in game after that separate change.

## Desert person names

Added 2026-11-06 at the user's request: use the same mixed-inspiration approach
for people, including every count, duke, and king currently authored in the desert.
These are proposed names in this document; `Court.ruler_name` is unchanged.

### Personal naming convention

- Use **one personal name** in this first register. Formal display is **title +
  personal name**, for example **King Amzuraki**. The title is not part of the name.
- No surname, house name, patronymic, succession number, or earned epithet is
  assigned yet. Mononyms give these characters complete usable names without
  implying undocumented family relationships. This is a fictional design choice,
  not a claim about the conventions of any source culture.
- A name remains the same when a person changes rank. Count, Duke, and King retain
  the existing game's English title vocabulary; no real-world title is borrowed.
- Names are not grammatically gendered in this proposal. Existing court titles
  are preserved without assigning additional character biography or pronouns.
- Use the same vowels and penultimate stress as settlements, but favor three
  syllables, with occasional four-syllable names. Personal names do not take the
  settlement endings `-en`, `-esh`, `-or`, `-vek`, `-avel`, or `-un` as productive
  personal-name suffixes.
- Use a different order and reshaping of the source fragments rather than simply
  shortening the name of the person's capital. Sound similarity is not kinship.
- In later dialogue, use the full personal name until a nickname is deliberately
  authored. “Of [settlement]” may disambiguate residence, but is not a surname.

### Inspirations and personal meanings

Reuse sources S1–S9 and their research boundaries. The six linguistic sources
provide water, stone, seasonal, dwelling, and field fragments. All seven requested
inspirations contribute across the tradition, not necessarily to every name.

For personal names, turn environmental images into **fictional naming wishes**:
water becomes generosity or continuity; stone becomes steadiness; cultivated
ground becomes patient care; seasonal change becomes adaptability; a dwelling
becomes welcome or protection. These associations are authored here. They are
neither real-language translations nor claims about the bearer's actual character.
A generous-sounding name could belong to a selfish ruler.

The **Mogollon contribution remains conceptual, not lexical**. The sheltered
construction documented at Gila (S5) inspires naming wishes about sheltering
others, providing dependable support, and preserving a household through hard
seasons. In particular Tukazai, Sokirua, Kizumra, and Kisoruma use that imagery.
This does not purport to recover Mogollon personal names or naming ceremonies.
The sounds in these names are explicitly drawn from other documented fragments
and our own inventions. No source culture's clan, sacred, or personal names are
used as templates.

### Person-name construction ledger

Start with the extracted fragments already defined above: `am`, `ar`, `ru`, `rai`,
`so`, `sa`, `ki`, `pa`, `ze`, `tu`. Here `ar` is the shortened `adrar` form used
by `aruk`. Join two or three source fragments; reshape vowels and add a closing
consonant where useful. Added `l`, `m`, `k`, and vowel tails have **no borrowed
meaning**. Changes are recorded per name, not asserted as historical sound laws.
In particular, `-ai`, `-em`, and `-ek` do not mean “person,” “son,” or “ruler.”

Capital letters in the pronunciation column mark the stressed syllable. Hyphens
are pronunciation aids only, not part of the written names. Every row below uses
at least two linguistic sources. A sequence such as `tu + ki + ze` therefore
means Apache + Hopi + Navajo inspiration, not a grammatical phrase in any of them.

| Personal name | Say it | Source fragments and authored reshaping | Fictional naming wish |
| --- | --- | --- | --- |
| Amzuraki | am-zu-RA-ki | am + ze→zu + ru→ra + ki | one who shares sustenance with the household |
| Tukazai | tu-KA-zai | tu + ki→ka + ze→zai | a dependable shelter for others |
| Raisekum | rai-SE-kum | rai + so→se + ki→ku, closing m | renewal after lean seasons |
| Zerukam | ze-RU-kam | ze + ru + ki→ka, closing m | steadfast in sustaining others |
| Sokirua | so-ki-RU-a | so + ki + ru, final a | a welcoming home when rain returns |
| Arutazi | a-ru-TA-zi | ar + ru, overlap r; tu→ta + ze→zi | resourceful where the ridge yields little |
| Pazurail | pa-ZU-rail | pa + ze→zu + rai, closing l | patient care of difficult ground |
| Kizumra | ki-ZUM-ra | ki + ze→zu + am→m + ru→ra | support that holds a household together |
| Sarumek | sa-RU-mek | sa + ru + am→me, closing k | endurance through scarcity |
| Tusekrai | tu-SE-krai | tu + so→se + ki→k + rai | foresight before the dry season |
| Rukazem | ru-KA-zem | ru + ki→ka + ze, closing m | generosity with a firm foundation |
| Zepurai | ze-PU-rai | ze + pa→pu + rai | persistence in cultivation |
| Amkazu | am-KA-zu | am + ki→ka + ze→zu | a steady provider |
| Kisoruma | ki-so-RU-ma | ki + so + ru + am→ma | a household carried through changing seasons |
| Tuzemai | tu-ZE-mai | tu + ze + am→mai | reliability under pressure |
| Raisukel | rai-SU-kel | rai + so→su + ki→ke, closing l | adaptability without losing one's home |
| Sazumek | sa-ZU-mek | sa + ze→zu + am→me, closing k | resolve through lean times |
| Paruzemai | pa-ru-ZE-mai | pa + ru + ze, invented mai tail | careful nurture with lasting results |
| Zekirum | ze-KI-rum | ze + ki + ru, closing m | steadfast welcome |
| Sotumek | so-TU-mek | so + tu + am→me, closing k | preserving plenty for the days ahead |
| Arukazem | a-ru-KA-zem | ar + ru, overlap r; ki→ka + ze, closing m | finding a way to sustain the household |
| Tumazek | tu-MA-zek | tu + am→ma + ze, closing k | strength that sustains |
| Kirazuma | ki-ra-ZU-ma | ki + rai→ra + ze→zu + am→ma | welcome even in difficult country |
| Rupazem | ru-PA-zem | ru + pa + ze, closing m | nourishment earned through patient work |

The metaphors are naming associations, not compositional dictionary definitions:
there is no independently verified real word for “steadfast welcome” behind Zekirum.
The three- and four-syllable forms, different openings, and personal vowel tails
distinguish the register from settlement names while preserving the biome's sound.

### Ruler register: current desert courts

Authority for coverage: current `vcom/Scenes/Map.tscn`, `Docs/COURTS.md`, and
`vcom/Scripts/WorldMap/Court.gd`, inspected 2026-11-06. There are **24 independent
Court resources: 20 Counts, 3 Dukes, and 1 King**. Each resource below exists and is
attached to the stated capital. Proposed seat names come from the settlement
register above; they have not yet replaced the scene's placeholders.

| Court resource ID | Rank / jurisdiction | Proposed ruler display | Proposed seat | County |
| --- | --- | --- | --- | --- |
| Court_Kingdom4Capital | King / Kingdom 4 | King Amzuraki | Amaravel | 85 |
| Court_Duchy15Capital | Duke / Duchy 15 | Duke Tukazai | Arukesh | 73 |
| Court_Duchy16Capital | Duke / Duchy 16 | Duke Raisekum | Sazelor | 79 |
| Court_Duchy18Capital | Duke / Duchy 18 | Duke Zerukam | Kisarvek | 91 |
| Court_County074Capital | Count / County 74 | Count Sokirua | Kiraivesh | 74 |
| Court_County075Capital | Count / County 75 | Count Arutazi | Zoruvel | 75 |
| Court_County076Capital | Count / County 76 | Count Pazurail | Sazelen | 76 |
| Court_County077Capital | Count / County 77 | Count Kizumra | Soruvek | 77 |
| Court_County078Capital | Count / County 78 | Count Sarumek | Raituvesh | 78 |
| Court_County080Capital | Count / County 80 | Count Tusekrai | Kisaror | 80 |
| Court_County081Capital | Count / County 81 | Count Rukazem | Tumarvek | 81 |
| Court_County082Capital | Count / County 82 | Count Zepurai | Kiraiven | 82 |
| Court_County083Capital | Count / County 83 | Count Amkazu | Pazekor | 83 |
| Court_County084Capital | Count / County 84 | Count Kisoruma | Tuseren | 84 |
| Court_County086Capital | Count / County 86 | Count Tuzemai | Azekavel | 86 |
| Court_County087Capital | Count / County 87 | Count Raisukel | Zoruvesh | 87 |
| Court_County088Capital | Count / County 88 | Count Sazumek | Sazelavel | 88 |
| Court_County089Capital | Count / County 89 | Count Paruzemai | Amarkiven | 89 |
| Court_County090Capital | Count / County 90 | Count Zekirum | Pazekavel | 90 |
| Court_County092Capital | Count / County 92 | Count Sotumek | Tumaror | 92 |
| Court_County093Capital | Count / County 93 | Count Arukazem | Kisaravel | 93 |
| Court_County094Capital | Count / County 94 | Count Tumazek | Raituvek | 94 |
| Court_County095Capital | Count / County 95 | Count Kirazuma | Tuseresh | 95 |
| Court_County096Capital | Count / County 96 | Count Rupazem | Arukor | 96 |

**Overlapping seats:** counties 73, 79, and 91 contain the three ducal courts;
county 85 contains the royal court, which is also at Duchy 17's capital. They have
no separately authored count courts, and Duchy 17 has no separately authored duke
court. Thus all 24 county capital sites and all four ducal capital sites are
covered, without creating five extra people. Co-location alone does not establish
that a higher ruler legally holds every lower title: that political rule remains
undecided. If separate incumbents are later introduced at shared seats, name them
as additional people rather than silently renaming these rulers.

### Personal-name review and implementation notes

Individual quoted-name web queries were run for the initial candidates and their
replacements on 2026-11-06. This is an initial collision screen, not proof of
global uniqueness or a complete sound-alike review. Search hits were inspected as
collision evidence only; they were not used to invent additional etymologies.

Examples of revisions that mattered:

- `Amzuri` matched an [existing organization](https://amzuri.org/); the final royal
  name is **Amzuraki**, with a documented additional dwelling fragment.
- `Raiseki` matched an [existing company name](https://www.raiseki.co.jp/company.html);
  revised to **Raisekum**.
- `Kizumel` appeared as a character name in an [official Sword Art Online product
  listing](https://store.playstation.com/en-tw/product/HP0700-CUSA04864_00-SAO4KFJ015500000);
  revised to **Kizumra**.
- `Arukazi` appeared as a real personal name in [published reporting](https://punchng.com/delta-riverside-community-names-journalist-as-development-committee-chair/);
  revised to **Arukazem**.
- `Kisorai` matched a [commercial brand](https://www.seafeshop.com/shop-index-detail-1011.html);
  revised to **Kisoruma**. `Paruzek` matched an [existing surname in a business
  register](https://www.evi.gv.at/f/629140g); revised to **Paruzemai**.

Not every incidental match was treated as a copied name. Final `Amkazu` and
`Kirazuma` returned online handles; `Rukazem` returned apparent OCR/ordinary-word
matches; `Tumazek` appeared within unrelated running text. These remain disclosed
collisions, not verified cultural etymologies or known major fictional characters.
Do not claim that every final name returned no results. If any becomes too strongly
associated with another use, revise it while preserving the assignment ID.

Validation for this pass: 24 unique personal names, none identical to a proposed
settlement name; exact coverage of the 24 desert Court resources; rank, county,
seat, and resource attachment checked against the current scene. Read-aloud review
should particularly compare Sarumek/Sazumek and Arutazi/Arukazem. These pairs remain
distinct but may need more separation if playtesting finds them confusing.

When implementation is requested, set each listed Court's `ruler_name` to the
complete proposed display string, such as `King Amzuraki`. Keep the location's
`display_name` (currently Court of King/Count/Duke) separate, preserve favor and
other court fields, and check header wrapping in the court UI. No game scene,
scripts, court descriptions, family trees, or character statistics changed here.

## Tundra / frozen mountains naming

Added 2026-11-07. This is **Tundra Mountains / Kingdom 1** in the current map,
covering counties 1–24 and duchies 1–4. The user's requested inspirations are
Inuit, Aleut, Nordic, Nenet, and Siberian cultures/languages. Use all five across
both naming registers, with two or more specific linguistic sources per name;
do not force five recognizable fragments into every name.

This section adds **77 settlement names and 24 ruler names**. It follows the
earlier document-only workflow: assignments are proposals, and no scene labels
or court resources have been changed.

### Identity and source choices

Aim for inhabited cold uplands: snow cover, footholds, river approaches, supplies,
shelter, and the return of travelers. The setting includes seasonal life, not just
perpetual blizzards. The names should feel firm and compact when spoken.

The requested labels are not five discrete languages. Here **Nenets** is the
spelling used for the user's Nenet inspiration; **Evenki** provides a specific
additional Siberian source. Nenets also belongs to the Siberian context, so those
categories overlap. Nordic is represented by Norwegian and Icelandic vocabulary,
not by adopting a generalized Viking naming system. Aleut/Unangam Tunuu is kept
distinct from Inuit/Inuktut. Their environments and histories are not identical.

| Inspiration | Specific source and verified vocabulary | Use in this fictional tradition |
| --- | --- | --- |
| Inuit | South Qikiqtaaluk Inuktut in Pirurvik's Tusaalanga: `nuna`, land; `tupiq`, tent. [T1] | Shortened land and shelter fragments. Do not reuse the lesson's real personal or community names. |
| Aleut | Unangam Tunuu: `tanax̂`, land, marked Eastern/Atkan in APIA's curriculum. [T2] | Reshaped ground/footing fragments. The curriculum's English search text preserves the special character better than its PDF text extraction. |
| Nordic | Norwegian `fjell`, mountain/upland; Icelandic `snjór`, snow. [T3, T4] | Reshaped ridge and snow fragments; restrained consonant clusters. No borrowed gods, saga heroes, patronymic system, or ready-made `-heim/-fjord` place templates. |
| Nenets | Yamal Nenets `syra`, snow, also winter, as documented by Roza Laptander. [T5] | Snow-season roots and an environmental emphasis on judging conditions and preparing for travel. |
| Siberian | Evenki `bira`, river; `imanna`, snow; `mu` / `mu:`, water, in the modern comparison column of Weston's vocabulary study. [T6] | River approaches, snow, and provisions. These entries are not a claim to represent every Siberian language or every Evenki dialect. |

The source words above are documented vocabulary. Every mixed root, name,
settlement ending, and personal naming wish below is **invented here**. These are
not valid translations or reconstructed ancestral forms. No source personal names,
clan names, naming ceremonies, sacred identities, or kinship rules are adopted.

### Sound, construction, and differentiation

- **Stress the first syllable**, for both settlements and people. This deliberately
  distinguishes this biome from the desert's penultimate stress.
- Vowels: `a` as in father, `e` as in bed, `i` as in machine, `o` as a plain
  rounded o, and `u` as in rule. Here **y is a vowel pronounced like i**; it never
  means the English consonant in “yes.” This differs from the desert spelling rule.
- Hard k, unvoiced s, ordinary f, and modest clusters such as `sn`, `lt`, `rn`,
  and `tup-r`. No silent final letters. This is a fictional reading convention,
  not pronunciation guidance for the source languages.
- Settlements generally have two or three syllables and consonant endings.
  Person names favor three syllables, often ending in a vowel or a distinct final
  consonant. Do not add the settlement suffixes mechanically to make people.
- Shorten roots, blend sources, and log inserted sounds or reversals. Never present
  a few shared letters as proof of a real etymology.
- Use plain Latin display spelling. Real orthographic distinctions remain in the
  research ledger; the game forms do not pretend to preserve them.
- Select a name image, blend two or more sources, check it aloud and against the
  existing register, screen exact spellings, and record a stable scene/resource ID.
  The written assignments below are the authority, not a random generator.
- The first allocation distributes root families across the kingdom; it does not
  assign one real-world inspiration to a duchy. Recurring roots are shared fictional
  vocabulary, not ethnicity, ancestry, or a rank code.

### Mixed settlement roots

These are whole fictional stems. The extracted pieces are not asserted to be
grammatical morphemes of the original languages. Added sounds have no independent
borrowed meaning. The root's fictional sense supplies the name's environmental
image; the ending supplies the settlement image.

| Root | Syllables | Construction | Fictional sense |
| --- | --- | --- | --- |
| nufel | nu-fel | nuna → nu + fjell → fel | upland ground |
| tanfel | tan-fel | tanax̂ → tan + fjell → fel | mountain footing |
| sirum | si-rum | syra → sir + mu → um (reversed) | water drawn from snow |
| birnun | bir-nun | bira → bir + nuna → nun | ground beside a river |
| snetan | sne-tan | snjór → sne + tanax̂ → tan | snow-covered ground |
| tuprel | tup-rel | tupiq → tup + fjell → rel (f replaced by r) | shelter below a ridge |
| imnel | im-nel | imanna → im + fjell → nel (f replaced by n) | snow on the heights |
| syrat | si-rat | syra → syr + tanax̂ → at (ta reversed) | winter stopping-ground |
| tanbir | tan-bir | tanax̂ → tan + bira → bir | river approach |
| nurim | nu-rim | nuna → nu + imanna → im, inserted r | snow-covered open country |
| feltup | fel-tup | fjell → fel + tupiq → tup | upland shelter |
| sytan | si-tan | syra → sy + tanax̂ → tan | ground used in the snow season |
| birsnel | bir-snel | bira → bir + snjór → sne, closing l | snow-fed river |
| tansyr | tan-sir | tanax̂ → tan + syra → syr | seasonal return-ground |
| felyr | fel-ir | fjell → fel + syra → yr (s removed) | winter ridge |
| nuksir | nuk-sir | nuna → nu + syra → sir, inserted k | firm ground under snow |

### Invented settlement endings

| Ending | Fictional sense |
| --- | --- |
| -ask | gathering settlement |
| -ek | sheltered dwelling cluster |
| -om | provisioning settlement |
| -ust | route stop |
| -al | inhabited terrace |
| -ir | return camp |

Join root + ending directly, with no unstated sound changes. These endings are
newly assigned fictional forms, not borrowed locative suffixes. A name does not
determine present size or rank: a city can retain an old camp name.

For example, **Nufelask** (`NU-fel-ask`) suggests an upland gathering settlement;
**Felyrom** (`FEL-ir-om`) suggests a provision store on a winter ridge.
Neither asserts a real structure or landscape feature at its assigned coordinate.

Some names use a second environmental fragment instead of a settlement ending,
including the collision revisions below. Their stories and exact construction
appear in the exception ledger; do not silently re-parse them as suffix forms.

| Name | Construction | Fictional name image |
| --- | --- | --- |
| Syratnuk | syrat + nuna→nu + k | winter camp on firm ground |
| Tanfelim | tanfel + imanna→im | snowbound mountain footing |
| Sirumtup | sirum + tupiq→tup | shelter supplied by snow-water |
| Syratfel | syrat + fjell→fel | winter camp on a ridge |
| Sirumnuk | sirum + nuna→nu + k | snow-water ground |
| Tanbirfel | tanbir + fjell→fel | mountain river approach |
| Nurimtup | nurim + tupiq→tup | shelter in open snowy country |
| Nurimfel | nurim + fjell→fel | heights above snowy open ground |
| Nufeltan | nufel + tanax̂→tan | settled upland ground |

### Tundra settlement assignments

Source: current `vcom/Scenes/Map.tscn`, settlement nodes with
`metadata/kingdom = 1`, inspected 2026-11-07. **77 unique nodes: 1 kingdom
capital, 3 duchy capitals, 20 county capitals, 11 villages, and 42 hamlets.**
IDs below are relative to `Settlements/<group>/`; groups are given by the table.

**Geographic limit:** meanings are proposed name stories, not an audit of local
terrain or buildings. No unverified river, storehouse, pasture, ice road, or terrace
is asserted to exist at a particular node. Inspect current geography before using
one of these meanings as an in-game description. Initial allocation prioritizes
distinct naming and complete coverage, not geographic matching.

#### Capitals

| Node | County | Name | Components | Fictional name image |
| --- | --- | --- | --- | --- |
| Kingdom1Capital | 13 | Nufelask | nufel + ask | gathering settlement; upland ground |
| Duchy01Capital | 1 | Syratnuk | syrat + nuna→nu + k | winter camp on firm ground |
| Duchy02Capital | 7 | Felyrom | felyr + om | provisioning settlement; winter ridge |
| Duchy04Capital | 19 | Tuprelust | tuprel + ust | route stop; shelter below a ridge |
| County002Capital | 2 | Birsnelal | birsnel + al | inhabited terrace; snow-fed river |
| County003Capital | 3 | Birnunir | birnun + ir | return camp; ground beside a river |
| County004Capital | 4 | Feltupask | feltup + ask | gathering settlement; upland shelter |
| County005Capital | 5 | Tanfelim | tanfel + imanna→im | snowbound mountain footing |
| County006Capital | 6 | Tanbirom | tanbir + om | provisioning settlement; river approach |
| County008Capital | 8 | Nuksirust | nuksir + ust | route stop; firm ground under snow |
| County009Capital | 9 | Imnelal | imnel + al | inhabited terrace; snow on the heights |
| County010Capital | 10 | Tansyrir | tansyr + ir | return camp; seasonal return-ground |
| County011Capital | 11 | Snetanask | snetan + ask | gathering settlement; snow-covered ground |
| County012Capital | 12 | Sytanek | sytan + ek | sheltered dwelling cluster; ground used in the snow season |
| County014Capital | 14 | Sirumom | sirum + om | provisioning settlement; water drawn from snow |
| County015Capital | 15 | Nurimust | nurim + ust | route stop; snow-covered open country |
| County016Capital | 16 | Nufelir | nufel + ir | return camp; upland ground |
| County017Capital | 17 | Syratask | syrat + ask | gathering settlement; winter stopping-ground |
| County018Capital | 18 | Felyrek | felyr + ek | sheltered dwelling cluster; winter ridge |
| County020Capital | 20 | Tuprelom | tuprel + om | provisioning settlement; shelter below a ridge |
| County021Capital | 21 | Birsnelust | birsnel + ust | route stop; snow-fed river |
| County022Capital | 22 | Birnunal | birnun + al | inhabited terrace; ground beside a river |
| County023Capital | 23 | Feltupir | feltup + ir | return camp; upland shelter |
| County024Capital | 24 | Tanfelask | tanfel + ask | gathering settlement; mountain footing |

#### Villages

| Node | County | Name | Components | Fictional name image |
| --- | --- | --- | --- | --- |
| County002Village1 | 2 | Tanbirek | tanbir + ek | sheltered dwelling cluster; river approach |
| County004Village1 | 4 | Nuksirom | nuksir + om | provisioning settlement; firm ground under snow |
| County007Village1 | 7 | Imnelust | imnel + ust | route stop; snow on the heights |
| County008Village1 | 8 | Tansyral | tansyr + al | inhabited terrace; seasonal return-ground |
| County010Village1 | 10 | Snetanir | snetan + ir | return camp; snow-covered ground |
| County011Village1 | 11 | Sytanask | sytan + ask | gathering settlement; ground used in the snow season |
| County012Village1 | 12 | Sirumtup | sirum + tupiq→tup | shelter supplied by snow-water |
| County014Village1 | 14 | Nurimtup | nurim + tupiq→tup | shelter in open snowy country |
| County018Village1 | 18 | Nufelal | nufel + al | inhabited terrace; upland ground |
| County018Village2 | 18 | Syratir | syrat + ir | return camp; winter stopping-ground |
| County020Village1 | 20 | Felyrask | felyr + ask | gathering settlement; winter ridge |

#### Hamlets

| Node | County | Name | Components | Fictional name image |
| --- | --- | --- | --- | --- |
| County002Hamlet1 | 2 | Tuprelek | tuprel + ek | sheltered dwelling cluster; shelter below a ridge |
| County002Hamlet2 | 2 | Birsnelom | birsnel + om | provisioning settlement; snow-fed river |
| County003Hamlet1 | 3 | Birnunust | birnun + ust | route stop; ground beside a river |
| County003Hamlet2 | 3 | Feltupal | feltup + al | inhabited terrace; upland shelter |
| County003Hamlet3 | 3 | Tanfelir | tanfel + ir | return camp; mountain footing |
| County004Hamlet1 | 4 | Tanbirask | tanbir + ask | gathering settlement; river approach |
| County004Hamlet2 | 4 | Nuksirek | nuksir + ek | sheltered dwelling cluster; firm ground under snow |
| County004Hamlet3 | 4 | Imnelom | imnel + om | provisioning settlement; snow on the heights |
| County004Hamlet4 | 4 | Tansyrust | tansyr + ust | route stop; seasonal return-ground |
| County007Hamlet1 | 7 | Snetanal | snetan + al | inhabited terrace; snow-covered ground |
| County007Hamlet2 | 7 | Sytanir | sytan + ir | return camp; ground used in the snow season |
| County007Hamlet3 | 7 | Sirumask | sirum + ask | gathering settlement; water drawn from snow |
| County008Hamlet1 | 8 | Nurimek | nurim + ek | sheltered dwelling cluster; snow-covered open country |
| County008Hamlet2 | 8 | Nufelust | nufel + ust | route stop; upland ground |
| County010Hamlet1 | 10 | Syratfel | syrat + fjell→fel | winter camp on a ridge |
| County010Hamlet2 | 10 | Felyrir | felyr + ir | return camp; winter ridge |
| County010Hamlet3 | 10 | Tuprelask | tuprel + ask | gathering settlement; shelter below a ridge |
| County010Hamlet4 | 10 | Birsnelek | birsnel + ek | sheltered dwelling cluster; snow-fed river |
| County010Hamlet5 | 10 | Birnunom | birnun + om | provisioning settlement; ground beside a river |
| County011Hamlet1 | 11 | Feltupust | feltup + ust | route stop; upland shelter |
| County011Hamlet2 | 11 | Tanfelal | tanfel + al | inhabited terrace; mountain footing |
| County011Hamlet3 | 11 | Tanbirir | tanbir + ir | return camp; river approach |
| County012Hamlet1 | 12 | Nuksirask | nuksir + ask | gathering settlement; firm ground under snow |
| County012Hamlet2 | 12 | Imnelek | imnel + ek | sheltered dwelling cluster; snow on the heights |
| County012Hamlet3 | 12 | Tansyrom | tansyr + om | provisioning settlement; seasonal return-ground |
| County013Hamlet1 | 13 | Snetanust | snetan + ust | route stop; snow-covered ground |
| County013Hamlet2 | 13 | Sytanal | sytan + al | inhabited terrace; ground used in the snow season |
| County014Hamlet1 | 14 | Sirumnuk | sirum + nuna→nu + k | snow-water ground |
| County014Hamlet2 | 14 | Nurimfel | nurim + fjell→fel | heights above snowy open ground |
| County014Hamlet3 | 14 | Nufeltan | nufel + tanax̂→tan | settled upland ground |
| County014Hamlet4 | 14 | Syratust | syrat + ust | route stop; winter stopping-ground |
| County015Hamlet1 | 15 | Felyral | felyr + al | inhabited terrace; winter ridge |
| County015Hamlet2 | 15 | Tuprelir | tuprel + ir | return camp; shelter below a ridge |
| County018Hamlet1 | 18 | Birsnelask | birsnel + ask | gathering settlement; snow-fed river |
| County018Hamlet2 | 18 | Birnunek | birnun + ek | sheltered dwelling cluster; ground beside a river |
| County018Hamlet3 | 18 | Feltupom | feltup + om | provisioning settlement; upland shelter |
| County019Hamlet1 | 19 | Tanfelust | tanfel + ust | route stop; mountain footing |
| County019Hamlet2 | 19 | Tanbirfel | tanbir + fjell→fel | mountain river approach |
| County019Hamlet3 | 19 | Nuksirir | nuksir + ir | return camp; firm ground under snow |
| County021Hamlet1 | 21 | Imnelask | imnel + ask | gathering settlement; snow on the heights |
| County021Hamlet2 | 21 | Tansyrek | tansyr + ek | sheltered dwelling cluster; seasonal return-ground |
| County024Hamlet1 | 24 | Snetanom | snetan + om | provisioning settlement; snow-covered ground |

### Tundra person naming

Use the established first-pass personal format: **title + one personal name**,
with no invented family tree or mandatory surname. The name forms are not
grammatically gendered. Count, Duke, and King remain the game's title vocabulary.
A person's name stays the same if their rank changes. Additional house names,
nicknames, and succession numerals remain separate future decisions.

Personal meanings are **naming wishes**, not literal source-language translations
or character traits. Snow can suggest patience; ground and mountains can suggest
steadiness; shelter can suggest welcome; a river route can suggest return or good
judgment. These associations are authored for the setting.

The following ledger records every personal spelling, pronunciation, and source
combination. `mu` comes from Evenki, not the Apache `tu` used in the desert;
a similar sound is not license to transfer that desert etymology. The ruler and
their seat can share some sound material, but no ruler takes their entire seat
name as a personal name.

| Personal name | Say it | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Birtunel | BIR-tu-nel | bira→bir + tupiq→tu + fjell→nel | one who brings travelers to shelter |
| Tanfelmu | TAN-fel-mu | tanax̂→tan + fjell→fel + mu | steadiness with the means to sustain others |
| Syrumta | SI-rum-ta | syra→syr + mu→um + tanax̂→ta | prepared for winter's demands |
| Nufelmi | NU-fel-mi | nuna→nu + fjell→fel + mu→mi | a sustaining presence on difficult ground |
| Snetumi | SNE-tu-mi | snjór→sne + tupiq→tu + mu→mi | care that carries a household through snow |
| Felnyra | FEL-ni-ra | fjell→fel + nuna→ny + syra→ra | steadfast through the winter |
| Tupimrel | TUP-im-rel | tupiq→tup + imanna→im + fjell→rel | shelter when the heights close in |
| Nusyrka | NU-sir-ka | nuna→nu + syra→syr, invented ka tail | one who finds secure footing |
| Tanmurli | TAN-mur-li | tanax̂→tan + mu, invented rli tail | one who sustains the journey |
| Imfelna | IM-fel-na | imanna→im + fjell→fel + nuna→na | endurance above the snowline |
| Syrtuni | SIR-tu-ni | syra→syr + tupiq→tu + nuna→ni | one who makes winter habitable |
| Birmutal | BIR-mu-tal | bira→bir + mu + tanax̂→ta, closing l | a reliable source of help along the way |
| Felmunta | FEL-mun-ta | fjell→fel + mu + nuna→n + tanax̂→ta | support shared across hard country |
| Tunebri | TU-ne-bri | tupiq→tu + nuna→ne + bira→bri (contracted) | one who welcomes returning travelers |
| Sneryma | SNE-ri-ma | snjór→sne + syra→ry + imanna→ma | patience through a long winter |
| Nubirta | NU-bir-ta | nuna→nu + bira→bir + tanax̂→ta | one who remembers the way home |
| Tanfilra | TAN-fil-ra | tanax̂→tan + fjell→fil + syra→ra | resolve through changing seasons |
| Imtupsa | IM-tup-sa | imanna→im + tupiq→tup + syra→sa | a welcome in snow season |
| Syrfeli | SIR-fe-li | syra→syr + fjell→fel, final i | clear judgment in exposed country |
| Birnuki | BIR-nu-ki | bira→bir + nuna→nu, invented ki tail | one who notices the safe route |
| Tupsnela | TUP-sne-la | tupiq→tup + snjór→sne, invented la tail | shelter offered freely |
| Felnumra | FEL-num-ra | fjell→fel + nuna→nu + mu→m + syra→ra | strength that helps others endure |
| Nusneti | NU-sne-ti | nuna→nu + snjór→sne, invented ti tail | one who returns despite the season |
| Mufeltan | MU-fel-tan | mu + fjell→fel + tanax̂→tan | provision made before hardship |

### Tundra ruler assignments

There are **24 currently authored courts: 20 Counts, 3 Dukes, and 1 King**.
The Court resource IDs below are verified against the scene. Seat names refer
to this document's proposals, not labels already applied in game.

| Court resource ID | Rank / jurisdiction | Proposed ruler display | Proposed seat | County |
| --- | --- | --- | --- | --- |
| Court_Kingdom1Capital | King / Kingdom 1 | King Birtunel | Nufelask | 13 |
| Court_Duchy01Capital | Duke / Duchy 1 | Duke Tanfelmu | Syratnuk | 1 |
| Court_Duchy02Capital | Duke / Duchy 2 | Duke Syrumta | Felyrom | 7 |
| Court_Duchy04Capital | Duke / Duchy 4 | Duke Nufelmi | Tuprelust | 19 |
| Court_County002Capital | Count / County 2 | Count Snetumi | Birsnelal | 2 |
| Court_County003Capital | Count / County 3 | Count Felnyra | Birnunir | 3 |
| Court_County004Capital | Count / County 4 | Count Tupimrel | Feltupask | 4 |
| Court_County005Capital | Count / County 5 | Count Nusyrka | Tanfelim | 5 |
| Court_County006Capital | Count / County 6 | Count Tanmurli | Tanbirom | 6 |
| Court_County008Capital | Count / County 8 | Count Imfelna | Nuksirust | 8 |
| Court_County009Capital | Count / County 9 | Count Syrtuni | Imnelal | 9 |
| Court_County010Capital | Count / County 10 | Count Birmutal | Tansyrir | 10 |
| Court_County011Capital | Count / County 11 | Count Felmunta | Snetanask | 11 |
| Court_County012Capital | Count / County 12 | Count Tunebri | Sytanek | 12 |
| Court_County014Capital | Count / County 14 | Count Sneryma | Sirumom | 14 |
| Court_County015Capital | Count / County 15 | Count Nubirta | Nurimust | 15 |
| Court_County016Capital | Count / County 16 | Count Tanfilra | Nufelir | 16 |
| Court_County017Capital | Count / County 17 | Count Imtupsa | Syratask | 17 |
| Court_County018Capital | Count / County 18 | Count Syrfeli | Felyrek | 18 |
| Court_County020Capital | Count / County 20 | Count Birnuki | Tuprelom | 20 |
| Court_County021Capital | Count / County 21 | Count Tupsnela | Birsnelust | 21 |
| Court_County022Capital | Count / County 22 | Count Felnumra | Birnunal | 22 |
| Court_County023Capital | Count / County 23 | Count Nusneti | Feltupir | 23 |
| Court_County024Capital | Count / County 24 | Count Mufeltan | Tanfelask | 24 |

**Shared seats:** counties 1, 7, and 19 contain the ducal courts. County 13 contains
the royal court and is also Duchy 3's capital. There are no additional count courts
at those four sites, nor a separate Duke of Duchy 3 resource. All county-capital
sites and all four ducal seats are covered without inventing five extra people.
Co-location does not by itself settle the constitutional question of who holds
a lower title; keep that undecided, as in the desert register.

### Collision screening, validation, and status

On 2026-11-07, individual quoted-name queries were submitted for all 101 original
candidate spellings (77 settlements + 24 people), in batches of four separate
queries, followed by queries for revised forms. Results were examined for
recognizable place, person, business, and fictional-name matches. Absence of a
result is not proof of uniqueness. OCR fragments, automatic anagram pages, and
incidental usernames were distinguished from established names.

Examples of revisions:

| Rejected form | Evidence / reason | Final form |
| --- | --- | --- |
| Syratek | [Existing company/trademark](https://www.findcompany.com.tw/trademark/01515291_100032811) | Syratnuk |
| Tanfelek | [Existing fictional town in a roleplaying account](https://bigyojdr.blogspot.com/2017/04/) | Tanfelim |
| Sirumek | [Existing pharmaceutical trademark](https://www.sakpatenti.gov.ge/media/publication_pdf/BL1715.pdf) | Sirumtup |
| Syratal | Existing German place/facility usage in [local authority material](https://www2.vogtlandkreis.de/loom/formulare/Behindertenplan08_Teil_III.pdf) | Syratfel |
| Sirumir | Existing development name in [municipal documentation](https://majorvieira.sc.gov.br/uploads/sites/382/2025/03/Lei-no-2.733-de-27-de-marco-de-2025-Autoriza-o-Poder-Executivo-a-adquirir-imoveis-e-da-outras-providencias.pdf) | Sirumnuk |
| Tanferi | [Existing surname in municipal staff information](https://comune.castelbelforte.mn.it/it/page/ufficio-servizi-finanziari) | Tanfelmu |
| Imfelsa | [Existing business name](https://tytenlinea.com/imfelsa/) | Imfelna |

Additional revised candidates: Tanbiral → Tanbirfel, Nurimom → Nurimtup,
Nurimask → Nurimfel, Nufelom → Nufeltan, Tanmuri → Tanmurli,
Tupimra → Tupimrel, Birmuta → Birmutal, Felmuni → Felmunta,
and Felnima → Felnumra. These removed personal, product, or other recognizable
name matches. The intermediate Tanfelri was also replaced after a surname site's
automatic spelling-variant match; that result was not treated as linguistic proof.

Some retained spellings have incidental search hits: Sytanek and Sirumom as
handles; Imnelal, Imnelek, Syratust, Tanfelim, and Nurimfel in apparent OCR noise;
Nufelmi, Snetumi, and Imfelna in automatic anagram pages; Feltupir, Tanbirek,
Imnelom, Tunebri, and Nubirta within unrelated running text. This is **not** a
claim that all final names are absent from the internet. Broader sound-alike and
native-speaker review remain open. No source personal names were intentionally
copied and no authenticity claim is made.

Validation: exactly 77 settlement IDs and 24 Court resource IDs matched the
current Kingdom 1 scene entries, including counties, ranks, resource attachments,
and seat-name correspondence. All 101 tundra names are distinct, and none exactly
matches a desert name in this document. The first-stress reading rule and root
ledger apply to every assignment. Similar root families remain an intentional
feature; spoken confusion between neighboring names should be revisited in playtests.

Names and rules are proposals, not individually approved canon. No game labels,
resources, scripts, character descriptions, or terrain have changed. When names
are implemented, change only the corresponding settlement `display_name` and
Court `ruler_name` fields, preserve existing manual edits, then inspect map
tooltips and court headers in game. Do not claim runtime testing for this
documentation-only pass.

### Tundra research sources

Consulted 2026-11-07. These sources support the vocabulary and scope notes above,
not the invented compound names or their fictional meanings.

- **T1:** Pirurvik, [Tusaalanga lesson 1, South Qikiqtaaluk](https://www.tusaalanga.ca/lesson/1),
  grammar section: `nuna` and `tupiq`. No personal names from the dialogue were borrowed.
- **T2:** Aleutian Pribilof Islands Association, [Qaqamiiĝux̂ curriculum, Unit 4](https://www.apiai.org/wp-content/uploads/2017/06/Qaqaqmiigux-Curriculum_Unit-4.pdf),
  printed p. 60 / PDF p. 2: `tanax̂`, land; Eastern/Atkan designation.
- **T3:** Norwegian Language Council / University of Bergen,
  [Bokmålsordboka: fjell](https://ordbokene.no/bm/15001).
- **T4:** Árni Magnússon Institute,
  [Icelandic–English dictionary: snjór](https://enska.arnastofnun.is/en/ord/38183/tungumal/EN).
- **T5:** Roza Laptander (2023), [The Yamal Nenets' traditional and contemporary
  environmental knowledge of snow, ice, and permafrost](https://par.nsf.gov/servlets/purl/10442791),
  *Ecology and Society* 28(3):6. Source for `syra` and the environmental emphasis
  on conditions and travel; not a personal-naming source.
- **T6:** David Weston (2016), [An Evenki vocabulary from the papers of
  Theophilus Siegfried Bayer](https://www.gla.ac.uk/media/Media_489484_smxx.pdf),
  University of Glasgow, PDF pp. 3–4. Use the modern comparison forms sourced
  there to Nedjalkov (1997) / Boldyrev (1988), not an indiscriminate copy of the
  eighteenth-century transcription.

## Volcanic Mountains / Ruins naming

### Scope and identity

Requested 2026-11-07: Hawaiian, Japanese, and Indonesian inspiration for both
settlements and people. As with the earlier traditions, use all inspirations
across the register and blend a smaller selection within each name. Every
settlement stem below combines at least two source languages; person names do too.

The intended impression is inhabited volcanic country: ash slopes, river-cut
stone, mountain valleys, cultivated ground, old masonry, and rebuilding.
Ruins belong to the fictional setting; they do not characterize the living
cultures supplying the vocabulary. Renewal and ordinary settlement life matter
as much as fire. No real royal names, religious figures, famous mountains, or
existing fictional place names are intentionally borrowed.

This pass covers **Kingdom 2** in `vcom/Scenes/Map.tscn`: **157 settlements**
(1 kingdom capital, 3 duchy capitals, 20 county capitals, 47 villages, 86 hamlets)
and **24 existing courts** (1 king, 3 dukes, 20 counts). These remain documentation
assignments; scene labels and court resources are unchanged.

### Source palette

| Inspiration | Selected words and source | Design contribution |
| --- | --- | --- |
| Hawaiian | `lehu`, ash; `pōhaku`, stone/rock; `ulu`, grow [V1–V3] | Ash, durable stone, and returning growth; shortened and recombined with Japanese or Indonesian material. |
| Japanese | `yama`, mountain; `tani`, valley; `kawa`, river [V4–V6] | Terrain and movement through mountain country. These ordinary words do not import Japanese surnames or actual place-name constructions. |
| Indonesian | Bahasa Indonesia `abu`, ash; `api`, fire; `tanah`, soil; `batu`, stone [V7] | Fire, settled ash, workable ground, and reused stone. Bahasa Indonesia is the specific lexical selection, not a stand-in for every language of Indonesia. |

Source glosses are not translations of finished names. Hawaiian `ulu` here is
growth, not `ʻulu` (breadfruit). Preserve source spelling in the ledger; the
fictional spelling has its own rules. The appendix used for Indonesian also
contains regional-language columns; only its Indonesian column is borrowed.

### Sound and construction rules

- Use five vowels, `a e i o u`, approximately ah, eh, ee, oh, oo. Each written
  vowel forms a syllable; `y` is the consonant in *yes*. No silent letters.
- Favor open syllables and flowing sequences of `h k l m n p t w y`, with
  `b r s v` also available. Keep `r` and `l` distinct. This combined inventory
  is invented, not an assertion about any source language's phonology.
- Stress the **third-last syllable**: Lehamarava = le-ha-MA-ra-va;
  Lehabumi = le-HA-bu-mi. This differs from desert penultimate stress and tundra
  initial stress. Hyphens and capitals in pronunciation guides are not spelling.
- Settlement names use a three-syllable blended stem plus a two-syllable invented
  habitation ending. This first register consistently uses five syllables.
  Person names use four or five syllables and do not take settlement endings.
- Select ordinary environmental roots, shorten them, adjust vowels or consonants,
  and join the result. All such changes are authored transformations, not
  historical sound laws. Even when a full source word survives inside a compound,
  the whole name must be a new blend.
- Give each result a fictional name story or personal naming wish. These are
  semantic inventions, not authentic etymologies, biographies, or verified local
  terrain. An ash name does not establish an active volcano at that node.
- Let stems recur across county boundaries. Do not map Hawaiian, Japanese, and
  Indonesian elements onto separate fictional ethnic groups or ranks.

### Settlement stem ledger

The spellings at the left are fictional. The construction column records the
actual source choices, including deliberate contractions and vowel changes.

| Stem | Syllables | Source transformations | Fictional image |
| --- | --- | --- | --- |
| lehama | le-ha-ma | lehu→leh + yama→ama | ash-covered heights |
| pohani | po-ha-ni | pōhaku→poha + tani→ni | stone-sided valley |
| ulaya | u-la-ya | ulu→ula + yama→ya | regrowth on the heights |
| batelu | ba-te-lu | batu→bat + lehu→elu | stone amid ash |
| yamolu | ya-mo-lu | yama→yamo + ulu→lu | renewed mountain ground |
| tanahu | ta-na-hu | tani→tana + lehu→hu | ash-settled valley |
| apohu | a-po-hu | api→a + pōhaku→pohu | fire-marked stone |
| abule | a-bu-le | abu + lehu→le | deep ash ground |
| pokawa | po-ka-wa | pōhaku→po + kawa | river-cut stone |
| tanulu | ta-nu-lu | tanah→tan + ulu | cultivated soil |
| lebatu | le-ba-tu | lehu→le + batu | ash over old masonry |
| poyama | po-ya-ma | pōhaku→po + yama | rocky heights |
| hutale | hu-ta-le | lehu→hu + tanah→ta, invented le | settled ash soil |
| ulapi | u-la-pi | ulu→ul + api | regrowth after burning |
| kawelu | ka-we-lu | kawa→kaw + lehu→elu | river through ash ground |
| yatanu | ya-ta-nu | yama→ya + tanah→tanu | mountain soil |
| batani | ba-ta-ni | batu→ba + tani | stone valley |
| tanapi | ta-na-pi | tani→tan + api | fire-marked valley |
| kawabu | ka-wa-bu | kawa + abu→bu | riverborne ash |
| yamabu | ya-ma-bu | yama + abu→bu | ash mountain |
| kabatu | ka-ba-tu | kawa→ka + batu | river stones |
| tabuya | ta-bu-ya | tani→ta + abu→bu + yama→ya | ash valley between heights |
| huluma | hu-lu-ma | lehu→hu + ulu→lu + yama→ma | new growth on an ash slope |
| pobumi | po-bu-mi | pōhaku→po + abu→bu + yama→mi | stone emerging from ash |

### Invented settlement endings

These endings and their senses are authored for this kingdom. They are not
claimed to be Hawaiian, Japanese, or Indonesian morphemes. They describe a
proposed settlement history, not political rank or verified scene content.

| Ending | Fictional sense |
| --- | --- |
| rava | rebuilt quarter |
| nelo | terraced habitation |
| meka | gathering court |
| sulo | workshop settlement |
| kera | reused-stone settlement |
| vani | route stop |
| remu | garden settlement |

For example, **Lehamarava** combines `lehama` (ash-covered heights) with
`rava` (rebuilt quarter): a proposed story of habitation rebuilt on ash-covered
heights. The following tables expose each combination so its source ancestry can
be traced through the stem ledger. Stems and endings were distributed across the
scene inventory for variety; detailed terrain placement has not been audited.

### Settlement assignments

Node identifiers are exact scene node names. County and duchy numbers are scene
metadata, not proposed names for the political territories.

#### Capitals

| Scene node | County | Duchy | Proposed name | Construction | Fictional name story |
| --- | --- | --- | --- | --- | --- |
| `Kingdom2Capital` | 31 | 6 | Lehamarava | lehama + rava | rebuilt quarter amid ash-covered heights |
| `Duchy05Capital` | 25 | 5 | Abulenelo | abule + nelo | terraced habitation amid deep ash ground |
| `Duchy07Capital` | 37 | 7 | Kawelumeka | kawelu + meka | gathering court amid river through ash ground |
| `Duchy08Capital` | 43 | 8 | Tabuyasulo | tabuya + sulo | workshop settlement amid ash valley between heights |
| `County026Capital` | 26 | 5 | Yamolukera | yamolu + kera | reused-stone settlement amid renewed mountain ground |
| `County027Capital` | 27 | 5 | Poyamavani | poyama + vani | route stop amid rocky heights |
| `County028Capital` | 28 | 5 | Kawaburemu | kawabu + remu | garden settlement amid riverborne ash |
| `County029Capital` | 29 | 5 | Pohanirava | pohani + rava | rebuilt quarter amid stone-sided valley |
| `County030Capital` | 30 | 5 | Pokawanelo | pokawa + nelo | terraced habitation amid river-cut stone |
| `County032Capital` | 32 | 6 | Yatanumeka | yatanu + meka | gathering court amid mountain soil |
| `County033Capital` | 33 | 6 | Hulumasulo | huluma + sulo | workshop settlement amid new growth on an ash slope |
| `County034Capital` | 34 | 6 | Tanahukera | tanahu + kera | reused-stone settlement amid ash-settled valley |
| `County035Capital` | 35 | 6 | Hutalevani | hutale + vani | route stop amid settled ash soil |
| `County036Capital` | 36 | 6 | Yamaburemu | yamabu + remu | garden settlement amid ash mountain |
| `County038Capital` | 38 | 7 | Ulayarava | ulaya + rava | rebuilt quarter amid regrowth on the heights |
| `County039Capital` | 39 | 7 | Tanulunelo | tanulu + nelo | terraced habitation amid cultivated soil |
| `County040Capital` | 40 | 7 | Batanimeka | batani + meka | gathering court amid stone valley |
| `County041Capital` | 41 | 7 | Pobumisulo | pobumi + sulo | workshop settlement amid stone emerging from ash |
| `County042Capital` | 42 | 7 | Apohukera | apohu + kera | reused-stone settlement amid fire-marked stone |
| `County044Capital` | 44 | 8 | Ulapivani | ulapi + vani | route stop amid regrowth after burning |
| `County045Capital` | 45 | 8 | Kabaturemu | kabatu + remu | garden settlement amid river stones |
| `County046Capital` | 46 | 8 | Batelurava | batelu + rava | rebuilt quarter amid stone amid ash |
| `County047Capital` | 47 | 8 | Lebatunelo | lebatu + nelo | terraced habitation amid ash over old masonry |
| `County048Capital` | 48 | 8 | Tanapimeka | tanapi + meka | gathering court amid fire-marked valley |

#### Villages

| Scene node | County | Duchy | Proposed name | Construction | Fictional name story |
| --- | --- | --- | --- | --- | --- |
| `County025Village1` | 25 | 5 | Lehamakera | lehama + kera | reused-stone settlement amid ash-covered heights |
| `County025Village2` | 25 | 5 | Abulevani | abule + vani | route stop amid deep ash ground |
| `County025Village3` | 25 | 5 | Kaweluremu | kawelu + remu | garden settlement amid river through ash ground |
| `County027Village1` | 27 | 5 | Tabuyarava | tabuya + rava | rebuilt quarter amid ash valley between heights |
| `County027Village2` | 27 | 5 | Yamolunelo | yamolu + nelo | terraced habitation amid renewed mountain ground |
| `County028Village1` | 28 | 5 | Poyamameka | poyama + meka | gathering court amid rocky heights |
| `County028Village2` | 28 | 5 | Kawabusulo | kawabu + sulo | workshop settlement amid riverborne ash |
| `County028Village3` | 28 | 5 | Pohanikera | pohani + kera | reused-stone settlement amid stone-sided valley |
| `County028Village4` | 28 | 5 | Pokawavani | pokawa + vani | route stop amid river-cut stone |
| `County029Village1` | 29 | 5 | Yatanuremu | yatanu + remu | garden settlement amid mountain soil |
| `County029Village2` | 29 | 5 | Hulumarava | huluma + rava | rebuilt quarter amid new growth on an ash slope |
| `County031Village1` | 31 | 6 | Tanahunelo | tanahu + nelo | terraced habitation amid ash-settled valley |
| `County032Village1` | 32 | 6 | Hutalemeka | hutale + meka | gathering court amid settled ash soil |
| `County032Village2` | 32 | 6 | Yamabusulo | yamabu + sulo | workshop settlement amid ash mountain |
| `County032Village3` | 32 | 6 | Ulayakera | ulaya + kera | reused-stone settlement amid regrowth on the heights |
| `County033Village1` | 33 | 6 | Tanuluvani | tanulu + vani | route stop amid cultivated soil |
| `County033Village2` | 33 | 6 | Bataniremu | batani + remu | garden settlement amid stone valley |
| `County034Village1` | 34 | 6 | Pobumirava | pobumi + rava | rebuilt quarter amid stone emerging from ash |
| `County035Village1` | 35 | 6 | Apohunelo | apohu + nelo | terraced habitation amid fire-marked stone |
| `County035Village2` | 35 | 6 | Ulapimeka | ulapi + meka | gathering court amid regrowth after burning |
| `County037Village1` | 37 | 7 | Kabatusulo | kabatu + sulo | workshop settlement amid river stones |
| `County037Village2` | 37 | 7 | Batelukera | batelu + kera | reused-stone settlement amid stone amid ash |
| `County037Village3` | 37 | 7 | Lebatuvani | lebatu + vani | route stop amid ash over old masonry |
| `County038Village1` | 38 | 7 | Tanapiremu | tanapi + remu | garden settlement amid fire-marked valley |
| `County038Village2` | 38 | 7 | Lehamanelo | lehama + nelo | terraced habitation amid ash-covered heights |
| `County038Village3` | 38 | 7 | Abulemeka | abule + meka | gathering court amid deep ash ground |
| `County039Village1` | 39 | 7 | Kawelusulo | kawelu + sulo | workshop settlement amid river through ash ground |
| `County039Village2` | 39 | 7 | Tabuyakera | tabuya + kera | reused-stone settlement amid ash valley between heights |
| `County039Village3` | 39 | 7 | Yamoluvani | yamolu + vani | route stop amid renewed mountain ground |
| `County039Village4` | 39 | 7 | Poyamaremu | poyama + remu | garden settlement amid rocky heights |
| `County040Village1` | 40 | 7 | Kawaburava | kawabu + rava | rebuilt quarter amid riverborne ash |
| `County040Village2` | 40 | 7 | Pohaninelo | pohani + nelo | terraced habitation amid stone-sided valley |
| `County040Village3` | 40 | 7 | Pokawameka | pokawa + meka | gathering court amid river-cut stone |
| `County040Village4` | 40 | 7 | Yatanusulo | yatanu + sulo | workshop settlement amid mountain soil |
| `County041Village1` | 41 | 7 | Hulumakera | huluma + kera | reused-stone settlement amid new growth on an ash slope |
| `County042Village1` | 42 | 7 | Tanahuvani | tanahu + vani | route stop amid ash-settled valley |
| `County042Village2` | 42 | 7 | Hutaleremu | hutale + remu | garden settlement amid settled ash soil |
| `County044Village1` | 44 | 8 | Yamaburava | yamabu + rava | rebuilt quarter amid ash mountain |
| `County045Village1` | 45 | 8 | Ulayanelo | ulaya + nelo | terraced habitation amid regrowth on the heights |
| `County045Village2` | 45 | 8 | Tanulumeka | tanulu + meka | gathering court amid cultivated soil |
| `County045Village3` | 45 | 8 | Batanisulo | batani + sulo | workshop settlement amid stone valley |
| `County046Village1` | 46 | 8 | Pobumikera | pobumi + kera | reused-stone settlement amid stone emerging from ash |
| `County046Village2` | 46 | 8 | Apohuvani | apohu + vani | route stop amid fire-marked stone |
| `County047Village1` | 47 | 8 | Ulapiremu | ulapi + remu | garden settlement amid regrowth after burning |
| `County048Village1` | 48 | 8 | Kabaturava | kabatu + rava | rebuilt quarter amid river stones |
| `County048Village2` | 48 | 8 | Batelunelo | batelu + nelo | terraced habitation amid stone amid ash |
| `County048Village3` | 48 | 8 | Lebatumeka | lebatu + meka | gathering court amid ash over old masonry |

#### Hamlets

| Scene node | County | Duchy | Proposed name | Construction | Fictional name story |
| --- | --- | --- | --- | --- | --- |
| `County025Hamlet1` | 25 | 5 | Tanapisulo | tanapi + sulo | workshop settlement amid fire-marked valley |
| `County025Hamlet2` | 25 | 5 | Lehamavani | lehama + vani | route stop amid ash-covered heights |
| `County025Hamlet3` | 25 | 5 | Abuleremu | abule + remu | garden settlement amid deep ash ground |
| `County025Hamlet4` | 25 | 5 | Kawelurava | kawelu + rava | rebuilt quarter amid river through ash ground |
| `County025Hamlet5` | 25 | 5 | Tabuyanelo | tabuya + nelo | terraced habitation amid ash valley between heights |
| `County027Hamlet1` | 27 | 5 | Yamolumeka | yamolu + meka | gathering court amid renewed mountain ground |
| `County027Hamlet2` | 27 | 5 | Poyamasulo | poyama + sulo | workshop settlement amid rocky heights |
| `County027Hamlet3` | 27 | 5 | Kawabukera | kawabu + kera | reused-stone settlement amid riverborne ash |
| `County027Hamlet4` | 27 | 5 | Pohanivani | pohani + vani | route stop amid stone-sided valley |
| `County028Hamlet1` | 28 | 5 | Pokawaremu | pokawa + remu | garden settlement amid river-cut stone |
| `County028Hamlet2` | 28 | 5 | Yatanurava | yatanu + rava | rebuilt quarter amid mountain soil |
| `County028Hamlet3` | 28 | 5 | Hulumanelo | huluma + nelo | terraced habitation amid new growth on an ash slope |
| `County029Hamlet1` | 29 | 5 | Tanahumeka | tanahu + meka | gathering court amid ash-settled valley |
| `County029Hamlet2` | 29 | 5 | Hutalesulo | hutale + sulo | workshop settlement amid settled ash soil |
| `County029Hamlet3` | 29 | 5 | Yamabukera | yamabu + kera | reused-stone settlement amid ash mountain |
| `County029Hamlet4` | 29 | 5 | Ulayavani | ulaya + vani | route stop amid regrowth on the heights |
| `County029Hamlet5` | 29 | 5 | Tanuluremu | tanulu + remu | garden settlement amid cultivated soil |
| `County029Hamlet6` | 29 | 5 | Batanirava | batani + rava | rebuilt quarter amid stone valley |
| `County030Hamlet1` | 30 | 5 | Pobuminelo | pobumi + nelo | terraced habitation amid stone emerging from ash |
| `County030Hamlet2` | 30 | 5 | Apohumeka | apohu + meka | gathering court amid fire-marked stone |
| `County030Hamlet3` | 30 | 5 | Ulapisulo | ulapi + sulo | workshop settlement amid regrowth after burning |
| `County030Hamlet4` | 30 | 5 | Kabatukera | kabatu + kera | reused-stone settlement amid river stones |
| `County030Hamlet5` | 30 | 5 | Bateluvani | batelu + vani | route stop amid stone amid ash |
| `County031Hamlet1` | 31 | 6 | Lebaturemu | lebatu + remu | garden settlement amid ash over old masonry |
| `County031Hamlet2` | 31 | 6 | Tanapirava | tanapi + rava | rebuilt quarter amid fire-marked valley |
| `County031Hamlet3` | 31 | 6 | Lehamameka | lehama + meka | gathering court amid ash-covered heights |
| `County031Hamlet4` | 31 | 6 | Abulesulo | abule + sulo | workshop settlement amid deep ash ground |
| `County031Hamlet5` | 31 | 6 | Kawelukera | kawelu + kera | reused-stone settlement amid river through ash ground |
| `County032Hamlet1` | 32 | 6 | Tabuyavani | tabuya + vani | route stop amid ash valley between heights |
| `County032Hamlet2` | 32 | 6 | Yamoluremu | yamolu + remu | garden settlement amid renewed mountain ground |
| `County032Hamlet3` | 32 | 6 | Poyamarava | poyama + rava | rebuilt quarter amid rocky heights |
| `County032Hamlet4` | 32 | 6 | Kawabunelo | kawabu + nelo | terraced habitation amid riverborne ash |
| `County033Hamlet1` | 33 | 6 | Pohanimeka | pohani + meka | gathering court amid stone-sided valley |
| `County033Hamlet2` | 33 | 6 | Pokawasulo | pokawa + sulo | workshop settlement amid river-cut stone |
| `County033Hamlet3` | 33 | 6 | Yatanukera | yatanu + kera | reused-stone settlement amid mountain soil |
| `County033Hamlet4` | 33 | 6 | Hulumavani | huluma + vani | route stop amid new growth on an ash slope |
| `County033Hamlet5` | 33 | 6 | Tanahuremu | tanahu + remu | garden settlement amid ash-settled valley |
| `County033Hamlet6` | 33 | 6 | Hutalerava | hutale + rava | rebuilt quarter amid settled ash soil |
| `County034Hamlet1` | 34 | 6 | Yamabunelo | yamabu + nelo | terraced habitation amid ash mountain |
| `County034Hamlet2` | 34 | 6 | Ulayameka | ulaya + meka | gathering court amid regrowth on the heights |
| `County035Hamlet1` | 35 | 6 | Tanulusulo | tanulu + sulo | workshop settlement amid cultivated soil |
| `County035Hamlet2` | 35 | 6 | Batanikera | batani + kera | reused-stone settlement amid stone valley |
| `County035Hamlet3` | 35 | 6 | Pobumivani | pobumi + vani | route stop amid stone emerging from ash |
| `County036Hamlet1` | 36 | 6 | Apohuremu | apohu + remu | garden settlement amid fire-marked stone |
| `County036Hamlet2` | 36 | 6 | Ulapirava | ulapi + rava | rebuilt quarter amid regrowth after burning |
| `County036Hamlet3` | 36 | 6 | Kabatunelo | kabatu + nelo | terraced habitation amid river stones |
| `County036Hamlet4` | 36 | 6 | Batelumeka | batelu + meka | gathering court amid stone amid ash |
| `County037Hamlet1` | 37 | 7 | Lebatusulo | lebatu + sulo | workshop settlement amid ash over old masonry |
| `County037Hamlet2` | 37 | 7 | Tanapikera | tanapi + kera | reused-stone settlement amid fire-marked valley |
| `County037Hamlet3` | 37 | 7 | Lehamaremu | lehama + remu | garden settlement amid ash-covered heights |
| `County038Hamlet1` | 38 | 7 | Abulerava | abule + rava | rebuilt quarter amid deep ash ground |
| `County038Hamlet2` | 38 | 7 | Kawelunelo | kawelu + nelo | terraced habitation amid river through ash ground |
| `County039Hamlet1` | 39 | 7 | Tabuyameka | tabuya + meka | gathering court amid ash valley between heights |
| `County039Hamlet2` | 39 | 7 | Yamolusulo | yamolu + sulo | workshop settlement amid renewed mountain ground |
| `County039Hamlet3` | 39 | 7 | Poyamakera | poyama + kera | reused-stone settlement amid rocky heights |
| `County039Hamlet4` | 39 | 7 | Kawabuvani | kawabu + vani | route stop amid riverborne ash |
| `County039Hamlet5` | 39 | 7 | Pohaniremu | pohani + remu | garden settlement amid stone-sided valley |
| `County039Hamlet6` | 39 | 7 | Pokawarava | pokawa + rava | rebuilt quarter amid river-cut stone |
| `County039Hamlet7` | 39 | 7 | Yatanunelo | yatanu + nelo | terraced habitation amid mountain soil |
| `County040Hamlet1` | 40 | 7 | Hulumameka | huluma + meka | gathering court amid new growth on an ash slope |
| `County040Hamlet2` | 40 | 7 | Tanahusulo | tanahu + sulo | workshop settlement amid ash-settled valley |
| `County040Hamlet3` | 40 | 7 | Hutalekera | hutale + kera | reused-stone settlement amid settled ash soil |
| `County041Hamlet1` | 41 | 7 | Yamabuvani | yamabu + vani | route stop amid ash mountain |
| `County041Hamlet2` | 41 | 7 | Ulayaremu | ulaya + remu | garden settlement amid regrowth on the heights |
| `County041Hamlet3` | 41 | 7 | Tanulurava | tanulu + rava | rebuilt quarter amid cultivated soil |
| `County041Hamlet4` | 41 | 7 | Bataninelo | batani + nelo | terraced habitation amid stone valley |
| `County042Hamlet1` | 42 | 7 | Pobumimeka | pobumi + meka | gathering court amid stone emerging from ash |
| `County043Hamlet1` | 43 | 8 | Apohusulo | apohu + sulo | workshop settlement amid fire-marked stone |
| `County043Hamlet2` | 43 | 8 | Ulapikera | ulapi + kera | reused-stone settlement amid regrowth after burning |
| `County044Hamlet1` | 44 | 8 | Kabatuvani | kabatu + vani | route stop amid river stones |
| `County044Hamlet2` | 44 | 8 | Bateluremu | batelu + remu | garden settlement amid stone amid ash |
| `County045Hamlet1` | 45 | 8 | Lebaturava | lebatu + rava | rebuilt quarter amid ash over old masonry |
| `County045Hamlet2` | 45 | 8 | Tanapinelo | tanapi + nelo | terraced habitation amid fire-marked valley |
| `County045Hamlet3` | 45 | 8 | Lehamasulo | lehama + sulo | workshop settlement amid ash-covered heights |
| `County045Hamlet4` | 45 | 8 | Abulekera | abule + kera | reused-stone settlement amid deep ash ground |
| `County045Hamlet5` | 45 | 8 | Kaweluvani | kawelu + vani | route stop amid river through ash ground |
| `County045Hamlet6` | 45 | 8 | Tabuyaremu | tabuya + remu | garden settlement amid ash valley between heights |
| `County046Hamlet1` | 46 | 8 | Yamolurava | yamolu + rava | rebuilt quarter amid renewed mountain ground |
| `County047Hamlet1` | 47 | 8 | Poyamanelo | poyama + nelo | terraced habitation amid rocky heights |
| `County047Hamlet2` | 47 | 8 | Kawabumeka | kawabu + meka | gathering court amid riverborne ash |
| `County047Hamlet3` | 47 | 8 | Pohanisulo | pohani + sulo | workshop settlement amid stone-sided valley |
| `County048Hamlet1` | 48 | 8 | Pokawakera | pokawa + kera | reused-stone settlement amid river-cut stone |
| `County048Hamlet2` | 48 | 8 | Yatanuvani | yatanu + vani | route stop amid mountain soil |
| `County048Hamlet3` | 48 | 8 | Hulumaremu | huluma + remu | garden settlement amid new growth on an ash slope |
| `County048Hamlet4` | 48 | 8 | Tanahurava | tanahu + rava | rebuilt quarter amid ash-settled valley |
| `County048Hamlet5` | 48 | 8 | Hutalenelo | hutale + nelo | terraced habitation amid settled ash soil |

### Person-name decisions

Use mononyms and title-first display: **King Lehabumi**, **Duke Poyatanu**,
**Count Yamuleba**. Forms are not gender-coded. No family names, dynasties,
genealogies, or hereditary title rules are implied. Rank comes from the court
resource, not the name's length or a borrowed real-world honorific.

Names draw on the same environmental vocabulary but express naming wishes:
patience, renewal, care, steadiness, and provision. They are not claims about an
incumbent's personality. A ruler may share imagery with a seat, but the personal
name is independently constructed, not the capital's name with its ending removed.

#### Personal construction ledger

Pronunciations show the invented third-last-syllable stress. Source words have
the meanings recorded above; the complete wishes below are creative readings.

| Name | Pronunciation | Source transformations | Fictional naming wish |
| --- | --- | --- | --- |
| Lehabumi | le-HA-bu-mi | lehu→leha + abu→bu + yama→mi | one who makes a beginning after loss |
| Poyatanu | po-YA-ta-nu | pōhaku→po + yama→ya + tanah→tanu | steadiness that supports a new home |
| Ulabakeni | u-la-BA-ke-ni | ulu→ula + batu→ba + kawa→ke, invented ni | patient growth on difficult ground |
| Tanapolu | ta-NA-po-lu | tani→tana + pōhaku→po + ulu→lu | one who restores shelter in the valley |
| Yamuleba | ya-MU-le-ba | yama→yamu + lehu→le + batu→ba | resolve after upheaval |
| Kawapolu | ka-WA-po-lu | kawa + pōhaku→po + ulu→lu | one who clears the way for renewal |
| Batuyale | ba-TU-ya-le | batu + yama→ya + lehu→le | a steady hand among broken things |
| Lehutami | le-HU-ta-mi | lehu + tanah→ta + yama→mi | care for what remains |
| Apoyalu | a-PO-ya-lu | api→a + pōhaku→po + yama→ya + ulu→lu | strength directed toward rebuilding |
| Pobatani | po-BA-ta-ni | pōhaku→po + batu→ba + tani | one who finds sound foundations |
| Ulutanemi | u-lu-TA-ne-mi | ulu + tanah→tane + yama→mi | patient cultivation of a future |
| Yabulehu | ya-BU-le-hu | yama→ya + abu→bu + lehu | endurance through a season of ash |
| Tanulemi | ta-NU-le-mi | tanah→tanu + lehu→le + yama→mi | one who turns loss into provision |
| Kawulabi | ka-WU-la-bi | kawa→kawu + ulu→la + api→bi | renewal kept in motion |
| Bapoyami | ba-PO-ya-mi | batu→ba + pōhaku→po + yama→yami | dependability under strain |
| Huyatabu | hu-YA-ta-bu | lehu→hu + yama→ya + tanah→ta + abu→bu | one who remains to rebuild |
| Ulapokani | u-la-PO-ka-ni | ulu→ula + pōhaku→po + kawa→kani | growth sustained by careful work |
| Yapolabu | ya-PO-la-bu | yama→ya + pōhaku→po + lehu→la + abu→bu | memory preserved through rebuilding |
| Pitanoluba | pi-ta-NO-lu-ba | api→pi + tani→tano + ulu→lu + batu→ba | life returning to a scarred valley |
| Lehuyaba | le-HU-ya-ba | lehu + yama→ya + batu→ba | one who steadies others after change |
| Katulameya | ka-tu-LA-me-ya | kawa→ka + batu→tu + ulu→la + yama→meya | patient work that joins a community |
| Tulapoya | tu-LA-po-ya | batu→tu + ulu→la + pōhaku→po + yama→ya | strength used to help others grow |
| Abuyalemi | a-bu-YA-le-mi | abu + yama→ya + lehu→lemi | hope carried through hard seasons |
| Polutaya | po-LU-ta-ya | pōhaku→po + ulu→lu + tanah→ta + yama→ya | a lasting foundation for renewal |

#### Court assignments

| Court resource | Rank | Proposed person name | Seat node | Proposed seat name | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom2Capital` | King | Lehabumi | `Kingdom2Capital` | Lehamarava | 31 | 6 |
| `Court_Duchy05Capital` | Duke | Poyatanu | `Duchy05Capital` | Abulenelo | 25 | 5 |
| `Court_Duchy07Capital` | Duke | Ulabakeni | `Duchy07Capital` | Kawelumeka | 37 | 7 |
| `Court_Duchy08Capital` | Duke | Tanapolu | `Duchy08Capital` | Tabuyasulo | 43 | 8 |
| `Court_County026Capital` | Count | Yamuleba | `County026Capital` | Yamolukera | 26 | 5 |
| `Court_County027Capital` | Count | Kawapolu | `County027Capital` | Poyamavani | 27 | 5 |
| `Court_County028Capital` | Count | Batuyale | `County028Capital` | Kawaburemu | 28 | 5 |
| `Court_County029Capital` | Count | Lehutami | `County029Capital` | Pohanirava | 29 | 5 |
| `Court_County030Capital` | Count | Apoyalu | `County030Capital` | Pokawanelo | 30 | 5 |
| `Court_County032Capital` | Count | Pobatani | `County032Capital` | Yatanumeka | 32 | 6 |
| `Court_County033Capital` | Count | Ulutanemi | `County033Capital` | Hulumasulo | 33 | 6 |
| `Court_County034Capital` | Count | Yabulehu | `County034Capital` | Tanahukera | 34 | 6 |
| `Court_County035Capital` | Count | Tanulemi | `County035Capital` | Hutalevani | 35 | 6 |
| `Court_County036Capital` | Count | Kawulabi | `County036Capital` | Yamaburemu | 36 | 6 |
| `Court_County038Capital` | Count | Bapoyami | `County038Capital` | Ulayarava | 38 | 7 |
| `Court_County039Capital` | Count | Huyatabu | `County039Capital` | Tanulunelo | 39 | 7 |
| `Court_County040Capital` | Count | Ulapokani | `County040Capital` | Batanimeka | 40 | 7 |
| `Court_County041Capital` | Count | Yapolabu | `County041Capital` | Pobumisulo | 41 | 7 |
| `Court_County042Capital` | Count | Pitanoluba | `County042Capital` | Apohukera | 42 | 7 |
| `Court_County044Capital` | Count | Lehuyaba | `County044Capital` | Ulapivani | 44 | 8 |
| `Court_County045Capital` | Count | Katulameya | `County045Capital` | Kabaturemu | 45 | 8 |
| `Court_County046Capital` | Count | Tulapoya | `County046Capital` | Batelurava | 46 | 8 |
| `Court_County047Capital` | Count | Abuyalemi | `County047Capital` | Lebatunelo | 47 | 8 |
| `Court_County048Capital` | Count | Polutaya | `County048Capital` | Tanapimeka | 48 | 8 |

There are no additional count courts at counties **25, 31, 37, or 43**, and no
separate duchy-6 court in the current scene. County 25 uses Duchy05Capital;
county 31 and duchy 6 use Kingdom2Capital; counties 37 and 43 use Duchy07Capital
and Duchy08Capital respectively. These are shared seats, not evidence that one
person legally holds several titles. Do not invent five extra incumbents.

### Review and collision screening

On 2026-11-07, screened all 181 initial full-name candidates using individually
quoted web searches, followed by searches for the two replacements below.
Screening covered names as whole strings, not just their component syllables.

- Replaced **Katulami** with **Katulameya** after a gazette/OCR result suggested a
  geographic collision or near-collision. Replaced **Pitanolu** with
  **Pitanoluba** after a transliterated lyric occurrence, to reduce an unintended
  association. Both replacements had no results in the exact searches used.
- Retained incidental running-text/OCR matches such as Abulenelo, Abulekera,
  Poyatanu, Tanapolu, Batuyale, Lehutami, and Apoyalu. Yamuleba also appeared as
  joined text around “ya Muleba”; this is a resemblance to note during review,
  not a claim that the invented name is a verified real-world personal name.
- **Pobatani** overlaps an existing gaming handle (`PobATaNi#9877`). Retained as
  an incidental handle collision rather than copying an established character
  or place; this overlap is explicitly recorded for review.
- Searches are a limited screen, not proof of worldwide uniqueness. Short source
  syllables naturally recur. The register is an authored proposal and can be
  revised if a prominent real or fictional association emerges.
- Local validation checks all 157 settlement nodes and 24 court assignments,
  exact metadata/ranks, unique final names, and overlap with earlier registers.
  No claim of in-game display testing is made.

Screening references: [Kenya gazette, 1992-12-04](https://archive.gazettes.africa/archive/ke/1992/ke-government-gazette-dated-1992-12-04-no-62.pdf)
for the geographic/OCR concern; [music research compilation](https://www.ibiblio.org/guruguha/MusicResearchLibrary/Books-English/BkE-SrivatsaVV-Papers-vol.1-13Jul2001-0131.pdf)
for the incidental lyric occurrence. These informed rejection decisions, not
the source vocabulary.

### Volcanic research sources

Consulted 2026-11-07. These support the small source vocabulary, not the invented
compounds, suffixes, stress, wishes, or fictional settlement histories.

- **V1:** University of Hawaiʻi at Hilo, [Wehewehe: lehu](https://wehe.hilo.hawaii.edu/?l=&q=lehu),
  especially the Pukui–Elbert ash sense; unrelated homonyms are not used.
- **V2:** University of Hawaiʻi at Hilo, [Wehewehe: pōhaku](https://hilo.hawaii.edu/wehe/?q=pohaku),
  Pukui–Elbert stone/rock entry.
- **V3:** University of Hawaiʻi at Hilo, [Wehewehe: ulu](https://wehe.hilo.hawaii.edu/?q=ulu),
  growth sense; distinct from the breadfruit word.
- **V4:** Geospatial Information Authority of Japan, [Report to the 29th UNGEGN session](https://unstats.un.org/unsd/geoinfo/ungegn/docs/29th-gegn-docs/WP/WP22_11_29UNGEGN_REPORT_JAPAN.pdf),
  geographical romanization and mountain terminology, including `yama`.
- **V5:** National Institute for Japanese Language and Linguistics,
  [Japanese–Indonesian dictionary: kawa](https://mmsrv.ninjal.ac.jp/kamus/data/item1518.html),
  river entry.
- **V6:** [The Annals of the Hitotsubashi Academy, discussion of Japanese animal names](https://hit-u.repo.nii.ac.jp/record/2034718/files/annals0030202270.pdf),
  p. 230, explicitly analyzes `tani` as valley/glen. Only that lexical gloss is used.
- **V7:** Universitas Pendidikan Ganesha repository,
  [research appendices, Appendix 1 Swadesh list](https://repo.undiksha.ac.id/10177/9/1812021195-LAMPIRAN.pdf),
  PDF p. 3, Indonesian entries 75 (`abu`), 76 (`api`), 79 (`tanah`),
  and 80 (`batu`). Regional-language equivalents in adjacent columns are not used.

## Evergreen Temperate Rainforest naming

### Scope and identity

Requested 2026-11-07: settlement and person names inspired by various Pacific
Northwest cultures and languages. This authored selection uses **Lushootseed,
Tlingit, and Chinuk Wawa**, spanning Puget Sound, the northern coastal rainforest,
and the lower Columbia's contact-language tradition. They are distinct sources,
not a single “Pacific Northwest language,” and this is a selective palette rather
than a survey of every regional culture.

The intended impression is a lived-in evergreen forest: cedar, rain, thick
undergrowth, covered landings, sheltered workspaces, paths, and riverbank homes.
Use woodland shelter and mutual provision alongside wilderness imagery.
Political titles belong to the game's existing system; this does not model
actual Indigenous governments or personal naming customs.

Current scene inventory: **Kingdom 6**, counties **122–146**, duchies **24–28**.
There are **226 settlements**: 1 kingdom capital, 4 duchy capitals, 20 county
capitals, 60 villages, and 141 hamlets. The **25 courts** comprise 1 king,
4 dukes, and 20 counts. Counts and boundaries come from the current
`vcom/Scenes/Map.tscn`, not an assumed repeat of another kingdom's layout.
This is a documentation register; no game labels or resources are changed.

### Specific inspirations and source vocabulary

| Source tradition | Verified vocabulary | Contribution and limits |
| --- | --- | --- |
| Lushootseed, using Tulalip language materials | `x̱pay̓ac`, cedar tree; `qʷuʔ`, water [R1, R2] | Cedar and wet ground. The fictional pay/pa and kwa/kwu fragments are deliberate transformations, not pronunciation guides for Lushootseed. |
| Tlingit / Lingít, using language teaching and dictionary materials | `aas`, tree; `héen`, water/river; `séew`, rain [R3, R4] | Canopy, channels, and rainfall; tone and vowel length are not reproduced in the fictional language. No clan names, ceremonial compounds, or inherited personal names are borrowed. |
| Chinuk Wawa, specifically vocabulary attested in George Gibbs's 1863 dictionary | `snass`, rain; `tipso`, leaves/grass; `illahie`, earth/land [R5] | Rain, foliage, and habitable ground. These are historical spellings, not a proposed modern standard. Chinuk Wawa is a contact language, distinct from the Chinookan languages; the Chinook Indian Nation explains its multilingual history [R6]. |

Only ordinary vocabulary is used from these sources. The Tulalip cedar activity
also includes cultural practices; this naming exercise borrows the tree word,
not the activity's prayers or practices. The historical dictionary supplies
lexical evidence, not authority for its period descriptions of peoples.

Each fictional stem combines two source languages. All three sources appear in
both settlement and person registers. No name is required to contain every source,
consistent with the user's earlier clarification. Invented meanings below are
name stories, not translations or proof of actual terrain at a scene node.

### Sound, spelling, and construction

- Favor `s sh h n l w`, with `kw`, `sn`, and occasional closed syllables.
  `sh` sounds as in *shore*, `kw` as in *quick*, and `th` as in *thin*.
  `v` and `r` in some endings are fictional additions.
- Use approximate vowels ah, eh, ee, oh, oo for `a e i o u`.
  `ay` and `ai` sound like *eye*. `aw`, `ow`, and `ew` are one syllable
  each: ah-w, oh-w, and eh-w. Other adjacent vowels remain separate at the
  boundaries shown in the ledgers. Do not interpret the spelling as English.
- **Stress the final syllable**: Pashenelth = pa-shen-ELTH;
  Pasheniv = pa-shen-IV. This contrasts with the desert's penultimate stress,
  tundra's initial stress, and volcanic third-last-syllable stress.
- Place names combine a mixed stem with an invented habitation ending. Most have
  three or four syllables; the longer three-syllable stems can produce five.
  All syllable boundaries are recoverable from the stem and ending ledgers.
- Personal names combine a mixed stem with a separately recorded invented tail.
  Tails have no authentic source meaning, gender, lineage, or rank. The naming
  wish belongs to the complete authored name. Do not reuse a full settlement
  name as a person's name.
- Preserve source diacritics in research notes. Use plain fictional spelling in
  assignments, without decorative apostrophes or claims of authentic phonology.
  Sound changes, inserted consonants, contractions, and altered vowels are
  creative choices, not reconstructed linguistic history.
- Distribute stems across the kingdom rather than mapping real cultures onto
  separate duchies. This first allocation varies combinations systematically;
  detailed geographical fitting remains a future editorial pass.

### Blended stem ledger

| Fictional stem | Syllables | Source transformations | Fictional image |
| --- | --- | --- | --- |
| pashen | pa-shen | x̱pay̓ac→pa + héen→shen | cedar-lined water |
| kwasel | kwa-sel | qʷuʔ→kwa + séew→sel | rain-fed pools |
| asnip | as-nip | aas→as + tipso→nip | leafy woodland |
| hesnal | hes-nal | héen→he + snass→snal | rain-swollen stream |
| paynas | pay-nas | x̱pay̓ac→pay + snass→nas | rain on cedar |
| tiphen | tip-hen | tipso→tip + héen→hen | green riverbank |
| kwatil | kwa-til | qʷuʔ→kwa + tipso→til | wet undergrowth |
| sehpai | seh-pai | séew→seh + x̱pay̓ac→pai | rain beneath cedar |
| ilasen | i-la-sen | illahie→ila + aas→sen | wooded earth |
| asnaw | as-naw | aas→as + snass→naw | rain-dark canopy |
| hentil | hen-til | héen→hen + tipso→til | leaves beside water |
| pasil | pa-sil | x̱pay̓ac→pa + illahie→sil | cedar-rooted ground |
| kwasen | kwa-sen | qʷuʔ→kwa + aas→sen | water beneath trees |
| tipas | ti-pas | tipso→tip + aas→as, shorten aa | leaf-covered woodland |
| sekwan | se-kwan | séew→se + qʷuʔ→kwan | collected rainfall |
| ilhen | il-hen | illahie→il + héen→hen | ground beside a stream |
| pasew | pa-sew | x̱pay̓ac→pa + séew→sew | wet cedar boughs |
| naswen | nas-wen | snass→nas + séew→wen | rain through the trees |
| kwalis | kwa-lis | qʷuʔ→kwa + illahie→lis | waterlogged earth |
| hepay | he-pay | héen→he + x̱pay̓ac→pay | cedar beside a channel |
| tisek | ti-sek | tipso→ti + séew→sek | rain-bright foliage |
| asanil | a-sa-nil | aas→asa + illahie→nil | deep woodland soil |
| paysin | pay-sin | x̱pay̓ac→pay + tipso→sin | cedar undergrowth |
| snakwu | sna-kwu | snass→sna + qʷuʔ→kwu | water gathered after rain |

The transformations are intentionally free: for example, `héen→shen` includes
an inserted sh sound, while `aas→sen` adds and changes sounds around a shortened
tree fragment. These derivations record design inspiration rather than asserting
that the fictional syllables retain dictionary meanings outside this scheme.

### Invented settlement endings

| Ending | Syllables | Fictional habitation sense |
| --- | --- | --- |
| elth | elth | sheltered gathering place |
| owan | o-wan | linked riverside homes |
| esh | esh | woodland clearing |
| avel | a-vel | raised walkway settlement |
| un | un | garden enclosure |
| eth | eth | covered landing |
| olan | o-lan | settlement along a forest path |
| em | em | sheltered workshop quarter |
| ask | ask | habitation on firmer ground |
| owen | o-wen | streamside meeting place |
| ereth | e-reth | variant of olan: forest-path habitation |
| aveth | a-veth | variant of ask: firmer-ground habitation |
| avun | a-vun | variant of un: garden enclosure |
| eresh | e-resh | variant of esh: woodland clearing |
| erem | e-rem | variant of em: sheltered workshop quarter |

The five longer variants were introduced during collision screening. They retain
their base ending's fictional sense. Endings carry no political rank. A garden,
walkway, or landing is a proposed name story, not a newly established game asset.

### Settlement assignments

Combine the stem's image with the ending's habitation sense to read a name story:
**Pashenelth** suggests a sheltered gathering place beside cedar-lined water.
Node names and metadata below identify existing settlements exactly.

#### Capitals

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `Kingdom6Capital` | 122 | 24 | Pashenelth | pashen + elth | pa-shen-ELTH |
| `Duchy25Capital` | 127 | 25 | Sehpaiowan | sehpai + owan | seh-pai-o-WAN |
| `Duchy26Capital` | 132 | 26 | Sekwanesh | sekwan + esh | se-kwan-ESH |
| `Duchy27Capital` | 137 | 27 | Asanilavel | asanil + avel | a-sa-nil-a-VEL |
| `Duchy28Capital` | 142 | 28 | Paynasun | paynas + un | pay-nas-UN |
| `County123Capital` | 123 | 24 | Pasileth | pasil + eth | pa-sil-ETH |
| `County124Capital` | 124 | 24 | Kwalisolan | kwalis + olan | kwa-lis-o-LAN |
| `County125Capital` | 125 | 24 | Kwaselem | kwasel + em | kwa-sel-EM |
| `County126Capital` | 126 | 24 | Ilasenask | ilasen + ask | i-la-sen-ASK |
| `County128Capital` | 128 | 25 | Ilhenowen | ilhen + owen | il-hen-o-WEN |
| `County129Capital` | 129 | 25 | Paysinelth | paysin + elth | pay-sin-ELTH |
| `County130Capital` | 130 | 25 | Tiphenowan | tiphen + owan | tip-hen-o-WAN |
| `County131Capital` | 131 | 25 | Kwasenesh | kwasen + esh | kwa-sen-ESH |
| `County133Capital` | 133 | 26 | Hepayavel | hepay + avel | he-pay-a-VEL |
| `County134Capital` | 134 | 26 | Asnipun | asnip + un | as-nip-UN |
| `County135Capital` | 135 | 26 | Asnaweth | asnaw + eth | as-naw-ETH |
| `County136Capital` | 136 | 26 | Pasewolan | pasew + olan | pa-sew-o-LAN |
| `County138Capital` | 138 | 27 | Snakwuem | snakwu + em | sna-kwu-EM |
| `County139Capital` | 139 | 27 | Kwatilask | kwatil + ask | kwa-til-ASK |
| `County140Capital` | 140 | 27 | Tipasowen | tipas + owen | ti-pas-o-WEN |
| `County141Capital` | 141 | 27 | Tisekelth | tisek + elth | ti-sek-ELTH |
| `County143Capital` | 143 | 28 | Hesnalowan | hesnal + owan | hes-nal-o-WAN |
| `County144Capital` | 144 | 28 | Hentilesh | hentil + esh | hen-til-ESH |
| `County145Capital` | 145 | 28 | Naswenavel | naswen + avel | nas-wen-a-VEL |
| `County146Capital` | 146 | 28 | Pashenowan | pashen + owan | pa-shen-o-WAN |

#### Villages

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County122Village1` | 122 | 24 | Sehpaiesh | sehpai + esh | seh-pai-ESH |
| `County122Village2` | 122 | 24 | Sekwanavel | sekwan + avel | se-kwan-a-VEL |
| `County122Village3` | 122 | 24 | Asanilun | asanil + un | a-sa-nil-UN |
| `County122Village4` | 122 | 24 | Paynaseth | paynas + eth | pay-nas-ETH |
| `County122Village5` | 122 | 24 | Pasilereth | pasil + ereth | pa-sil-e-RETH |
| `County122Village6` | 122 | 24 | Kwalisem | kwalis + em | kwa-lis-EM |
| `County122Village7` | 122 | 24 | Kwaselask | kwasel + ask | kwa-sel-ASK |
| `County123Village1` | 123 | 24 | Ilasenowen | ilasen + owen | i-la-sen-o-WEN |
| `County123Village2` | 123 | 24 | Ilhenelth | ilhen + elth | il-hen-ELTH |
| `County124Village1` | 124 | 24 | Paysinowan | paysin + owan | pay-sin-o-WAN |
| `County124Village2` | 124 | 24 | Tiphenesh | tiphen + esh | tip-hen-ESH |
| `County124Village3` | 124 | 24 | Kwasenavel | kwasen + avel | kwa-sen-a-VEL |
| `County125Village1` | 125 | 24 | Hepayun | hepay + un | he-pay-UN |
| `County126Village1` | 126 | 24 | Asnipeth | asnip + eth | as-nip-ETH |
| `County126Village2` | 126 | 24 | Asnawolan | asnaw + olan | as-naw-o-LAN |
| `County127Village1` | 127 | 25 | Pasewem | pasew + em | pa-sew-EM |
| `County127Village2` | 127 | 25 | Snakwuask | snakwu + ask | sna-kwu-ASK |
| `County127Village3` | 127 | 25 | Kwatilowen | kwatil + owen | kwa-til-o-WEN |
| `County127Village4` | 127 | 25 | Tipaselth | tipas + elth | ti-pas-ELTH |
| `County127Village5` | 127 | 25 | Tisekowan | tisek + owan | ti-sek-o-WAN |
| `County127Village6` | 127 | 25 | Hesnalesh | hesnal + esh | hes-nal-ESH |
| `County128Village1` | 128 | 25 | Hentilavel | hentil + avel | hen-til-a-VEL |
| `County128Village2` | 128 | 25 | Naswenun | naswen + un | nas-wen-UN |
| `County129Village1` | 129 | 25 | Pashenesh | pashen + esh | pa-shen-ESH |
| `County129Village2` | 129 | 25 | Sehpaiavel | sehpai + avel | seh-pai-a-VEL |
| `County129Village3` | 129 | 25 | Sekwanun | sekwan + un | se-kwan-UN |
| `County129Village4` | 129 | 25 | Asanileth | asanil + eth | a-sa-nil-ETH |
| `County130Village1` | 130 | 25 | Paynasolan | paynas + olan | pay-nas-o-LAN |
| `County130Village2` | 130 | 25 | Pasilem | pasil + em | pa-sil-EM |
| `County130Village3` | 130 | 25 | Kwalisask | kwalis + ask | kwa-lis-ASK |
| `County131Village1` | 131 | 25 | Kwaselowen | kwasel + owen | kwa-sel-o-WEN |
| `County131Village2` | 131 | 25 | Ilasenelth | ilasen + elth | i-la-sen-ELTH |
| `County132Village1` | 132 | 26 | Ilhenowan | ilhen + owan | il-hen-o-WAN |
| `County132Village2` | 132 | 26 | Paysinesh | paysin + esh | pay-sin-ESH |
| `County132Village3` | 132 | 26 | Tiphenavel | tiphen + avel | tip-hen-a-VEL |
| `County132Village4` | 132 | 26 | Kwasenun | kwasen + un | kwa-sen-UN |
| `County133Village1` | 133 | 26 | Hepayeth | hepay + eth | he-pay-ETH |
| `County133Village2` | 133 | 26 | Asnipolan | asnip + olan | as-nip-o-LAN |
| `County134Village1` | 134 | 26 | Asnawem | asnaw + em | as-naw-EM |
| `County134Village2` | 134 | 26 | Pasewaveth | pasew + aveth | pa-sew-a-VETH |
| `County135Village1` | 135 | 26 | Snakwuowen | snakwu + owen | sna-kwu-o-WEN |
| `County136Village1` | 136 | 26 | Kwatilelth | kwatil + elth | kwa-til-ELTH |
| `County137Village1` | 137 | 27 | Tipasowan | tipas + owan | ti-pas-o-WAN |
| `County138Village1` | 138 | 27 | Tisekesh | tisek + esh | ti-sek-ESH |
| `County138Village2` | 138 | 27 | Hesnalavel | hesnal + avel | hes-nal-a-VEL |
| `County139Village1` | 139 | 27 | Hentilavun | hentil + avun | hen-til-a-VUN |
| `County139Village2` | 139 | 27 | Nasweneth | naswen + eth | nas-wen-ETH |
| `County139Village3` | 139 | 27 | Pashenavel | pashen + avel | pa-shen-a-VEL |
| `County140Village1` | 140 | 27 | Sehpaiun | sehpai + un | seh-pai-UN |
| `County141Village1` | 141 | 27 | Sekwaneth | sekwan + eth | se-kwan-ETH |
| `County142Village1` | 142 | 28 | Asanilolan | asanil + olan | a-sa-nil-o-LAN |
| `County142Village2` | 142 | 28 | Paynasem | paynas + em | pay-nas-EM |
| `County142Village3` | 142 | 28 | Pasilask | pasil + ask | pa-sil-ASK |
| `County142Village4` | 142 | 28 | Kwalisowen | kwalis + owen | kwa-lis-o-WEN |
| `County143Village1` | 143 | 28 | Kwaselelth | kwasel + elth | kwa-sel-ELTH |
| `County143Village2` | 143 | 28 | Ilasenowan | ilasen + owan | i-la-sen-o-WAN |
| `County144Village1` | 144 | 28 | Ilhenesh | ilhen + esh | il-hen-ESH |
| `County145Village1` | 145 | 28 | Paysinavel | paysin + avel | pay-sin-a-VEL |
| `County145Village2` | 145 | 28 | Tiphenun | tiphen + un | tip-hen-UN |
| `County146Village1` | 146 | 28 | Kwaseneth | kwasen + eth | kwa-sen-ETH |

#### Hamlets

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County122Hamlet1` | 122 | 24 | Hepayolan | hepay + olan | he-pay-o-LAN |
| `County122Hamlet2` | 122 | 24 | Asnipem | asnip + em | as-nip-EM |
| `County123Hamlet1` | 123 | 24 | Asnawask | asnaw + ask | as-naw-ASK |
| `County123Hamlet2` | 123 | 24 | Pasewowen | pasew + owen | pa-sew-o-WEN |
| `County123Hamlet3` | 123 | 24 | Snakwuelth | snakwu + elth | sna-kwu-ELTH |
| `County123Hamlet4` | 123 | 24 | Kwatilowan | kwatil + owan | kwa-til-o-WAN |
| `County123Hamlet5` | 123 | 24 | Tipasesh | tipas + esh | ti-pas-ESH |
| `County123Hamlet6` | 123 | 24 | Tisekavel | tisek + avel | ti-sek-a-VEL |
| `County123Hamlet7` | 123 | 24 | Hesnalun | hesnal + un | hes-nal-UN |
| `County124Hamlet1` | 124 | 24 | Hentileth | hentil + eth | hen-til-ETH |
| `County124Hamlet2` | 124 | 24 | Naswenolan | naswen + olan | nas-wen-o-LAN |
| `County124Hamlet3` | 124 | 24 | Pashenun | pashen + un | pa-shen-UN |
| `County124Hamlet4` | 124 | 24 | Sehpaieth | sehpai + eth | seh-pai-ETH |
| `County124Hamlet5` | 124 | 24 | Sekwanolan | sekwan + olan | se-kwan-o-LAN |
| `County124Hamlet6` | 124 | 24 | Asanilem | asanil + em | a-sa-nil-EM |
| `County125Hamlet1` | 125 | 24 | Paynasask | paynas + ask | pay-nas-ASK |
| `County125Hamlet2` | 125 | 24 | Pasilowen | pasil + owen | pa-sil-o-WEN |
| `County125Hamlet3` | 125 | 24 | Kwaliselth | kwalis + elth | kwa-lis-ELTH |
| `County126Hamlet1` | 126 | 24 | Kwaselowan | kwasel + owan | kwa-sel-o-WAN |
| `County126Hamlet2` | 126 | 24 | Ilasenesh | ilasen + esh | i-la-sen-ESH |
| `County126Hamlet3` | 126 | 24 | Ilhenavel | ilhen + avel | il-hen-a-VEL |
| `County126Hamlet4` | 126 | 24 | Paysinun | paysin + un | pay-sin-UN |
| `County126Hamlet5` | 126 | 24 | Tipheneth | tiphen + eth | tip-hen-ETH |
| `County126Hamlet6` | 126 | 24 | Kwasenolan | kwasen + olan | kwa-sen-o-LAN |
| `County126Hamlet7` | 126 | 24 | Hepayem | hepay + em | he-pay-EM |
| `County126Hamlet8` | 126 | 24 | Asnipask | asnip + ask | as-nip-ASK |
| `County127Hamlet1` | 127 | 25 | Asnawowen | asnaw + owen | as-naw-o-WEN |
| `County127Hamlet2` | 127 | 25 | Pasewelth | pasew + elth | pa-sew-ELTH |
| `County127Hamlet3` | 127 | 25 | Snakwuowan | snakwu + owan | sna-kwu-o-WAN |
| `County127Hamlet4` | 127 | 25 | Kwatilesh | kwatil + esh | kwa-til-ESH |
| `County127Hamlet5` | 127 | 25 | Tipasavel | tipas + avel | ti-pas-a-VEL |
| `County127Hamlet6` | 127 | 25 | Tisekun | tisek + un | ti-sek-UN |
| `County127Hamlet7` | 127 | 25 | Hesnaleth | hesnal + eth | hes-nal-ETH |
| `County127Hamlet8` | 127 | 25 | Hentilolan | hentil + olan | hen-til-o-LAN |
| `County127Hamlet9` | 127 | 25 | Naswenem | naswen + em | nas-wen-EM |
| `County127Hamlet10` | 127 | 25 | Pasheneth | pashen + eth | pa-shen-ETH |
| `County127Hamlet11` | 127 | 25 | Sehpaiolan | sehpai + olan | seh-pai-o-LAN |
| `County127Hamlet12` | 127 | 25 | Sekwanem | sekwan + em | se-kwan-EM |
| `County128Hamlet1` | 128 | 25 | Asanilask | asanil + ask | a-sa-nil-ASK |
| `County128Hamlet2` | 128 | 25 | Paynasowen | paynas + owen | pay-nas-o-WEN |
| `County128Hamlet3` | 128 | 25 | Pasilelth | pasil + elth | pa-sil-ELTH |
| `County129Hamlet1` | 129 | 25 | Kwalisowan | kwalis + owan | kwa-lis-o-WAN |
| `County129Hamlet2` | 129 | 25 | Kwaselesh | kwasel + esh | kwa-sel-ESH |
| `County129Hamlet3` | 129 | 25 | Ilasenavel | ilasen + avel | i-la-sen-a-VEL |
| `County129Hamlet4` | 129 | 25 | Ilhenun | ilhen + un | il-hen-UN |
| `County129Hamlet5` | 129 | 25 | Paysineth | paysin + eth | pay-sin-ETH |
| `County129Hamlet6` | 129 | 25 | Tiphenolan | tiphen + olan | tip-hen-o-LAN |
| `County130Hamlet1` | 130 | 25 | Kwasenem | kwasen + em | kwa-sen-EM |
| `County130Hamlet2` | 130 | 25 | Hepayask | hepay + ask | he-pay-ASK |
| `County130Hamlet3` | 130 | 25 | Asnipowen | asnip + owen | as-nip-o-WEN |
| `County130Hamlet4` | 130 | 25 | Asnawelth | asnaw + elth | as-naw-ELTH |
| `County130Hamlet5` | 130 | 25 | Pasewowan | pasew + owan | pa-sew-o-WAN |
| `County130Hamlet6` | 130 | 25 | Snakwuesh | snakwu + esh | sna-kwu-ESH |
| `County131Hamlet1` | 131 | 25 | Kwatilavel | kwatil + avel | kwa-til-a-VEL |
| `County131Hamlet2` | 131 | 25 | Tipasun | tipas + un | ti-pas-UN |
| `County131Hamlet3` | 131 | 25 | Tiseketh | tisek + eth | ti-sek-ETH |
| `County131Hamlet4` | 131 | 25 | Hesnalolan | hesnal + olan | hes-nal-o-LAN |
| `County131Hamlet5` | 131 | 25 | Hentilerem | hentil + erem | hen-til-e-REM |
| `County131Hamlet6` | 131 | 25 | Naswenask | naswen + ask | nas-wen-ASK |
| `County131Hamlet7` | 131 | 25 | Pashenolan | pashen + olan | pa-shen-o-LAN |
| `County131Hamlet8` | 131 | 25 | Sehpaiem | sehpai + em | seh-pai-EM |
| `County131Hamlet9` | 131 | 25 | Sekwanask | sekwan + ask | se-kwan-ASK |
| `County132Hamlet1` | 132 | 26 | Asanilowen | asanil + owen | a-sa-nil-o-WEN |
| `County132Hamlet2` | 132 | 26 | Paynaselth | paynas + elth | pay-nas-ELTH |
| `County132Hamlet3` | 132 | 26 | Pasilowan | pasil + owan | pa-sil-o-WAN |
| `County132Hamlet4` | 132 | 26 | Kwalisesh | kwalis + esh | kwa-lis-ESH |
| `County132Hamlet5` | 132 | 26 | Kwaselavel | kwasel + avel | kwa-sel-a-VEL |
| `County132Hamlet6` | 132 | 26 | Ilasenun | ilasen + un | i-la-sen-UN |
| `County132Hamlet7` | 132 | 26 | Ilheneth | ilhen + eth | il-hen-ETH |
| `County132Hamlet8` | 132 | 26 | Paysinolan | paysin + olan | pay-sin-o-LAN |
| `County133Hamlet1` | 133 | 26 | Tiphenem | tiphen + em | tip-hen-EM |
| `County133Hamlet2` | 133 | 26 | Kwasenask | kwasen + ask | kwa-sen-ASK |
| `County133Hamlet3` | 133 | 26 | Hepayowen | hepay + owen | he-pay-o-WEN |
| `County133Hamlet4` | 133 | 26 | Asnipelth | asnip + elth | as-nip-ELTH |
| `County134Hamlet1` | 134 | 26 | Asnawowan | asnaw + owan | as-naw-o-WAN |
| `County134Hamlet2` | 134 | 26 | Pasewesh | pasew + esh | pa-sew-ESH |
| `County134Hamlet3` | 134 | 26 | Snakwuavel | snakwu + avel | sna-kwu-a-VEL |
| `County134Hamlet4` | 134 | 26 | Kwatilun | kwatil + un | kwa-til-UN |
| `County134Hamlet5` | 134 | 26 | Tipaseth | tipas + eth | ti-pas-ETH |
| `County134Hamlet6` | 134 | 26 | Tisekolan | tisek + olan | ti-sek-o-LAN |
| `County134Hamlet7` | 134 | 26 | Hesnalem | hesnal + em | hes-nal-EM |
| `County135Hamlet1` | 135 | 26 | Hentilask | hentil + ask | hen-til-ASK |
| `County135Hamlet2` | 135 | 26 | Naswenowen | naswen + owen | nas-wen-o-WEN |
| `County135Hamlet3` | 135 | 26 | Pashenem | pashen + em | pa-shen-EM |
| `County136Hamlet1` | 136 | 26 | Sehpaiask | sehpai + ask | seh-pai-ASK |
| `County136Hamlet2` | 136 | 26 | Sekwanowen | sekwan + owen | se-kwan-o-WEN |
| `County136Hamlet3` | 136 | 26 | Asanilelth | asanil + elth | a-sa-nil-ELTH |
| `County136Hamlet4` | 136 | 26 | Paynasowan | paynas + owan | pay-nas-o-WAN |
| `County136Hamlet5` | 136 | 26 | Pasilesh | pasil + esh | pa-sil-ESH |
| `County136Hamlet6` | 136 | 26 | Kwalisavel | kwalis + avel | kwa-lis-a-VEL |
| `County137Hamlet1` | 137 | 27 | Kwaselun | kwasel + un | kwa-sel-UN |
| `County137Hamlet2` | 137 | 27 | Ilaseneth | ilasen + eth | i-la-sen-ETH |
| `County137Hamlet3` | 137 | 27 | Ilhenolan | ilhen + olan | il-hen-o-LAN |
| `County137Hamlet4` | 137 | 27 | Paysinem | paysin + em | pay-sin-EM |
| `County137Hamlet5` | 137 | 27 | Tiphenask | tiphen + ask | tip-hen-ASK |
| `County138Hamlet1` | 138 | 27 | Kwasenowen | kwasen + owen | kwa-sen-o-WEN |
| `County138Hamlet2` | 138 | 27 | Hepayelth | hepay + elth | he-pay-ELTH |
| `County138Hamlet3` | 138 | 27 | Asnipowan | asnip + owan | as-nip-o-WAN |
| `County138Hamlet4` | 138 | 27 | Asnaweresh | asnaw + eresh | as-naw-e-RESH |
| `County138Hamlet5` | 138 | 27 | Pasewavel | pasew + avel | pa-sew-a-VEL |
| `County138Hamlet6` | 138 | 27 | Snakwuun | snakwu + un | sna-kwu-UN |
| `County139Hamlet1` | 139 | 27 | Kwatileth | kwatil + eth | kwa-til-ETH |
| `County139Hamlet2` | 139 | 27 | Tipasolan | tipas + olan | ti-pas-o-LAN |
| `County139Hamlet3` | 139 | 27 | Tisekem | tisek + em | ti-sek-EM |
| `County139Hamlet4` | 139 | 27 | Hesnalask | hesnal + ask | hes-nal-ASK |
| `County140Hamlet1` | 140 | 27 | Hentilowen | hentil + owen | hen-til-o-WEN |
| `County140Hamlet2` | 140 | 27 | Naswenelth | naswen + elth | nas-wen-ELTH |
| `County140Hamlet3` | 140 | 27 | Pashenask | pashen + ask | pa-shen-ASK |
| `County140Hamlet4` | 140 | 27 | Sehpaiowen | sehpai + owen | seh-pai-o-WEN |
| `County140Hamlet5` | 140 | 27 | Sekwanelth | sekwan + elth | se-kwan-ELTH |
| `County140Hamlet6` | 140 | 27 | Asanilowan | asanil + owan | a-sa-nil-o-WAN |
| `County140Hamlet7` | 140 | 27 | Paynasesh | paynas + esh | pay-nas-ESH |
| `County141Hamlet1` | 141 | 27 | Pasilavel | pasil + avel | pa-sil-a-VEL |
| `County141Hamlet2` | 141 | 27 | Kwalisavun | kwalis + avun | kwa-lis-a-VUN |
| `County142Hamlet1` | 142 | 28 | Kwaseleth | kwasel + eth | kwa-sel-ETH |
| `County142Hamlet2` | 142 | 28 | Ilasenolan | ilasen + olan | i-la-sen-o-LAN |
| `County142Hamlet3` | 142 | 28 | Ilhenem | ilhen + em | il-hen-EM |
| `County143Hamlet1` | 143 | 28 | Paysinask | paysin + ask | pay-sin-ASK |
| `County143Hamlet2` | 143 | 28 | Tiphenowen | tiphen + owen | tip-hen-o-WEN |
| `County143Hamlet3` | 143 | 28 | Kwasenelth | kwasen + elth | kwa-sen-ELTH |
| `County143Hamlet4` | 143 | 28 | Hepayowan | hepay + owan | he-pay-o-WAN |
| `County144Hamlet1` | 144 | 28 | Asnipesh | asnip + esh | as-nip-ESH |
| `County144Hamlet2` | 144 | 28 | Asnawavel | asnaw + avel | as-naw-a-VEL |
| `County144Hamlet3` | 144 | 28 | Pasewun | pasew + un | pa-sew-UN |
| `County144Hamlet4` | 144 | 28 | Snakwueth | snakwu + eth | sna-kwu-ETH |
| `County144Hamlet5` | 144 | 28 | Kwatilolan | kwatil + olan | kwa-til-o-LAN |
| `County144Hamlet6` | 144 | 28 | Tipasem | tipas + em | ti-pas-EM |
| `County144Hamlet7` | 144 | 28 | Tisekask | tisek + ask | ti-sek-ASK |
| `County144Hamlet8` | 144 | 28 | Hesnalowen | hesnal + owen | hes-nal-o-WEN |
| `County145Hamlet1` | 145 | 28 | Hentilelth | hentil + elth | hen-til-ELTH |
| `County145Hamlet2` | 145 | 28 | Naswenowan | naswen + owan | nas-wen-o-WAN |
| `County145Hamlet3` | 145 | 28 | Pashenowen | pashen + owen | pa-shen-o-WEN |
| `County146Hamlet1` | 146 | 28 | Sehpaielth | sehpai + elth | seh-pai-ELTH |
| `County146Hamlet2` | 146 | 28 | Sekwanowan | sekwan + owan | se-kwan-o-WAN |
| `County146Hamlet3` | 146 | 28 | Asanilesh | asanil + esh | a-sa-nil-ESH |
| `County146Hamlet4` | 146 | 28 | Paynasavel | paynas + avel | pay-nas-a-VEL |
| `County146Hamlet5` | 146 | 28 | Pasilun | pasil + un | pa-sil-UN |
| `County146Hamlet6` | 146 | 28 | Kwaliseth | kwalis + eth | kwa-lis-ETH |
| `County146Hamlet7` | 146 | 28 | Kwaselolan | kwasel + olan | kwa-sel-o-LAN |
| `County146Hamlet8` | 146 | 28 | Ilasenem | ilasen + em | i-la-sen-EM |
| `County146Hamlet9` | 146 | 28 | Ilhenask | ilhen + ask | il-hen-ASK |

### Person-name decisions and ledger

Use mononyms, title-first: **King Pasheniv**, **Duke Kwaseliv**. Names are
ungendered; no family, dynasty, real-world honorific, or invented genealogy is
implied. Sharing a stem with a settlement reflects shared vocabulary, not descent,
ownership, or a surname. Naming wishes describe hopes, not established traits.

The mixed stem supplies two researched language inspirations; its complete
construction is recorded above. The tail and the whole-name wish are invented.

| Name | Pronunciation | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Pasheniv | pa-shen-IV | pashen + invented iv | one who offers shelter |
| Kwaseliv | kwa-sel-IV | kwasel + invented iv | patience through long rains |
| Asnipolen | as-nip-o-LEN | asnip + invented olen | care for returning growth |
| Hesnalow | hes-nal-OW | hesnal + invented ow | steadiness when waters rise |
| Paynasiv | pay-nas-IV | paynas + invented iv | one who preserves a welcoming home |
| Tiphenaw | tip-hen-AW | tiphen + invented aw | provision shared along the river |
| Kwatilen | kwa-til-EN | kwatil + invented en | attention to small growing things |
| Sehpaioth | seh-pai-OTH | sehpai + invented oth | a welcome at the journey's end |
| Ilasenoth | i-la-sen-OTH | ilasen + invented oth | care for the ground that sustains others |
| Asnawolen | as-naw-o-LEN | asnaw + invented olen | endurance in difficult seasons |
| Hentilav | hen-til-AV | hentil + invented av | one who keeps a route open |
| Pasilen | pa-sil-EN | pasil + invented en | strength rooted in care |
| Kwasenov | kwa-sen-OV | kwasen + invented ov | one who brings people together |
| Tipashel | ti-pas-HEL | tipas + invented hel | room for others to flourish |
| Sekwanim | se-kwan-IM | sekwan + invented im | thoughtful preparation |
| Ilhenaw | il-hen-AW | ilhen + invented aw | a dependable place to return |
| Pasewil | pa-sew-IL | pasew + invented il | kindness in hard weather |
| Naswenen | nas-wen-EN | naswen + invented en | one who listens before acting |
| Kwalishem | kwa-lis-HEM | kwalis + invented hem | steady judgment in uncertain ground |
| Hepayev | he-pay-EV | hepay + invented ev | one who helps others cross |
| Tisekan | ti-sek-AN | tisek + invented an | hope renewed by small changes |
| Asanilev | a-sa-nil-EV | asanil + invented ev | memory carried into new growth |
| Paysinow | pay-sin-OW | paysin + invented ow | care for the next generation |
| Snakwulen | sna-kwu-LEN | snakwu + invented len | one who gathers help when needed |
| Pashenol | pa-shen-OL | pashen + invented ol | shelter freely shared |

### Court assignments

| Court resource | Rank | Proposed person name | Seat node | Proposed seat name | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom6Capital` | King | Pasheniv | `Kingdom6Capital` | Pashenelth | 122 | 24 |
| `Court_Duchy25Capital` | Duke | Kwaseliv | `Duchy25Capital` | Sehpaiowan | 127 | 25 |
| `Court_Duchy26Capital` | Duke | Asnipolen | `Duchy26Capital` | Sekwanesh | 132 | 26 |
| `Court_Duchy27Capital` | Duke | Hesnalow | `Duchy27Capital` | Asanilavel | 137 | 27 |
| `Court_Duchy28Capital` | Duke | Paynasiv | `Duchy28Capital` | Paynasun | 142 | 28 |
| `Court_County123Capital` | Count | Tiphenaw | `County123Capital` | Pasileth | 123 | 24 |
| `Court_County124Capital` | Count | Kwatilen | `County124Capital` | Kwalisolan | 124 | 24 |
| `Court_County125Capital` | Count | Sehpaioth | `County125Capital` | Kwaselem | 125 | 24 |
| `Court_County126Capital` | Count | Ilasenoth | `County126Capital` | Ilasenask | 126 | 24 |
| `Court_County128Capital` | Count | Asnawolen | `County128Capital` | Ilhenowen | 128 | 25 |
| `Court_County129Capital` | Count | Hentilav | `County129Capital` | Paysinelth | 129 | 25 |
| `Court_County130Capital` | Count | Pasilen | `County130Capital` | Tiphenowan | 130 | 25 |
| `Court_County131Capital` | Count | Kwasenov | `County131Capital` | Kwasenesh | 131 | 25 |
| `Court_County133Capital` | Count | Tipashel | `County133Capital` | Hepayavel | 133 | 26 |
| `Court_County134Capital` | Count | Sekwanim | `County134Capital` | Asnipun | 134 | 26 |
| `Court_County135Capital` | Count | Ilhenaw | `County135Capital` | Asnaweth | 135 | 26 |
| `Court_County136Capital` | Count | Pasewil | `County136Capital` | Pasewolan | 136 | 26 |
| `Court_County138Capital` | Count | Naswenen | `County138Capital` | Snakwuem | 138 | 27 |
| `Court_County139Capital` | Count | Kwalishem | `County139Capital` | Kwatilask | 139 | 27 |
| `Court_County140Capital` | Count | Hepayev | `County140Capital` | Tipasowen | 140 | 27 |
| `Court_County141Capital` | Count | Tisekan | `County141Capital` | Tisekelth | 141 | 27 |
| `Court_County143Capital` | Count | Asanilev | `County143Capital` | Hesnalowan | 143 | 28 |
| `Court_County144Capital` | Count | Paysinow | `County144Capital` | Hentilesh | 144 | 28 |
| `Court_County145Capital` | Count | Snakwulen | `County145Capital` | Naswenavel | 145 | 28 |
| `Court_County146Capital` | Count | Pashenol | `County146Capital` | Pashenowan | 146 | 28 |

Kingdom6Capital is the shared seat for county 122 and duchy 24. Duchy25Capital,
Duchy26Capital, Duchy27Capital, and Duchy28Capital are the shared seats for
counties 127, 132, 137, and 142 respectively. There are no separate count courts
at those five seats and no separate duchy-24 court. Co-location does not establish
combined legal titles; do not add six hypothetical incumbents.

### Screening and revisions

Individually quoted searches covered all **251 initial candidates**, followed
by exact searches for every revised full name. Review date: 2026-11-07.
Names are checked locally against the previous three registers and one another.

| Initial candidate or family | Final decision | Reason |
| --- | --- | --- |
| nastas family, including Nastasen | naswen family, including Naswenen | Nastasen is a historical king; Nastasun also matched an inflected fictional character name. Rebuilt the whole family with snass + séew. |
| pasin family | paysin family | Pasinem and Pasinun appeared as personal names; Pasinow as a surname/place string; Pasinowan as an existing food term. Revised the shared stem consistently. |
| sepay family | sehpai family | Sepayesh appeared as a surname/street; Sepayun as a settlement label. |
| hetil family | hentil family | Hetilesh appeared as a personal name. Hentilun then also matched a personal name, so that settlement became Hentilavun. |
| Pasilolan | Pasilereth | Existing personal-name occurrence. |
| Pasewask | Pasewaveth | Existing surname occurrence. |
| Kwalisun | Kwalisavun | Existing business-name occurrence. |
| Asnawesh | Asnaweresh | Personal-name occurrence in a document. |
| Asnawil, then Asnawiv | Asnawolen | Existing personal name; the intermediate spelling also appeared in an author reference, possibly a typo. |
| Paynasim | Paynasiv | Existing product-name proposal. |
| Hentilem | Hentilerem | Existing online handle; replaced to reduce the association. |

Some early person candidates also duplicated settlement constructions; these were
changed before the web screen. All final person and settlement names are distinct.
Incidental ordinary-word, OCR, and handle matches remain, including Asnipun,
Kwalisem, Pasilem, Asanilun, Hepayeth, Asnawem, Pasilun (a line-broken longer name),
Pasilen (a handle and truncated word), Tisekan, Pashenol (apparent ingredient-text
error), and Paysinun (garbled OCR). These were not treated as verified name copies.
Exact-search absence is not proof of worldwide uniqueness.

Representative collision evidence:
[historical Nastasen text](https://www.attalus.org/egypt/nastasen.html),
[Asnawil profile](https://iiiteasea.org/professor-dr-asnawil-g-ronsing/),
[Hentilun in an official staff table](https://nlsic.nagaland.gov.in/wp-content/uploads/2019/09/manual10-4.pdf).
These sources informed rejection decisions; they supplied no naming vocabulary.

Validation checks the 226 exact settlement nodes, their county/duchy metadata,
all 25 court resource links and ranks, the personal ledger, unique final names,
and overlap with earlier registers. This verifies documentation assignments,
not runtime display behavior or geographical suitability.

### Rainforest research sources

Consulted 2026-11-07. Sources support the stated lexical glosses and language
context only; the fictional names, sound rules, suffixes, and wishes are authored.

- **R1:** Tulalip Tribes Lushootseed Department,
  [Making Cedar Oil activity](https://tulaliplushootseed.com/wp-content/uploads/2024/11/summer-cedar_oil-family.pdf),
  `x̱pay̓ac`, cedar tree. Only the lexical item informs the register.
- **R2:** Tulalip Tribes Lushootseed Department,
  [Dining-room vocabulary](https://tulaliplushootseed.com/lushootseed-dining-room-prayer/),
  beverage list: `qʷuʔ`, water. No prayer text is used.
- **R3:** [Intermediate Tlingit](https://tlingitlanguage.com/wp-content/uploads/2015/01/Intermediate-Tlingit-2012.pdf),
  possessed-noun examples for `aas` and `héen`, plus relational-noun examples
  involving `séew`. Ordinary tree, water/river, and rain vocabulary.
- **R4:** [Lingít dictionary, English index](https://tlingitlanguage.com/dictionary/English.html),
  rain entry `séew`; [Tlingit index](https://tlingitlanguage.com/dictionary/Tlingit.html)
  for tree vocabulary. Do not borrow the ceremonial “Tree People” compound.
- **R5:** George Gibbs, [A Dictionary of the Chinook Jargon (1863), transcription](https://alfredgibbs.com/george-gibbs-project/works/chinook-jargon-dictionary-1863/),
  entries snass, tipso/tupso, and illahie. Historical lexical source; modern
  language practice and spelling are not inferred from it.
- **R6:** Chinook Indian Nation, [Language: Chinuk Wawa](https://chinooknation.org/language/),
  context for the contact language and its multiple contributing languages.

## Tropical Rainforest naming

### Scope and identity

Requested 2026-11-07: settlement and person names inspired by cultures and languages
of the **Amazon rainforest, Congo, Borneo, and New Guinea**. This first palette
selects **Nheengatu, Lingala, Iban, and West Kewa**, respectively. These are
specific linguistic inspirations, not labels for all the peoples in those regions.
All four contribute to both registers; individual names blend two or three,
following the user's established preference for a smaller blend per name.

The intended impression is inhabited tropical forest: layered canopy, rain-fed
growth, waterways, boat travel, gardens, shared building work, and homes above
seasonal water. Avoid reducing the kingdom to danger or an undifferentiated
“jungle culture.” The game’s counts, dukes, and king are existing fictional offices,
not adaptations of these cultures' political institutions.

The current `vcom/Scenes/Map.tscn` identifies this as **Kingdom 9**, counties
**195–219**, duchies **40–44**. Its **192 settlements** comprise 1 kingdom
capital, 4 duchy capitals, 20 county capitals, 67 villages, and 100 hamlets.
Its **25 current courts** comprise 1 king, 4 dukes, and 20 counts. These names
are documentation proposals; scene labels and resources are unchanged.

### Source palette and boundaries

| Requested region | Specific selection and verified words | Contribution |
| --- | --- | --- |
| Amazon | Nheengatu, using the canoe-focused publication *Mayé yamuyã bügu*: `igara`, wooden canoe; `mirá`, tree/wood; `kaá`, vegetation [TR1] | Forest growth, building timber, and movement by boat. Preserve the accent on source `mirá`; it is distinct from `mira`, person/people, in that glossary. |
| Congo | Lingala: `zámba`, forest; `nzete` / `nzeté`, tree/wood; `mbúla`, rain [TR2–TR4] | Canopy, rainfall, and wooded ground. This is a Congo-basin language selection, not a claim that every forest community speaks Lingala. |
| Borneo | Iban: `kayuʔ`, tree/wood, in the comparative dictionary; `ai`, water, in Borneo Dictionary [TR5, TR6] | Trees, workable wood, and waterside life. Source orthographies differ; the final glottal stop is recorded where supplied, not reproduced in the fictional spelling. |
| New Guinea | West Kewa teaching and comparative material: `ipa`, water; `repena`, tree/wood in the selected context [TR7–TR9] | Water, wood, and construction. This is a Southern Highlands selection, not a generic lowland New Guinea language. The source also uses repena in fire-related senses; the authored lexicon selects its tree/wood imagery. |

The ordinary vocabulary supplies inspiration only. No real settlement, clan,
ruler, ceremonial title, or personal naming formula is intentionally copied.
The habitation vocabulary, naming wishes, and semantic combinations below are
invented; they are not translations in any source language.

### Sound and construction rules

- Stress the **second syllable from the beginning** in every name:
  Mirumbunalo = mi-RU-mbu-na-lo; Aygarandi = ay-GA-ra-ndi.
- Use clear vowels `a e i o u`, approximately ah, eh, ee, oh, oo.
  `ay` is one syllable, like *eye*; elsewhere `y` is the consonant in *yes*.
  Follow the ledgers' syllable boundaries.
- Favor flowing vowels with `m n r l` and compact `mb nd nz ng nj` clusters.
  A cluster starts the syllable shown: `mbu` has no extra vowel before b;
  `nga` uses ng as in *finger*, and `nji` uses n plus j as in *jam*.
  These are fictional pronunciation conventions, not instruction in the source languages.
- Settlement stems have three or four syllables and take a two-syllable invented
  habitation ending. Personal names take a one-syllable invented tail.
  The longer place names help separate this tradition from the clipped tundra
  forms and the evergreen rainforest's final stress.
- Five-syllable place names stress their second syllable, whereas the volcanic
  tradition stresses the third. Some shorter personal names share a stress
  position with volcanic names; consonant patterns and the root palette provide
  additional distinction. Stress alone is not a biome identifier.
- Transform ordinary words through shortening, vowel adjustment, insertion, or
  recombination. These are design operations, not historical sound changes.
  A real word may survive within a compound, but the complete name must be a new blend.
- Preserve diacritics in source notes; use the fictional spelling in assignments.
  Do not import real noun classes, tone systems, gender, or grammatical suffixes.
- Allocate mixed stems across political boundaries. No duchy is equated with a
  real culture. This first register distributes combinations for variety;
  a name story does not establish actual terrain, buildings, or travel routes.

### Blended stem ledger

| Fictional stem | Syllables | Source transformations | Fictional image | Regional blend |
| --- | --- | --- | --- | --- |
| mirumbu | mi-ru-mbu | mirá→miru + mbúla→mbu | rain through tall trees | Amazon + Congo |
| garanza | ga-ra-nza | igara→gara + zámba→nza | boat routes into forest | Amazon + Congo |
| kambule | ka-mbu-le | kaá→ka + mbúla→mbu, invented le | rain-fed undergrowth | Amazon + Congo |
| zarepa | za-re-pa | zámba→za + repena→repa | deep wooded country | Congo + New Guinea |
| nzekayu | nze-ka-yu | nzete→nze + kayuʔ→kayu | interwoven tree canopy | Congo + Borneo |
| repayu | re-pa-yu | repena→repa + kayuʔ→yu | wood for shared construction | New Guinea + Borneo |
| kayumba | ka-yu-mba | kayuʔ→kayu + mbúla→mba | rain-washed trunks | Borneo + Congo |
| ipamiru | i-pa-mi-ru | ipa + mirá→miru | water beneath trees | New Guinea + Amazon |
| aygara | ay-ga-ra | ai→ay + igara→gara | passage by boat | Borneo + Amazon |
| mirayu | mi-ra-yu | mirá→mira + kayuʔ→yu | layered canopy | Amazon + Borneo |
| garipa | ga-ri-pa | igara→gari + ipa→pa | boat landing water | Amazon + New Guinea |
| repenza | re-pe-nza | repena→repe + zámba→nza | woodland building ground | New Guinea + Congo |
| mbukaya | mbu-ka-ya | mbúla→mbu + kayuʔ→kaya | rain caught by branches | Congo + Borneo |
| zambayu | za-mba-yu | zámba→zamba + kayuʔ→yu | dense tree cover | Congo + Borneo |
| karemi | ka-re-mi | kaá→ka + repena→re, mirá→mi | regrowth around old trunks | Amazon + New Guinea |
| penayu | pe-na-yu | repena→pena + kayuʔ→yu | timber carried along paths | New Guinea + Borneo |
| nzepira | nze-pi-ra | nzete→nze + ipa→pi + mirá→ra | trees beside running water | Congo + New Guinea + Amazon |
| kayipuna | ka-yi-pu-na | kayuʔ→kay + ipa→ipu, invented na | water among roots | Borneo + New Guinea |
| garayun | ga-ra-yun | igara→gara + kayuʔ→yun | wooden boats | Amazon + Borneo |
| mburepa | mbu-re-pa | mbúla→mbu + repena→repa | wet timber and fresh growth | Congo + New Guinea |
| kamayu | ka-ma-yu | kaá→ka + kayuʔ→mayu | green understory | Amazon + Borneo |
| ipazame | i-pa-za-me | ipa + zámba→zame | water through forest | New Guinea + Congo |
| mirenze | mi-re-nze | mirá→mire + nzete→nze | branches meeting overhead | Amazon + Congo |
| ayrepen | ay-re-pen | ai→ay + repena→repen | streamside trees | Borneo + New Guinea |

For example, `kamayu` includes a creatively expanded `kayuʔ→mayu`, and
`garayun` adds a closing n to its shortened tree fragment. Such changes are
explicitly authored. A fictional stem's entire image need not be contained in
the literal meanings of its two source words.

### Invented settlement endings

These endings have only the fictional meanings below. They are independent of
rank: a hamlet and a capital may share an ending. Gardens, raised homes, and
landings are proposed name stories, not verified scene features.

| Ending | Syllables | Fictional habitation sense |
| --- | --- | --- |
| nalo | na-lo | raised waterside homes |
| dume | du-me | shared garden quarter |
| peli | pe-li | covered boat landing |
| wena | we-na | settlement along a forest path |
| sumi | su-mi | sheltered craft quarter |
| ngali | nga-li | homes beside a branching channel |
| belo | be-lo | canopy clearing |
| runi | ru-ni | habitation on higher ground |

**Mirumbunalo** combines rain through tall trees with raised waterside homes.
All other place-name stories are obtained by pairing the stem image with the
ending sense. This keeps the assignments traceable without pretending to supply
authentic translations.

### Settlement assignments

#### Capitals

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `Kingdom9Capital` | 195 | 40 | Mirumbunalo | mirumbu + nalo | mi-RU-mbu-na-lo |
| `Duchy41Capital` | 200 | 41 | Garanzadume | garanza + dume | ga-RA-nza-du-me |
| `Duchy42Capital` | 205 | 42 | Kambulepeli | kambule + peli | ka-MBU-le-pe-li |
| `Duchy43Capital` | 210 | 43 | Zarepawena | zarepa + wena | za-RE-pa-we-na |
| `Duchy44Capital` | 215 | 44 | Nzekayusumi | nzekayu + sumi | nze-KA-yu-su-mi |
| `County196Capital` | 196 | 40 | Repayungali | repayu + ngali | re-PA-yu-nga-li |
| `County197Capital` | 197 | 40 | Kayumbabelo | kayumba + belo | ka-YU-mba-be-lo |
| `County198Capital` | 198 | 40 | Ipamiruruni | ipamiru + runi | i-PA-mi-ru-ru-ni |
| `County199Capital` | 199 | 40 | Aygaranalo | aygara + nalo | ay-GA-ra-na-lo |
| `County201Capital` | 201 | 41 | Mirayudume | mirayu + dume | mi-RA-yu-du-me |
| `County202Capital` | 202 | 41 | Garipapeli | garipa + peli | ga-RI-pa-pe-li |
| `County203Capital` | 203 | 41 | Repenzawena | repenza + wena | re-PE-nza-we-na |
| `County204Capital` | 204 | 41 | Mbukayasumi | mbukaya + sumi | mbu-KA-ya-su-mi |
| `County206Capital` | 206 | 42 | Zambayungali | zambayu + ngali | za-MBA-yu-nga-li |
| `County207Capital` | 207 | 42 | Karemibelo | karemi + belo | ka-RE-mi-be-lo |
| `County208Capital` | 208 | 42 | Penayuruni | penayu + runi | pe-NA-yu-ru-ni |
| `County209Capital` | 209 | 42 | Nzepiranalo | nzepira + nalo | nze-PI-ra-na-lo |
| `County211Capital` | 211 | 43 | Kayipunadume | kayipuna + dume | ka-YI-pu-na-du-me |
| `County212Capital` | 212 | 43 | Garayunpeli | garayun + peli | ga-RA-yun-pe-li |
| `County213Capital` | 213 | 43 | Mburepawena | mburepa + wena | mbu-RE-pa-we-na |
| `County214Capital` | 214 | 43 | Kamayusumi | kamayu + sumi | ka-MA-yu-su-mi |
| `County216Capital` | 216 | 44 | Ipazamengali | ipazame + ngali | i-PA-za-me-nga-li |
| `County217Capital` | 217 | 44 | Mirenzebelo | mirenze + belo | mi-RE-nze-be-lo |
| `County218Capital` | 218 | 44 | Ayrepenruni | ayrepen + runi | ay-RE-pen-ru-ni |
| `County219Capital` | 219 | 44 | Mirumbudume | mirumbu + dume | mi-RU-mbu-du-me |

#### Villages

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County195Village1` | 195 | 40 | Garanzapeli | garanza + peli | ga-RA-nza-pe-li |
| `County195Village2` | 195 | 40 | Kambulewena | kambule + wena | ka-MBU-le-we-na |
| `County195Village3` | 195 | 40 | Zarepasumi | zarepa + sumi | za-RE-pa-su-mi |
| `County196Village1` | 196 | 40 | Nzekayungali | nzekayu + ngali | nze-KA-yu-nga-li |
| `County196Village2` | 196 | 40 | Repayubelo | repayu + belo | re-PA-yu-be-lo |
| `County197Village1` | 197 | 40 | Kayumbaruni | kayumba + runi | ka-YU-mba-ru-ni |
| `County197Village2` | 197 | 40 | Ipamirunalo | ipamiru + nalo | i-PA-mi-ru-na-lo |
| `County197Village3` | 197 | 40 | Aygaradume | aygara + dume | ay-GA-ra-du-me |
| `County198Village1` | 198 | 40 | Mirayupeli | mirayu + peli | mi-RA-yu-pe-li |
| `County198Village2` | 198 | 40 | Garipawena | garipa + wena | ga-RI-pa-we-na |
| `County198Village3` | 198 | 40 | Repenzasumi | repenza + sumi | re-PE-nza-su-mi |
| `County198Village4` | 198 | 40 | Mbukayangali | mbukaya + ngali | mbu-KA-ya-nga-li |
| `County199Village1` | 199 | 40 | Zambayubelo | zambayu + belo | za-MBA-yu-be-lo |
| `County199Village2` | 199 | 40 | Karemiruni | karemi + runi | ka-RE-mi-ru-ni |
| `County199Village3` | 199 | 40 | Penayunalo | penayu + nalo | pe-NA-yu-na-lo |
| `County199Village4` | 199 | 40 | Nzepiradume | nzepira + dume | nze-PI-ra-du-me |
| `County200Village1` | 200 | 41 | Kayipunapeli | kayipuna + peli | ka-YI-pu-na-pe-li |
| `County200Village2` | 200 | 41 | Garayunwena | garayun + wena | ga-RA-yun-we-na |
| `County200Village3` | 200 | 41 | Mburepasumi | mburepa + sumi | mbu-RE-pa-su-mi |
| `County200Village4` | 200 | 41 | Kamayungali | kamayu + ngali | ka-MA-yu-nga-li |
| `County200Village5` | 200 | 41 | Ipazamebelo | ipazame + belo | i-PA-za-me-be-lo |
| `County201Village1` | 201 | 41 | Mirenzeruni | mirenze + runi | mi-RE-nze-ru-ni |
| `County201Village2` | 201 | 41 | Ayrepennalo | ayrepen + nalo | ay-RE-pen-na-lo |
| `County201Village3` | 201 | 41 | Mirumbupeli | mirumbu + peli | mi-RU-mbu-pe-li |
| `County202Village1` | 202 | 41 | Garanzawena | garanza + wena | ga-RA-nza-we-na |
| `County202Village2` | 202 | 41 | Kambulesumi | kambule + sumi | ka-MBU-le-su-mi |
| `County203Village1` | 203 | 41 | Zarepangali | zarepa + ngali | za-RE-pa-nga-li |
| `County203Village2` | 203 | 41 | Nzekayubelo | nzekayu + belo | nze-KA-yu-be-lo |
| `County203Village3` | 203 | 41 | Repayuruni | repayu + runi | re-PA-yu-ru-ni |
| `County204Village1` | 204 | 41 | Kayumbanalo | kayumba + nalo | ka-YU-mba-na-lo |
| `County204Village2` | 204 | 41 | Ipamirudume | ipamiru + dume | i-PA-mi-ru-du-me |
| `County204Village3` | 204 | 41 | Aygarapeli | aygara + peli | ay-GA-ra-pe-li |
| `County204Village4` | 204 | 41 | Mirayuwena | mirayu + wena | mi-RA-yu-we-na |
| `County204Village5` | 204 | 41 | Garipasumi | garipa + sumi | ga-RI-pa-su-mi |
| `County205Village1` | 205 | 42 | Repenzangali | repenza + ngali | re-PE-nza-nga-li |
| `County205Village2` | 205 | 42 | Mbukayabelo | mbukaya + belo | mbu-KA-ya-be-lo |
| `County205Village3` | 205 | 42 | Zambayuruni | zambayu + runi | za-MBA-yu-ru-ni |
| `County206Village1` | 206 | 42 | Kareminalo | karemi + nalo | ka-RE-mi-na-lo |
| `County206Village2` | 206 | 42 | Penayudume | penayu + dume | pe-NA-yu-du-me |
| `County206Village3` | 206 | 42 | Nzepirapeli | nzepira + peli | nze-PI-ra-pe-li |
| `County207Village1` | 207 | 42 | Kayipunawena | kayipuna + wena | ka-YI-pu-na-we-na |
| `County207Village2` | 207 | 42 | Garayunsumi | garayun + sumi | ga-RA-yun-su-mi |
| `County208Village1` | 208 | 42 | Mburepangali | mburepa + ngali | mbu-RE-pa-nga-li |
| `County208Village2` | 208 | 42 | Kamayubelo | kamayu + belo | ka-MA-yu-be-lo |
| `County208Village3` | 208 | 42 | Ipazameruni | ipazame + runi | i-PA-za-me-ru-ni |
| `County209Village1` | 209 | 42 | Mirenzenalo | mirenze + nalo | mi-RE-nze-na-lo |
| `County210Village1` | 210 | 43 | Ayrependume | ayrepen + dume | ay-RE-pen-du-me |
| `County212Village1` | 212 | 43 | Mirumbuwena | mirumbu + wena | mi-RU-mbu-we-na |
| `County213Village1` | 213 | 43 | Garanzasumi | garanza + sumi | ga-RA-nza-su-mi |
| `County213Village2` | 213 | 43 | Kambulengali | kambule + ngali | ka-MBU-le-nga-li |
| `County213Village3` | 213 | 43 | Zarepabelo | zarepa + belo | za-RE-pa-be-lo |
| `County213Village4` | 213 | 43 | Nzekayuruni | nzekayu + runi | nze-KA-yu-ru-ni |
| `County214Village1` | 214 | 43 | Repayunalo | repayu + nalo | re-PA-yu-na-lo |
| `County214Village2` | 214 | 43 | Kayumbadume | kayumba + dume | ka-YU-mba-du-me |
| `County214Village3` | 214 | 43 | Ipamirupeli | ipamiru + peli | i-PA-mi-ru-pe-li |
| `County214Village4` | 214 | 43 | Aygarawena | aygara + wena | ay-GA-ra-we-na |
| `County215Village1` | 215 | 44 | Mirayusumi | mirayu + sumi | mi-RA-yu-su-mi |
| `County215Village2` | 215 | 44 | Garipangali | garipa + ngali | ga-RI-pa-nga-li |
| `County216Village1` | 216 | 44 | Repenzabelo | repenza + belo | re-PE-nza-be-lo |
| `County217Village1` | 217 | 44 | Mbukayaruni | mbukaya + runi | mbu-KA-ya-ru-ni |
| `County218Village1` | 218 | 44 | Zambayunalo | zambayu + nalo | za-MBA-yu-na-lo |
| `County218Village2` | 218 | 44 | Karemidume | karemi + dume | ka-RE-mi-du-me |
| `County218Village3` | 218 | 44 | Penayupeli | penayu + peli | pe-NA-yu-pe-li |
| `County218Village4` | 218 | 44 | Nzepirawena | nzepira + wena | nze-PI-ra-we-na |
| `County219Village1` | 219 | 44 | Kayipunasumi | kayipuna + sumi | ka-YI-pu-na-su-mi |
| `County219Village2` | 219 | 44 | Garayunngali | garayun + ngali | ga-RA-yun-nga-li |
| `County219Village3` | 219 | 44 | Mburepabelo | mburepa + belo | mbu-RE-pa-be-lo |

#### Hamlets

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County195Hamlet1` | 195 | 40 | Kamayuruni | kamayu + runi | ka-MA-yu-ru-ni |
| `County196Hamlet1` | 196 | 40 | Ipazamenalo | ipazame + nalo | i-PA-za-me-na-lo |
| `County196Hamlet2` | 196 | 40 | Mirenzedume | mirenze + dume | mi-RE-nze-du-me |
| `County196Hamlet3` | 196 | 40 | Ayrepenpeli | ayrepen + peli | ay-RE-pen-pe-li |
| `County197Hamlet1` | 197 | 40 | Mirumbusumi | mirumbu + sumi | mi-RU-mbu-su-mi |
| `County197Hamlet2` | 197 | 40 | Garanzangali | garanza + ngali | ga-RA-nza-nga-li |
| `County197Hamlet3` | 197 | 40 | Kambulebelo | kambule + belo | ka-MBU-le-be-lo |
| `County197Hamlet4` | 197 | 40 | Zareparuni | zarepa + runi | za-RE-pa-ru-ni |
| `County197Hamlet5` | 197 | 40 | Nzekayunalo | nzekayu + nalo | nze-KA-yu-na-lo |
| `County198Hamlet1` | 198 | 40 | Repayudume | repayu + dume | re-PA-yu-du-me |
| `County198Hamlet2` | 198 | 40 | Kayumbapeli | kayumba + peli | ka-YU-mba-pe-li |
| `County198Hamlet3` | 198 | 40 | Ipamiruwena | ipamiru + wena | i-PA-mi-ru-we-na |
| `County198Hamlet4` | 198 | 40 | Aygarasumi | aygara + sumi | ay-GA-ra-su-mi |
| `County198Hamlet5` | 198 | 40 | Mirayungali | mirayu + ngali | mi-RA-yu-nga-li |
| `County198Hamlet6` | 198 | 40 | Garipabelo | garipa + belo | ga-RI-pa-be-lo |
| `County199Hamlet1` | 199 | 40 | Repenzaruni | repenza + runi | re-PE-nza-ru-ni |
| `County199Hamlet2` | 199 | 40 | Mbukayanalo | mbukaya + nalo | mbu-KA-ya-na-lo |
| `County199Hamlet3` | 199 | 40 | Zambayudume | zambayu + dume | za-MBA-yu-du-me |
| `County199Hamlet4` | 199 | 40 | Karemipeli | karemi + peli | ka-RE-mi-pe-li |
| `County199Hamlet5` | 199 | 40 | Penayuwena | penayu + wena | pe-NA-yu-we-na |
| `County199Hamlet6` | 199 | 40 | Nzepirasumi | nzepira + sumi | nze-PI-ra-su-mi |
| `County199Hamlet7` | 199 | 40 | Kayipunangali | kayipuna + ngali | ka-YI-pu-na-nga-li |
| `County199Hamlet8` | 199 | 40 | Garayunbelo | garayun + belo | ga-RA-yun-be-lo |
| `County200Hamlet1` | 200 | 41 | Mbureparuni | mburepa + runi | mbu-RE-pa-ru-ni |
| `County200Hamlet2` | 200 | 41 | Kamayunalo | kamayu + nalo | ka-MA-yu-na-lo |
| `County200Hamlet3` | 200 | 41 | Ipazamedume | ipazame + dume | i-PA-za-me-du-me |
| `County201Hamlet1` | 201 | 41 | Mirenzepeli | mirenze + peli | mi-RE-nze-pe-li |
| `County201Hamlet2` | 201 | 41 | Ayrepenwena | ayrepen + wena | ay-RE-pen-we-na |
| `County201Hamlet3` | 201 | 41 | Mirumbungali | mirumbu + ngali | mi-RU-mbu-nga-li |
| `County202Hamlet1` | 202 | 41 | Garanzabelo | garanza + belo | ga-RA-nza-be-lo |
| `County202Hamlet2` | 202 | 41 | Kambuleruni | kambule + runi | ka-MBU-le-ru-ni |
| `County202Hamlet3` | 202 | 41 | Zarepanalo | zarepa + nalo | za-RE-pa-na-lo |
| `County202Hamlet4` | 202 | 41 | Nzekayudume | nzekayu + dume | nze-KA-yu-du-me |
| `County203Hamlet1` | 203 | 41 | Repayupeli | repayu + peli | re-PA-yu-pe-li |
| `County203Hamlet2` | 203 | 41 | Kayumbawena | kayumba + wena | ka-YU-mba-we-na |
| `County203Hamlet3` | 203 | 41 | Ipamirusumi | ipamiru + sumi | i-PA-mi-ru-su-mi |
| `County203Hamlet4` | 203 | 41 | Aygarangali | aygara + ngali | ay-GA-ra-nga-li |
| `County203Hamlet5` | 203 | 41 | Mirayubelo | mirayu + belo | mi-RA-yu-be-lo |
| `County204Hamlet1` | 204 | 41 | Gariparuni | garipa + runi | ga-RI-pa-ru-ni |
| `County204Hamlet2` | 204 | 41 | Repenzanalo | repenza + nalo | re-PE-nza-na-lo |
| `County204Hamlet3` | 204 | 41 | Mbukayadume | mbukaya + dume | mbu-KA-ya-du-me |
| `County204Hamlet4` | 204 | 41 | Zambayupeli | zambayu + peli | za-MBA-yu-pe-li |
| `County205Hamlet1` | 205 | 42 | Karemiwena | karemi + wena | ka-RE-mi-we-na |
| `County205Hamlet2` | 205 | 42 | Penayusumi | penayu + sumi | pe-NA-yu-su-mi |
| `County205Hamlet3` | 205 | 42 | Nzepirangali | nzepira + ngali | nze-PI-ra-nga-li |
| `County205Hamlet4` | 205 | 42 | Kayipunabelo | kayipuna + belo | ka-YI-pu-na-be-lo |
| `County205Hamlet5` | 205 | 42 | Garayunruni | garayun + runi | ga-RA-yun-ru-ni |
| `County206Hamlet1` | 206 | 42 | Mburepanalo | mburepa + nalo | mbu-RE-pa-na-lo |
| `County206Hamlet2` | 206 | 42 | Kamayudume | kamayu + dume | ka-MA-yu-du-me |
| `County207Hamlet1` | 207 | 42 | Ipazamepeli | ipazame + peli | i-PA-za-me-pe-li |
| `County207Hamlet2` | 207 | 42 | Mirenzewena | mirenze + wena | mi-RE-nze-we-na |
| `County207Hamlet3` | 207 | 42 | Ayrepensumi | ayrepen + sumi | ay-RE-pen-su-mi |
| `County208Hamlet1` | 208 | 42 | Mirumbubelo | mirumbu + belo | mi-RU-mbu-be-lo |
| `County208Hamlet2` | 208 | 42 | Garanzaruni | garanza + runi | ga-RA-nza-ru-ni |
| `County208Hamlet3` | 208 | 42 | Kambulenalo | kambule + nalo | ka-MBU-le-na-lo |
| `County208Hamlet4` | 208 | 42 | Zarepadume | zarepa + dume | za-RE-pa-du-me |
| `County208Hamlet5` | 208 | 42 | Nzekayupeli | nzekayu + peli | nze-KA-yu-pe-li |
| `County208Hamlet6` | 208 | 42 | Repayuwena | repayu + wena | re-PA-yu-we-na |
| `County209Hamlet1` | 209 | 42 | Kayumbasumi | kayumba + sumi | ka-YU-mba-su-mi |
| `County209Hamlet2` | 209 | 42 | Ipamirungali | ipamiru + ngali | i-PA-mi-ru-nga-li |
| `County209Hamlet3` | 209 | 42 | Aygarabelo | aygara + belo | ay-GA-ra-be-lo |
| `County209Hamlet4` | 209 | 42 | Mirayuruni | mirayu + runi | mi-RA-yu-ru-ni |
| `County210Hamlet1` | 210 | 43 | Garipanalo | garipa + nalo | ga-RI-pa-na-lo |
| `County210Hamlet2` | 210 | 43 | Repenzadume | repenza + dume | re-PE-nza-du-me |
| `County210Hamlet3` | 210 | 43 | Mbukayapeli | mbukaya + peli | mbu-KA-ya-pe-li |
| `County210Hamlet4` | 210 | 43 | Zambayuwena | zambayu + wena | za-MBA-yu-we-na |
| `County210Hamlet5` | 210 | 43 | Karemisumi | karemi + sumi | ka-RE-mi-su-mi |
| `County211Hamlet1` | 211 | 43 | Penayungali | penayu + ngali | pe-NA-yu-nga-li |
| `County212Hamlet1` | 212 | 43 | Nzepirabelo | nzepira + belo | nze-PI-ra-be-lo |
| `County212Hamlet2` | 212 | 43 | Kayipunaruni | kayipuna + runi | ka-YI-pu-na-ru-ni |
| `County213Hamlet1` | 213 | 43 | Garayunnalo | garayun + nalo | ga-RA-yun-na-lo |
| `County213Hamlet2` | 213 | 43 | Mburepadume | mburepa + dume | mbu-RE-pa-du-me |
| `County213Hamlet3` | 213 | 43 | Kamayupeli | kamayu + peli | ka-MA-yu-pe-li |
| `County213Hamlet4` | 213 | 43 | Ipazamewena | ipazame + wena | i-PA-za-me-we-na |
| `County213Hamlet5` | 213 | 43 | Mirenzesumi | mirenze + sumi | mi-RE-nze-su-mi |
| `County214Hamlet1` | 214 | 43 | Ayrepenngali | ayrepen + ngali | ay-RE-pen-nga-li |
| `County214Hamlet2` | 214 | 43 | Mirumburuni | mirumbu + runi | mi-RU-mbu-ru-ni |
| `County214Hamlet3` | 214 | 43 | Garanzanalo | garanza + nalo | ga-RA-nza-na-lo |
| `County214Hamlet4` | 214 | 43 | Kambuledume | kambule + dume | ka-MBU-le-du-me |
| `County214Hamlet5` | 214 | 43 | Zarepapeli | zarepa + peli | za-RE-pa-pe-li |
| `County214Hamlet6` | 214 | 43 | Nzekayuwena | nzekayu + wena | nze-KA-yu-we-na |
| `County214Hamlet7` | 214 | 43 | Repayusumi | repayu + sumi | re-PA-yu-su-mi |
| `County214Hamlet8` | 214 | 43 | Kayumbangali | kayumba + ngali | ka-YU-mba-nga-li |
| `County215Hamlet1` | 215 | 44 | Ipamirubelo | ipamiru + belo | i-PA-mi-ru-be-lo |
| `County215Hamlet2` | 215 | 44 | Aygararuni | aygara + runi | ay-GA-ra-ru-ni |
| `County215Hamlet3` | 215 | 44 | Mirayunalo | mirayu + nalo | mi-RA-yu-na-lo |
| `County215Hamlet4` | 215 | 44 | Garipadume | garipa + dume | ga-RI-pa-du-me |
| `County215Hamlet5` | 215 | 44 | Repenzapeli | repenza + peli | re-PE-nza-pe-li |
| `County215Hamlet6` | 215 | 44 | Mbukayawena | mbukaya + wena | mbu-KA-ya-we-na |
| `County215Hamlet7` | 215 | 44 | Zambayusumi | zambayu + sumi | za-MBA-yu-su-mi |
| `County216Hamlet1` | 216 | 44 | Karemingali | karemi + ngali | ka-RE-mi-nga-li |
| `County218Hamlet1` | 218 | 44 | Penayubelo | penayu + belo | pe-NA-yu-be-lo |
| `County218Hamlet2` | 218 | 44 | Nzepiraruni | nzepira + runi | nze-PI-ra-ru-ni |
| `County218Hamlet3` | 218 | 44 | Kayipunanalo | kayipuna + nalo | ka-YI-pu-na-na-lo |
| `County219Hamlet1` | 219 | 44 | Garayundume | garayun + dume | ga-RA-yun-du-me |
| `County219Hamlet2` | 219 | 44 | Mburepapeli | mburepa + peli | mbu-RE-pa-pe-li |
| `County219Hamlet3` | 219 | 44 | Kamayuwena | kamayu + wena | ka-MA-yu-we-na |
| `County219Hamlet4` | 219 | 44 | Ipazamesumi | ipazame + sumi | i-PA-za-me-su-mi |
| `County219Hamlet5` | 219 | 44 | Mirenzengali | mirenze + ngali | mi-RE-nze-nga-li |
| `County219Hamlet6` | 219 | 44 | Ayrepenbelo | ayrepen + belo | ay-RE-pen-be-lo |

### Person names and construction ledger

Use ungendered mononyms and title-first display: **King Aygarandi**,
**Duke Mirayumo**. No family names, dynasties, genealogies, or real-world honorifics
are inferred. A personal name uses the same mixed vocabulary as settlements,
with a separate invented tail; it is not an abbreviated name for the ruler's seat.

Each stem's two- or three-language construction appears in the stem ledger.
Personal tails have no independent authentic meaning. Naming wishes are authored
hopes for a person, not statements about an incumbent's behavior or abilities.

| Name | Pronunciation | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Aygarandi | ay-GA-ra-ndi | aygara + invented ndi | one who keeps a passage open |
| Mirayumo | mi-RA-yu-mo | mirayu + invented mo | care that helps others flourish |
| Garipanga | ga-RI-pa-nga | garipa + invented nga | patience through rising waters |
| Repenzali | re-PE-nza-li | repenza + invented li | one who provides a welcome |
| Mbukayanu | mbu-KA-ya-nu | mbukaya + invented nu | strength used in common work |
| Zambayunji | za-MBA-yu-nji | zambayu + invented nji | care for returning growth |
| Karemindu | ka-RE-mi-ndu | karemi + invented ndu | one who remembers the way home |
| Penayune | pe-NA-yu-ne | penayu + invented ne | provision shared freely |
| Nzepiramu | nze-PI-ra-mu | nzepira + invented mu | steady hands in changing weather |
| Kayipunanda | ka-YI-pu-na-nda | kayipuna + invented nda | room for the next generation |
| Garayunvi | ga-RA-yun-vi | garayun + invented vi | one who brings neighbors together |
| Mburepalu | mbu-RE-pa-lu | mburepa + invented lu | thoughtful use of what grows |
| Kamayunzi | ka-MA-yu-nzi | kamayu + invented nzi | one who helps others cross |
| Ipazamepo | i-PA-za-me-po | ipazame + invented po | steadiness when plans change |
| Mirenzeme | mi-RE-nze-me | mirenze + invented me | one who tends small beginnings |
| Ayrepenni | ay-RE-pen-ni | ayrepen + invented ni | skill placed at others' service |
| Mirumbungu | mi-RU-mbu-ngu | mirumbu + invented ngu | a welcome after a long journey |
| Garanzava | ga-RA-nza-va | garanza + invented va | one who listens before deciding |
| Kambulemi | ka-MBU-le-mi | kambule + invented mi | resolve tempered by care |
| Zarepano | za-RE-pa-no | zarepa + invented no | patient work that lasts |
| Nzekayupa | nze-KA-yu-pa | nzekayu + invented pa | one who renews a shared home |
| Repayudu | re-PA-yu-du | repayu + invented du | a dependable source of help |
| Kayumbalo | ka-YU-mba-lo | kayumba + invented lo | one who makes room for new growth |
| Ipamiruna | i-PA-mi-ru-na | ipamiru + invented na | good judgment along uncertain routes |
| Aygaranzo | ay-GA-ra-nzo | aygara + invented nzo | shelter offered without hesitation |

### Court assignments

| Court resource | Rank | Proposed person name | Seat node | Proposed seat name | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom9Capital` | King | Aygarandi | `Kingdom9Capital` | Mirumbunalo | 195 | 40 |
| `Court_Duchy41Capital` | Duke | Mirayumo | `Duchy41Capital` | Garanzadume | 200 | 41 |
| `Court_Duchy42Capital` | Duke | Garipanga | `Duchy42Capital` | Kambulepeli | 205 | 42 |
| `Court_Duchy43Capital` | Duke | Repenzali | `Duchy43Capital` | Zarepawena | 210 | 43 |
| `Court_Duchy44Capital` | Duke | Mbukayanu | `Duchy44Capital` | Nzekayusumi | 215 | 44 |
| `Court_County196Capital` | Count | Zambayunji | `County196Capital` | Repayungali | 196 | 40 |
| `Court_County197Capital` | Count | Karemindu | `County197Capital` | Kayumbabelo | 197 | 40 |
| `Court_County198Capital` | Count | Penayune | `County198Capital` | Ipamiruruni | 198 | 40 |
| `Court_County199Capital` | Count | Nzepiramu | `County199Capital` | Aygaranalo | 199 | 40 |
| `Court_County201Capital` | Count | Kayipunanda | `County201Capital` | Mirayudume | 201 | 41 |
| `Court_County202Capital` | Count | Garayunvi | `County202Capital` | Garipapeli | 202 | 41 |
| `Court_County203Capital` | Count | Mburepalu | `County203Capital` | Repenzawena | 203 | 41 |
| `Court_County204Capital` | Count | Kamayunzi | `County204Capital` | Mbukayasumi | 204 | 41 |
| `Court_County206Capital` | Count | Ipazamepo | `County206Capital` | Zambayungali | 206 | 42 |
| `Court_County207Capital` | Count | Mirenzeme | `County207Capital` | Karemibelo | 207 | 42 |
| `Court_County208Capital` | Count | Ayrepenni | `County208Capital` | Penayuruni | 208 | 42 |
| `Court_County209Capital` | Count | Mirumbungu | `County209Capital` | Nzepiranalo | 209 | 42 |
| `Court_County211Capital` | Count | Garanzava | `County211Capital` | Kayipunadume | 211 | 43 |
| `Court_County212Capital` | Count | Kambulemi | `County212Capital` | Garayunpeli | 212 | 43 |
| `Court_County213Capital` | Count | Zarepano | `County213Capital` | Mburepawena | 213 | 43 |
| `Court_County214Capital` | Count | Nzekayupa | `County214Capital` | Kamayusumi | 214 | 43 |
| `Court_County216Capital` | Count | Repayudu | `County216Capital` | Ipazamengali | 216 | 44 |
| `Court_County217Capital` | Count | Kayumbalo | `County217Capital` | Mirenzebelo | 217 | 44 |
| `Court_County218Capital` | Count | Ipamiruna | `County218Capital` | Ayrepenruni | 218 | 44 |
| `Court_County219Capital` | Count | Aygaranzo | `County219Capital` | Mirumbudume | 219 | 44 |

Kingdom9Capital is the shared seat for county 195 and duchy 40. Duchy41Capital,
Duchy42Capital, Duchy43Capital, and Duchy44Capital are shared seats for counties
200, 205, 210, and 215 respectively. No additional count courts exist at those
five seats, and there is no separate duchy-40 court. This does not establish
combined legal titles; do not invent six more incumbents.

### Screening, revisions, and validation

On 2026-11-07, individually quoted web searches screened all **217 initial names**
(192 settlements and 25 people), followed by searches for revised full names.

| Candidate | Decision | Reason |
| --- | --- | --- |
| Zambayumba | Replace with **Zambayunji** | Existing personal-profile name occurrence. The zambayu stem remains; the invented tail changes to nji. |
| Karemiro | Replace with **Karemindu** | Existing online handle/name occurrence. The karemi stem remains; the invented tail changes to ndu. |
| Mirayumo | Retain | Apparent OCR error in a bibliographic publisher reference; not established as a copied name. |
| Zarepano | Retain | Ordinary running-text usage in Slovenian; not established as a personal or settlement name. |

The exact searches returned no results for the two replacement spellings.
Searches are a limited collision screen, not proof of worldwide uniqueness.
Common short syllables and source fragments will naturally recur elsewhere.

Local validation checks all 192 settlement nodes against Kingdom 9 scene metadata,
all 25 court links and existing ranks, the personal ledger, construction and
pronunciation spellings, and uniqueness across this register and the previous
four biome registers. Geographical suitability and in-game display are not
established by those checks.

### Tropical rainforest research sources

Consulted 2026-11-07. These establish source words and context, not the invented
names, tails, endings, or complete name stories.

- **TR1:** [*Mayé yamuyã bügu*, Nheengatu canoe publication, glossary](https://files.cercomp.ufg.br/weby/up/26/o/LIVRO_MYB_EBOOK-1.pdf),
  hosted by Universidade Federal de Goiás, printed p. 96 onward. Igara,
  mirá, and kaá are taken from this particular glossary; its Portuguese senses
  govern the selected meanings rather than broad English shorthand.
- **TR2:** [Lingala dictionary: zámba](https://dic.lingala.be/fr/nzamba),
  forest/woods entry; the page explicitly distinguishes zámba from the erroneous
  nzámba spelling. Our nza fragment is a fictional transformation, not that spelling.
- **TR3:** [Lingala dictionary: nzete / nzeté](https://dic.lingala.be/en/nzete),
  tree/wood entry, including its marked Kinshasa usage. No noun-class rules are borrowed.
- **TR4:** Royal Museum for Central Africa,
  [Lingala comparative lexical data](https://www.africamuseum.be/lexico_bantu/C/C36d_lingala.pdf),
  entry 63, rain, mbúla, with its underlying lexicographic attribution.
- **TR5:** Austronesian Comparative Dictionary,
  [*kaSiw cognate set](https://acd.clld.org/cognatesets/30531),
  specifically the Iban kayuʔ entry, tree/wood. The reconstructed headword is
  not used as an Iban word.
- **TR6:** Borneo Dictionary, [Iban ai](https://borneodictionary.com/iban/ai),
  water; entry credited to Borneo Lingua-Hack.
- **TR7:** Karl Franklin, Joice Franklin, and Yapua Kirapeasi,
  [*Learn West Kewa*, 2008 revision of 1973 lessons, available transcription](https://www.scribd.com/document/472257976/West-Kewa-learn),
  lessons 5–6, water and building vocabulary, especially ipa and repena.
  This is an authored teaching text accessed through a third-party transcription.
- **TR8:** Karl J. Franklin, [“Samberigi (Sau) and Kewa”](https://www.langlxmelanesia.com/_files/ugd/4bb486_478328b060c74921990813493aff54b2.pdf),
  *Language & Linguistics in Melanesia* 41 (2023), comparative tree/wood vocabulary
  corroborating repena. Samberigi forms are not borrowed into this register.
- **TR9:** Karl J. and Joice A. Franklin,
  [Kewa dictionary archive](https://pnglanguages.sil.org/resources/archives/31046)
  and [Kewa–English dictionary PDF](https://www-01.sil.org/pacific/png/pubs/928474531046/Kewa_English_dict.pdf),
  ipa water/steam and repena-related entries. The dictionary's fire-related uses
  are acknowledged rather than treating the tree/wood gloss as exhaustive.

## Swamp naming

### Scope and identity

Requested 2026-11-07: settlement and person names inspired by **Uros, Aztec,
Cajan, and Native cultures of Louisiana**. This pass interprets “Cajan” as
**Cajun**. That spelling interpretation is an editorial assumption, not a separate
user clarification.

The selected lexical sources are **Uru (Uchumataqu), historical Nahuatl, Cajun
French, Tunica, and Biloxi**. All five appear in both settlement and person
registers. Individual names blend two or three sources rather than every source
at once, consistent with the user's earlier preference.

The intended impression is a working wetland: reed margins, moss-hung woods,
shallow channels, paddling routes, raised homes, gardens on firm ground, woven
materials, and landing repairs. Avoid making the swamp synonymous with decay,
disease, or menace. The game's feudal offices do not claim to reproduce the
political or naming institutions of the source cultures.

The current `vcom/Scenes/Map.tscn` identifies **Kingdom 7** with **192 settlements**:
1 kingdom capital, 5 duchy capitals, 18 county capitals, 67 villages, and 101
hamlets. There are **24 current courts**: 1 king, 5 dukes, and 18 counts.
Counties are **147–169 plus 220**, across duchies **29–34**. County 220 belongs
to duchy 33; its unusual number is retained exactly. This is a documentation
register, not a change to scene labels or game resources.

### Source palette and distinctions

| Requested inspiration | Specific basis | Contribution and boundary |
| --- | --- | --- |
| Uros | Uru/Uchumataqu `qhasi`, water, and `juwa`, totora reeds, as attributed to Muysken (2005) in the compiled Uru vocabulary [SW1] | Shallow water and reeds. These are specific documented Uru forms, not a claim that every present-day Uros community uses this vocabulary. Uru-Chipaya varieties are distinguished in the research documentation [SW2]; Chipaya is not silently substituted for Uchumataqu. |
| Aztec | Historical Nahuatl `acatl`, reed/cane, and `atl` / `ātl`, water [SW3, SW4] | Reed beds and water channels. “Aztec” is the user's cultural reference; Nahuatl is the linguistic selection. Only ordinary environmental senses are used, not calendrical names or existing rulers' names. |
| Cajun | Cajun French `cyprière`, cypress grove/swamp, and `pagaille`, paddle, in LSU's glossary [SW5] | Swamp woodland and paddling. The fictional forms deliberately depart from French spelling and pronunciation. These words need not be exclusive to Cajun French to serve as documented Cajun-language inspiration. |
| Native Louisiana: Tunica | `wishi`, water, and `mohtini`, Spanish moss, in the Tunica-Biloxi Tribe/Louisiana Wildlife Federation's public Tunica learning book [SW6] | Water and moss-shaded habitation. The ordinary plant and water words are used; personal names, ceremonial language, and real offices are not borrowed. |
| Native Louisiana: Biloxi | `aní`, water, among documented Biloxi variants in the Comparative Siouan Dictionary [SW7] | Water links across the marsh. Tunica and Biloxi are separate languages, despite their joint presence in the Tunica-Biloxi Tribe of Louisiana's language work [SW8]. |

The Uru vocabulary records different historical transcriptions and source dates;
the two selected forms above are kept identifiable rather than treating all
variants as interchangeable. The Nahuatl dictionary also records personal and
calendrical uses of acatl; those uses do not motivate these fictional compounds.
Tunica and Biloxi forms come from public linguistic sources, with no claim of
community endorsement of the resulting fantasy names.

### Sound and construction rules

- Stress the **penultimate syllable**. Qasirelenne = qa-si-rel-EN-ne;
  Anacelnel = a-na-CEL-nel. Stress is shared with the desert scheme; the softer
  consonant palette and longer place-name shapes distinguish the swamp.
- Approximate vowels are ah, eh, ee, oh, oo for `a e i o u`. `au` is a single
  rounded oh vowel. All other vowels are pronounced at the boundaries shown.
  Final e is never silent.
- `q` and `c` are always hard k sounds; `j` sounds like the s in *measure*;
  `sh` as in *shore*; `ch` as in *chair*; `th` as in *thin*.
  `y` is the consonant in *yes*. Written doubled consonants cross the listed
  syllable boundary without introducing a new sound.
- Favor `sh j w m n l r`, occasional `pr`, and closed syllables such as
  `qas`, `rel`, and `tin`. These are fictional rules, not authentic
  Uru, Nahuatl, Cajun French, Tunica, or Biloxi phonology.
- Settlement names combine a three-syllable mixed stem and a two-syllable
  invented habitation ending. This first set therefore has five syllables.
  Personal names take a separate invented tail and have four or five syllables.
- Shorten, respell, and reshape ordinary roots before blending. Inserted sounds
  and new endings are authored decisions, not linguistic reconstructions.
  Preserve source accents in the research ledger; use the fictional spelling in
  the assignments. A source word may remain inside a compound, but the whole
  name must be newly constructed.
- Mix sources across counties instead of assigning each real culture to a duchy.
  The first allocation distributes stem/ending combinations for variety.
  Geography-specific name stories remain proposals, not verified descriptions.
- Use neither complete real names nor generic French place-name templates to
  carry the identity. Environmental imagery and consistent fictional vocabulary
  provide the shared sound.

### Blended stem ledger

| Fictional stem | Syllables | Source transformations | Fictional image | Source blend |
| --- | --- | --- | --- | --- |
| qasirel | qa-si-rel | qhasi→qasi + cyprière→rel | wooded shallow water | Uru + Cajun French |
| juwacel | ju-wa-cel | juwa + acatl→cel | dense reed margins | Uru + Nahuatl |
| acawish | a-ca-wish | acatl→aca + wishi→wish | water between reeds | Nahuatl + Tunica |
| moharel | mo-ha-rel | mohtini→moh + cyprière→arel | moss-hung swamp trees | Tunica + Cajun French |
| pagani | pa-ga-ni | pagaille→paga + aní→ni | water crossed by paddle | Cajun French + Biloxi |
| qasitin | qa-si-tin | qhasi→qasi + mohtini→tin | moss above quiet water | Uru + Tunica |
| shiwarel | shi-wa-rel | wishi→shi + juwa→wa + cyprière→rel | reed channels below wooded banks | Tunica + Uru + Cajun French |
| anacel | a-na-cel | aní→ana + acatl→cel | reeds along a channel | Biloxi + Nahuatl |
| siwashi | si-wa-shi | cyprière→si + wishi→washi | woodland pools | Cajun French + Tunica |
| juparel | ju-pa-rel | juwa→ju + pagaille→parel | paddled paths through reeds | Uru + Cajun French |
| atamoh | a-ta-moh | atl→ata + mohtini→moh | moss-shaded water | Nahuatl + Tunica |
| aniju | a-ni-ju | aní→ani + juwa→ju | water at reed beds | Biloxi + Uru |
| qaspaga | qas-pa-ga | qhasi→qas + pagaille→paga | a navigable shallow channel | Uru + Cajun French |
| acaprel | a-ca-prel | acatl→aca + cyprière→prel | reed edge beside swamp woods | Nahuatl + Cajun French |
| mohaju | mo-ha-ju | mohtini→moha + juwa→ju | reeds beneath hanging moss | Tunica + Uru |
| pagatel | pa-ga-tel | pagaille→paga + atl→tel | a familiar paddling route | Cajun French + Nahuatl |
| qasani | qa-sa-ni | qhasi→qasa + aní→ni | connected shallow pools | Uru + Biloxi |
| shicaya | shi-ca-ya | wishi→shi + acatl→ca + pagaille→ya | a passage opened through reeds | Tunica + Nahuatl + Cajun French |
| aniprel | a-ni-prel | aní→ani + cyprière→prel | water in the swamp woods | Biloxi + Cajun French |
| juwatel | ju-wa-tel | juwa + atl→tel | flood-fed reeds | Uru + Nahuatl |
| mohani | mo-ha-ni | mohtini→moha + aní→ni | moss over sheltered water | Tunica + Biloxi |
| pagashi | pa-ga-shi | pagaille→paga + wishi→shi | a crossing kept open | Cajun French + Tunica |
| qacatel | qa-ca-tel | qhasi→qa + acatl→catel | shallow water among canes | Uru + Nahuatl |
| jushani | ju-sha-ni | juwa→ju + wishi→sha + aní→ni | reedy waterways meeting | Uru + Tunica + Biloxi |

The whole image is invented. For example, `acatl→cel` and `cyprière→arel`
involve free sound reshaping; cel and arel are not authentic morphemes with the
glosses assigned here. Two water roots can combine into an image of connected
pools, but “connected” is a fictional elaboration.

### Invented settlement endings

| Ending | Syllables | Fictional habitation sense |
| --- | --- | --- |
| enne | en-ne | raised dwelling cluster |
| ovel | o-vel | covered landing |
| aume | au-me | woven-work quarter |
| ossel | os-sel | settlement on firmer ground |
| eche | e-che | garden terrace |
| ulon | u-lon | channel-side meeting place |
| iren | i-ren | homes linked by walkways |
| oreth | o-reth | sheltered repair yard |

These endings encode no political rank and are not attributed to a real language.
A complete place-name story pairs the stem image with the ending sense:
**Qasirelenne** suggests raised homes amid wooded shallow water. The story does
not establish raised buildings or a specific water depth in the current scene.

### Settlement assignments

#### Capitals

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `Kingdom7Capital` | 147 | 29 | Qasirelenne | qasirel + enne | qa-si-rel-EN-ne |
| `Duchy30Capital` | 151 | 30 | Juwacelovel | juwacel + ovel | ju-wa-cel-O-vel |
| `Duchy31Capital` | 155 | 31 | Acawishaume | acawish + aume | a-ca-wish-AU-me |
| `Duchy32Capital` | 159 | 32 | Moharelossel | moharel + ossel | mo-ha-rel-OS-sel |
| `Duchy33Capital` | 163 | 33 | Paganieche | pagani + eche | pa-ga-ni-E-che |
| `Duchy34Capital` | 166 | 34 | Qasitinulon | qasitin + ulon | qa-si-tin-U-lon |
| `County148Capital` | 148 | 29 | Shiwareliren | shiwarel + iren | shi-wa-rel-I-ren |
| `County149Capital` | 149 | 29 | Anaceloreth | anacel + oreth | a-na-cel-O-reth |
| `County150Capital` | 150 | 29 | Siwashienne | siwashi + enne | si-wa-shi-EN-ne |
| `County152Capital` | 152 | 30 | Juparelovel | juparel + ovel | ju-pa-rel-O-vel |
| `County153Capital` | 153 | 30 | Atamohaume | atamoh + aume | a-ta-moh-AU-me |
| `County154Capital` | 154 | 30 | Anijuossel | aniju + ossel | a-ni-ju-OS-sel |
| `County156Capital` | 156 | 31 | Qaspagaeche | qaspaga + eche | qas-pa-ga-E-che |
| `County157Capital` | 157 | 31 | Acaprelulon | acaprel + ulon | a-ca-prel-U-lon |
| `County158Capital` | 158 | 31 | Mohajuiren | mohaju + iren | mo-ha-ju-I-ren |
| `County160Capital` | 160 | 32 | Pagateloreth | pagatel + oreth | pa-ga-tel-O-reth |
| `County161Capital` | 161 | 32 | Qasanienne | qasani + enne | qa-sa-ni-EN-ne |
| `County162Capital` | 162 | 32 | Shicayaovel | shicaya + ovel | shi-ca-ya-O-vel |
| `County164Capital` | 164 | 33 | Aniprelaume | aniprel + aume | a-ni-prel-AU-me |
| `County165Capital` | 165 | 33 | Juwatelossel | juwatel + ossel | ju-wa-tel-OS-sel |
| `County167Capital` | 167 | 34 | Mohanieche | mohani + eche | mo-ha-ni-E-che |
| `County168Capital` | 168 | 34 | Pagashiulon | pagashi + ulon | pa-ga-shi-U-lon |
| `County169Capital` | 169 | 34 | Qacateliren | qacatel + iren | qa-ca-tel-I-ren |
| `County220Capital` | 220 | 33 | Jushanioreth | jushani + oreth | ju-sha-ni-O-reth |

#### Villages

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County148Village1` | 148 | 29 | Qasirelovel | qasirel + ovel | qa-si-rel-O-vel |
| `County148Village2` | 148 | 29 | Juwacelaume | juwacel + aume | ju-wa-cel-AU-me |
| `County149Village1` | 149 | 29 | Acawishossel | acawish + ossel | a-ca-wish-OS-sel |
| `County149Village2` | 149 | 29 | Mohareleche | moharel + eche | mo-ha-rel-E-che |
| `County150Village1` | 150 | 29 | Paganiulon | pagani + ulon | pa-ga-ni-U-lon |
| `County150Village2` | 150 | 29 | Qasitiniren | qasitin + iren | qa-si-tin-I-ren |
| `County151Village1` | 151 | 30 | Shiwareloreth | shiwarel + oreth | shi-wa-rel-O-reth |
| `County151Village2` | 151 | 30 | Anacelenne | anacel + enne | a-na-cel-EN-ne |
| `County151Village3` | 151 | 30 | Siwashiovel | siwashi + ovel | si-wa-shi-O-vel |
| `County152Village1` | 152 | 30 | Juparelaume | juparel + aume | ju-pa-rel-AU-me |
| `County153Village1` | 153 | 30 | Atamohossel | atamoh + ossel | a-ta-moh-OS-sel |
| `County153Village2` | 153 | 30 | Anijueche | aniju + eche | a-ni-ju-E-che |
| `County153Village3` | 153 | 30 | Qaspagaulon | qaspaga + ulon | qas-pa-ga-U-lon |
| `County153Village4` | 153 | 30 | Acapreliren | acaprel + iren | a-ca-prel-I-ren |
| `County154Village1` | 154 | 30 | Mohajuoreth | mohaju + oreth | mo-ha-ju-O-reth |
| `County154Village2` | 154 | 30 | Pagatelenne | pagatel + enne | pa-ga-tel-EN-ne |
| `County154Village3` | 154 | 30 | Qasaniovel | qasani + ovel | qa-sa-ni-O-vel |
| `County154Village4` | 154 | 30 | Shicayaaume | shicaya + aume | shi-ca-ya-AU-me |
| `County155Village1` | 155 | 31 | Aniprelossel | aniprel + ossel | a-ni-prel-OS-sel |
| `County155Village2` | 155 | 31 | Juwateleche | juwatel + eche | ju-wa-tel-E-che |
| `County155Village3` | 155 | 31 | Mohaniulon | mohani + ulon | mo-ha-ni-U-lon |
| `County155Village4` | 155 | 31 | Pagashiiren | pagashi + iren | pa-ga-shi-I-ren |
| `County156Village1` | 156 | 31 | Qacateloreth | qacatel + oreth | qa-ca-tel-O-reth |
| `County156Village2` | 156 | 31 | Jushanienne | jushani + enne | ju-sha-ni-EN-ne |
| `County156Village3` | 156 | 31 | Qasirelaume | qasirel + aume | qa-si-rel-AU-me |
| `County156Village4` | 156 | 31 | Juwacelossel | juwacel + ossel | ju-wa-cel-OS-sel |
| `County156Village5` | 156 | 31 | Acawisheche | acawish + eche | a-ca-wish-E-che |
| `County156Village6` | 156 | 31 | Moharelulon | moharel + ulon | mo-ha-rel-U-lon |
| `County156Village7` | 156 | 31 | Paganiiren | pagani + iren | pa-ga-ni-I-ren |
| `County156Village8` | 156 | 31 | Qasitinoreth | qasitin + oreth | qa-si-tin-O-reth |
| `County157Village1` | 157 | 31 | Shiwarelenne | shiwarel + enne | shi-wa-rel-EN-ne |
| `County157Village2` | 157 | 31 | Anacelovel | anacel + ovel | a-na-cel-O-vel |
| `County157Village3` | 157 | 31 | Siwashiaume | siwashi + aume | si-wa-shi-AU-me |
| `County157Village4` | 157 | 31 | Juparelossel | juparel + ossel | ju-pa-rel-OS-sel |
| `County157Village5` | 157 | 31 | Atamoheche | atamoh + eche | a-ta-moh-E-che |
| `County157Village6` | 157 | 31 | Anijuulon | aniju + ulon | a-ni-ju-U-lon |
| `County158Village1` | 158 | 31 | Qaspagairen | qaspaga + iren | qas-pa-ga-I-ren |
| `County158Village2` | 158 | 31 | Acapreloreth | acaprel + oreth | a-ca-prel-O-reth |
| `County158Village3` | 158 | 31 | Mohajuenne | mohaju + enne | mo-ha-ju-EN-ne |
| `County159Village1` | 159 | 32 | Pagatelovel | pagatel + ovel | pa-ga-tel-O-vel |
| `County159Village2` | 159 | 32 | Qasaniaume | qasani + aume | qa-sa-ni-AU-me |
| `County159Village3` | 159 | 32 | Shicayaossel | shicaya + ossel | shi-ca-ya-OS-sel |
| `County160Village1` | 160 | 32 | Anipreleche | aniprel + eche | a-ni-prel-E-che |
| `County161Village1` | 161 | 32 | Juwatelulon | juwatel + ulon | ju-wa-tel-U-lon |
| `County162Village1` | 162 | 32 | Mohaniiren | mohani + iren | mo-ha-ni-I-ren |
| `County162Village2` | 162 | 32 | Pagashioreth | pagashi + oreth | pa-ga-shi-O-reth |
| `County163Village1` | 163 | 33 | Qacatelenne | qacatel + enne | qa-ca-tel-EN-ne |
| `County164Village1` | 164 | 33 | Jushaniovel | jushani + ovel | ju-sha-ni-O-vel |
| `County164Village2` | 164 | 33 | Qasirelossel | qasirel + ossel | qa-si-rel-OS-sel |
| `County164Village3` | 164 | 33 | Juwaceleche | juwacel + eche | ju-wa-cel-E-che |
| `County164Village4` | 164 | 33 | Acawishulon | acawish + ulon | a-ca-wish-U-lon |
| `County165Village1` | 165 | 33 | Mohareliren | moharel + iren | mo-ha-rel-I-ren |
| `County165Village2` | 165 | 33 | Paganioreth | pagani + oreth | pa-ga-ni-O-reth |
| `County165Village3` | 165 | 33 | Qasitinenne | qasitin + enne | qa-si-tin-EN-ne |
| `County166Village1` | 166 | 34 | Shiwarelovel | shiwarel + ovel | shi-wa-rel-O-vel |
| `County166Village2` | 166 | 34 | Anacelaume | anacel + aume | a-na-cel-AU-me |
| `County166Village3` | 166 | 34 | Siwashiossel | siwashi + ossel | si-wa-shi-OS-sel |
| `County166Village4` | 166 | 34 | Jupareleche | juparel + eche | ju-pa-rel-E-che |
| `County167Village1` | 167 | 34 | Atamohulon | atamoh + ulon | a-ta-moh-U-lon |
| `County167Village2` | 167 | 34 | Anijuiren | aniju + iren | a-ni-ju-I-ren |
| `County167Village3` | 167 | 34 | Qaspagaoreth | qaspaga + oreth | qas-pa-ga-O-reth |
| `County167Village4` | 167 | 34 | Acaprelenne | acaprel + enne | a-ca-prel-EN-ne |
| `County168Village1` | 168 | 34 | Mohajuovel | mohaju + ovel | mo-ha-ju-O-vel |
| `County168Village2` | 168 | 34 | Pagatelaume | pagatel + aume | pa-ga-tel-AU-me |
| `County168Village3` | 168 | 34 | Qasaniossel | qasani + ossel | qa-sa-ni-OS-sel |
| `County169Village1` | 169 | 34 | Shicayaeche | shicaya + eche | shi-ca-ya-E-che |
| `County169Village2` | 169 | 34 | Aniprelulon | aniprel + ulon | a-ni-prel-U-lon |

#### Hamlets

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County147Hamlet1` | 147 | 29 | Juwateliren | juwatel + iren | ju-wa-tel-I-ren |
| `County147Hamlet2` | 147 | 29 | Mohanioreth | mohani + oreth | mo-ha-ni-O-reth |
| `County147Hamlet3` | 147 | 29 | Pagashienne | pagashi + enne | pa-ga-shi-EN-ne |
| `County147Hamlet4` | 147 | 29 | Qacatelovel | qacatel + ovel | qa-ca-tel-O-vel |
| `County147Hamlet5` | 147 | 29 | Jushaniaume | jushani + aume | ju-sha-ni-AU-me |
| `County147Hamlet6` | 147 | 29 | Qasireleche | qasirel + eche | qa-si-rel-E-che |
| `County147Hamlet7` | 147 | 29 | Juwacelulon | juwacel + ulon | ju-wa-cel-U-lon |
| `County147Hamlet8` | 147 | 29 | Acawishiren | acawish + iren | a-ca-wish-I-ren |
| `County148Hamlet1` | 148 | 29 | Mohareloreth | moharel + oreth | mo-ha-rel-O-reth |
| `County148Hamlet2` | 148 | 29 | Paganienne | pagani + enne | pa-ga-ni-EN-ne |
| `County148Hamlet3` | 148 | 29 | Qasitinovel | qasitin + ovel | qa-si-tin-O-vel |
| `County149Hamlet1` | 149 | 29 | Shiwarelaume | shiwarel + aume | shi-wa-rel-AU-me |
| `County149Hamlet2` | 149 | 29 | Anacelossel | anacel + ossel | a-na-cel-OS-sel |
| `County150Hamlet1` | 150 | 29 | Siwashieche | siwashi + eche | si-wa-shi-E-che |
| `County150Hamlet2` | 150 | 29 | Juparelulon | juparel + ulon | ju-pa-rel-U-lon |
| `County150Hamlet3` | 150 | 29 | Atamohiren | atamoh + iren | a-ta-moh-I-ren |
| `County150Hamlet4` | 150 | 29 | Anijuoreth | aniju + oreth | a-ni-ju-O-reth |
| `County150Hamlet5` | 150 | 29 | Qaspagaenne | qaspaga + enne | qas-pa-ga-EN-ne |
| `County150Hamlet6` | 150 | 29 | Acaprelovel | acaprel + ovel | a-ca-prel-O-vel |
| `County150Hamlet7` | 150 | 29 | Mohajuaume | mohaju + aume | mo-ha-ju-AU-me |
| `County150Hamlet8` | 150 | 29 | Pagatelossel | pagatel + ossel | pa-ga-tel-OS-sel |
| `County150Hamlet9` | 150 | 29 | Qasanieche | qasani + eche | qa-sa-ni-E-che |
| `County150Hamlet10` | 150 | 29 | Shicayaulon | shicaya + ulon | shi-ca-ya-U-lon |
| `County151Hamlet1` | 151 | 30 | Anipreliren | aniprel + iren | a-ni-prel-I-ren |
| `County151Hamlet2` | 151 | 30 | Juwateloreth | juwatel + oreth | ju-wa-tel-O-reth |
| `County151Hamlet3` | 151 | 30 | Mohanienne | mohani + enne | mo-ha-ni-EN-ne |
| `County151Hamlet4` | 151 | 30 | Pagashiovel | pagashi + ovel | pa-ga-shi-O-vel |
| `County151Hamlet5` | 151 | 30 | Qacatelaume | qacatel + aume | qa-ca-tel-AU-me |
| `County152Hamlet1` | 152 | 30 | Jushaniossel | jushani + ossel | ju-sha-ni-OS-sel |
| `County152Hamlet2` | 152 | 30 | Qasirelulon | qasirel + ulon | qa-si-rel-U-lon |
| `County152Hamlet3` | 152 | 30 | Juwaceliren | juwacel + iren | ju-wa-cel-I-ren |
| `County152Hamlet4` | 152 | 30 | Acawishoreth | acawish + oreth | a-ca-wish-O-reth |
| `County152Hamlet5` | 152 | 30 | Moharelenne | moharel + enne | mo-ha-rel-EN-ne |
| `County152Hamlet6` | 152 | 30 | Paganiovel | pagani + ovel | pa-ga-ni-O-vel |
| `County153Hamlet1` | 153 | 30 | Qasitinaume | qasitin + aume | qa-si-tin-AU-me |
| `County153Hamlet2` | 153 | 30 | Shiwarelossel | shiwarel + ossel | shi-wa-rel-OS-sel |
| `County153Hamlet3` | 153 | 30 | Anaceleche | anacel + eche | a-na-cel-E-che |
| `County154Hamlet1` | 154 | 30 | Siwashiulon | siwashi + ulon | si-wa-shi-U-lon |
| `County154Hamlet2` | 154 | 30 | Jupareliren | juparel + iren | ju-pa-rel-I-ren |
| `County154Hamlet3` | 154 | 30 | Atamohoreth | atamoh + oreth | a-ta-moh-O-reth |
| `County155Hamlet1` | 155 | 31 | Anijuenne | aniju + enne | a-ni-ju-EN-ne |
| `County155Hamlet2` | 155 | 31 | Qaspagaovel | qaspaga + ovel | qas-pa-ga-O-vel |
| `County155Hamlet3` | 155 | 31 | Acaprelaume | acaprel + aume | a-ca-prel-AU-me |
| `County155Hamlet4` | 155 | 31 | Mohajuossel | mohaju + ossel | mo-ha-ju-OS-sel |
| `County155Hamlet5` | 155 | 31 | Pagateleche | pagatel + eche | pa-ga-tel-E-che |
| `County156Hamlet1` | 156 | 31 | Qasaniulon | qasani + ulon | qa-sa-ni-U-lon |
| `County156Hamlet2` | 156 | 31 | Shicayairen | shicaya + iren | shi-ca-ya-I-ren |
| `County157Hamlet1` | 157 | 31 | Anipreloreth | aniprel + oreth | a-ni-prel-O-reth |
| `County157Hamlet2` | 157 | 31 | Juwatelenne | juwatel + enne | ju-wa-tel-EN-ne |
| `County157Hamlet3` | 157 | 31 | Mohaniovel | mohani + ovel | mo-ha-ni-O-vel |
| `County158Hamlet1` | 158 | 31 | Pagashiaume | pagashi + aume | pa-ga-shi-AU-me |
| `County158Hamlet2` | 158 | 31 | Qacatelossel | qacatel + ossel | qa-ca-tel-OS-sel |
| `County158Hamlet3` | 158 | 31 | Jushanieche | jushani + eche | ju-sha-ni-E-che |
| `County159Hamlet1` | 159 | 32 | Qasireliren | qasirel + iren | qa-si-rel-I-ren |
| `County159Hamlet2` | 159 | 32 | Juwaceloreth | juwacel + oreth | ju-wa-cel-O-reth |
| `County159Hamlet3` | 159 | 32 | Acawishenne | acawish + enne | a-ca-wish-EN-ne |
| `County160Hamlet1` | 160 | 32 | Moharelovel | moharel + ovel | mo-ha-rel-O-vel |
| `County160Hamlet2` | 160 | 32 | Paganiaume | pagani + aume | pa-ga-ni-AU-me |
| `County160Hamlet3` | 160 | 32 | Qasitinossel | qasitin + ossel | qa-si-tin-OS-sel |
| `County161Hamlet1` | 161 | 32 | Shiwareleche | shiwarel + eche | shi-wa-rel-E-che |
| `County161Hamlet2` | 161 | 32 | Anacelulon | anacel + ulon | a-na-cel-U-lon |
| `County162Hamlet1` | 162 | 32 | Siwashiiren | siwashi + iren | si-wa-shi-I-ren |
| `County163Hamlet1` | 163 | 33 | Jupareloreth | juparel + oreth | ju-pa-rel-O-reth |
| `County163Hamlet2` | 163 | 33 | Atamohenne | atamoh + enne | a-ta-moh-EN-ne |
| `County163Hamlet3` | 163 | 33 | Anijuovel | aniju + ovel | a-ni-ju-O-vel |
| `County163Hamlet4` | 163 | 33 | Qaspagaaume | qaspaga + aume | qas-pa-ga-AU-me |
| `County163Hamlet5` | 163 | 33 | Acaprelossel | acaprel + ossel | a-ca-prel-OS-sel |
| `County163Hamlet6` | 163 | 33 | Mohajueche | mohaju + eche | mo-ha-ju-E-che |
| `County164Hamlet1` | 164 | 33 | Pagatelulon | pagatel + ulon | pa-ga-tel-U-lon |
| `County164Hamlet2` | 164 | 33 | Qasaniiren | qasani + iren | qa-sa-ni-I-ren |
| `County164Hamlet3` | 164 | 33 | Shicayaoreth | shicaya + oreth | shi-ca-ya-O-reth |
| `County164Hamlet4` | 164 | 33 | Aniprelenne | aniprel + enne | a-ni-prel-EN-ne |
| `County164Hamlet5` | 164 | 33 | Juwatelovel | juwatel + ovel | ju-wa-tel-O-vel |
| `County164Hamlet6` | 164 | 33 | Mohaniaume | mohani + aume | mo-ha-ni-AU-me |
| `County164Hamlet7` | 164 | 33 | Pagashiossel | pagashi + ossel | pa-ga-shi-OS-sel |
| `County164Hamlet8` | 164 | 33 | Qacateleche | qacatel + eche | qa-ca-tel-E-che |
| `County164Hamlet9` | 164 | 33 | Jushaniulon | jushani + ulon | ju-sha-ni-U-lon |
| `County165Hamlet1` | 165 | 33 | Qasireloreth | qasirel + oreth | qa-si-rel-O-reth |
| `County165Hamlet2` | 165 | 33 | Juwacelenne | juwacel + enne | ju-wa-cel-EN-ne |
| `County165Hamlet3` | 165 | 33 | Acawishovel | acawish + ovel | a-ca-wish-O-vel |
| `County166Hamlet1` | 166 | 34 | Moharelaume | moharel + aume | mo-ha-rel-AU-me |
| `County166Hamlet2` | 166 | 34 | Paganiossel | pagani + ossel | pa-ga-ni-OS-sel |
| `County166Hamlet3` | 166 | 34 | Qasitineche | qasitin + eche | qa-si-tin-E-che |
| `County166Hamlet4` | 166 | 34 | Shiwarelulon | shiwarel + ulon | shi-wa-rel-U-lon |
| `County166Hamlet5` | 166 | 34 | Anaceliren | anacel + iren | a-na-cel-I-ren |
| `County166Hamlet6` | 166 | 34 | Siwashioreth | siwashi + oreth | si-wa-shi-O-reth |
| `County166Hamlet7` | 166 | 34 | Juparelenne | juparel + enne | ju-pa-rel-EN-ne |
| `County167Hamlet1` | 167 | 34 | Atamohovel | atamoh + ovel | a-ta-moh-O-vel |
| `County167Hamlet2` | 167 | 34 | Anijuaume | aniju + aume | a-ni-ju-AU-me |
| `County167Hamlet3` | 167 | 34 | Qaspagaossel | qaspaga + ossel | qas-pa-ga-OS-sel |
| `County168Hamlet1` | 168 | 34 | Acapreleche | acaprel + eche | a-ca-prel-E-che |
| `County168Hamlet2` | 168 | 34 | Mohajuulon | mohaju + ulon | mo-ha-ju-U-lon |
| `County169Hamlet1` | 169 | 34 | Pagateliren | pagatel + iren | pa-ga-tel-I-ren |
| `County169Hamlet2` | 169 | 34 | Qasanioreth | qasani + oreth | qa-sa-ni-O-reth |
| `County220Hamlet1` | 220 | 33 | Shicayaenne | shicaya + enne | shi-ca-ya-EN-ne |
| `County220Hamlet2` | 220 | 33 | Aniprelovel | aniprel + ovel | a-ni-prel-O-vel |
| `County220Hamlet3` | 220 | 33 | Juwatelaume | juwatel + aume | ju-wa-tel-AU-me |
| `County220Hamlet4` | 220 | 33 | Mohaniossel | mohani + ossel | mo-ha-ni-OS-sel |
| `County220Hamlet5` | 220 | 33 | Pagashieche | pagashi + eche | pa-ga-shi-E-che |
| `County220Hamlet6` | 220 | 33 | Qacatelulon | qacatel + ulon | qa-ca-tel-U-lon |
| `County220Hamlet7` | 220 | 33 | Jushaniiren | jushani + iren | ju-sha-ni-I-ren |

### Person names and construction ledger

Use mononyms and title-first display: **King Anacelnel**, **Duke Siwashivo**.
Forms are ungendered; they imply no family, dynasty, genealogy, or real-world
honorific. A shared stem reflects shared vocabulary, not a surname or a ruler's
descent from a settlement.

Each stem blends the sources recorded above. The personal tails are invented and
carry no authentic independent meaning. Wishes belong to the whole fictional
name; they are not established traits of the current incumbent.

| Name | Pronunciation | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Anacelnel | a-na-CEL-nel | anacel + invented nel | one who guides others safely home |
| Siwashivo | si-wa-SHI-vo | siwashi + invented vo | care for what sustains a household |
| Juparelmin | ju-pa-REL-min | juparel + invented min | patience through changing water |
| Atamohsha | a-ta-MOH-sha | atamoh + invented sha | one who keeps a welcome ready |
| Anijuveth | a-ni-JU-veth | aniju + invented veth | a dependable hand in shared work |
| Qaspagarin | qas-pa-GA-rin | qaspaga + invented rin | one who tends small beginnings |
| Acaprelve | a-ca-PREL-ve | acaprel + invented ve | steadiness when the footing changes |
| Mohajunol | mo-ha-JU-nol | mohaju + invented nol | one who repairs what others need |
| Pagatelsen | pa-ga-TEL-sen | pagatel + invented sen | care for those arriving late |
| Qasanimi | qa-sa-NI-mi | qasani + invented mi | good judgment on unfamiliar routes |
| Shicayaven | shi-ca-YA-ven | shicaya + invented ven | one who remembers useful paths |
| Aniprelune | a-ni-prel-U-ne | aniprel + invented une | skill shared without hesitation |
| Juwatelnim | ju-wa-TEL-nim | juwatel + invented nim | a calm presence in hard weather |
| Mohaniven | mo-ha-NI-ven | mohani + invented ven | one who makes room for new growth |
| Pagashisel | pa-ga-SHI-sel | pagashi + invented sel | provision kept for lean seasons |
| Qacatelri | qa-ca-TEL-ri | qacatel + invented ri | one who joins divided neighbors |
| Jushanimon | ju-sha-NI-mon | jushani + invented mon | attention to quiet needs |
| Qasirelva | qa-si-REL-va | qasirel + invented va | a steady hand at a difficult crossing |
| Juwacellen | ju-wa-CEL-len | juwacel + invented len | one who protects a place to rest |
| Acawishsho | a-ca-WISH-sho | acawish + invented sho | care passed to the next generation |
| Moharelvin | mo-ha-REL-vin | moharel + invented vin | one who follows through on promises |
| Paganimel | pa-ga-NI-mel | pagani + invented mel | patience in careful work |
| Qasitinrel | qa-si-TIN-rel | qasitin + invented rel | one who leaves a clear way for others |
| Shiwarelnu | shi-wa-REL-nu | shiwarel + invented nu | hope carried through a long wet season |

### Court assignments

| Court resource | Rank | Proposed person name | Seat node | Proposed seat name | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom7Capital` | King | Anacelnel | `Kingdom7Capital` | Qasirelenne | 147 | 29 |
| `Court_Duchy30Capital` | Duke | Siwashivo | `Duchy30Capital` | Juwacelovel | 151 | 30 |
| `Court_Duchy31Capital` | Duke | Juparelmin | `Duchy31Capital` | Acawishaume | 155 | 31 |
| `Court_Duchy32Capital` | Duke | Atamohsha | `Duchy32Capital` | Moharelossel | 159 | 32 |
| `Court_Duchy33Capital` | Duke | Anijuveth | `Duchy33Capital` | Paganieche | 163 | 33 |
| `Court_Duchy34Capital` | Duke | Qaspagarin | `Duchy34Capital` | Qasitinulon | 166 | 34 |
| `Court_County148Capital` | Count | Acaprelve | `County148Capital` | Shiwareliren | 148 | 29 |
| `Court_County149Capital` | Count | Mohajunol | `County149Capital` | Anaceloreth | 149 | 29 |
| `Court_County150Capital` | Count | Pagatelsen | `County150Capital` | Siwashienne | 150 | 29 |
| `Court_County152Capital` | Count | Qasanimi | `County152Capital` | Juparelovel | 152 | 30 |
| `Court_County153Capital` | Count | Shicayaven | `County153Capital` | Atamohaume | 153 | 30 |
| `Court_County154Capital` | Count | Aniprelune | `County154Capital` | Anijuossel | 154 | 30 |
| `Court_County156Capital` | Count | Juwatelnim | `County156Capital` | Qaspagaeche | 156 | 31 |
| `Court_County157Capital` | Count | Mohaniven | `County157Capital` | Acaprelulon | 157 | 31 |
| `Court_County158Capital` | Count | Pagashisel | `County158Capital` | Mohajuiren | 158 | 31 |
| `Court_County160Capital` | Count | Qacatelri | `County160Capital` | Pagateloreth | 160 | 32 |
| `Court_County161Capital` | Count | Jushanimon | `County161Capital` | Qasanienne | 161 | 32 |
| `Court_County162Capital` | Count | Qasirelva | `County162Capital` | Shicayaovel | 162 | 32 |
| `Court_County164Capital` | Count | Juwacellen | `County164Capital` | Aniprelaume | 164 | 33 |
| `Court_County165Capital` | Count | Acawishsho | `County165Capital` | Juwatelossel | 165 | 33 |
| `Court_County167Capital` | Count | Moharelvin | `County167Capital` | Mohanieche | 167 | 34 |
| `Court_County168Capital` | Count | Paganimel | `County168Capital` | Pagashiulon | 168 | 34 |
| `Court_County169Capital` | Count | Qasitinrel | `County169Capital` | Qacateliren | 169 | 34 |
| `Court_County220Capital` | Count | Shiwarelnu | `County220Capital` | Jushanioreth | 220 | 33 |

Kingdom7Capital is the shared seat for county 147 and duchy 29. Duchy30Capital,
Duchy31Capital, Duchy32Capital, Duchy33Capital, and Duchy34Capital are the shared
seats for counties 151, 155, 159, 163, and 166 respectively. There are no
additional count courts at those six seats, and no separate duchy-29 court.
Co-location does not establish combined legal titles; do not invent seven
additional incumbents. County220Capital has its own count and is included.

### Screening, revisions, and validation

On 2026-11-07, individually quoted web searches screened all **216 initial
candidates** (192 settlements, 24 people), followed by searches for four
replacement spellings.

| Initial candidate | Final decision | Reason |
| --- | --- | --- |
| Anijulo | **Anijuveth** | Surname-directory occurrence; changed rather than relying on the directory's uncertain provenance. |
| Aniprella | **Aniprelune** | Personal-name occurrence in a published administrative table. |
| Mohanivo | **Mohaniven** | Repeated occurrence in transliterated literary material; revised to reduce an unintended association. |
| Paganima | **Paganimel** | Existing album title, in addition to ordinary-word occurrences. |
| Paganienne | Retain | Derived adjective in running text, including a reference to a surname; not established as a copied settlement or person name. |

No results were returned for the four replacements in the exact searches used.
The screen does not prove worldwide uniqueness; short fragments and ordinary
words naturally recur. Incidental OCR/noisy results are not automatically
evidence of an existing name.

Local validation checks the 192 exact scene nodes and their metadata, all 24
court links and ranks, the personal construction ledger, pronunciation spelling,
and uniqueness within this register and against the five earlier biome registers.
These checks do not establish in-game display or detailed geographical suitability.

### Swamp research sources

Consulted 2026-11-07. These support the stated lexical inspirations, not the
fictional compounds, sound rules, habitation senses, or personal wishes.

- **SW1:** [*Vocabulario Uru (Uchumataqu)*](https://www.illaa.org/pirwa/diccionarios/VocabularioUru-Hannss-output.html),
  compiled vocabulary hosted by the Instituto de Lenguas y Literaturas
  Andinas-Amazónicas, and its
  [introduction](https://www.illaa.org/pirwa/diccionarios/VocabularioUru-Introduccion.pdf).
  Water entry qhasi and totora entry juwa, each attributed there to Muysken (2005).
  Other listed forms and the lake word qota are not borrowed in this pass.
- **SW2:** DOBES, [Uru-Chipaya language documentation](https://dobes.mpi.nl/projects/uru-chipaya/language/),
  context on the related but distinct varieties and their Altiplano setting.
  Aquatic vocabulary is the bridge to the fictional biome; the Altiplano is not
  being described as a Louisiana-style swamp.
- **SW3:** University of Oregon, Online Nahuatl Dictionary,
  [acatl](https://nahuatl.wired-humanities.org/content/acatl), reed/cane entry.
  Personal and calendrical senses are recorded by the source but not adopted.
- **SW4:** University of Oregon, Online Nahuatl Dictionary,
  [atl / ātl](https://nahuatl.wired-humanities.org/content/atl), ordinary water sense.
  War metaphors and calendar terminology are not used.
- **SW5:** Amanda LaFleur, with Benjamin Forkner, LSU Department of French Studies,
  [*A Cajun French-English Glossary*](https://www.lsu.edu/hss/french/undergraduate_program/cajun_french/cajun_french_english_glossary.php),
  cyprière and pagaille entries. Cyprière is used directly for swamp woods;
  the neighboring cyprès entry is not silently re-glossed.
- **SW6:** Tunica-Biloxi Tribe of Louisiana / Louisiana Wildlife Federation,
  [Tunica coloring and language book, 2022](https://www.tunicabiloxi.org/wp-content/uploads/Tunica-LWF-coloring-book-Copyright-2022.pdf),
  pronunciation-key page 63: wishi, water; mohtini, Spanish moss.
  The fictional pronunciation above is independent of the source key.
- **SW7:** Rankin, Carter, Jones, Koontz, Rood, and Hartmann, eds.,
  [Comparative Siouan Dictionary: water/liquid](https://csd.clld.org/parameters/55),
  specifically the Biloxi aní variant attributed to Dorsey and Swanton, p. 173a.
  Reconstructed forms and other languages' cognates are not used.
- **SW8:** Tunica-Biloxi Tribe,
  [public language resources](https://www.tunicabiloxi.org/tribal-info/departments/language-culture-revitalization-program/online-resources/),
  and the tribe/Louisiana Wildlife Federation's
  [Biloxi language book, 2024](https://lawildlifefed.org/wp-content/uploads/LWF-Biloxi-coloring-book-2024-web.pdf),
  introduction, identifying the separate Tunica and Biloxi learning projects.
  The latter is contextual evidence; Biloxi lexical spelling comes from SW7.

## Temperate Mountains naming

### Scope and identity

Requested 2026-11-07: settlement and person names drawing on Indigenous cultures
and languages of the **Andes, especially Incan**, the **Himalayas**, and the
**Rocky Mountains**. This first palette emphasizes **Quechua**, blended with
**Sherpa, Ute, and Blackfoot**. Quechua appears in 19 of the 24 mixed stem
families. The Incan emphasis is expressed through Andean vocabulary and imagined
stonework, cultivated slopes, and connected settlements, not copied royal names.

“Incan” is a cultural and historical reference, not a claim that these modern
teaching materials reconstruct a single imperial language. The chosen forms
come from the specific sources below. Sherpa is not interchangeable with every
Himalayan language; Ute and Blackfoot are distinct Rocky Mountain-region sources.
The selection is deliberately limited and does not claim to represent every
Indigenous mountain people.

The intended impression is inhabited temperate mountain country: river valleys,
stone paths, terraces, cultivated ground, sheltered work courts, carried
provisions, and routes between heights. Peaks are part of the identity, but
permanent ice and snow do not dominate it as they do the tundra. The game’s
counts, dukes, and king remain fictional offices, not adaptations of actual
Indigenous governments or naming customs.

Current `vcom/Scenes/Map.tscn` inventory: **Kingdom 3**, counties **49–72**,
duchies **9–14**. There are **258 settlements**: 1 kingdom capital, 5 duchy
capitals, 18 county capitals, 70 villages, and 164 hamlets. The **24 courts**
comprise 1 king, 5 dukes, and 18 counts. This is a documentation register;
scene labels and court resources are unchanged.

### Source palette

| Requested region | Specific lexical selection | Contribution and limit |
| --- | --- | --- |
| Andes, especially Incan | Quechua `urqu`, mountain/hill; `rumi`, stone; `mayu`, river, in the cited Andean educational sources [TM1, TM2] | Heights, stonework, and river-fed settlement. Ordinary words supply inspiration; no complete Inca ruler, dynasty, sacred mountain, or actual settlement name is used. |
| Himalayas | Sherpa `ri`, mountain/hill; `lam`, path, in *Sherpa Conversation & Basic Words* [TM3] | Routes, slopes, and movement through inhabited mountains. The romanizations are from this teaching source; fictional stress is not Sherpa tone or pronunciation. |
| Rocky Mountains: Ute | `too pwech`, rock; `seer a wots`, basket, in the CSU/Ute educator resource, which identifies its vocabulary source as Wardle's Northern Ute phonetic material [TM4] | Stone and carried provisions. These spaced source spellings are preserved in the ledger. They are not claimed as a current standard orthography for every Ute community. |
| Rocky Mountains: Blackfoot | `miistak`, mountain, as documented in linguistic research [TM5] | Ridge and mountain-shoulder imagery. The shorter fictional tak, tal, stal, and met fragments are creative changes, not authentic Blackfoot suffixes. |

No source's ordinary word carries all the meaning assigned to a fictional stem.
For example, a basket word motivates carrying and provision imagery; it does not
literally mean “upland store.” Cultural stories and ceremonial vocabulary in
the source publications are not borrowed into the register.

### Sound and construction rules

- Use **initial stress**: Urkelamad = UR-ke-lam-ad; Miseruqen = MI-se-ruq-en.
  This shares a stress position with tundra, but uses fuller three-syllable stems,
  a different vowel inventory, and its own endings. Stress alone cannot
  distinguish all nine biome traditions.
- Vowels `a e i o u` are approximately ah, eh, ee, oh, oo. `ay` is one
  syllable like *eye*; elsewhere `y` is the consonant in *yes*. There are no
  silent final vowels.
- `q` is a hard k sound in the fictional spelling. `ch` sounds as in *chair*;
  `pw` joins p and w in one onset. Keep `st`, `rk`, `rm`, and similar
  consonant contacts as shown by the syllable guides.
- Favor `r m l t k p`, occasional `w`, and firm closing consonants. Long
  vowels, aspiration, tone, and glottal distinctions from real languages are not
  imitated with decorative spelling.
- Settlement names take a three-syllable mixed stem plus a one- or two-syllable
  invented habitation ending, for four or five syllables. Personal names use a
  separately recorded one-syllable invented tail, for four syllables.
- Reshape and combine at least two language sources per stem. Sound insertions,
  vowel changes, contractions, and reordered fragments are authored operations,
  not reconstructed historical developments.
- Keep all four traditions represented across both registers, while individual
  names blend two or three. No duchy corresponds to a real culture.
- The first assignment distributes combinations for variety. Terraces, gardens,
  springs, and provision stores are proposed name stories, not verified assets
  or exact terrain at the scene nodes.

### Mixed stem ledger

| Fictional stem | Syllables | Source transformations | Fictional image | Source blend |
| --- | --- | --- | --- | --- |
| urkelam | ur-ke-lam | urqu→urke + lam | paths across the heights | Quechua + Sherpa |
| rumistal | ru-mi-stal | rumi + miistak→stal | stone mountain shoulders | Quechua + Blackfoot |
| mayucher | ma-yu-cher | mayu + too pwech→cher | river-worn stone | Quechua + Ute |
| laturmi | la-tur-mi | lam→la + rumi→turmi | stone-laid paths | Sherpa + Quechua |
| tuperi | tu-pe-ri | too pwech→tupe + ri | rocky high ground | Ute + Sherpa |
| serumay | se-ru-may | seer a wots→seru + mayu→may | provisions carried along a river | Ute + Quechua |
| rikumet | ri-ku-met | ri + urqu→ku + miistak→met | interlocking ridges | Sherpa + Quechua + Blackfoot |
| lamutak | la-mu-tak | lam→lamu + miistak→tak | a route across a mountain shoulder | Sherpa + Blackfoot |
| urwetsa | ur-wet-sa | urqu→ur + too pwech→wetsa | stony upland ground | Quechua + Ute |
| miseruq | mi-se-ruq | miistak→mi + seer a wots→se + urqu→ruq | provisions carried into the heights | Blackfoot + Ute + Quechua |
| rumilam | ru-mi-lam | rumi + lam | a dependable stone path | Quechua + Sherpa |
| mayutal | ma-yu-tal | mayu + miistak→tal | river below a ridge | Quechua + Blackfoot |
| ritupel | ri-tu-pel | ri + too pwech→tupel | sheltering outcrops | Sherpa + Ute |
| serurqa | se-rur-qa | seer a wots→se + urqu→rurqa | supplies stored above the valley | Ute + Quechua |
| takurmi | ta-kur-mi | miistak→tak + rumi→urmi | broken stone on a slope | Blackfoot + Quechua |
| lamuyek | la-mu-yek | lam + mayu→uyek | a path following the river | Sherpa + Quechua |
| pwerumi | pwe-ru-mi | too pwech→pwe + rumi | stones fitted together | Ute + Quechua |
| urmitak | ur-mi-tak | urqu→ur + miistak→mitak | heights overlooking lower slopes | Quechua + Blackfoot |
| riyuma | ri-yu-ma | ri + mayu→yuma | river-fed mountain country | Sherpa + Quechua |
| tulamur | tu-la-mur | too pwech→tu + lam→lamur | a path between rocks | Ute + Sherpa |
| mayuser | ma-yu-ser | mayu + seer a wots→ser | goods carried between riverside homes | Quechua + Ute |
| stakeri | sta-ke-ri | miistak→stake + ri | successive mountain shoulders | Blackfoot + Sherpa |
| urqase | ur-qa-se | urqu→urqa + seer a wots→se | a place to gather upland provisions | Quechua + Ute |
| rumetak | ru-me-tak | rumi→rume + miistak→tak | exposed stone above the valley | Quechua + Blackfoot |

The basket-related forms may evoke carrying, storing, and sharing provisions;
the full images remain invented. Transformations such as `mayu→uyek` and
`miistak→met` are deliberately free. Their derivation is a design record,
not an etymological claim about an actual language.

### Invented settlement endings

| Ending | Syllables | Fictional habitation sense |
| --- | --- | --- |
| ad | ad | terraced habitation |
| ek | ek | sheltered waystation |
| urna | ur-na | cluster of slope-side homes |
| etal | e-tal | shared work court |
| om | om | garden enclosure |
| ard | ard | settlement above a crossing |
| evi | e-vi | workshops beside a path |
| osk | osk | sheltered provision store |
| ira | i-ra | homes around a spring |
| ust | ust | habitation under an outcrop |
| alen | a-len | meeting place between routes |

Endings indicate neither political rank nor authentic real-language morphology.
**Urkelamad** combines paths across the heights with terraced habitation.
Other name stories pair the stem image with the ending sense in the same way.

### Settlement assignments

#### Capitals

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `Kingdom3Capital` | 57 | 11 | Urkelamad | urkelam + ad | UR-ke-lam-ad |
| `Duchy09Capital` | 49 | 9 | Rumistalek | rumistal + ek | RU-mi-stal-ek |
| `Duchy10Capital` | 53 | 10 | Mayucherurna | mayucher + urna | MA-yu-cher-ur-na |
| `Duchy12Capital` | 61 | 12 | Laturmietal | laturmi + etal | LA-tur-mi-e-tal |
| `Duchy13Capital` | 65 | 13 | Tuperiom | tuperi + om | TU-pe-ri-om |
| `Duchy14Capital` | 69 | 14 | Serumayard | serumay + ard | SE-ru-may-ard |
| `County050Capital` | 50 | 9 | Rikumetevi | rikumet + evi | RI-ku-met-e-vi |
| `County051Capital` | 51 | 9 | Lamutakosk | lamutak + osk | LA-mu-tak-osk |
| `County052Capital` | 52 | 9 | Urwetsaira | urwetsa + ira | UR-wet-sa-i-ra |
| `County054Capital` | 54 | 10 | Miseruqust | miseruq + ust | MI-se-ruq-ust |
| `County055Capital` | 55 | 10 | Rumilamalen | rumilam + alen | RU-mi-lam-a-len |
| `County056Capital` | 56 | 10 | Mayutalad | mayutal + ad | MA-yu-tal-ad |
| `County058Capital` | 58 | 11 | Ritupelek | ritupel + ek | RI-tu-pel-ek |
| `County059Capital` | 59 | 11 | Serurqaurna | serurqa + urna | SE-rur-qa-ur-na |
| `County060Capital` | 60 | 11 | Takurmietal | takurmi + etal | TA-kur-mi-e-tal |
| `County062Capital` | 62 | 12 | Lamuyekom | lamuyek + om | LA-mu-yek-om |
| `County063Capital` | 63 | 12 | Pwerumiard | pwerumi + ard | PWE-ru-mi-ard |
| `County064Capital` | 64 | 12 | Urmitakevi | urmitak + evi | UR-mi-tak-e-vi |
| `County066Capital` | 66 | 13 | Riyumaosk | riyuma + osk | RI-yu-ma-osk |
| `County067Capital` | 67 | 13 | Tulamurira | tulamur + ira | TU-la-mur-i-ra |
| `County068Capital` | 68 | 13 | Mayuserust | mayuser + ust | MA-yu-ser-ust |
| `County070Capital` | 70 | 14 | Stakerialen | stakeri + alen | STA-ke-ri-a-len |
| `County071Capital` | 71 | 14 | Urqasead | urqase + ad | UR-qa-se-ad |
| `County072Capital` | 72 | 14 | Rumetakek | rumetak + ek | RU-me-tak-ek |

#### Villages

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County049Village1` | 49 | 9 | Urkelamek | urkelam + ek | UR-ke-lam-ek |
| `County049Village2` | 49 | 9 | Rumistalurna | rumistal + urna | RU-mi-stal-ur-na |
| `County049Village3` | 49 | 9 | Mayucheretal | mayucher + etal | MA-yu-cher-e-tal |
| `County050Village1` | 50 | 9 | Laturmiom | laturmi + om | LA-tur-mi-om |
| `County051Village1` | 51 | 9 | Tuperiard | tuperi + ard | TU-pe-ri-ard |
| `County051Village2` | 51 | 9 | Serumayevi | serumay + evi | SE-ru-may-e-vi |
| `County051Village3` | 51 | 9 | Rikumetosk | rikumet + osk | RI-ku-met-osk |
| `County051Village4` | 51 | 9 | Lamutakira | lamutak + ira | LA-mu-tak-i-ra |
| `County051Village5` | 51 | 9 | Urwetsaust | urwetsa + ust | UR-wet-sa-ust |
| `County052Village1` | 52 | 9 | Miseruqalen | miseruq + alen | MI-se-ruq-a-len |
| `County052Village2` | 52 | 9 | Rumilamad | rumilam + ad | RU-mi-lam-ad |
| `County052Village3` | 52 | 9 | Mayutalek | mayutal + ek | MA-yu-tal-ek |
| `County053Village1` | 53 | 10 | Ritupelurna | ritupel + urna | RI-tu-pel-ur-na |
| `County053Village2` | 53 | 10 | Serurqaetal | serurqa + etal | SE-rur-qa-e-tal |
| `County053Village3` | 53 | 10 | Takurmiom | takurmi + om | TA-kur-mi-om |
| `County055Village1` | 55 | 10 | Lamuyekard | lamuyek + ard | LA-mu-yek-ard |
| `County056Village1` | 56 | 10 | Pwerumievi | pwerumi + evi | PWE-ru-mi-e-vi |
| `County056Village2` | 56 | 10 | Urmitakosk | urmitak + osk | UR-mi-tak-osk |
| `County056Village3` | 56 | 10 | Riyumaira | riyuma + ira | RI-yu-ma-i-ra |
| `County056Village4` | 56 | 10 | Tulamurust | tulamur + ust | TU-la-mur-ust |
| `County057Village1` | 57 | 11 | Mayuseralen | mayuser + alen | MA-yu-ser-a-len |
| `County057Village2` | 57 | 11 | Stakeriad | stakeri + ad | STA-ke-ri-ad |
| `County057Village3` | 57 | 11 | Urqaseek | urqase + ek | UR-qa-se-ek |
| `County058Village1` | 58 | 11 | Rumetakurna | rumetak + urna | RU-me-tak-ur-na |
| `County058Village2` | 58 | 11 | Urkelamurna | urkelam + urna | UR-ke-lam-ur-na |
| `County059Village1` | 59 | 11 | Rumistaletal | rumistal + etal | RU-mi-stal-e-tal |
| `County059Village2` | 59 | 11 | Mayucherom | mayucher + om | MA-yu-cher-om |
| `County059Village3` | 59 | 11 | Laturmiard | laturmi + ard | LA-tur-mi-ard |
| `County060Village1` | 60 | 11 | Tuperievi | tuperi + evi | TU-pe-ri-e-vi |
| `County060Village2` | 60 | 11 | Serumayosk | serumay + osk | SE-ru-may-osk |
| `County060Village3` | 60 | 11 | Rikumetira | rikumet + ira | RI-ku-met-i-ra |
| `County060Village4` | 60 | 11 | Lamutakust | lamutak + ust | LA-mu-tak-ust |
| `County060Village5` | 60 | 11 | Urwetsaalen | urwetsa + alen | UR-wet-sa-a-len |
| `County060Village6` | 60 | 11 | Miseruqad | miseruq + ad | MI-se-ruq-ad |
| `County061Village1` | 61 | 12 | Rumilamek | rumilam + ek | RU-mi-lam-ek |
| `County061Village2` | 61 | 12 | Mayutalurna | mayutal + urna | MA-yu-tal-ur-na |
| `County061Village3` | 61 | 12 | Ritupeletal | ritupel + etal | RI-tu-pel-e-tal |
| `County061Village4` | 61 | 12 | Serurqaom | serurqa + om | SE-rur-qa-om |
| `County061Village5` | 61 | 12 | Takurmiard | takurmi + ard | TA-kur-mi-ard |
| `County061Village6` | 61 | 12 | Lamuyekevi | lamuyek + evi | LA-mu-yek-e-vi |
| `County061Village7` | 61 | 12 | Pwerumiosk | pwerumi + osk | PWE-ru-mi-osk |
| `County061Village8` | 61 | 12 | Urmitakira | urmitak + ira | UR-mi-tak-i-ra |
| `County062Village1` | 62 | 12 | Riyumaust | riyuma + ust | RI-yu-ma-ust |
| `County062Village2` | 62 | 12 | Tulamuralen | tulamur + alen | TU-la-mur-a-len |
| `County062Village3` | 62 | 12 | Mayuserad | mayuser + ad | MA-yu-ser-ad |
| `County063Village1` | 63 | 12 | Stakeriek | stakeri + ek | STA-ke-ri-ek |
| `County063Village2` | 63 | 12 | Urqaseurna | urqase + urna | UR-qa-se-ur-na |
| `County064Village1` | 64 | 12 | Rumetaketal | rumetak + etal | RU-me-tak-e-tal |
| `County064Village2` | 64 | 12 | Urkelametal | urkelam + etal | UR-ke-lam-e-tal |
| `County064Village3` | 64 | 12 | Rumistalom | rumistal + om | RU-mi-stal-om |
| `County064Village4` | 64 | 12 | Mayucherard | mayucher + ard | MA-yu-cher-ard |
| `County065Village1` | 65 | 13 | Laturmievi | laturmi + evi | LA-tur-mi-e-vi |
| `County065Village2` | 65 | 13 | Tuperiosk | tuperi + osk | TU-pe-ri-osk |
| `County065Village3` | 65 | 13 | Serumayira | serumay + ira | SE-ru-may-i-ra |
| `County066Village1` | 66 | 13 | Rikumetust | rikumet + ust | RI-ku-met-ust |
| `County066Village2` | 66 | 13 | Lamutakalen | lamutak + alen | LA-mu-tak-a-len |
| `County066Village3` | 66 | 13 | Urwetsaad | urwetsa + ad | UR-wet-sa-ad |
| `County067Village1` | 67 | 13 | Miseruqek | miseruq + ek | MI-se-ruq-ek |
| `County067Village2` | 67 | 13 | Rumilamurna | rumilam + urna | RU-mi-lam-ur-na |
| `County067Village3` | 67 | 13 | Mayutaletal | mayutal + etal | MA-yu-tal-e-tal |
| `County067Village4` | 67 | 13 | Ritupelom | ritupel + om | RI-tu-pel-om |
| `County068Village1` | 68 | 13 | Serurqaard | serurqa + ard | SE-rur-qa-ard |
| `County069Village1` | 69 | 14 | Takurmievi | takurmi + evi | TA-kur-mi-e-vi |
| `County069Village2` | 69 | 14 | Lamuyekosk | lamuyek + osk | LA-mu-yek-osk |
| `County070Village1` | 70 | 14 | Pwerumiira | pwerumi + ira | PWE-ru-mi-i-ra |
| `County070Village2` | 70 | 14 | Urmitakust | urmitak + ust | UR-mi-tak-ust |
| `County070Village3` | 70 | 14 | Riyumaalen | riyuma + alen | RI-yu-ma-a-len |
| `County071Village1` | 71 | 14 | Tulamurad | tulamur + ad | TU-la-mur-ad |
| `County071Village2` | 71 | 14 | Mayuserek | mayuser + ek | MA-yu-ser-ek |
| `County072Village1` | 72 | 14 | Stakeriurna | stakeri + urna | STA-ke-ri-ur-na |

#### Hamlets

| Scene node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County049Hamlet1` | 49 | 9 | Urqaseetal | urqase + etal | UR-qa-se-e-tal |
| `County049Hamlet2` | 49 | 9 | Rumetakom | rumetak + om | RU-me-tak-om |
| `County049Hamlet3` | 49 | 9 | Urkelamom | urkelam + om | UR-ke-lam-om |
| `County049Hamlet4` | 49 | 9 | Rumistalard | rumistal + ard | RU-mi-stal-ard |
| `County049Hamlet5` | 49 | 9 | Mayucherevi | mayucher + evi | MA-yu-cher-e-vi |
| `County049Hamlet6` | 49 | 9 | Laturmiosk | laturmi + osk | LA-tur-mi-osk |
| `County049Hamlet7` | 49 | 9 | Tuperiira | tuperi + ira | TU-pe-ri-i-ra |
| `County049Hamlet8` | 49 | 9 | Serumayust | serumay + ust | SE-ru-may-ust |
| `County049Hamlet9` | 49 | 9 | Rikumetalen | rikumet + alen | RI-ku-met-a-len |
| `County050Hamlet1` | 50 | 9 | Lamutakad | lamutak + ad | LA-mu-tak-ad |
| `County050Hamlet2` | 50 | 9 | Urwetsaek | urwetsa + ek | UR-wet-sa-ek |
| `County050Hamlet3` | 50 | 9 | Miseruqurna | miseruq + urna | MI-se-ruq-ur-na |
| `County050Hamlet4` | 50 | 9 | Rumilametal | rumilam + etal | RU-mi-lam-e-tal |
| `County050Hamlet5` | 50 | 9 | Mayutalom | mayutal + om | MA-yu-tal-om |
| `County050Hamlet6` | 50 | 9 | Ritupelard | ritupel + ard | RI-tu-pel-ard |
| `County051Hamlet1` | 51 | 9 | Serurqaevi | serurqa + evi | SE-rur-qa-e-vi |
| `County051Hamlet2` | 51 | 9 | Takurmiosk | takurmi + osk | TA-kur-mi-osk |
| `County051Hamlet3` | 51 | 9 | Lamuyekira | lamuyek + ira | LA-mu-yek-i-ra |
| `County052Hamlet1` | 52 | 9 | Pwerumiust | pwerumi + ust | PWE-ru-mi-ust |
| `County052Hamlet2` | 52 | 9 | Urmitakalen | urmitak + alen | UR-mi-tak-a-len |
| `County052Hamlet3` | 52 | 9 | Riyumaad | riyuma + ad | RI-yu-ma-ad |
| `County052Hamlet4` | 52 | 9 | Tulamurek | tulamur + ek | TU-la-mur-ek |
| `County052Hamlet5` | 52 | 9 | Mayuserurna | mayuser + urna | MA-yu-ser-ur-na |
| `County052Hamlet6` | 52 | 9 | Stakerietal | stakeri + etal | STA-ke-ri-e-tal |
| `County052Hamlet7` | 52 | 9 | Urqaseom | urqase + om | UR-qa-se-om |
| `County052Hamlet8` | 52 | 9 | Rumetakard | rumetak + ard | RU-me-tak-ard |
| `County053Hamlet1` | 53 | 10 | Urkelamard | urkelam + ard | UR-ke-lam-ard |
| `County053Hamlet2` | 53 | 10 | Rumistalevi | rumistal + evi | RU-mi-stal-e-vi |
| `County053Hamlet3` | 53 | 10 | Mayucherosk | mayucher + osk | MA-yu-cher-osk |
| `County053Hamlet4` | 53 | 10 | Laturmiira | laturmi + ira | LA-tur-mi-i-ra |
| `County053Hamlet5` | 53 | 10 | Tuperiust | tuperi + ust | TU-pe-ri-ust |
| `County053Hamlet6` | 53 | 10 | Serumayalen | serumay + alen | SE-ru-may-a-len |
| `County053Hamlet7` | 53 | 10 | Rikumetad | rikumet + ad | RI-ku-met-ad |
| `County054Hamlet1` | 54 | 10 | Lamutakek | lamutak + ek | LA-mu-tak-ek |
| `County054Hamlet2` | 54 | 10 | Urwetsaurna | urwetsa + urna | UR-wet-sa-ur-na |
| `County054Hamlet3` | 54 | 10 | Miseruqetal | miseruq + etal | MI-se-ruq-e-tal |
| `County054Hamlet4` | 54 | 10 | Rumilamom | rumilam + om | RU-mi-lam-om |
| `County054Hamlet5` | 54 | 10 | Mayutalard | mayutal + ard | MA-yu-tal-ard |
| `County054Hamlet6` | 54 | 10 | Ritupelevi | ritupel + evi | RI-tu-pel-e-vi |
| `County054Hamlet7` | 54 | 10 | Serurqaosk | serurqa + osk | SE-rur-qa-osk |
| `County054Hamlet8` | 54 | 10 | Takurmiira | takurmi + ira | TA-kur-mi-i-ra |
| `County055Hamlet1` | 55 | 10 | Lamuyekust | lamuyek + ust | LA-mu-yek-ust |
| `County055Hamlet2` | 55 | 10 | Pwerumialen | pwerumi + alen | PWE-ru-mi-a-len |
| `County055Hamlet3` | 55 | 10 | Urmitakad | urmitak + ad | UR-mi-tak-ad |
| `County055Hamlet4` | 55 | 10 | Riyumaek | riyuma + ek | RI-yu-ma-ek |
| `County055Hamlet5` | 55 | 10 | Tulamururna | tulamur + urna | TU-la-mur-ur-na |
| `County056Hamlet1` | 56 | 10 | Mayuseretal | mayuser + etal | MA-yu-ser-e-tal |
| `County056Hamlet2` | 56 | 10 | Stakeriom | stakeri + om | STA-ke-ri-om |
| `County056Hamlet3` | 56 | 10 | Urqaseard | urqase + ard | UR-qa-se-ard |
| `County056Hamlet4` | 56 | 10 | Rumetakevi | rumetak + evi | RU-me-tak-e-vi |
| `County056Hamlet5` | 56 | 10 | Urkelamevi | urkelam + evi | UR-ke-lam-e-vi |
| `County057Hamlet1` | 57 | 11 | Rumistalosk | rumistal + osk | RU-mi-stal-osk |
| `County057Hamlet2` | 57 | 11 | Mayucherira | mayucher + ira | MA-yu-cher-i-ra |
| `County057Hamlet3` | 57 | 11 | Laturmiust | laturmi + ust | LA-tur-mi-ust |
| `County058Hamlet1` | 58 | 11 | Tuperialen | tuperi + alen | TU-pe-ri-a-len |
| `County058Hamlet2` | 58 | 11 | Serumayad | serumay + ad | SE-ru-may-ad |
| `County058Hamlet3` | 58 | 11 | Rikumetek | rikumet + ek | RI-ku-met-ek |
| `County058Hamlet4` | 58 | 11 | Lamutakurna | lamutak + urna | LA-mu-tak-ur-na |
| `County058Hamlet5` | 58 | 11 | Urwetsaetal | urwetsa + etal | UR-wet-sa-e-tal |
| `County058Hamlet6` | 58 | 11 | Miseruqom | miseruq + om | MI-se-ruq-om |
| `County058Hamlet7` | 58 | 11 | Rumilamard | rumilam + ard | RU-mi-lam-ard |
| `County058Hamlet8` | 58 | 11 | Mayutalevi | mayutal + evi | MA-yu-tal-e-vi |
| `County059Hamlet1` | 59 | 11 | Ritupelosk | ritupel + osk | RI-tu-pel-osk |
| `County059Hamlet2` | 59 | 11 | Serurqaira | serurqa + ira | SE-rur-qa-i-ra |
| `County059Hamlet3` | 59 | 11 | Takurmiust | takurmi + ust | TA-kur-mi-ust |
| `County059Hamlet4` | 59 | 11 | Lamuyekalen | lamuyek + alen | LA-mu-yek-a-len |
| `County059Hamlet5` | 59 | 11 | Pwerumiad | pwerumi + ad | PWE-ru-mi-ad |
| `County059Hamlet6` | 59 | 11 | Urmitakek | urmitak + ek | UR-mi-tak-ek |
| `County059Hamlet7` | 59 | 11 | Riyumaurna | riyuma + urna | RI-yu-ma-ur-na |
| `County059Hamlet8` | 59 | 11 | Tulamuretal | tulamur + etal | TU-la-mur-e-tal |
| `County059Hamlet9` | 59 | 11 | Mayuserom | mayuser + om | MA-yu-ser-om |
| `County060Hamlet1` | 60 | 11 | Stakeriard | stakeri + ard | STA-ke-ri-ard |
| `County060Hamlet2` | 60 | 11 | Urqaseevi | urqase + evi | UR-qa-se-e-vi |
| `County060Hamlet3` | 60 | 11 | Rumetakosk | rumetak + osk | RU-me-tak-osk |
| `County060Hamlet4` | 60 | 11 | Urkelamosk | urkelam + osk | UR-ke-lam-osk |
| `County060Hamlet5` | 60 | 11 | Rumistalira | rumistal + ira | RU-mi-stal-i-ra |
| `County060Hamlet6` | 60 | 11 | Mayucherust | mayucher + ust | MA-yu-cher-ust |
| `County060Hamlet7` | 60 | 11 | Laturmialen | laturmi + alen | LA-tur-mi-a-len |
| `County061Hamlet1` | 61 | 12 | Tuperiad | tuperi + ad | TU-pe-ri-ad |
| `County061Hamlet2` | 61 | 12 | Serumayek | serumay + ek | SE-ru-may-ek |
| `County061Hamlet3` | 61 | 12 | Rikumeturna | rikumet + urna | RI-ku-met-ur-na |
| `County061Hamlet4` | 61 | 12 | Lamutaketal | lamutak + etal | LA-mu-tak-e-tal |
| `County062Hamlet1` | 62 | 12 | Urwetsaom | urwetsa + om | UR-wet-sa-om |
| `County062Hamlet2` | 62 | 12 | Miseruqard | miseruq + ard | MI-se-ruq-ard |
| `County062Hamlet3` | 62 | 12 | Rumilamevi | rumilam + evi | RU-mi-lam-e-vi |
| `County062Hamlet4` | 62 | 12 | Mayutalosk | mayutal + osk | MA-yu-tal-osk |
| `County062Hamlet5` | 62 | 12 | Ritupelira | ritupel + ira | RI-tu-pel-i-ra |
| `County062Hamlet6` | 62 | 12 | Serurqaust | serurqa + ust | SE-rur-qa-ust |
| `County062Hamlet7` | 62 | 12 | Takurmialen | takurmi + alen | TA-kur-mi-a-len |
| `County062Hamlet8` | 62 | 12 | Lamuyekad | lamuyek + ad | LA-mu-yek-ad |
| `County062Hamlet9` | 62 | 12 | Pwerumiek | pwerumi + ek | PWE-ru-mi-ek |
| `County062Hamlet10` | 62 | 12 | Urmitakurna | urmitak + urna | UR-mi-tak-ur-na |
| `County062Hamlet11` | 62 | 12 | Riyumaetal | riyuma + etal | RI-yu-ma-e-tal |
| `County062Hamlet12` | 62 | 12 | Tulamurom | tulamur + om | TU-la-mur-om |
| `County062Hamlet13` | 62 | 12 | Mayuserard | mayuser + ard | MA-yu-ser-ard |
| `County062Hamlet14` | 62 | 12 | Stakerievi | stakeri + evi | STA-ke-ri-e-vi |
| `County062Hamlet15` | 62 | 12 | Urqaseosk | urqase + osk | UR-qa-se-osk |
| `County063Hamlet1` | 63 | 12 | Rumetakira | rumetak + ira | RU-me-tak-i-ra |
| `County063Hamlet2` | 63 | 12 | Urkelamira | urkelam + ira | UR-ke-lam-i-ra |
| `County063Hamlet3` | 63 | 12 | Rumistalust | rumistal + ust | RU-mi-stal-ust |
| `County063Hamlet4` | 63 | 12 | Mayucheralen | mayucher + alen | MA-yu-cher-a-len |
| `County063Hamlet5` | 63 | 12 | Laturmiad | laturmi + ad | LA-tur-mi-ad |
| `County063Hamlet6` | 63 | 12 | Tuperiek | tuperi + ek | TU-pe-ri-ek |
| `County063Hamlet7` | 63 | 12 | Serumayurna | serumay + urna | SE-ru-may-ur-na |
| `County064Hamlet1` | 64 | 12 | Rikumetetal | rikumet + etal | RI-ku-met-e-tal |
| `County064Hamlet2` | 64 | 12 | Lamutakom | lamutak + om | LA-mu-tak-om |
| `County064Hamlet3` | 64 | 12 | Urwetsaard | urwetsa + ard | UR-wet-sa-ard |
| `County064Hamlet4` | 64 | 12 | Miseruqevi | miseruq + evi | MI-se-ruq-e-vi |
| `County065Hamlet1` | 65 | 13 | Rumilamosk | rumilam + osk | RU-mi-lam-osk |
| `County065Hamlet2` | 65 | 13 | Mayutalira | mayutal + ira | MA-yu-tal-i-ra |
| `County065Hamlet3` | 65 | 13 | Ritupelust | ritupel + ust | RI-tu-pel-ust |
| `County065Hamlet4` | 65 | 13 | Serurqaalen | serurqa + alen | SE-rur-qa-a-len |
| `County065Hamlet5` | 65 | 13 | Takurmiad | takurmi + ad | TA-kur-mi-ad |
| `County065Hamlet6` | 65 | 13 | Lamuyekek | lamuyek + ek | LA-mu-yek-ek |
| `County065Hamlet7` | 65 | 13 | Pwerumiurna | pwerumi + urna | PWE-ru-mi-ur-na |
| `County065Hamlet8` | 65 | 13 | Urmitaketal | urmitak + etal | UR-mi-tak-e-tal |
| `County065Hamlet9` | 65 | 13 | Riyumaom | riyuma + om | RI-yu-ma-om |
| `County065Hamlet10` | 65 | 13 | Tulamurard | tulamur + ard | TU-la-mur-ard |
| `County065Hamlet11` | 65 | 13 | Mayuserevi | mayuser + evi | MA-yu-ser-e-vi |
| `County065Hamlet12` | 65 | 13 | Stakeriosk | stakeri + osk | STA-ke-ri-osk |
| `County065Hamlet13` | 65 | 13 | Urqaseira | urqase + ira | UR-qa-se-i-ra |
| `County065Hamlet14` | 65 | 13 | Rumetakust | rumetak + ust | RU-me-tak-ust |
| `County066Hamlet1` | 66 | 13 | Urkelamust | urkelam + ust | UR-ke-lam-ust |
| `County066Hamlet2` | 66 | 13 | Rumistalalen | rumistal + alen | RU-mi-stal-a-len |
| `County066Hamlet3` | 66 | 13 | Mayucherad | mayucher + ad | MA-yu-cher-ad |
| `County066Hamlet4` | 66 | 13 | Laturmiek | laturmi + ek | LA-tur-mi-ek |
| `County066Hamlet5` | 66 | 13 | Tuperiurna | tuperi + urna | TU-pe-ri-ur-na |
| `County066Hamlet6` | 66 | 13 | Serumayetal | serumay + etal | SE-ru-may-e-tal |
| `County067Hamlet1` | 67 | 13 | Rikumetom | rikumet + om | RI-ku-met-om |
| `County067Hamlet2` | 67 | 13 | Lamutakard | lamutak + ard | LA-mu-tak-ard |
| `County067Hamlet3` | 67 | 13 | Urwetsaevi | urwetsa + evi | UR-wet-sa-e-vi |
| `County067Hamlet4` | 67 | 13 | Miseruqosk | miseruq + osk | MI-se-ruq-osk |
| `County067Hamlet5` | 67 | 13 | Rumilamira | rumilam + ira | RU-mi-lam-i-ra |
| `County068Hamlet1` | 68 | 13 | Mayutalust | mayutal + ust | MA-yu-tal-ust |
| `County068Hamlet2` | 68 | 13 | Ritupelalen | ritupel + alen | RI-tu-pel-a-len |
| `County068Hamlet3` | 68 | 13 | Serurqaad | serurqa + ad | SE-rur-qa-ad |
| `County068Hamlet4` | 68 | 13 | Takurmiek | takurmi + ek | TA-kur-mi-ek |
| `County068Hamlet5` | 68 | 13 | Lamuyekurna | lamuyek + urna | LA-mu-yek-ur-na |
| `County069Hamlet1` | 69 | 14 | Pwerumietal | pwerumi + etal | PWE-ru-mi-e-tal |
| `County069Hamlet2` | 69 | 14 | Urmitakom | urmitak + om | UR-mi-tak-om |
| `County069Hamlet3` | 69 | 14 | Riyumaard | riyuma + ard | RI-yu-ma-ard |
| `County069Hamlet4` | 69 | 14 | Tulamurevi | tulamur + evi | TU-la-mur-e-vi |
| `County069Hamlet5` | 69 | 14 | Mayuserosk | mayuser + osk | MA-yu-ser-osk |
| `County069Hamlet6` | 69 | 14 | Stakeriira | stakeri + ira | STA-ke-ri-i-ra |
| `County069Hamlet7` | 69 | 14 | Urqaseust | urqase + ust | UR-qa-se-ust |
| `County069Hamlet8` | 69 | 14 | Rumetakalen | rumetak + alen | RU-me-tak-a-len |
| `County070Hamlet1` | 70 | 14 | Urkelamalen | urkelam + alen | UR-ke-lam-a-len |
| `County070Hamlet2` | 70 | 14 | Rumistalad | rumistal + ad | RU-mi-stal-ad |
| `County070Hamlet3` | 70 | 14 | Mayucherek | mayucher + ek | MA-yu-cher-ek |
| `County070Hamlet4` | 70 | 14 | Laturmiurna | laturmi + urna | LA-tur-mi-ur-na |
| `County070Hamlet5` | 70 | 14 | Tuperietal | tuperi + etal | TU-pe-ri-e-tal |
| `County070Hamlet6` | 70 | 14 | Serumayom | serumay + om | SE-ru-may-om |
| `County071Hamlet1` | 71 | 14 | Rikumetard | rikumet + ard | RI-ku-met-ard |
| `County071Hamlet2` | 71 | 14 | Lamutakevi | lamutak + evi | LA-mu-tak-e-vi |
| `County071Hamlet3` | 71 | 14 | Urwetsaosk | urwetsa + osk | UR-wet-sa-osk |
| `County071Hamlet4` | 71 | 14 | Miseruqira | miseruq + ira | MI-se-ruq-i-ra |
| `County071Hamlet5` | 71 | 14 | Rumilamust | rumilam + ust | RU-mi-lam-ust |
| `County071Hamlet6` | 71 | 14 | Mayutalalen | mayutal + alen | MA-yu-tal-a-len |
| `County071Hamlet7` | 71 | 14 | Ritupelad | ritupel + ad | RI-tu-pel-ad |
| `County072Hamlet1` | 72 | 14 | Serurqaek | serurqa + ek | SE-rur-qa-ek |
| `County072Hamlet2` | 72 | 14 | Takurmiurna | takurmi + urna | TA-kur-mi-ur-na |
| `County072Hamlet3` | 72 | 14 | Lamuyeketal | lamuyek + etal | LA-mu-yek-e-tal |
| `County072Hamlet4` | 72 | 14 | Pwerumiom | pwerumi + om | PWE-ru-mi-om |
| `County072Hamlet5` | 72 | 14 | Urmitakard | urmitak + ard | UR-mi-tak-ard |

### Person names and construction ledger

Use mononyms and title-first display: **King Miseruqen**, **Duke Rumilamav**.
Forms are ungendered and imply no family name, dynasty, genealogy, or borrowed
honorific. Shared stems reflect shared fictional vocabulary, not descent from
a capital or ownership of a place.

The mixed stems' real-language inspirations are traced above. Each personal
tail is invented and carries no independent authentic meaning. Naming wishes
belong to the complete authored name and do not establish an incumbent's traits.

| Name | Pronunciation | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Miseruqen | MI-se-ruq-en | miseruq + invented en | steadiness that helps others find footing |
| Rumilamav | RU-mi-lam-av | rumilam + invented av | one who keeps a path open |
| Mayutalil | MA-yu-tal-il | mayutal + invented il | careful work that lasts |
| Ritupelun | RI-tu-pel-un | ritupel + invented un | one who shares provisions |
| Serurqaar | SE-rur-qa-ar | serurqa + invented ar | patience on a difficult ascent |
| Takurmiim | TA-kur-mi-im | takurmi + invented im | a welcome at the end of a journey |
| Lamuyekel | LA-mu-yek-el | lamuyek + invented el | one who brings neighbors together |
| Pwerumian | PWE-ru-mi-an | pwerumi + invented an | resolve guided by good judgment |
| Urmitakor | UR-mi-tak-or | urmitak + invented or | care for what supports a home |
| Riyumain | RI-yu-ma-in | riyuma + invented in | one who remembers the return route |
| Tulamurva | TU-la-mur-va | tulamur + invented va | skill placed at others' service |
| Mayuserul | MA-yu-ser-ul | mayuser + invented ul | room for the next generation |
| Stakeriem | STA-ke-ri-em | stakeri + invented em | one who helps carry a burden |
| Urqasei | UR-qa-se-i | urqase + invented i | a dependable hand at a crossing |
| Rumetakon | RU-me-tak-on | rumetak + invented on | provision prepared for hard weather |
| Urkelamev | UR-ke-lam-ev | urkelam + invented ev | one who repairs before things fail |
| Rumistalal | RU-mi-stal-al | rumistal + invented al | patience with slow growth |
| Mayucherir | MA-yu-cher-ir | mayucher + invented ir | one who shelters travelers |
| Laturmiu | LA-tur-mi-u | laturmi + invented u | thoughtfulness before a difficult choice |
| Tuperien | TU-pe-ri-en | tuperi + invented en | one who tends a shared place |
| Serumayav | SE-ru-may-av | serumay + invented av | courage without recklessness |
| Rikumetin | RI-ku-met-in | rikumet + invented in | one who honors a promise |
| Lamutakel | LA-mu-tak-el | lamutak + invented el | careful use of what the land provides |
| Urwetsaor | UR-wet-sa-or | urwetsa + invented or | one who leaves the way clearer |

### Court assignments

| Court resource | Rank | Proposed person name | Seat node | Proposed seat name | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom3Capital` | King | Miseruqen | `Kingdom3Capital` | Urkelamad | 57 | 11 |
| `Court_Duchy09Capital` | Duke | Rumilamav | `Duchy09Capital` | Rumistalek | 49 | 9 |
| `Court_Duchy10Capital` | Duke | Mayutalil | `Duchy10Capital` | Mayucherurna | 53 | 10 |
| `Court_Duchy12Capital` | Duke | Ritupelun | `Duchy12Capital` | Laturmietal | 61 | 12 |
| `Court_Duchy13Capital` | Duke | Serurqaar | `Duchy13Capital` | Tuperiom | 65 | 13 |
| `Court_Duchy14Capital` | Duke | Takurmiim | `Duchy14Capital` | Serumayard | 69 | 14 |
| `Court_County050Capital` | Count | Lamuyekel | `County050Capital` | Rikumetevi | 50 | 9 |
| `Court_County051Capital` | Count | Pwerumian | `County051Capital` | Lamutakosk | 51 | 9 |
| `Court_County052Capital` | Count | Urmitakor | `County052Capital` | Urwetsaira | 52 | 9 |
| `Court_County054Capital` | Count | Riyumain | `County054Capital` | Miseruqust | 54 | 10 |
| `Court_County055Capital` | Count | Tulamurva | `County055Capital` | Rumilamalen | 55 | 10 |
| `Court_County056Capital` | Count | Mayuserul | `County056Capital` | Mayutalad | 56 | 10 |
| `Court_County058Capital` | Count | Stakeriem | `County058Capital` | Ritupelek | 58 | 11 |
| `Court_County059Capital` | Count | Urqasei | `County059Capital` | Serurqaurna | 59 | 11 |
| `Court_County060Capital` | Count | Rumetakon | `County060Capital` | Takurmietal | 60 | 11 |
| `Court_County062Capital` | Count | Urkelamev | `County062Capital` | Lamuyekom | 62 | 12 |
| `Court_County063Capital` | Count | Rumistalal | `County063Capital` | Pwerumiard | 63 | 12 |
| `Court_County064Capital` | Count | Mayucherir | `County064Capital` | Urmitakevi | 64 | 12 |
| `Court_County066Capital` | Count | Laturmiu | `County066Capital` | Riyumaosk | 66 | 13 |
| `Court_County067Capital` | Count | Tuperien | `County067Capital` | Tulamurira | 67 | 13 |
| `Court_County068Capital` | Count | Serumayav | `County068Capital` | Mayuserust | 68 | 13 |
| `Court_County070Capital` | Count | Rikumetin | `County070Capital` | Stakerialen | 70 | 14 |
| `Court_County071Capital` | Count | Lamutakel | `County071Capital` | Urqasead | 71 | 14 |
| `Court_County072Capital` | Count | Urwetsaor | `County072Capital` | Rumetakek | 72 | 14 |

Kingdom3Capital is the shared seat for county 57 and duchy 11. Duchy09Capital,
Duchy10Capital, Duchy12Capital, Duchy13Capital, and Duchy14Capital are the shared
seats for counties 49, 53, 61, 65, and 69 respectively. No additional count courts
exist at those six seats, and there is no separate duchy-11 court.
Co-location does not prove combined legal titles; do not invent seven additional
incumbents.

### Screening, revisions, and validation

On 2026-11-07, individually quoted web searches screened all **282 initial
candidates** (258 settlements and 24 people), followed by searches for every
revised full name.

| Initial candidate or family | Final decision | Reason |
| --- | --- | --- |
| lamayur family, including Lamayurust | Rebuild as **lamuyek**, from lam + reshaped mayu | Lamayurust appeared as an inflected reference to a Himalayan place. Replaced the entire family to reduce resemblance to Lamayuru rather than retaining neighboring variants. |
| Rumilama | **Rumilamav** | Existing place-name occurrence in a list; changed the invented personal tail. |
| Tuperiom and Tuperien | Retain | Apparent OCR artifacts in scanned running text, not established as copied names. |
| Serumayom | Retain | Joined product-description text (“Serum” plus a brand), not established as a settlement or personal name. |
| Stakeriem | Retain | An ordinary inflected equipment term in Latvian running text, not established as a copied name. |

The replacement searches returned no results. Search screening is limited and
does not prove worldwide uniqueness. Real words and short syllables will recur;
a prominent association discovered later may justify another revision.

Local validation checks all 258 scene nodes and metadata, all 24 court resource
links and ranks, the personal ledger, construction and pronunciation spellings,
and uniqueness within this register and against the six earlier biome registers.
It does not establish runtime display behavior or detailed geographical fit.

### Temperate mountain research sources

Consulted 2026-11-07. These support source words and their documented contexts,
not the fictional names, stress rules, endings, or complete name stories.

- **TM1:** [Quechua dictionary hosted by Chile's Ministry of Education](https://bibliotecadigital.mineduc.cl/bitstream/handle/20.500.12365/14482/dicc_quechua.pdf?isAllowed=y&sequence=1),
  entries rumi, mayu, and urqu. These are documented educational forms, not
  claimed reconstructions of imperial Inca speech.
- **TM2:** Peru's Ministry of Education,
  [*Yachachinapaq simikuna – Urin Qichwa: vocabulario pedagógico quechua sureño*](https://repositorio.minedu.gob.pe/bitstream/handle/20.500.12799/7490/Yachachinapaq%20simikuna%20-%20Urin%20Qichwa%20vocabulario%20pedag%C3%B3gico%20quechua%20sure%C3%B1o.pdf?isAllowed=y&sequence=1),
  terrain vocabulary, including urqu and mayu. Proper geographical names in
  its examples are not adopted.
- **TM3:** Lhakpa Doma Sherpa, Chhiri Tendi Sherpa, and Karl-Heinz Krämer,
  [*Sherpa Conversation & Basic Words*](https://languages.nepalresearch.org/sh-eng.pdf),
  ri, mountain/hill, and lam, path. This Sherpa source supplies the romanized
  forms; Tibetan or Nepali cognates are not silently substituted.
- **TM4:** Barbara J. Shaw and Tina King-Washington,
  [*Utes and STEM*, CSU Extension, November 2021](https://tra.extension.colostate.edu/wp-content/uploads/sites/9/2022/01/66.UteSTEM_condensed.pdf),
  p. 65 vocabulary and p. 1 provenance: Northern Ute phonetic material from
  Hazel Wardle (1969). Rock and basket forms are used; the publication's
  sacred-mountain narrative, names, and numerical tables are not used.
- **TM5:** [“The Indefinite Possessor Prefix in Blackfoot”](https://ojs.library.carleton.ca/index.php/ALGQP/article/download/812/702/1994),
  p. 137, miistak- / istak- mountain stem; corroborated by the miistak mountain
  entry in [“Animating the narrow syntax”](https://www.degruyterbrill.com/de/document/doi/10.1515/tlr-2015-0011/html).
  Neither the authentic morphology nor the source's grammatical categories are
  imported into the fictional naming rules.

## Deciduous Forest naming

### Brief, scope, and identity

Added 2026-11-07. The user requests Celtic, Slavic, Korean, and Iroquoian
inspiration, with a more clearly European impression than the earlier kingdoms.
This direction also applies to Grassland, whose completed initial scheme now
appears in the Grassland section below.

The intended landscape is inhabited seasonal woodland: oak and hazel, coppice,
orchards, leaf-covered paths, timber halls, mills, and small cultivated clearings.
The European impression comes from the fictional sound design: strong initial
stress, compact roots, audible consonant endings, and clusters such as `cr`,
`rn`, `ld`, and `nt`. Korean and Mohawk material remains structurally present
in every name. These names do not imitate the personal-name systems of the
source peoples.

The current scene identifies **Kingdom 8** as Deciduous Forest. This register
covers **695 settlements**: 335 hamlets, 335 villages, 20 county capitals,
4 duchy capitals, and 1 kingdom capital. Its **25 existing courts** contain
20 counts, 4 dukes, and 1 king. Counties are 170–194; duchies are 35–39.
Names are proposals recorded here only; scene/resource display names are unchanged.

### Source palette and transformations

Celtic, Slavic, and Iroquoian are language-family categories. This pass selects
**Irish**, **Polish**, and **Mohawk (Kanien’kéha)** respectively, alongside
**Korean**. None is treated as interchangeable with the rest of its family.

| Requested source | Attested vocabulary used | Fictional transformation |
| --- | --- | --- |
| Celtic: Irish | `dair`, oak; `coll`, hazel; `crann`, tree [DF1] | `dar-`, `col-`, `cran-`; trim spelling and use the game's consonants, without importing Irish inflection or pronunciation |
| Slavic: Polish | `las`, forest; `gaj`, grove; `dąb`, oak [DF2–DF4] | `las-`, `gel-`, `dov-`; retain one forest form, reshape the grove vowel and glide, replace nasal vowel/b with plain o/v in the oak form |
| Korean | `나무` (`namu`), tree; `숲` (`sup`), forest; `잎` (`ip`), leaf [DF5–DF7] | `-nam`, `-suv`, `-iv`; clip the final vowel or change p to v for the fictional sound system |
| Iroquoian: Mohawk | `Karón:ta`, tree/log/trunk; `Ónerahte`, leaf; `Kahiónha`, river/stream [DF8] | `-ront`, `-ner`, `-ion`; select internal sound material and shorten it, without pretending these fragments are authentic standalone morphemes |

The changes above are authorial choices, not historical sound laws or
transliterations. Source words supply imagery; the mixed roots below carry
invented associations. In particular, old oak, worked timber, fallen leaves,
deep shade, and new leaves are fictional elaborations of the ordinary glosses.
Every root pairs one Irish/Polish contribution with one Korean/Mohawk contribution.
Across the full set all four requested traditions contribute equally to the
36-family design (18 Irish, 18 Polish; 18 Korean, 18 Mohawk). Final assignment
counts differ slightly because 695 does not divide evenly by 36.

### Construction and pronunciation

1. Choose a mixed root from the ledger, then add one settlement ending or one
   personal tail. Keep the spelling of the listed root when joining.
2. Stress the first syllable, shown in capitals. Every hyphen marks a syllable;
   it is omitted in the actual name. `a` is ah, `e` eh, `i` ee, `o` oh,
   and `u` oo. C and g are always hard, s is unvoiced, r is audible,
   and no written final consonant is silent.
3. The `ion` element has two syllables, i-on. Most other root halves have one.
   Pronunciation guides describe the fictional names, not their source words.
4. The r after `dar-` and `cran-` is dropped before `-ront`, giving
   `daront` and `cranont`. This is a listed fictional joining adjustment.
5. Favor three- or four-syllable settlements, with occasional longer forms.
   Short endings are used at every rank; an ending does not identify a capital.
6. Shared roots indicate a common language, not kinship or political allegiance.
   Distribute them across counties instead of assigning a real-world culture
   to each district. The node assignment is stable in the tables below.
7. Use ordinary lexical material. Do not import clan names, ceremonial names,
   historic rulers, complete real place names, or a recognizable fictional
   dynasty. No authentic cultural naming ceremony is being asserted.

### Mixed-root ledger

All associations in the final column are fictional. Source glosses and the
precise clipping/substitution decisions are in the palette above.

| Root | Pronunciation | Source pairing | Fictional association |
| --- | --- | --- | --- |
| darnam | DAR-nam | Irish `dair` + Korean `namu` | oak / standing trees |
| darsuv | DAR-suv | Irish `dair` + Korean `sup` | oak / deep shade |
| dariv | DAR-iv | Irish `dair` + Korean `ip` | oak / new leaves |
| daront | DAR-ont | Irish `dair` + Mohawk `Karón:ta` | oak / worked timber |
| darner | DAR-ner | Irish `dair` + Mohawk `Ónerahte` | oak / fallen leaves |
| darion | DAR-i-on | Irish `dair` + Mohawk `Kahiónha` | oak / woodland streams |
| colnam | COL-nam | Irish `coll` + Korean `namu` | hazel / standing trees |
| colsuv | COL-suv | Irish `coll` + Korean `sup` | hazel / deep shade |
| coliv | COL-iv | Irish `coll` + Korean `ip` | hazel / new leaves |
| colront | COL-ront | Irish `coll` + Mohawk `Karón:ta` | hazel / worked timber |
| colner | COL-ner | Irish `coll` + Mohawk `Ónerahte` | hazel / fallen leaves |
| colion | COL-i-on | Irish `coll` + Mohawk `Kahiónha` | hazel / woodland streams |
| crannam | CRAN-nam | Irish `crann` + Korean `namu` | timber / standing trees |
| cransuv | CRAN-suv | Irish `crann` + Korean `sup` | timber / deep shade |
| craniv | CRAN-iv | Irish `crann` + Korean `ip` | timber / new leaves |
| cranont | CRAN-ont | Irish `crann` + Mohawk `Karón:ta` | timber / worked timber |
| cranner | CRAN-ner | Irish `crann` + Mohawk `Ónerahte` | timber / fallen leaves |
| cranion | CRAN-i-on | Irish `crann` + Mohawk `Kahiónha` | timber / woodland streams |
| lasnam | LAS-nam | Polish `las` + Korean `namu` | woodland / standing trees |
| lassuv | LAS-suv | Polish `las` + Korean `sup` | woodland / deep shade |
| lasiv | LAS-iv | Polish `las` + Korean `ip` | woodland / new leaves |
| lasront | LAS-ront | Polish `las` + Mohawk `Karón:ta` | woodland / worked timber |
| lasner | LAS-ner | Polish `las` + Mohawk `Ónerahte` | woodland / fallen leaves |
| lasion | LAS-i-on | Polish `las` + Mohawk `Kahiónha` | woodland / woodland streams |
| gelnam | GEL-nam | Polish `gaj` + Korean `namu` | grove / standing trees |
| gelsuv | GEL-suv | Polish `gaj` + Korean `sup` | grove / deep shade |
| geliv | GEL-iv | Polish `gaj` + Korean `ip` | grove / new leaves |
| gelront | GEL-ront | Polish `gaj` + Mohawk `Karón:ta` | grove / worked timber |
| gelner | GEL-ner | Polish `gaj` + Mohawk `Ónerahte` | grove / fallen leaves |
| gelion | GEL-i-on | Polish `gaj` + Mohawk `Kahiónha` | grove / woodland streams |
| dovnam | DOV-nam | Polish `dąb` + Korean `namu` | old oak / standing trees |
| dovsuv | DOV-suv | Polish `dąb` + Korean `sup` | old oak / deep shade |
| doviv | DOV-iv | Polish `dąb` + Korean `ip` | old oak / new leaves |
| dovront | DOV-ront | Polish `dąb` + Mohawk `Karón:ta` | old oak / worked timber |
| dovner | DOV-ner | Polish `dąb` + Mohawk `Ónerahte` | old oak / fallen leaves |
| dovion | DOV-i-on | Polish `dąb` + Mohawk `Kahiónha` | old oak / woodland streams |

### Settlement endings

These are invented habitation terms in the game language. Their assigned
meanings are not translations of similar-looking European suffixes. A name's
imagery is a proposed remembered origin, not confirmation that its scene has
an orchard, bridge, mill, or other particular feature.

| Ending | Pronunciation | Fictional sense |
| --- | --- | --- |
| avel | a-vel | crossing settlement |
| eld | eld | common clearing |
| orin | o-rin | enclosed orchards |
| ast | ast | raised hall |
| evren | ev-ren | streamside lanes |
| olt | olt | timber yard |
| arden | ar-den | terraced gardens |
| esk | esk | wayside enclosure |
| ovan | o-van | gathering green |
| ent | ent | sheltered crofts |
| avren | av-ren | bridge quarter |
| ord | ord | bank-side settlement |
| elvar | el-var | coppice holdings |
| ost | ost | watch clearing |
| erlan | er-lan | mill settlement |
| und | und | hollow settlement |
| alven | al-ven | shared pasture |
| ern | ern | old hearths |
| evard | e-vard | road junction |
| ald | ald | fenced woodland |
| erent | e-rent | sheltered crofts; extended form of ent |
| orren | or-ren | bank-side hearths; alternative to ord/ern |
| erral | er-ral | fenced woodland; extended alternative to ald |
| erost | e-rost | watch clearing; extended form of ost |

The four alternatives resolve specific candidate overlaps recorded below.
They are not mandatory replacements for the shorter endings elsewhere.

### Settlement assignment register

Exact existing node identifiers are retained. County/duchy numbers refer to
scene metadata. Meaning is recoverable from the root and ending ledgers.

#### Capitals

| Existing node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `Kingdom8Capital` | 180 | 37 | Darontavel | daront + avel | DAR-ont-a-vel |
| `Duchy35Capital` | 170 | 35 | Cranivesk | craniv + esk | CRAN-iv-esk |
| `Duchy36Capital` | 175 | 36 | Gelsuverlan | gelsuv + erlan | GEL-suv-er-lan |
| `Duchy38Capital` | 185 | 38 | Darnameld | darnam + eld | DAR-nam-eld |
| `Duchy39Capital` | 190 | 39 | Colionovan | colion + ovan | COL-i-on-o-van |
| `County171Capital` | 171 | 35 | Lasnerund | lasner + und | LAS-ner-und |
| `County172Capital` | 172 | 35 | Dovrontorin | dovront + orin | DOV-ront-o-rin |
| `County173Capital` | 173 | 35 | Coliverent | coliv + erent | COL-iv-e-rent |
| `County174Capital` | 174 | 35 | Lassuvalven | lassuv + alven | LAS-suv-al-ven |
| `County176Capital` | 176 | 36 | Dovnamast | dovnam + ast | DOV-nam-ast |
| `County177Capital` | 177 | 36 | Darionavren | darion + avren | DAR-i-on-av-ren |
| `County178Capital` | 178 | 36 | Crannerern | cranner + ern | CRAN-ner-ern |
| `County179Capital` | 179 | 36 | Gelrontevren | gelront + evren | GEL-ront-ev-ren |
| `County181Capital` | 181 | 37 | Darivord | dariv + ord | DAR-iv-ord |
| `County182Capital` | 182 | 37 | Cransuvevard | cransuv + evard | CRAN-suv-e-vard |
| `County183Capital` | 183 | 37 | Gelnamolt | gelnam + olt | GEL-nam-olt |
| `County184Capital` | 184 | 37 | Dovionelvar | dovion + elvar | DOV-i-on-el-var |
| `County186Capital` | 186 | 38 | Colnerald | colner + ald | COL-ner-ald |
| `County187Capital` | 187 | 38 | Lasrontarden | lasront + arden | LAS-ront-ar-den |
| `County188Capital` | 188 | 38 | Dovivost | doviv + ost | DOV-iv-ost |
| `County189Capital` | 189 | 38 | Colsuvavel | colsuv + avel | COL-suv-a-vel |
| `County191Capital` | 191 | 39 | Lasnamesk | lasnam + esk | LAS-nam-esk |
| `County192Capital` | 192 | 39 | Gelionerlan | gelion + erlan | GEL-i-on-er-lan |
| `County193Capital` | 193 | 39 | Darnereld | darner + eld | DAR-ner-eld |
| `County194Capital` | 194 | 39 | Cranontovan | cranont + ovan | CRAN-ont-o-van |

#### Villages

| Existing node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County170Village1` | 170 | 35 | Gelivund | geliv + und | GEL-iv-und |
| `County170Village2` | 170 | 35 | Darsuvorin | darsuv + orin | DAR-suv-o-rin |
| `County170Village3` | 170 | 35 | Crannament | crannam + ent | CRAN-nam-ent |
| `County170Village4` | 170 | 35 | Lasionalven | lasion + alven | LAS-i-on-al-ven |
| `County170Village5` | 170 | 35 | Dovnerast | dovner + ast | DOV-ner-ast |
| `County170Village6` | 170 | 35 | Colrontavren | colront + avren | COL-ront-av-ren |
| `County170Village7` | 170 | 35 | Lasivorren | lasiv + orren | LAS-iv-or-ren |
| `County170Village8` | 170 | 35 | Dovsuvevren | dovsuv + evren | DOV-suv-ev-ren |
| `County170Village9` | 170 | 35 | Colnamord | colnam + ord | COL-nam-ord |
| `County170Village10` | 170 | 35 | Cranionevard | cranion + evard | CRAN-i-on-e-vard |
| `County170Village11` | 170 | 35 | Gelnerolt | gelner + olt | GEL-ner-olt |
| `County170Village12` | 170 | 35 | Daronteld | daront + eld | DAR-ont-eld |
| `County170Village13` | 170 | 35 | Cranivovan | craniv + ovan | CRAN-iv-o-van |
| `County170Village14` | 170 | 35 | Gelsuvund | gelsuv + und | GEL-suv-und |
| `County170Village15` | 170 | 35 | Darnamorin | darnam + orin | DAR-nam-o-rin |
| `County171Village1` | 171 | 35 | Colionent | colion + ent | COL-i-on-ent |
| `County171Village2` | 171 | 35 | Lasneralven | lasner + alven | LAS-ner-al-ven |
| `County171Village3` | 171 | 35 | Dovrontast | dovront + ast | DOV-ront-ast |
| `County171Village4` | 171 | 35 | Colivavren | coliv + avren | COL-iv-av-ren |
| `County171Village5` | 171 | 35 | Lassuvern | lassuv + ern | LAS-suv-ern |
| `County171Village6` | 171 | 35 | Dovnamevren | dovnam + evren | DOV-nam-ev-ren |
| `County171Village7` | 171 | 35 | Darionord | darion + ord | DAR-i-on-ord |
| `County171Village8` | 171 | 35 | Crannerevard | cranner + evard | CRAN-ner-e-vard |
| `County171Village9` | 171 | 35 | Gelrontolt | gelront + olt | GEL-ront-olt |
| `County171Village10` | 171 | 35 | Darivelvar | dariv + elvar | DAR-iv-el-var |
| `County172Village1` | 172 | 35 | Cransuvald | cransuv + ald | CRAN-suv-ald |
| `County172Village2` | 172 | 35 | Gelnamarden | gelnam + arden | GEL-nam-ar-den |
| `County172Village3` | 172 | 35 | Dovionost | dovion + ost | DOV-i-on-ost |
| `County172Village4` | 172 | 35 | Colneravel | colner + avel | COL-ner-a-vel |
| `County172Village5` | 172 | 35 | Lasrontesk | lasront + esk | LAS-ront-esk |
| `County172Village6` | 172 | 35 | Doviverlan | doviv + erlan | DOV-iv-er-lan |
| `County172Village7` | 172 | 35 | Colsuveld | colsuv + eld | COL-suv-eld |
| `County172Village8` | 172 | 35 | Lasnamovan | lasnam + ovan | LAS-nam-o-van |
| `County172Village9` | 172 | 35 | Gelionund | gelion + und | GEL-i-on-und |
| `County172Village10` | 172 | 35 | Darnerorin | darner + orin | DAR-ner-o-rin |
| `County172Village11` | 172 | 35 | Cranontent | cranont + ent | CRAN-ont-ent |
| `County172Village12` | 172 | 35 | Gelivalven | geliv + alven | GEL-iv-al-ven |
| `County172Village13` | 172 | 35 | Darsuvast | darsuv + ast | DAR-suv-ast |
| `County173Village1` | 173 | 35 | Crannamavren | crannam + avren | CRAN-nam-av-ren |
| `County173Village2` | 173 | 35 | Lasionern | lasion + ern | LAS-i-on-ern |
| `County173Village3` | 173 | 35 | Dovnerevren | dovner + evren | DOV-ner-ev-ren |
| `County173Village4` | 173 | 35 | Colrontord | colront + ord | COL-ront-ord |
| `County173Village5` | 173 | 35 | Lasivevard | lasiv + evard | LAS-iv-e-vard |
| `County173Village6` | 173 | 35 | Dovsuvolt | dovsuv + olt | DOV-suv-olt |
| `County173Village7` | 173 | 35 | Colnamelvar | colnam + elvar | COL-nam-el-var |
| `County173Village8` | 173 | 35 | Cranionald | cranion + ald | CRAN-i-on-ald |
| `County173Village9` | 173 | 35 | Gelnerarden | gelner + arden | GEL-ner-ar-den |
| `County173Village10` | 173 | 35 | Darontorin | daront + orin | DAR-ont-o-rin |
| `County174Village1` | 174 | 35 | Cranivent | craniv + ent | CRAN-iv-ent |
| `County174Village2` | 174 | 35 | Gelsuvalven | gelsuv + alven | GEL-suv-al-ven |
| `County174Village3` | 174 | 35 | Darnamast | darnam + ast | DAR-nam-ast |
| `County174Village4` | 174 | 35 | Colionavren | colion + avren | COL-i-on-av-ren |
| `County174Village5` | 174 | 35 | Lasnerern | lasner + ern | LAS-ner-ern |
| `County174Village6` | 174 | 35 | Dovrontevren | dovront + evren | DOV-ront-ev-ren |
| `County174Village7` | 174 | 35 | Colivorren | coliv + orren | COL-iv-or-ren |
| `County174Village8` | 174 | 35 | Lassuvevard | lassuv + evard | LAS-suv-e-vard |
| `County174Village9` | 174 | 35 | Dovnamolt | dovnam + olt | DOV-nam-olt |
| `County174Village10` | 174 | 35 | Darionelvar | darion + elvar | DAR-i-on-el-var |
| `County174Village11` | 174 | 35 | Crannerald | cranner + ald | CRAN-ner-ald |
| `County174Village12` | 174 | 35 | Gelrontarden | gelront + arden | GEL-ront-ar-den |
| `County175Village1` | 175 | 36 | Dariverost | dariv + erost | DAR-iv-e-rost |
| `County175Village2` | 175 | 36 | Cransuvavel | cransuv + avel | CRAN-suv-a-vel |
| `County175Village3` | 175 | 36 | Gelnamesk | gelnam + esk | GEL-nam-esk |
| `County175Village4` | 175 | 36 | Dovionerlan | dovion + erlan | DOV-i-on-er-lan |
| `County175Village5` | 175 | 36 | Colnereld | colner + eld | COL-ner-eld |
| `County175Village6` | 175 | 36 | Lasrontovan | lasront + ovan | LAS-ront-o-van |
| `County175Village7` | 175 | 36 | Dovivund | doviv + und | DOV-iv-und |
| `County175Village8` | 175 | 36 | Colsuvorin | colsuv + orin | COL-suv-o-rin |
| `County175Village9` | 175 | 36 | Lasnament | lasnam + ent | LAS-nam-ent |
| `County175Village10` | 175 | 36 | Gelionalven | gelion + alven | GEL-i-on-al-ven |
| `County175Village11` | 175 | 36 | Darnerast | darner + ast | DAR-ner-ast |
| `County175Village12` | 175 | 36 | Cranontavren | cranont + avren | CRAN-ont-av-ren |
| `County175Village13` | 175 | 36 | Gelivern | geliv + ern | GEL-iv-ern |
| `County175Village14` | 175 | 36 | Darsuvevren | darsuv + evren | DAR-suv-ev-ren |
| `County175Village15` | 175 | 36 | Crannamord | crannam + ord | CRAN-nam-ord |
| `County175Village16` | 175 | 36 | Lasionevard | lasion + evard | LAS-i-on-e-vard |
| `County176Village1` | 176 | 36 | Dovnerolt | dovner + olt | DOV-ner-olt |
| `County176Village2` | 176 | 36 | Colrontelvar | colront + elvar | COL-ront-el-var |
| `County176Village3` | 176 | 36 | Lasiverral | lasiv + erral | LAS-iv-er-ral |
| `County176Village4` | 176 | 36 | Dovsuvarden | dovsuv + arden | DOV-suv-ar-den |
| `County176Village5` | 176 | 36 | Colnamost | colnam + ost | COL-nam-ost |
| `County176Village6` | 176 | 36 | Cranionavel | cranion + avel | CRAN-i-on-a-vel |
| `County176Village7` | 176 | 36 | Gelneresk | gelner + esk | GEL-ner-esk |
| `County176Village8` | 176 | 36 | Darontast | daront + ast | DAR-ont-ast |
| `County176Village9` | 176 | 36 | Cranivavren | craniv + avren | CRAN-iv-av-ren |
| `County176Village10` | 176 | 36 | Gelsuvern | gelsuv + ern | GEL-suv-ern |
| `County176Village11` | 176 | 36 | Darnamevren | darnam + evren | DAR-nam-ev-ren |
| `County176Village12` | 176 | 36 | Colionord | colion + ord | COL-i-on-ord |
| `County176Village13` | 176 | 36 | Lasnerevard | lasner + evard | LAS-ner-e-vard |
| `County177Village1` | 177 | 36 | Dovrontolt | dovront + olt | DOV-ront-olt |
| `County177Village2` | 177 | 36 | Colivelvar | coliv + elvar | COL-iv-el-var |
| `County177Village3` | 177 | 36 | Lassuvald | lassuv + ald | LAS-suv-ald |
| `County177Village4` | 177 | 36 | Dovnamarden | dovnam + arden | DOV-nam-ar-den |
| `County177Village5` | 177 | 36 | Darionost | darion + ost | DAR-i-on-ost |
| `County177Village6` | 177 | 36 | Cranneravel | cranner + avel | CRAN-ner-a-vel |
| `County177Village7` | 177 | 36 | Gelrontesk | gelront + esk | GEL-ront-esk |
| `County177Village8` | 177 | 36 | Dariverlan | dariv + erlan | DAR-iv-er-lan |
| `County177Village9` | 177 | 36 | Cransuveld | cransuv + eld | CRAN-suv-eld |
| `County177Village10` | 177 | 36 | Gelnamovan | gelnam + ovan | GEL-nam-o-van |
| `County177Village11` | 177 | 36 | Dovionund | dovion + und | DOV-i-on-und |
| `County178Village1` | 178 | 36 | Colnerorin | colner + orin | COL-ner-o-rin |
| `County178Village2` | 178 | 36 | Lasrontent | lasront + ent | LAS-ront-ent |
| `County178Village3` | 178 | 36 | Dovivalven | doviv + alven | DOV-iv-al-ven |
| `County178Village4` | 178 | 36 | Colsuvast | colsuv + ast | COL-suv-ast |
| `County178Village5` | 178 | 36 | Lasnamavren | lasnam + avren | LAS-nam-av-ren |
| `County178Village6` | 178 | 36 | Gelionern | gelion + ern | GEL-i-on-ern |
| `County178Village7` | 178 | 36 | Darnerevren | darner + evren | DAR-ner-ev-ren |
| `County178Village8` | 178 | 36 | Cranontord | cranont + ord | CRAN-ont-ord |
| `County178Village9` | 178 | 36 | Gelivevard | geliv + evard | GEL-iv-e-vard |
| `County178Village10` | 178 | 36 | Darsuvolt | darsuv + olt | DAR-suv-olt |
| `County178Village11` | 178 | 36 | Crannamelvar | crannam + elvar | CRAN-nam-el-var |
| `County178Village12` | 178 | 36 | Lasionald | lasion + ald | LAS-i-on-ald |
| `County178Village13` | 178 | 36 | Dovnerarden | dovner + arden | DOV-ner-ar-den |
| `County179Village1` | 179 | 36 | Colrontost | colront + ost | COL-ront-ost |
| `County179Village2` | 179 | 36 | Lasivavel | lasiv + avel | LAS-iv-a-vel |
| `County179Village3` | 179 | 36 | Dovsuvesk | dovsuv + esk | DOV-suv-esk |
| `County179Village4` | 179 | 36 | Colnamerlan | colnam + erlan | COL-nam-er-lan |
| `County179Village5` | 179 | 36 | Cranioneld | cranion + eld | CRAN-i-on-eld |
| `County179Village6` | 179 | 36 | Gelnerovan | gelner + ovan | GEL-ner-o-van |
| `County179Village7` | 179 | 36 | Darontevren | daront + evren | DAR-ont-ev-ren |
| `County179Village8` | 179 | 36 | Cranivord | craniv + ord | CRAN-iv-ord |
| `County179Village9` | 179 | 36 | Gelsuvevard | gelsuv + evard | GEL-suv-e-vard |
| `County179Village10` | 179 | 36 | Darnamolt | darnam + olt | DAR-nam-olt |
| `County179Village11` | 179 | 36 | Colionelvar | colion + elvar | COL-i-on-el-var |
| `County179Village12` | 179 | 36 | Lasnerald | lasner + ald | LAS-ner-ald |
| `County179Village13` | 179 | 36 | Dovrontarden | dovront + arden | DOV-ront-ar-den |
| `County179Village14` | 179 | 36 | Colivost | coliv + ost | COL-iv-ost |
| `County180Village1` | 180 | 37 | Lassuvavel | lassuv + avel | LAS-suv-a-vel |
| `County180Village2` | 180 | 37 | Dovnamesk | dovnam + esk | DOV-nam-esk |
| `County180Village3` | 180 | 37 | Darionerlan | darion + erlan | DAR-i-on-er-lan |
| `County180Village4` | 180 | 37 | Crannereld | cranner + eld | CRAN-ner-eld |
| `County180Village5` | 180 | 37 | Gelrontovan | gelront + ovan | GEL-ront-o-van |
| `County180Village6` | 180 | 37 | Darivund | dariv + und | DAR-iv-und |
| `County180Village7` | 180 | 37 | Cransuvorin | cransuv + orin | CRAN-suv-o-rin |
| `County180Village8` | 180 | 37 | Gelnament | gelnam + ent | GEL-nam-ent |
| `County180Village9` | 180 | 37 | Dovionalven | dovion + alven | DOV-i-on-al-ven |
| `County180Village10` | 180 | 37 | Colnerast | colner + ast | COL-ner-ast |
| `County180Village11` | 180 | 37 | Lasrontavren | lasront + avren | LAS-ront-av-ren |
| `County180Village12` | 180 | 37 | Dovivern | doviv + ern | DOV-iv-ern |
| `County180Village13` | 180 | 37 | Colsuvevren | colsuv + evren | COL-suv-ev-ren |
| `County180Village14` | 180 | 37 | Lasnamord | lasnam + ord | LAS-nam-ord |
| `County181Village1` | 181 | 37 | Gelionevard | gelion + evard | GEL-i-on-e-vard |
| `County181Village2` | 181 | 37 | Darnerolt | darner + olt | DAR-ner-olt |
| `County181Village3` | 181 | 37 | Cranontelvar | cranont + elvar | CRAN-ont-el-var |
| `County181Village4` | 181 | 37 | Geliverral | geliv + erral | GEL-iv-er-ral |
| `County181Village5` | 181 | 37 | Darsuvarden | darsuv + arden | DAR-suv-ar-den |
| `County181Village6` | 181 | 37 | Crannamost | crannam + ost | CRAN-nam-ost |
| `County181Village7` | 181 | 37 | Lasionavel | lasion + avel | LAS-i-on-a-vel |
| `County181Village8` | 181 | 37 | Dovneresk | dovner + esk | DOV-ner-esk |
| `County181Village9` | 181 | 37 | Colronterlan | colront + erlan | COL-ront-er-lan |
| `County182Village1` | 182 | 37 | Lasiveld | lasiv + eld | LAS-iv-eld |
| `County182Village2` | 182 | 37 | Dovsuvovan | dovsuv + ovan | DOV-suv-o-van |
| `County182Village3` | 182 | 37 | Colnamund | colnam + und | COL-nam-und |
| `County182Village4` | 182 | 37 | Cranionorin | cranion + orin | CRAN-i-on-o-rin |
| `County182Village5` | 182 | 37 | Gelnerent | gelner + ent | GEL-ner-ent |
| `County182Village6` | 182 | 37 | Darontolt | daront + olt | DAR-ont-olt |
| `County182Village7` | 182 | 37 | Cranivelvar | craniv + elvar | CRAN-iv-el-var |
| `County182Village8` | 182 | 37 | Gelsuvald | gelsuv + ald | GEL-suv-ald |
| `County182Village9` | 182 | 37 | Darnamarden | darnam + arden | DAR-nam-ar-den |
| `County182Village10` | 182 | 37 | Colionost | colion + ost | COL-i-on-ost |
| `County182Village11` | 182 | 37 | Lasneravel | lasner + avel | LAS-ner-a-vel |
| `County183Village1` | 183 | 37 | Dovrontesk | dovront + esk | DOV-ront-esk |
| `County183Village2` | 183 | 37 | Coliverlan | coliv + erlan | COL-iv-er-lan |
| `County183Village3` | 183 | 37 | Lassuveld | lassuv + eld | LAS-suv-eld |
| `County183Village4` | 183 | 37 | Dovnamovan | dovnam + ovan | DOV-nam-o-van |
| `County183Village5` | 183 | 37 | Darionund | darion + und | DAR-i-on-und |
| `County183Village6` | 183 | 37 | Crannerorin | cranner + orin | CRAN-ner-o-rin |
| `County183Village7` | 183 | 37 | Gelrontent | gelront + ent | GEL-ront-ent |
| `County183Village8` | 183 | 37 | Darivalven | dariv + alven | DAR-iv-al-ven |
| `County183Village9` | 183 | 37 | Cransuvast | cransuv + ast | CRAN-suv-ast |
| `County183Village10` | 183 | 37 | Gelnamavren | gelnam + avren | GEL-nam-av-ren |
| `County183Village11` | 183 | 37 | Dovionern | dovion + ern | DOV-i-on-ern |
| `County184Village1` | 184 | 37 | Colnerevren | colner + evren | COL-ner-ev-ren |
| `County184Village2` | 184 | 37 | Lasrontord | lasront + ord | LAS-ront-ord |
| `County184Village3` | 184 | 37 | Dovivevard | doviv + evard | DOV-iv-e-vard |
| `County184Village4` | 184 | 37 | Colsuvolt | colsuv + olt | COL-suv-olt |
| `County184Village5` | 184 | 37 | Lasnamelvar | lasnam + elvar | LAS-nam-el-var |
| `County184Village6` | 184 | 37 | Gelionald | gelion + ald | GEL-i-on-ald |
| `County184Village7` | 184 | 37 | Darnerarden | darner + arden | DAR-ner-ar-den |
| `County184Village8` | 184 | 37 | Cranontost | cranont + ost | CRAN-ont-ost |
| `County184Village9` | 184 | 37 | Gelivavel | geliv + avel | GEL-iv-a-vel |
| `County184Village10` | 184 | 37 | Darsuvesk | darsuv + esk | DAR-suv-esk |
| `County184Village11` | 184 | 37 | Crannamerlan | crannam + erlan | CRAN-nam-er-lan |
| `County184Village12` | 184 | 37 | Lasioneld | lasion + eld | LAS-i-on-eld |
| `County184Village13` | 184 | 37 | Dovnerovan | dovner + ovan | DOV-ner-o-van |
| `County184Village14` | 184 | 37 | Colrontund | colront + und | COL-ront-und |
| `County184Village15` | 184 | 37 | Lasivorin | lasiv + orin | LAS-iv-o-rin |
| `County184Village16` | 184 | 37 | Dovsuvent | dovsuv + ent | DOV-suv-ent |
| `County184Village17` | 184 | 37 | Colnamalven | colnam + alven | COL-nam-al-ven |
| `County185Village1` | 185 | 38 | Cranionast | cranion + ast | CRAN-i-on-ast |
| `County185Village2` | 185 | 38 | Gelneravren | gelner + avren | GEL-ner-av-ren |
| `County185Village3` | 185 | 38 | Darontarden | daront + arden | DAR-ont-ar-den |
| `County185Village4` | 185 | 38 | Cranivost | craniv + ost | CRAN-iv-ost |
| `County185Village5` | 185 | 38 | Gelsuvavel | gelsuv + avel | GEL-suv-a-vel |
| `County185Village6` | 185 | 38 | Darnamesk | darnam + esk | DAR-nam-esk |
| `County185Village7` | 185 | 38 | Colionerlan | colion + erlan | COL-i-on-er-lan |
| `County185Village8` | 185 | 38 | Lasnereld | lasner + eld | LAS-ner-eld |
| `County185Village9` | 185 | 38 | Dovrontovan | dovront + ovan | DOV-ront-o-van |
| `County185Village10` | 185 | 38 | Colivund | coliv + und | COL-iv-und |
| `County185Village11` | 185 | 38 | Lassuvorin | lassuv + orin | LAS-suv-o-rin |
| `County185Village12` | 185 | 38 | Dovnament | dovnam + ent | DOV-nam-ent |
| `County185Village13` | 185 | 38 | Darionalven | darion + alven | DAR-i-on-al-ven |
| `County185Village14` | 185 | 38 | Crannerast | cranner + ast | CRAN-ner-ast |
| `County185Village15` | 185 | 38 | Gelrontavren | gelront + avren | GEL-ront-av-ren |
| `County185Village16` | 185 | 38 | Darivern | dariv + ern | DAR-iv-ern |
| `County185Village17` | 185 | 38 | Cransuvevren | cransuv + evren | CRAN-suv-ev-ren |
| `County185Village18` | 185 | 38 | Gelnamord | gelnam + ord | GEL-nam-ord |
| `County185Village19` | 185 | 38 | Dovionevard | dovion + evard | DOV-i-on-e-vard |
| `County185Village20` | 185 | 38 | Colnerolt | colner + olt | COL-ner-olt |
| `County185Village21` | 185 | 38 | Lasrontelvar | lasront + elvar | LAS-ront-el-var |
| `County186Village1` | 186 | 38 | Dovivald | doviv + ald | DOV-iv-ald |
| `County186Village2` | 186 | 38 | Colsuvarden | colsuv + arden | COL-suv-ar-den |
| `County186Village3` | 186 | 38 | Lasnamost | lasnam + ost | LAS-nam-ost |
| `County186Village4` | 186 | 38 | Gelionavel | gelion + avel | GEL-i-on-a-vel |
| `County186Village5` | 186 | 38 | Darneresk | darner + esk | DAR-ner-esk |
| `County186Village6` | 186 | 38 | Cranonterlan | cranont + erlan | CRAN-ont-er-lan |
| `County186Village7` | 186 | 38 | Geliveld | geliv + eld | GEL-iv-eld |
| `County186Village8` | 186 | 38 | Darsuvovan | darsuv + ovan | DAR-suv-o-van |
| `County186Village9` | 186 | 38 | Crannamund | crannam + und | CRAN-nam-und |
| `County186Village10` | 186 | 38 | Lasionorin | lasion + orin | LAS-i-on-o-rin |
| `County186Village11` | 186 | 38 | Dovnerent | dovner + ent | DOV-ner-ent |
| `County186Village12` | 186 | 38 | Colrontalven | colront + alven | COL-ront-al-ven |
| `County186Village13` | 186 | 38 | Lasivast | lasiv + ast | LAS-iv-ast |
| `County186Village14` | 186 | 38 | Dovsuvavren | dovsuv + avren | DOV-suv-av-ren |
| `County186Village15` | 186 | 38 | Colnamern | colnam + ern | COL-nam-ern |
| `County187Village1` | 187 | 38 | Cranionevren | cranion + evren | CRAN-i-on-ev-ren |
| `County187Village2` | 187 | 38 | Gelnerord | gelner + ord | GEL-ner-ord |
| `County187Village3` | 187 | 38 | Darontesk | daront + esk | DAR-ont-esk |
| `County187Village4` | 187 | 38 | Craniverlan | craniv + erlan | CRAN-iv-er-lan |
| `County187Village5` | 187 | 38 | Gelsuveld | gelsuv + eld | GEL-suv-eld |
| `County187Village6` | 187 | 38 | Darnamovan | darnam + ovan | DAR-nam-o-van |
| `County187Village7` | 187 | 38 | Colionund | colion + und | COL-i-on-und |
| `County187Village8` | 187 | 38 | Lasnerorin | lasner + orin | LAS-ner-o-rin |
| `County187Village9` | 187 | 38 | Dovrontent | dovront + ent | DOV-ront-ent |
| `County187Village10` | 187 | 38 | Colivalven | coliv + alven | COL-iv-al-ven |
| `County188Village1` | 188 | 38 | Lassuvast | lassuv + ast | LAS-suv-ast |
| `County188Village2` | 188 | 38 | Dovnamavren | dovnam + avren | DOV-nam-av-ren |
| `County188Village3` | 188 | 38 | Darionern | darion + ern | DAR-i-on-ern |
| `County188Village4` | 188 | 38 | Crannerevren | cranner + evren | CRAN-ner-ev-ren |
| `County188Village5` | 188 | 38 | Gelrontord | gelront + ord | GEL-ront-ord |
| `County188Village6` | 188 | 38 | Darivevard | dariv + evard | DAR-iv-e-vard |
| `County188Village7` | 188 | 38 | Cransuvolt | cransuv + olt | CRAN-suv-olt |
| `County188Village8` | 188 | 38 | Gelnamelvar | gelnam + elvar | GEL-nam-el-var |
| `County188Village9` | 188 | 38 | Dovionald | dovion + ald | DOV-i-on-ald |
| `County188Village10` | 188 | 38 | Colnerarden | colner + arden | COL-ner-ar-den |
| `County188Village11` | 188 | 38 | Lasrontost | lasront + ost | LAS-ront-ost |
| `County188Village12` | 188 | 38 | Dovivavel | doviv + avel | DOV-iv-a-vel |
| `County188Village13` | 188 | 38 | Colsuvesk | colsuv + esk | COL-suv-esk |
| `County189Village1` | 189 | 38 | Lasnamerlan | lasnam + erlan | LAS-nam-er-lan |
| `County189Village2` | 189 | 38 | Gelioneld | gelion + eld | GEL-i-on-eld |
| `County189Village3` | 189 | 38 | Darnerovan | darner + ovan | DAR-ner-o-van |
| `County189Village4` | 189 | 38 | Cranontund | cranont + und | CRAN-ont-und |
| `County189Village5` | 189 | 38 | Gelivorin | geliv + orin | GEL-iv-o-rin |
| `County189Village6` | 189 | 38 | Darsuvent | darsuv + ent | DAR-suv-ent |
| `County189Village7` | 189 | 38 | Crannamalven | crannam + alven | CRAN-nam-al-ven |
| `County189Village8` | 189 | 38 | Lasionast | lasion + ast | LAS-i-on-ast |
| `County189Village9` | 189 | 38 | Dovneravren | dovner + avren | DOV-ner-av-ren |
| `County189Village10` | 189 | 38 | Colrontern | colront + ern | COL-ront-ern |
| `County189Village11` | 189 | 38 | Lasivevren | lasiv + evren | LAS-iv-ev-ren |
| `County189Village12` | 189 | 38 | Dovsuvord | dovsuv + ord | DOV-suv-ord |
| `County189Village13` | 189 | 38 | Colnamevard | colnam + evard | COL-nam-e-vard |
| `County189Village14` | 189 | 38 | Cranionolt | cranion + olt | CRAN-i-on-olt |
| `County189Village15` | 189 | 38 | Gelnerelvar | gelner + elvar | GEL-ner-el-var |
| `County189Village16` | 189 | 38 | Darontovan | daront + ovan | DAR-ont-o-van |
| `County190Village1` | 190 | 39 | Cranivund | craniv + und | CRAN-iv-und |
| `County190Village2` | 190 | 39 | Gelsuvorin | gelsuv + orin | GEL-suv-o-rin |
| `County190Village3` | 190 | 39 | Darnament | darnam + ent | DAR-nam-ent |
| `County190Village4` | 190 | 39 | Colionalven | colion + alven | COL-i-on-al-ven |
| `County190Village5` | 190 | 39 | Lasnerast | lasner + ast | LAS-ner-ast |
| `County190Village6` | 190 | 39 | Dovrontavren | dovront + avren | DOV-ront-av-ren |
| `County190Village7` | 190 | 39 | Colivern | coliv + ern | COL-iv-ern |
| `County190Village8` | 190 | 39 | Lassuvevren | lassuv + evren | LAS-suv-ev-ren |
| `County190Village9` | 190 | 39 | Dovnamord | dovnam + ord | DOV-nam-ord |
| `County190Village10` | 190 | 39 | Darionevard | darion + evard | DAR-i-on-e-vard |
| `County190Village11` | 190 | 39 | Crannerolt | cranner + olt | CRAN-ner-olt |
| `County190Village12` | 190 | 39 | Gelrontelvar | gelront + elvar | GEL-ront-el-var |
| `County190Village13` | 190 | 39 | Darivald | dariv + ald | DAR-iv-ald |
| `County190Village14` | 190 | 39 | Cransuvarden | cransuv + arden | CRAN-suv-ar-den |
| `County190Village15` | 190 | 39 | Gelnamost | gelnam + ost | GEL-nam-ost |
| `County190Village16` | 190 | 39 | Dovionavel | dovion + avel | DOV-i-on-a-vel |
| `County190Village17` | 190 | 39 | Colneresk | colner + esk | COL-ner-esk |
| `County191Village1` | 191 | 39 | Lasronterlan | lasront + erlan | LAS-ront-er-lan |
| `County191Village2` | 191 | 39 | Doviveld | doviv + eld | DOV-iv-eld |
| `County191Village3` | 191 | 39 | Colsuvovan | colsuv + ovan | COL-suv-o-van |
| `County191Village4` | 191 | 39 | Lasnamund | lasnam + und | LAS-nam-und |
| `County191Village5` | 191 | 39 | Gelionorin | gelion + orin | GEL-i-on-o-rin |
| `County191Village6` | 191 | 39 | Darnerent | darner + ent | DAR-ner-ent |
| `County191Village7` | 191 | 39 | Cranontalven | cranont + alven | CRAN-ont-al-ven |
| `County191Village8` | 191 | 39 | Gelivast | geliv + ast | GEL-iv-ast |
| `County191Village9` | 191 | 39 | Darsuvavren | darsuv + avren | DAR-suv-av-ren |
| `County191Village10` | 191 | 39 | Crannamern | crannam + ern | CRAN-nam-ern |
| `County191Village11` | 191 | 39 | Lasionevren | lasion + evren | LAS-i-on-ev-ren |
| `County191Village12` | 191 | 39 | Dovnerord | dovner + ord | DOV-ner-ord |
| `County192Village1` | 192 | 39 | Colrontevard | colront + evard | COL-ront-e-vard |
| `County192Village2` | 192 | 39 | Lasivolt | lasiv + olt | LAS-iv-olt |
| `County192Village3` | 192 | 39 | Dovsuvelvar | dovsuv + elvar | DOV-suv-el-var |
| `County192Village4` | 192 | 39 | Colnamald | colnam + ald | COL-nam-ald |
| `County192Village5` | 192 | 39 | Cranionarden | cranion + arden | CRAN-i-on-ar-den |
| `County192Village6` | 192 | 39 | Gelnerost | gelner + ost | GEL-ner-ost |
| `County192Village7` | 192 | 39 | Darontent | daront + ent | DAR-ont-ent |
| `County192Village8` | 192 | 39 | Cranivalven | craniv + alven | CRAN-iv-al-ven |
| `County192Village9` | 192 | 39 | Gelsuvast | gelsuv + ast | GEL-suv-ast |
| `County192Village10` | 192 | 39 | Darnamavren | darnam + avren | DAR-nam-av-ren |
| `County192Village11` | 192 | 39 | Colionern | colion + ern | COL-i-on-ern |
| `County192Village12` | 192 | 39 | Lasnerevren | lasner + evren | LAS-ner-ev-ren |
| `County192Village13` | 192 | 39 | Dovrontord | dovront + ord | DOV-ront-ord |
| `County192Village14` | 192 | 39 | Colivevard | coliv + evard | COL-iv-e-vard |
| `County192Village15` | 192 | 39 | Lassuvolt | lassuv + olt | LAS-suv-olt |
| `County193Village1` | 193 | 39 | Dovnamelvar | dovnam + elvar | DOV-nam-el-var |
| `County193Village2` | 193 | 39 | Darionald | darion + ald | DAR-i-on-ald |
| `County193Village3` | 193 | 39 | Crannerarden | cranner + arden | CRAN-ner-ar-den |
| `County193Village4` | 193 | 39 | Gelrontost | gelront + ost | GEL-ront-ost |
| `County193Village5` | 193 | 39 | Darivavel | dariv + avel | DAR-iv-a-vel |
| `County193Village6` | 193 | 39 | Cransuvesk | cransuv + esk | CRAN-suv-esk |
| `County193Village7` | 193 | 39 | Gelnamerlan | gelnam + erlan | GEL-nam-er-lan |
| `County193Village8` | 193 | 39 | Dovioneld | dovion + eld | DOV-i-on-eld |
| `County193Village9` | 193 | 39 | Colnerovan | colner + ovan | COL-ner-o-van |
| `County193Village10` | 193 | 39 | Lasrontund | lasront + und | LAS-ront-und |
| `County193Village11` | 193 | 39 | Dovivorin | doviv + orin | DOV-iv-o-rin |
| `County193Village12` | 193 | 39 | Colsuvent | colsuv + ent | COL-suv-ent |
| `County193Village13` | 193 | 39 | Lasnamalven | lasnam + alven | LAS-nam-al-ven |
| `County194Village1` | 194 | 39 | Gelionast | gelion + ast | GEL-i-on-ast |
| `County194Village2` | 194 | 39 | Darneravren | darner + avren | DAR-ner-av-ren |
| `County194Village3` | 194 | 39 | Cranontern | cranont + ern | CRAN-ont-ern |
| `County194Village4` | 194 | 39 | Gelivevren | geliv + evren | GEL-iv-ev-ren |
| `County194Village5` | 194 | 39 | Darsuvord | darsuv + ord | DAR-suv-ord |
| `County194Village6` | 194 | 39 | Crannamevard | crannam + evard | CRAN-nam-e-vard |
| `County194Village7` | 194 | 39 | Lasionolt | lasion + olt | LAS-i-on-olt |
| `County194Village8` | 194 | 39 | Dovnerelvar | dovner + elvar | DOV-ner-el-var |
| `County194Village9` | 194 | 39 | Colrontald | colront + ald | COL-ront-ald |
| `County194Village10` | 194 | 39 | Lasivarden | lasiv + arden | LAS-iv-ar-den |
| `County194Village11` | 194 | 39 | Dovsuvost | dovsuv + ost | DOV-suv-ost |
| `County194Village12` | 194 | 39 | Colnamavel | colnam + avel | COL-nam-a-vel |
| `County194Village13` | 194 | 39 | Cranionesk | cranion + esk | CRAN-i-on-esk |
| `County194Village14` | 194 | 39 | Gelnererlan | gelner + erlan | GEL-ner-er-lan |

#### Hamlets

| Existing node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County170Hamlet1` | 170 | 35 | Darontavren | daront + avren | DAR-ont-av-ren |
| `County170Hamlet2` | 170 | 35 | Cranivern | craniv + ern | CRAN-iv-ern |
| `County170Hamlet3` | 170 | 35 | Gelsuvevren | gelsuv + evren | GEL-suv-ev-ren |
| `County170Hamlet4` | 170 | 35 | Darnamord | darnam + ord | DAR-nam-ord |
| `County170Hamlet5` | 170 | 35 | Colionevard | colion + evard | COL-i-on-e-vard |
| `County170Hamlet6` | 170 | 35 | Lasnerolt | lasner + olt | LAS-ner-olt |
| `County170Hamlet7` | 170 | 35 | Dovrontelvar | dovront + elvar | DOV-ront-el-var |
| `County170Hamlet8` | 170 | 35 | Coliverral | coliv + erral | COL-iv-er-ral |
| `County170Hamlet9` | 170 | 35 | Lassuvarden | lassuv + arden | LAS-suv-ar-den |
| `County170Hamlet10` | 170 | 35 | Dovnamost | dovnam + ost | DOV-nam-ost |
| `County170Hamlet11` | 170 | 35 | Darionavel | darion + avel | DAR-i-on-a-vel |
| `County170Hamlet12` | 170 | 35 | Cranneresk | cranner + esk | CRAN-ner-esk |
| `County170Hamlet13` | 170 | 35 | Gelronterlan | gelront + erlan | GEL-ront-er-lan |
| `County170Hamlet14` | 170 | 35 | Dariveld | dariv + eld | DAR-iv-eld |
| `County170Hamlet15` | 170 | 35 | Cransuvovan | cransuv + ovan | CRAN-suv-o-van |
| `County171Hamlet1` | 171 | 35 | Gelnamund | gelnam + und | GEL-nam-und |
| `County171Hamlet2` | 171 | 35 | Dovionorin | dovion + orin | DOV-i-on-o-rin |
| `County171Hamlet3` | 171 | 35 | Colnerent | colner + ent | COL-ner-ent |
| `County171Hamlet4` | 171 | 35 | Lasrontalven | lasront + alven | LAS-ront-al-ven |
| `County171Hamlet5` | 171 | 35 | Dovivast | doviv + ast | DOV-iv-ast |
| `County171Hamlet6` | 171 | 35 | Colsuvavren | colsuv + avren | COL-suv-av-ren |
| `County171Hamlet7` | 171 | 35 | Lasnamern | lasnam + ern | LAS-nam-ern |
| `County171Hamlet8` | 171 | 35 | Gelionevren | gelion + evren | GEL-i-on-ev-ren |
| `County171Hamlet9` | 171 | 35 | Darnerord | darner + ord | DAR-ner-ord |
| `County171Hamlet10` | 171 | 35 | Cranontevard | cranont + evard | CRAN-ont-e-vard |
| `County171Hamlet11` | 171 | 35 | Gelivolt | geliv + olt | GEL-iv-olt |
| `County171Hamlet12` | 171 | 35 | Darsuvelvar | darsuv + elvar | DAR-suv-el-var |
| `County171Hamlet13` | 171 | 35 | Crannamald | crannam + ald | CRAN-nam-ald |
| `County171Hamlet14` | 171 | 35 | Lasionarden | lasion + arden | LAS-i-on-ar-den |
| `County171Hamlet15` | 171 | 35 | Dovnerost | dovner + ost | DOV-ner-ost |
| `County171Hamlet16` | 171 | 35 | Colrontavel | colront + avel | COL-ront-a-vel |
| `County171Hamlet17` | 171 | 35 | Lasivesk | lasiv + esk | LAS-iv-esk |
| `County172Hamlet1` | 172 | 35 | Dovsuverlan | dovsuv + erlan | DOV-suv-er-lan |
| `County172Hamlet2` | 172 | 35 | Colnameld | colnam + eld | COL-nam-eld |
| `County172Hamlet3` | 172 | 35 | Cranionovan | cranion + ovan | CRAN-i-on-o-van |
| `County172Hamlet4` | 172 | 35 | Gelnerund | gelner + und | GEL-ner-und |
| `County172Hamlet5` | 172 | 35 | Darontord | daront + ord | DAR-ont-ord |
| `County172Hamlet6` | 172 | 35 | Cranivevard | craniv + evard | CRAN-iv-e-vard |
| `County172Hamlet7` | 172 | 35 | Gelsuvolt | gelsuv + olt | GEL-suv-olt |
| `County172Hamlet8` | 172 | 35 | Darnamelvar | darnam + elvar | DAR-nam-el-var |
| `County172Hamlet9` | 172 | 35 | Colionald | colion + ald | COL-i-on-ald |
| `County172Hamlet10` | 172 | 35 | Lasnerarden | lasner + arden | LAS-ner-ar-den |
| `County172Hamlet11` | 172 | 35 | Dovrontost | dovront + ost | DOV-ront-ost |
| `County172Hamlet12` | 172 | 35 | Colivavel | coliv + avel | COL-iv-a-vel |
| `County172Hamlet13` | 172 | 35 | Lassuvesk | lassuv + esk | LAS-suv-esk |
| `County172Hamlet14` | 172 | 35 | Dovnamerlan | dovnam + erlan | DOV-nam-er-lan |
| `County173Hamlet1` | 173 | 35 | Darioneld | darion + eld | DAR-i-on-eld |
| `County173Hamlet2` | 173 | 35 | Crannerovan | cranner + ovan | CRAN-ner-o-van |
| `County173Hamlet3` | 173 | 35 | Gelrontund | gelront + und | GEL-ront-und |
| `County173Hamlet4` | 173 | 35 | Darivorin | dariv + orin | DAR-iv-o-rin |
| `County173Hamlet5` | 173 | 35 | Cransuvent | cransuv + ent | CRAN-suv-ent |
| `County173Hamlet6` | 173 | 35 | Gelnamalven | gelnam + alven | GEL-nam-al-ven |
| `County173Hamlet7` | 173 | 35 | Dovionast | dovion + ast | DOV-i-on-ast |
| `County173Hamlet8` | 173 | 35 | Colneravren | colner + avren | COL-ner-av-ren |
| `County173Hamlet9` | 173 | 35 | Lasrontern | lasront + ern | LAS-ront-ern |
| `County173Hamlet10` | 173 | 35 | Dovivevren | doviv + evren | DOV-iv-ev-ren |
| `County173Hamlet11` | 173 | 35 | Colsuvord | colsuv + ord | COL-suv-ord |
| `County173Hamlet12` | 173 | 35 | Lasnamevard | lasnam + evard | LAS-nam-e-vard |
| `County173Hamlet13` | 173 | 35 | Gelionolt | gelion + olt | GEL-i-on-olt |
| `County173Hamlet14` | 173 | 35 | Darnerelvar | darner + elvar | DAR-ner-el-var |
| `County173Hamlet15` | 173 | 35 | Cranontald | cranont + ald | CRAN-ont-ald |
| `County173Hamlet16` | 173 | 35 | Gelivarden | geliv + arden | GEL-iv-ar-den |
| `County173Hamlet17` | 173 | 35 | Darsuvost | darsuv + ost | DAR-suv-ost |
| `County173Hamlet18` | 173 | 35 | Crannamavel | crannam + avel | CRAN-nam-a-vel |
| `County174Hamlet1` | 174 | 35 | Lasionesk | lasion + esk | LAS-i-on-esk |
| `County174Hamlet2` | 174 | 35 | Dovnererlan | dovner + erlan | DOV-ner-er-lan |
| `County174Hamlet3` | 174 | 35 | Colronteld | colront + eld | COL-ront-eld |
| `County174Hamlet4` | 174 | 35 | Lasivovan | lasiv + ovan | LAS-iv-o-van |
| `County174Hamlet5` | 174 | 35 | Dovsuvund | dovsuv + und | DOV-suv-und |
| `County174Hamlet6` | 174 | 35 | Colnamorin | colnam + orin | COL-nam-o-rin |
| `County174Hamlet7` | 174 | 35 | Cranionent | cranion + ent | CRAN-i-on-ent |
| `County174Hamlet8` | 174 | 35 | Gelneralven | gelner + alven | GEL-ner-al-ven |
| `County174Hamlet9` | 174 | 35 | Darontelvar | daront + elvar | DAR-ont-el-var |
| `County175Hamlet1` | 175 | 36 | Cranivald | craniv + ald | CRAN-iv-ald |
| `County175Hamlet2` | 175 | 36 | Gelsuvarden | gelsuv + arden | GEL-suv-ar-den |
| `County175Hamlet3` | 175 | 36 | Darnamost | darnam + ost | DAR-nam-ost |
| `County175Hamlet4` | 175 | 36 | Colionavel | colion + avel | COL-i-on-a-vel |
| `County175Hamlet5` | 175 | 36 | Lasneresk | lasner + esk | LAS-ner-esk |
| `County175Hamlet6` | 175 | 36 | Dovronterlan | dovront + erlan | DOV-ront-er-lan |
| `County175Hamlet7` | 175 | 36 | Coliveld | coliv + eld | COL-iv-eld |
| `County175Hamlet8` | 175 | 36 | Lassuvovan | lassuv + ovan | LAS-suv-o-van |
| `County175Hamlet9` | 175 | 36 | Dovnamund | dovnam + und | DOV-nam-und |
| `County175Hamlet10` | 175 | 36 | Darionorin | darion + orin | DAR-i-on-o-rin |
| `County175Hamlet11` | 175 | 36 | Crannerent | cranner + ent | CRAN-ner-ent |
| `County175Hamlet12` | 175 | 36 | Gelrontalven | gelront + alven | GEL-ront-al-ven |
| `County175Hamlet13` | 175 | 36 | Darivast | dariv + ast | DAR-iv-ast |
| `County175Hamlet14` | 175 | 36 | Cransuvavren | cransuv + avren | CRAN-suv-av-ren |
| `County175Hamlet15` | 175 | 36 | Gelnamern | gelnam + ern | GEL-nam-ern |
| `County176Hamlet1` | 176 | 36 | Dovionevren | dovion + evren | DOV-i-on-ev-ren |
| `County176Hamlet2` | 176 | 36 | Colnerord | colner + ord | COL-ner-ord |
| `County176Hamlet3` | 176 | 36 | Lasrontevard | lasront + evard | LAS-ront-e-vard |
| `County176Hamlet4` | 176 | 36 | Dovivolt | doviv + olt | DOV-iv-olt |
| `County176Hamlet5` | 176 | 36 | Colsuvelvar | colsuv + elvar | COL-suv-el-var |
| `County176Hamlet6` | 176 | 36 | Lasnamald | lasnam + ald | LAS-nam-ald |
| `County176Hamlet7` | 176 | 36 | Gelionarden | gelion + arden | GEL-i-on-ar-den |
| `County176Hamlet8` | 176 | 36 | Darnerost | darner + ost | DAR-ner-ost |
| `County176Hamlet9` | 176 | 36 | Cranontavel | cranont + avel | CRAN-ont-a-vel |
| `County176Hamlet10` | 176 | 36 | Gelivesk | geliv + esk | GEL-iv-esk |
| `County177Hamlet1` | 177 | 36 | Darsuverlan | darsuv + erlan | DAR-suv-er-lan |
| `County177Hamlet2` | 177 | 36 | Crannameld | crannam + eld | CRAN-nam-eld |
| `County177Hamlet3` | 177 | 36 | Lasionovan | lasion + ovan | LAS-i-on-o-van |
| `County177Hamlet4` | 177 | 36 | Dovnerund | dovner + und | DOV-ner-und |
| `County177Hamlet5` | 177 | 36 | Colrontorin | colront + orin | COL-ront-o-rin |
| `County177Hamlet6` | 177 | 36 | Lasivent | lasiv + ent | LAS-iv-ent |
| `County177Hamlet7` | 177 | 36 | Dovsuvalven | dovsuv + alven | DOV-suv-al-ven |
| `County177Hamlet8` | 177 | 36 | Colnamast | colnam + ast | COL-nam-ast |
| `County177Hamlet9` | 177 | 36 | Cranionavren | cranion + avren | CRAN-i-on-av-ren |
| `County177Hamlet10` | 177 | 36 | Gelnerern | gelner + ern | GEL-ner-ern |
| `County177Hamlet11` | 177 | 36 | Darontost | daront + ost | DAR-ont-ost |
| `County177Hamlet12` | 177 | 36 | Cranivavel | craniv + avel | CRAN-iv-a-vel |
| `County177Hamlet13` | 177 | 36 | Gelsuvesk | gelsuv + esk | GEL-suv-esk |
| `County177Hamlet14` | 177 | 36 | Darnamerlan | darnam + erlan | DAR-nam-er-lan |
| `County177Hamlet15` | 177 | 36 | Colioneld | colion + eld | COL-i-on-eld |
| `County177Hamlet16` | 177 | 36 | Lasnerovan | lasner + ovan | LAS-ner-o-van |
| `County177Hamlet17` | 177 | 36 | Dovrontund | dovront + und | DOV-ront-und |
| `County177Hamlet18` | 177 | 36 | Colivorin | coliv + orin | COL-iv-o-rin |
| `County178Hamlet1` | 178 | 36 | Lassuvent | lassuv + ent | LAS-suv-ent |
| `County178Hamlet2` | 178 | 36 | Dovnamalven | dovnam + alven | DOV-nam-al-ven |
| `County178Hamlet3` | 178 | 36 | Darionast | darion + ast | DAR-i-on-ast |
| `County178Hamlet4` | 178 | 36 | Cranneravren | cranner + avren | CRAN-ner-av-ren |
| `County178Hamlet5` | 178 | 36 | Gelrontern | gelront + ern | GEL-ront-ern |
| `County178Hamlet6` | 178 | 36 | Darivevren | dariv + evren | DAR-iv-ev-ren |
| `County178Hamlet7` | 178 | 36 | Cransuvord | cransuv + ord | CRAN-suv-ord |
| `County178Hamlet8` | 178 | 36 | Gelnamevard | gelnam + evard | GEL-nam-e-vard |
| `County178Hamlet9` | 178 | 36 | Dovionolt | dovion + olt | DOV-i-on-olt |
| `County178Hamlet10` | 178 | 36 | Colnerelvar | colner + elvar | COL-ner-el-var |
| `County178Hamlet11` | 178 | 36 | Lasrontald | lasront + ald | LAS-ront-ald |
| `County178Hamlet12` | 178 | 36 | Dovivarden | doviv + arden | DOV-iv-ar-den |
| `County178Hamlet13` | 178 | 36 | Colsuvost | colsuv + ost | COL-suv-ost |
| `County178Hamlet14` | 178 | 36 | Lasnamavel | lasnam + avel | LAS-nam-a-vel |
| `County178Hamlet15` | 178 | 36 | Gelionesk | gelion + esk | GEL-i-on-esk |
| `County179Hamlet1` | 179 | 36 | Darnererlan | darner + erlan | DAR-ner-er-lan |
| `County179Hamlet2` | 179 | 36 | Cranonteld | cranont + eld | CRAN-ont-eld |
| `County179Hamlet3` | 179 | 36 | Gelivovan | geliv + ovan | GEL-iv-o-van |
| `County179Hamlet4` | 179 | 36 | Darsuvund | darsuv + und | DAR-suv-und |
| `County179Hamlet5` | 179 | 36 | Crannamorin | crannam + orin | CRAN-nam-o-rin |
| `County179Hamlet6` | 179 | 36 | Lasionent | lasion + ent | LAS-i-on-ent |
| `County179Hamlet7` | 179 | 36 | Dovneralven | dovner + alven | DOV-ner-al-ven |
| `County179Hamlet8` | 179 | 36 | Colrontast | colront + ast | COL-ront-ast |
| `County179Hamlet9` | 179 | 36 | Lasivavren | lasiv + avren | LAS-iv-av-ren |
| `County180Hamlet1` | 180 | 37 | Dovsuvern | dovsuv + ern | DOV-suv-ern |
| `County180Hamlet2` | 180 | 37 | Colnamevren | colnam + evren | COL-nam-ev-ren |
| `County180Hamlet3` | 180 | 37 | Cranionord | cranion + ord | CRAN-i-on-ord |
| `County180Hamlet4` | 180 | 37 | Gelnerevard | gelner + evard | GEL-ner-e-vard |
| `County180Hamlet5` | 180 | 37 | Daronterlan | daront + erlan | DAR-ont-er-lan |
| `County180Hamlet6` | 180 | 37 | Craniveld | craniv + eld | CRAN-iv-eld |
| `County180Hamlet7` | 180 | 37 | Gelsuvovan | gelsuv + ovan | GEL-suv-o-van |
| `County181Hamlet1` | 181 | 37 | Darnamund | darnam + und | DAR-nam-und |
| `County181Hamlet2` | 181 | 37 | Colionorin | colion + orin | COL-i-on-o-rin |
| `County181Hamlet3` | 181 | 37 | Lasnerent | lasner + ent | LAS-ner-ent |
| `County181Hamlet4` | 181 | 37 | Dovrontalven | dovront + alven | DOV-ront-al-ven |
| `County181Hamlet5` | 181 | 37 | Colivast | coliv + ast | COL-iv-ast |
| `County181Hamlet6` | 181 | 37 | Lassuvavren | lassuv + avren | LAS-suv-av-ren |
| `County181Hamlet7` | 181 | 37 | Dovnamern | dovnam + ern | DOV-nam-ern |
| `County181Hamlet8` | 181 | 37 | Darionevren | darion + evren | DAR-i-on-ev-ren |
| `County181Hamlet9` | 181 | 37 | Crannerord | cranner + ord | CRAN-ner-ord |
| `County181Hamlet10` | 181 | 37 | Gelrontevard | gelront + evard | GEL-ront-e-vard |
| `County181Hamlet11` | 181 | 37 | Darivolt | dariv + olt | DAR-iv-olt |
| `County181Hamlet12` | 181 | 37 | Cransuvelvar | cransuv + elvar | CRAN-suv-el-var |
| `County181Hamlet13` | 181 | 37 | Gelnamald | gelnam + ald | GEL-nam-ald |
| `County181Hamlet14` | 181 | 37 | Dovionarden | dovion + arden | DOV-i-on-ar-den |
| `County181Hamlet15` | 181 | 37 | Colnerost | colner + ost | COL-ner-ost |
| `County182Hamlet1` | 182 | 37 | Lasrontavel | lasront + avel | LAS-ront-a-vel |
| `County182Hamlet2` | 182 | 37 | Dovivesk | doviv + esk | DOV-iv-esk |
| `County182Hamlet3` | 182 | 37 | Colsuverlan | colsuv + erlan | COL-suv-er-lan |
| `County182Hamlet4` | 182 | 37 | Lasnameld | lasnam + eld | LAS-nam-eld |
| `County182Hamlet5` | 182 | 37 | Gelionovan | gelion + ovan | GEL-i-on-o-van |
| `County182Hamlet6` | 182 | 37 | Darnerund | darner + und | DAR-ner-und |
| `County182Hamlet7` | 182 | 37 | Cranontorin | cranont + orin | CRAN-ont-o-rin |
| `County182Hamlet8` | 182 | 37 | Gelivent | geliv + ent | GEL-iv-ent |
| `County182Hamlet9` | 182 | 37 | Darsuvalven | darsuv + alven | DAR-suv-al-ven |
| `County182Hamlet10` | 182 | 37 | Crannamast | crannam + ast | CRAN-nam-ast |
| `County182Hamlet11` | 182 | 37 | Lasionavren | lasion + avren | LAS-i-on-av-ren |
| `County183Hamlet1` | 183 | 37 | Dovnerern | dovner + ern | DOV-ner-ern |
| `County183Hamlet2` | 183 | 37 | Colrontevren | colront + evren | COL-ront-ev-ren |
| `County183Hamlet3` | 183 | 37 | Lasivord | lasiv + ord | LAS-iv-ord |
| `County183Hamlet4` | 183 | 37 | Dovsuvevard | dovsuv + evard | DOV-suv-e-vard |
| `County183Hamlet5` | 183 | 37 | Colnamolt | colnam + olt | COL-nam-olt |
| `County183Hamlet6` | 183 | 37 | Cranionelvar | cranion + elvar | CRAN-i-on-el-var |
| `County183Hamlet7` | 183 | 37 | Gelnerald | gelner + ald | GEL-ner-ald |
| `County183Hamlet8` | 183 | 37 | Darontund | daront + und | DAR-ont-und |
| `County183Hamlet9` | 183 | 37 | Cranivorin | craniv + orin | CRAN-iv-o-rin |
| `County183Hamlet10` | 183 | 37 | Gelsuvent | gelsuv + ent | GEL-suv-ent |
| `County183Hamlet11` | 183 | 37 | Darnamalven | darnam + alven | DAR-nam-al-ven |
| `County183Hamlet12` | 183 | 37 | Colionast | colion + ast | COL-i-on-ast |
| `County183Hamlet13` | 183 | 37 | Lasneravren | lasner + avren | LAS-ner-av-ren |
| `County183Hamlet14` | 183 | 37 | Dovrontern | dovront + ern | DOV-ront-ern |
| `County183Hamlet15` | 183 | 37 | Colivevren | coliv + evren | COL-iv-ev-ren |
| `County183Hamlet16` | 183 | 37 | Lassuvord | lassuv + ord | LAS-suv-ord |
| `County183Hamlet17` | 183 | 37 | Dovnamevard | dovnam + evard | DOV-nam-e-vard |
| `County183Hamlet18` | 183 | 37 | Darionolt | darion + olt | DAR-i-on-olt |
| `County184Hamlet1` | 184 | 37 | Crannerelvar | cranner + elvar | CRAN-ner-el-var |
| `County184Hamlet2` | 184 | 37 | Gelrontald | gelront + ald | GEL-ront-ald |
| `County184Hamlet3` | 184 | 37 | Darivarden | dariv + arden | DAR-iv-ar-den |
| `County184Hamlet4` | 184 | 37 | Cransuvost | cransuv + ost | CRAN-suv-ost |
| `County184Hamlet5` | 184 | 37 | Gelnamavel | gelnam + avel | GEL-nam-a-vel |
| `County184Hamlet6` | 184 | 37 | Dovionesk | dovion + esk | DOV-i-on-esk |
| `County184Hamlet7` | 184 | 37 | Colnererlan | colner + erlan | COL-ner-er-lan |
| `County184Hamlet8` | 184 | 37 | Lasronteld | lasront + eld | LAS-ront-eld |
| `County184Hamlet9` | 184 | 37 | Dovivovan | doviv + ovan | DOV-iv-o-van |
| `County184Hamlet10` | 184 | 37 | Colsuvund | colsuv + und | COL-suv-und |
| `County185Hamlet1` | 185 | 38 | Lasnamorin | lasnam + orin | LAS-nam-o-rin |
| `County185Hamlet2` | 185 | 38 | Gelionent | gelion + ent | GEL-i-on-ent |
| `County185Hamlet3` | 185 | 38 | Darneralven | darner + alven | DAR-ner-al-ven |
| `County185Hamlet4` | 185 | 38 | Cranontast | cranont + ast | CRAN-ont-ast |
| `County185Hamlet5` | 185 | 38 | Gelivavren | geliv + avren | GEL-iv-av-ren |
| `County185Hamlet6` | 185 | 38 | Darsuvern | darsuv + ern | DAR-suv-ern |
| `County185Hamlet7` | 185 | 38 | Crannamevren | crannam + evren | CRAN-nam-ev-ren |
| `County185Hamlet8` | 185 | 38 | Lasionord | lasion + ord | LAS-i-on-ord |
| `County185Hamlet9` | 185 | 38 | Dovnerevard | dovner + evard | DOV-ner-e-vard |
| `County185Hamlet10` | 185 | 38 | Colrontolt | colront + olt | COL-ront-olt |
| `County185Hamlet11` | 185 | 38 | Lasivelvar | lasiv + elvar | LAS-iv-el-var |
| `County185Hamlet12` | 185 | 38 | Dovsuvald | dovsuv + ald | DOV-suv-ald |
| `County185Hamlet13` | 185 | 38 | Colnamarden | colnam + arden | COL-nam-ar-den |
| `County186Hamlet1` | 186 | 38 | Cranionost | cranion + ost | CRAN-i-on-ost |
| `County186Hamlet2` | 186 | 38 | Gelneravel | gelner + avel | GEL-ner-a-vel |
| `County186Hamlet3` | 186 | 38 | Darontalven | daront + alven | DAR-ont-al-ven |
| `County186Hamlet4` | 186 | 38 | Cranivast | craniv + ast | CRAN-iv-ast |
| `County186Hamlet5` | 186 | 38 | Gelsuvavren | gelsuv + avren | GEL-suv-av-ren |
| `County186Hamlet6` | 186 | 38 | Darnamern | darnam + ern | DAR-nam-ern |
| `County186Hamlet7` | 186 | 38 | Colionevren | colion + evren | COL-i-on-ev-ren |
| `County186Hamlet8` | 186 | 38 | Lasnerord | lasner + ord | LAS-ner-ord |
| `County186Hamlet9` | 186 | 38 | Dovrontevard | dovront + evard | DOV-ront-e-vard |
| `County186Hamlet10` | 186 | 38 | Colivolt | coliv + olt | COL-iv-olt |
| `County186Hamlet11` | 186 | 38 | Lassuvelvar | lassuv + elvar | LAS-suv-el-var |
| `County187Hamlet1` | 187 | 38 | Dovnamald | dovnam + ald | DOV-nam-ald |
| `County187Hamlet2` | 187 | 38 | Darionarden | darion + arden | DAR-i-on-ar-den |
| `County187Hamlet3` | 187 | 38 | Crannerost | cranner + ost | CRAN-ner-ost |
| `County187Hamlet4` | 187 | 38 | Gelrontavel | gelront + avel | GEL-ront-a-vel |
| `County187Hamlet5` | 187 | 38 | Darivesk | dariv + esk | DAR-iv-esk |
| `County187Hamlet6` | 187 | 38 | Cransuverlan | cransuv + erlan | CRAN-suv-er-lan |
| `County187Hamlet7` | 187 | 38 | Gelnameld | gelnam + eld | GEL-nam-eld |
| `County187Hamlet8` | 187 | 38 | Dovionovan | dovion + ovan | DOV-i-on-o-van |
| `County187Hamlet9` | 187 | 38 | Colnerund | colner + und | COL-ner-und |
| `County187Hamlet10` | 187 | 38 | Lasrontorin | lasront + orin | LAS-ront-o-rin |
| `County187Hamlet11` | 187 | 38 | Dovivent | doviv + ent | DOV-iv-ent |
| `County187Hamlet12` | 187 | 38 | Colsuvalven | colsuv + alven | COL-suv-al-ven |
| `County187Hamlet13` | 187 | 38 | Lasnamast | lasnam + ast | LAS-nam-ast |
| `County187Hamlet14` | 187 | 38 | Gelionavren | gelion + avren | GEL-i-on-av-ren |
| `County187Hamlet15` | 187 | 38 | Darnerern | darner + ern | DAR-ner-ern |
| `County187Hamlet16` | 187 | 38 | Cranontevren | cranont + evren | CRAN-ont-ev-ren |
| `County188Hamlet1` | 188 | 38 | Gelivord | geliv + ord | GEL-iv-ord |
| `County188Hamlet2` | 188 | 38 | Darsuvevard | darsuv + evard | DAR-suv-e-vard |
| `County188Hamlet3` | 188 | 38 | Crannamolt | crannam + olt | CRAN-nam-olt |
| `County188Hamlet4` | 188 | 38 | Lasionelvar | lasion + elvar | LAS-i-on-el-var |
| `County188Hamlet5` | 188 | 38 | Dovnerald | dovner + ald | DOV-ner-ald |
| `County188Hamlet6` | 188 | 38 | Colrontarden | colront + arden | COL-ront-ar-den |
| `County188Hamlet7` | 188 | 38 | Lasivost | lasiv + ost | LAS-iv-ost |
| `County188Hamlet8` | 188 | 38 | Dovsuvavel | dovsuv + avel | DOV-suv-a-vel |
| `County188Hamlet9` | 188 | 38 | Colnamesk | colnam + esk | COL-nam-esk |
| `County188Hamlet10` | 188 | 38 | Cranionerlan | cranion + erlan | CRAN-i-on-er-lan |
| `County188Hamlet11` | 188 | 38 | Gelnereld | gelner + eld | GEL-ner-eld |
| `County188Hamlet12` | 188 | 38 | Darontern | daront + ern | DAR-ont-ern |
| `County188Hamlet13` | 188 | 38 | Cranivevren | craniv + evren | CRAN-iv-ev-ren |
| `County188Hamlet14` | 188 | 38 | Gelsuvord | gelsuv + ord | GEL-suv-ord |
| `County188Hamlet15` | 188 | 38 | Darnamevard | darnam + evard | DAR-nam-e-vard |
| `County189Hamlet1` | 189 | 38 | Colionolt | colion + olt | COL-i-on-olt |
| `County189Hamlet2` | 189 | 38 | Lasnerelvar | lasner + elvar | LAS-ner-el-var |
| `County189Hamlet3` | 189 | 38 | Dovrontald | dovront + ald | DOV-ront-ald |
| `County189Hamlet4` | 189 | 38 | Colivarden | coliv + arden | COL-iv-ar-den |
| `County189Hamlet5` | 189 | 38 | Lassuvost | lassuv + ost | LAS-suv-ost |
| `County189Hamlet6` | 189 | 38 | Dovnamavel | dovnam + avel | DOV-nam-a-vel |
| `County189Hamlet7` | 189 | 38 | Darionesk | darion + esk | DAR-i-on-esk |
| `County189Hamlet8` | 189 | 38 | Crannererlan | cranner + erlan | CRAN-ner-er-lan |
| `County189Hamlet9` | 189 | 38 | Gelronteld | gelront + eld | GEL-ront-eld |
| `County189Hamlet10` | 189 | 38 | Darivovan | dariv + ovan | DAR-iv-o-van |
| `County189Hamlet11` | 189 | 38 | Cransuvund | cransuv + und | CRAN-suv-und |
| `County189Hamlet12` | 189 | 38 | Gelnamorin | gelnam + orin | GEL-nam-o-rin |
| `County189Hamlet13` | 189 | 38 | Dovionent | dovion + ent | DOV-i-on-ent |
| `County189Hamlet14` | 189 | 38 | Colneralven | colner + alven | COL-ner-al-ven |
| `County190Hamlet1` | 190 | 39 | Lasrontast | lasront + ast | LAS-ront-ast |
| `County190Hamlet2` | 190 | 39 | Dovivavren | doviv + avren | DOV-iv-av-ren |
| `County190Hamlet3` | 190 | 39 | Colsuvern | colsuv + ern | COL-suv-ern |
| `County190Hamlet4` | 190 | 39 | Lasnamevren | lasnam + evren | LAS-nam-ev-ren |
| `County190Hamlet5` | 190 | 39 | Gelionord | gelion + ord | GEL-i-on-ord |
| `County190Hamlet6` | 190 | 39 | Darnerevard | darner + evard | DAR-ner-e-vard |
| `County190Hamlet7` | 190 | 39 | Cranontolt | cranont + olt | CRAN-ont-olt |
| `County190Hamlet8` | 190 | 39 | Gelivelvar | geliv + elvar | GEL-iv-el-var |
| `County190Hamlet9` | 190 | 39 | Darsuvald | darsuv + ald | DAR-suv-ald |
| `County190Hamlet10` | 190 | 39 | Crannamarden | crannam + arden | CRAN-nam-ar-den |
| `County190Hamlet11` | 190 | 39 | Lasionost | lasion + ost | LAS-i-on-ost |
| `County191Hamlet1` | 191 | 39 | Dovneravel | dovner + avel | DOV-ner-a-vel |
| `County191Hamlet2` | 191 | 39 | Colrontesk | colront + esk | COL-ront-esk |
| `County191Hamlet3` | 191 | 39 | Lasiverlan | lasiv + erlan | LAS-iv-er-lan |
| `County191Hamlet4` | 191 | 39 | Dovsuveld | dovsuv + eld | DOV-suv-eld |
| `County191Hamlet5` | 191 | 39 | Colnamovan | colnam + ovan | COL-nam-o-van |
| `County191Hamlet6` | 191 | 39 | Cranionund | cranion + und | CRAN-i-on-und |
| `County191Hamlet7` | 191 | 39 | Gelnerorin | gelner + orin | GEL-ner-o-rin |
| `County191Hamlet8` | 191 | 39 | Darontevard | daront + evard | DAR-ont-e-vard |
| `County191Hamlet9` | 191 | 39 | Cranivolt | craniv + olt | CRAN-iv-olt |
| `County191Hamlet10` | 191 | 39 | Gelsuvelvar | gelsuv + elvar | GEL-suv-el-var |
| `County191Hamlet11` | 191 | 39 | Darnamald | darnam + ald | DAR-nam-ald |
| `County191Hamlet12` | 191 | 39 | Colionarden | colion + arden | COL-i-on-ar-den |
| `County191Hamlet13` | 191 | 39 | Lasnerost | lasner + ost | LAS-ner-ost |
| `County192Hamlet1` | 192 | 39 | Dovrontavel | dovront + avel | DOV-ront-a-vel |
| `County192Hamlet2` | 192 | 39 | Colivesk | coliv + esk | COL-iv-esk |
| `County192Hamlet3` | 192 | 39 | Lassuverlan | lassuv + erlan | LAS-suv-er-lan |
| `County192Hamlet4` | 192 | 39 | Dovnameld | dovnam + eld | DOV-nam-eld |
| `County192Hamlet5` | 192 | 39 | Darionovan | darion + ovan | DAR-i-on-o-van |
| `County192Hamlet6` | 192 | 39 | Crannerund | cranner + und | CRAN-ner-und |
| `County192Hamlet7` | 192 | 39 | Gelrontorin | gelront + orin | GEL-ront-o-rin |
| `County192Hamlet8` | 192 | 39 | Darivent | dariv + ent | DAR-iv-ent |
| `County192Hamlet9` | 192 | 39 | Cransuvalven | cransuv + alven | CRAN-suv-al-ven |
| `County192Hamlet10` | 192 | 39 | Gelnamast | gelnam + ast | GEL-nam-ast |
| `County192Hamlet11` | 192 | 39 | Dovionavren | dovion + avren | DOV-i-on-av-ren |
| `County192Hamlet12` | 192 | 39 | Colnerern | colner + ern | COL-ner-ern |
| `County192Hamlet13` | 192 | 39 | Lasrontevren | lasront + evren | LAS-ront-ev-ren |
| `County192Hamlet14` | 192 | 39 | Dovivord | doviv + ord | DOV-iv-ord |
| `County192Hamlet15` | 192 | 39 | Colsuvevard | colsuv + evard | COL-suv-e-vard |
| `County193Hamlet1` | 193 | 39 | Lasnamolt | lasnam + olt | LAS-nam-olt |
| `County193Hamlet2` | 193 | 39 | Gelionelvar | gelion + elvar | GEL-i-on-el-var |
| `County193Hamlet3` | 193 | 39 | Darnerald | darner + ald | DAR-ner-ald |
| `County193Hamlet4` | 193 | 39 | Cranontarden | cranont + arden | CRAN-ont-ar-den |
| `County193Hamlet5` | 193 | 39 | Gelivost | geliv + ost | GEL-iv-ost |
| `County193Hamlet6` | 193 | 39 | Darsuvavel | darsuv + avel | DAR-suv-a-vel |
| `County193Hamlet7` | 193 | 39 | Crannamesk | crannam + esk | CRAN-nam-esk |
| `County193Hamlet8` | 193 | 39 | Lasionerlan | lasion + erlan | LAS-i-on-er-lan |
| `County193Hamlet9` | 193 | 39 | Dovnereld | dovner + eld | DOV-ner-eld |
| `County193Hamlet10` | 193 | 39 | Colrontovan | colront + ovan | COL-ront-o-van |
| `County193Hamlet11` | 193 | 39 | Lasivund | lasiv + und | LAS-iv-und |
| `County193Hamlet12` | 193 | 39 | Dovsuvorin | dovsuv + orin | DOV-suv-o-rin |
| `County193Hamlet13` | 193 | 39 | Colnament | colnam + ent | COL-nam-ent |
| `County193Hamlet14` | 193 | 39 | Cranionalven | cranion + alven | CRAN-i-on-al-ven |
| `County193Hamlet15` | 193 | 39 | Gelnerast | gelner + ast | GEL-ner-ast |
| `County194Hamlet1` | 194 | 39 | Darontald | daront + ald | DAR-ont-ald |
| `County194Hamlet2` | 194 | 39 | Cranivarden | craniv + arden | CRAN-iv-ar-den |
| `County194Hamlet3` | 194 | 39 | Gelsuvost | gelsuv + ost | GEL-suv-ost |
| `County194Hamlet4` | 194 | 39 | Darnamavel | darnam + avel | DAR-nam-a-vel |
| `County194Hamlet5` | 194 | 39 | Colionesk | colion + esk | COL-i-on-esk |
| `County194Hamlet6` | 194 | 39 | Lasnererlan | lasner + erlan | LAS-ner-er-lan |
| `County194Hamlet7` | 194 | 39 | Dovronteld | dovront + eld | DOV-ront-eld |
| `County194Hamlet8` | 194 | 39 | Colivovan | coliv + ovan | COL-iv-o-van |
| `County194Hamlet9` | 194 | 39 | Lassuvund | lassuv + und | LAS-suv-und |
| `County194Hamlet10` | 194 | 39 | Dovnamorin | dovnam + orin | DOV-nam-o-rin |
| `County194Hamlet11` | 194 | 39 | Darionent | darion + ent | DAR-i-on-ent |

### Person names

Use a single personal name after the existing title: **King Darneroven**,
**Duke Colionrel**, **Count Cranioneth**. These forms are ungendered.
Names encode a naming wish, not an assertion about a ruler's personality.
No surnames, inherited houses, or new title rules are introduced.

The same mixed roots connect people to the woodland naming tradition.
Personal tails are separate from the settlement endings: `-oven`
(steadfast judgement), `-rel` (care for others), `-eth` (patient counsel),
`-ric` (resourcefulness), and `-wen` (generosity). These meanings are
invented, even where the letter sequence resembles a real name element.
The wishes combine the root's natural image with the tail's virtue.

| Proposed person | Pronunciation | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Darneroven | DAR-ner-o-ven | darner + oven | steadfast judgement; imagery of oak / fallen leaves |
| Colionrel | COL-i-on-rel | colion + rel | care for others; imagery of hazel / woodland streams |
| Lasnameth | LAS-nam-eth | lasnam + eth | patient counsel; imagery of woodland / standing trees |
| Gelsuvric | GEL-suv-ric | gelsuv + ric | resourcefulness; imagery of grove / deep shade |
| Dovivwen | DOV-iv-wen | doviv + wen | generosity; imagery of old oak / new leaves |
| Darontoven | DAR-ont-o-ven | daront + oven | steadfast judgement; imagery of oak / worked timber |
| Colnerrel | COL-ner-rel | colner + rel | care for others; imagery of hazel / fallen leaves |
| Cranioneth | CRAN-i-on-eth | cranion + eth | patient counsel; imagery of timber / woodland streams |
| Gelnamric | GEL-nam-ric | gelnam + ric | resourcefulness; imagery of grove / standing trees |
| Dovsuvwen | DOV-suv-wen | dovsuv + wen | generosity; imagery of old oak / deep shade |
| Darivoven | DAR-iv-o-ven | dariv + oven | steadfast judgement; imagery of oak / new leaves |
| Colrontrel | COL-ront-rel | colront + rel | care for others; imagery of hazel / worked timber |
| Crannereth | CRAN-ner-eth | cranner + eth | patient counsel; imagery of timber / fallen leaves |
| Lasionric | LAS-i-on-ric | lasion + ric | resourcefulness; imagery of woodland / woodland streams |
| Dovnamwen | DOV-nam-wen | dovnam + wen | generosity; imagery of old oak / standing trees |
| Darsuvoven | DAR-suv-o-ven | darsuv + oven | steadfast judgement; imagery of oak / deep shade |
| Colivrel | COL-iv-rel | coliv + rel | care for others; imagery of hazel / new leaves |
| Cranonteth | CRAN-ont-eth | cranont + eth | patient counsel; imagery of timber / worked timber |
| Lasnerric | LAS-ner-ric | lasner + ric | resourcefulness; imagery of woodland / fallen leaves |
| Gelionwen | GEL-i-on-wen | gelion + wen | generosity; imagery of grove / woodland streams |
| Darnamoven | DAR-nam-o-ven | darnam + oven | steadfast judgement; imagery of oak / standing trees |
| Colsuvrel | COL-suv-rel | colsuv + rel | care for others; imagery of hazel / deep shade |
| Craniveth | CRAN-iv-eth | craniv + eth | patient counsel; imagery of timber / new leaves |
| Lasrontric | LAS-ront-ric | lasront + ric | resourcefulness; imagery of woodland / worked timber |
| Gelnerwen | GEL-ner-wen | gelner + wen | generosity; imagery of grove / fallen leaves |

### Court assignment register

| Existing court resource | Rank | Proposed person | Seat node | Proposed seat | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom8Capital` | King | Darneroven | `Kingdom8Capital` | Darontavel | 180 | 37 |
| `Court_Duchy35Capital` | Duke | Colionrel | `Duchy35Capital` | Cranivesk | 170 | 35 |
| `Court_Duchy36Capital` | Duke | Lasnameth | `Duchy36Capital` | Gelsuverlan | 175 | 36 |
| `Court_Duchy38Capital` | Duke | Gelsuvric | `Duchy38Capital` | Darnameld | 185 | 38 |
| `Court_Duchy39Capital` | Duke | Dovivwen | `Duchy39Capital` | Colionovan | 190 | 39 |
| `Court_County171Capital` | Count | Darontoven | `County171Capital` | Lasnerund | 171 | 35 |
| `Court_County172Capital` | Count | Colnerrel | `County172Capital` | Dovrontorin | 172 | 35 |
| `Court_County173Capital` | Count | Cranioneth | `County173Capital` | Coliverent | 173 | 35 |
| `Court_County174Capital` | Count | Gelnamric | `County174Capital` | Lassuvalven | 174 | 35 |
| `Court_County176Capital` | Count | Dovsuvwen | `County176Capital` | Dovnamast | 176 | 36 |
| `Court_County177Capital` | Count | Darivoven | `County177Capital` | Darionavren | 177 | 36 |
| `Court_County178Capital` | Count | Colrontrel | `County178Capital` | Crannerern | 178 | 36 |
| `Court_County179Capital` | Count | Crannereth | `County179Capital` | Gelrontevren | 179 | 36 |
| `Court_County181Capital` | Count | Lasionric | `County181Capital` | Darivord | 181 | 37 |
| `Court_County182Capital` | Count | Dovnamwen | `County182Capital` | Cransuvevard | 182 | 37 |
| `Court_County183Capital` | Count | Darsuvoven | `County183Capital` | Gelnamolt | 183 | 37 |
| `Court_County184Capital` | Count | Colivrel | `County184Capital` | Dovionelvar | 184 | 37 |
| `Court_County186Capital` | Count | Cranonteth | `County186Capital` | Colnerald | 186 | 38 |
| `Court_County187Capital` | Count | Lasnerric | `County187Capital` | Lasrontarden | 187 | 38 |
| `Court_County188Capital` | Count | Gelionwen | `County188Capital` | Dovivost | 188 | 38 |
| `Court_County189Capital` | Count | Darnamoven | `County189Capital` | Colsuvavel | 189 | 38 |
| `Court_County191Capital` | Count | Colsuvrel | `County191Capital` | Lasnamesk | 191 | 39 |
| `Court_County192Capital` | Count | Craniveth | `County192Capital` | Gelionerlan | 192 | 39 |
| `Court_County193Capital` | Count | Lasrontric | `County193Capital` | Darnereld | 193 | 39 |
| `Court_County194Capital` | Count | Gelnerwen | `County194Capital` | Cranontovan | 194 | 39 |

### Shared seats

| Existing capital | Seat coverage visible in metadata | Existing incumbent |
| --- | --- | --- |
| `Kingdom8Capital` (Darontavel) | County 180, Duchy 37, Kingdom 8 | King Darneroven |
| `Duchy35Capital` (Cranivesk) | County 170, Duchy 35 | Duke Colionrel |
| `Duchy36Capital` (Gelsuverlan) | County 175, Duchy 36 | Duke Lasnameth |
| `Duchy38Capital` (Darnameld) | County 185, Duchy 38 | Duke Gelsuvric |
| `Duchy39Capital` (Colionovan) | County 190, Duchy 39 | Duke Dovivwen |

There is no separate county-capital court at Counties 170, 175, 180, 185,
or 190, nor a separate Duchy 37 capital court. The register names the
25 existing incumbents; co-location does not establish a rule of combined
legal titles or justify inventing extra people.

### Review and collision screening

Checked against the current Kingdom 8 nodes, court resources, ranks, and
county/duchy metadata. All 720 final full names are distinct within this pass
and have no exact full-name duplicates in the earlier biome registers.

Quoted full-name web searches returned results for **316 initial settlement
candidates** before HTTP 429 rate limits prevented completion. This is partial
screening: **379 initial settlement candidates**, the **25 personal names**,
and the **7 replacement spellings** below do not have completed web screening.
An empty result is not proof of originality; no global uniqueness claim is made.
The authored names and scene assignment checks are complete.

| Initial candidate | Final candidate | Reason for revision |
| --- | --- | --- |
| Colivent | Coliverent | Existing commercial product name, documented in the [manufacturer's catalogue](https://www.univentismedicare.co.in/PDF%20Documents/PTR%202024-25.pdf) |
| Lasivern | Lasivorren | Existing [gaming-community handle](https://www.shsforums.net/members/?filter=3&max_results=20&name=L&name_box=begins&quickjump=L&sort_key=members_display_name&sort_order=asc&st=180) |
| Colivord | Colivorren | Appears in an [existing roleplaying spell text](https://ac-abercrombie.weebly.com/listagem-dos-feiticcedilos.html) |
| Darivost | Dariverost | Returned ordinary-language uses; changed to reduce resemblance to a complete existing word |
| Lasivald | Lasiverral | Appears as a surname-like entry in an [archival list](https://museum.dmna.ny.gov/download_file/6541/0); revised without relying on uncertain OCR |
| Gelivald | Geliverral | Search returned it as a misspelling of the existing given name [Gelivaldo](https://namesdir.com/F_Gelivaldo); revised for additional distance |
| Colivald | Coliverral | Returned a surname-like citation in indexed academic text; revised conservatively without claiming the OCR spelling is authoritative |

Other matches were code identifiers, anagram permutations, apparent OCR
artifacts, or ordinary prose rather than identifiable names. For example,
`Colnamern` matched a variable `colnameRN`; `Lasivorin` appeared in
an automatically generated anagram list. Those were not treated as evidence
that the fictional names had been copied. The screening deliberately distinguishes
a full-name match from incidental matching letters.

For reproducing the completed web coverage: take the settlement rows in their
printed order (capitals, villages, hamlets), restore the seven initial spellings,
and use zero-based positions. Positions 0–239 were checked, as were the four-row
blocks beginning at 240, 244, 248, 260, 268, 296, 300, 316, 320, 340, 344,
360, 364, 384, 392, 400, 424, 432, and 468. Other attempted blocks failed;
do not mark them as checked merely because a query was submitted.

### Research sources for this pass

Consulted 2026-11-07. These establish ordinary source words only; mixed roots,
sound substitutions, habitation terms, virtues, and finished names are authored.

- **DF1:** Logainm, [*Flóra agus fána*](https://www.logainm.ie/download/logainm.ie-scoil2-07-flora-agus-fana.pdf),
  vocabulary table, printed p. 5: dair, coll, and crann. Real place-name
  examples and the separate tree-alphabet exercise are not reused.
- **DF2:** Polish Academy of Sciences, *Wielki słownik języka polskiego PAN*,
  [las](https://wsjp.pl/haslo/podglad/262/las), forest sense.
- **DF3:** WSJP PAN, [gaj](https://wsjp.pl/haslo/podglad/481/gaj),
  a small wood/grove. Only its ordinary landscape sense is used.
- **DF4:** WSJP PAN, [dąb, tree sense](https://wsjp.pl/haslo/podglad/12670/dab/2090872/drzewo),
  oak.
- **DF5:** National Institute of Korean Language, [나무](https://krdict.korean.go.kr/eng/dicSearch/SearchView?ParaWordNo=32750),
  tree and wood senses.
- **DF6:** Defense Language Institute, [*Korean SOLT I, Module 1, Lesson 3*](https://fsi-languages.yojik.eu/languages/DLI/Korean/SOLT/Korean_SOLT1_text_workbook/M1/Korean_solt1_module1_lesson3.pdf),
  vocabulary for surroundings, 숲 (wood/forest). This is a mirror of the teaching material.
- **DF7:** Heo Yong, Busan University of Foreign Studies, [Korean morphology lecture](https://contents.kocw.or.kr/KOCW/document/2015/bufs/heoyong/11.pdf),
  leaf examples and 잎 forms. The ledger's p-to-v substitution is fictional.
- **DF8:** Stevie Jonathan, Tehakanere Henhawk, and Jersey Squire, Six Nations
  Polytechnic, [*Mohawk Language Learning Resources*](https://openlibrary-repo.ecampusontario.ca/jspui/bitstream/123456789/1773/8/Mohawk-Language-Learning-Resources-1678136465.html),
  Environment section: Karón:ta, Ónerahte, Kahiónha. Source vocabulary carries
  its own orthography; the game's shortened fragments are not Mohawk spelling rules.


## Grassland naming

### Brief, scope, and identity

Added 2026-11-07. The final requested kingdom draws on Germanic, French,
Plains North American, Eurasian Steppe, Mongolian, and Zulu sources.
Following the user's direction, this scheme and Deciduous Forest have a more
clearly European sound than the other kingdoms.

The landscape vocabulary centers on broad horizons, hay meadows, tilled fields,
pasture, watering places, wind, herds, and routes between settlements.
This is inhabited grassland with farms, markets, and seasonal movement.
The design does not reduce any source culture to warfare or horse riding.

The current scene identifies **Kingdom 5** as Grassland. The register covers
**359 settlements**: 117 hamlets, 217 villages, 20 county capitals,
4 duchy capitals, and 1 kingdom capital. Its **25 existing courts** contain
20 counts, 4 dukes, and 1 king. Counties are 97–121; duchies are 19–23.
Assignments are documentation-only proposals, retaining exact node/resource
identifiers. No game display names have been changed.

### Source palette

The six requested categories are represented by **German, French, Lakota,
Kazakh, Mongolian, and Zulu**. German is the selected Germanic language;
Lakota is one Plains language, not a label for all Plains peoples.
Kazakh provides a distinct Turkic steppe contribution alongside Mongolian.
The Eurasian Steppe category overlaps geographically with Mongolia; it is not
treated as a seventh language or as a homogeneous culture.

| Requested inspiration | Specific ordinary vocabulary | Authored fragments and contribution |
| --- | --- | --- |
| Germanic: German | `Feld`, field; `Wiese`, meadow [GR1, GR2] | `vel-` and `wes-`: fields and hay meadows; Feld loses d and changes f to v, while Wiese is shortened and respelled |
| French | `pré`, meadow; `vent`, wind [GR3, GR4] | `per-` and `ven-`: grazing commons and open winds; pré is reordered to per, vent loses t; no French nasal vowel is required |
| Plains North American: Lakota | `obláye`, prairie/plains; `mní`, water [GR5] | `-blen` and `-nim`: open plains and watering places; clip/reshape obláye, reorder mní, and use fictional vowels |
| Eurasian Steppe: Kazakh | `дала` (`dala`), steppe; `жел` (`jel`), wind [GR6, GR7] | `-dal` and `-zel`: open country and moving air; drop final a or substitute z for the source consonant |
| Mongolian | `тал` (`tal`), broad level country/plain; `морь` (working romanization `mori`), horse [GR8, GR9] | `-tav` and `-mor`: level grassland and horse routes; l changes to v or the final vowel is clipped |
| Zulu | `utshani`, grass; `imfuyo`, livestock [GR10] | `-shan` and `-fey`: growing grass and tended herds; select internal material, simplify consonants, and reshape the vowel |

The source glosses are factual lexical references; fragments, sound substitutions,
and narrowed images such as horse routes are inventions for the game.
These transformations are not claimed to be authentic morphology or sound laws.
Working romanizations help identify source words; they are not pronunciation
instructions for the real languages.

### European sound and distinction from Deciduous Forest

German and French material supplies the opening of most roots. Clear initial
stress, `v`, `f`, `r`, `l`, and `n`, and endings such as `-ain`,
`-elle`, and `-aldre` create the requested European impression.
Lakota, Kazakh, Mongolian, and Zulu elements remain identifiable through the
ledger in every name. No single source is assigned to an ethnic district.

Deciduous Forest favors clipped woodland roots and closed endings such as
`-eld` and `-ost`. Grassland favors a more flowing rhythm, broader vowel
sequences, and the recurring sounds `bl`, `fey`, `mor`, and `shan`.
A settlement such as **Veldalain** and a person such as **Pershaniel** should
sound related without simply copying the forest kingdom's vocabulary.

As previously agreed, the tradition uses every requested source, while each
individual name blends a smaller selection. Every mixed root here combines
German or French with one of the other four languages. In the 32-root design,
16 roots use German and 16 French; Lakota, Kazakh, Mongolian, and Zulu each
contribute to 8 roots. These are design counts, not claims of cultural ancestry
for the characters.

### Construction and pronunciation

1. Choose a mixed root from the ledger and add a settlement ending or a personal
   tail. Capitalize the finished name. The tables record the actual assignments.
2. Stress the first syllable, shown in capitals. Hyphens separate syllables
   only in pronunciation guides. `a` is ah, `e` eh, `i` ee, `o` oh,
   and `u` oo; `ai` and `ey` are each one vowel sound, like ay in day.
   Thus `fey` rhymes with day and `-ain` rhymes with rain.
3. W is English w; v is v; sh is one sound as in ship. R is audible, s is
   unvoiced, and all written vowels are pronounced. Final e is a light eh:
   `-elle` is el-le, not a claim of French pronunciation. Double consonants
   do not create an extra syllable.
4. `wes + shan` contracts to `weshan`, pronounced WE-shan.
   The French/Kazakh pairing originally `ven + dal` is recast as
   `valdren` (VAL-dren): reorder the combined letters and insert r.
   This authored fusion reduces resemblance to existing Vendal/Vendale forms.
   Other combinations retain the listed fragments directly.
5. Most names have three or four syllables. Settlement endings describe an
   imagined origin, not political rank. Capitals and hamlets share the same
   vocabulary; a name does not certify the presence of a scene feature.
6. Keep the same root spelling for place and person names. Shared roots do
   not establish kinship, houses, or inherited titles.
7. Borrow ordinary environmental words, not existing personal names, dynasties,
   sacred names, clan names, or complete real-world place names. The fictitious
   ruler naming wishes below are not borrowed cultural naming ceremonies.

### Mixed-root ledger

The final column contains fictional associations, not literal translations of
the completed roots. Full source glosses and transformations appear above.

| Root | Pronunciation | Source pairing | Fictional association |
| --- | --- | --- | --- |
| velblen | VEL-blen | German `Feld` + Lakota `obláye` | tilled fields / wide plains |
| velnim | VEL-nim | German `Feld` + Lakota `mní` | tilled fields / watering places |
| veldal | VEL-dal | German `Feld` + Kazakh `дала (dala)` | tilled fields / open steppe |
| velzel | VEL-zel | German `Feld` + Kazakh `жел (jel)` | tilled fields / moving air |
| veltav | VEL-tav | German `Feld` + Mongolian `тал (tal)` | tilled fields / level grassland |
| velmor | VEL-mor | German `Feld` + Mongolian `морь (mori)` | tilled fields / horse routes |
| velshan | VEL-shan | German `Feld` + Zulu `utshani` | tilled fields / fresh grass |
| velfey | VEL-fey | German `Feld` + Zulu `imfuyo` | tilled fields / tended herds |
| wesblen | WES-blen | German `Wiese` + Lakota `obláye` | hay meadows / wide plains |
| wesnim | WES-nim | German `Wiese` + Lakota `mní` | hay meadows / watering places |
| wesdal | WES-dal | German `Wiese` + Kazakh `дала (dala)` | hay meadows / open steppe |
| weszel | WES-zel | German `Wiese` + Kazakh `жел (jel)` | hay meadows / moving air |
| westav | WES-tav | German `Wiese` + Mongolian `тал (tal)` | hay meadows / level grassland |
| wesmor | WES-mor | German `Wiese` + Mongolian `морь (mori)` | hay meadows / horse routes |
| weshan | WE-shan | German `Wiese` + Zulu `utshani` | hay meadows / fresh grass |
| wesfey | WES-fey | German `Wiese` + Zulu `imfuyo` | hay meadows / tended herds |
| perblen | PER-blen | French `pré` + Lakota `obláye` | grazing commons / wide plains |
| pernim | PER-nim | French `pré` + Lakota `mní` | grazing commons / watering places |
| perdal | PER-dal | French `pré` + Kazakh `дала (dala)` | grazing commons / open steppe |
| perzel | PER-zel | French `pré` + Kazakh `жел (jel)` | grazing commons / moving air |
| pertav | PER-tav | French `pré` + Mongolian `тал (tal)` | grazing commons / level grassland |
| permor | PER-mor | French `pré` + Mongolian `морь (mori)` | grazing commons / horse routes |
| pershan | PER-shan | French `pré` + Zulu `utshani` | grazing commons / fresh grass |
| perfey | PER-fey | French `pré` + Zulu `imfuyo` | grazing commons / tended herds |
| venblen | VEN-blen | French `vent` + Lakota `obláye` | open winds / wide plains |
| vennim | VEN-nim | French `vent` + Lakota `mní` | open winds / watering places |
| valdren | VAL-dren | French `vent` + Kazakh `дала (dala)` | open winds / open steppe |
| venzel | VEN-zel | French `vent` + Kazakh `жел (jel)` | open winds / moving air |
| ventav | VEN-tav | French `vent` + Mongolian `тал (tal)` | open winds / level grassland |
| venmor | VEN-mor | French `vent` + Mongolian `морь (mori)` | open winds / horse routes |
| venshan | VEN-shan | French `vent` + Zulu `utshani` | open winds / fresh grass |
| venfey | VEN-fey | French `vent` + Zulu `imfuyo` | open winds / tended herds |

### Settlement endings

All meanings below belong to the invented naming system. Similar-looking real
European endings do not establish these meanings or a real etymology.
Place imagery records a proposed remembered origin rather than verified geography.

| Ending | Pronunciation | Fictional sense |
| --- | --- | --- |
| ain | ain | open common |
| erel | e-rel | market green |
| astel | as-tel | roadside hall |
| eran | e-ran | watered holdings |
| ovre | ov-re | seasonal stopping place |
| aldre | al-dre | boundary enclosure |
| esse | es-se | grain stores |
| evir | e-vir | crossing lanes |
| arve | ar-ve | grazing settlement |
| evel | e-vel | old hearths |
| elle | el-le | sheltered court |
| orent | o-rent | riverbank holdings |
| avain | a-vain | open common; expanded alternative to ain |
| irelle | i-rel-le | sheltered court; expanded alternative to elle |

The alternative endings are used for specific reviewed candidates; the shorter
forms remain available elsewhere.

### Settlement assignment register

Exact scene node identifiers and county/duchy metadata are preserved.
The root and ending columns link every name to the construction ledgers.

#### Capitals

| Existing node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `Kingdom5Capital` | 97 | 19 | Veldalain | veldal + ain | VEL-dal-ain |
| `Duchy20Capital` | 102 | 20 | Wesfeyaldre | wesfey + aldre | WES-fey-al-dre |
| `Duchy21Capital` | 107 | 21 | Ventavelle | ventav + elle | VEN-tav-el-le |
| `Duchy22Capital` | 112 | 22 | Wesnimeran | wesnim + eran | WES-nim-e-ran |
| `Duchy23Capital` | 117 | 23 | Pershanarve | pershan + arve | PER-shan-ar-ve |
| `County098Capital` | 98 | 19 | Velzelerel | velzel + erel | VEL-zel-e-rel |
| `County099Capital` | 99 | 19 | Perblenesse | perblen + esse | PER-blen-es-se |
| `County100Capital` | 100 | 19 | Venmororent | venmor + orent | VEN-mor-o-rent |
| `County101Capital` | 101 | 19 | Wesdalovre | wesdal + ovre | WES-dal-ov-re |
| `County103Capital` | 103 | 20 | Perfeyevel | perfey + evel | PER-fey-e-vel |
| `County104Capital` | 104 | 20 | Veltavastel | veltav + astel | VEL-tav-as-tel |
| `County105Capital` | 105 | 20 | Pernimevir | pernim + evir | PER-nim-e-vir |
| `County106Capital` | 106 | 20 | Venshanain | venshan + ain | VEN-shan-ain |
| `County108Capital` | 108 | 21 | Weszelaldre | weszel + aldre | WES-zel-al-dre |
| `County109Capital` | 109 | 21 | Venblenelle | venblen + elle | VEN-blen-el-le |
| `County110Capital` | 110 | 21 | Velmoreran | velmor + eran | VEL-mor-e-ran |
| `County111Capital` | 111 | 21 | Perdalarve | perdal + arve | PER-dal-ar-ve |
| `County113Capital` | 113 | 22 | Venfeyerel | venfey + erel | VEN-fey-e-rel |
| `County114Capital` | 114 | 22 | Westavesse | westav + esse | WES-tav-es-se |
| `County115Capital` | 115 | 22 | Vennimorent | vennim + orent | VEN-nim-o-rent |
| `County116Capital` | 116 | 22 | Velshanovre | velshan + ovre | VEL-shan-ov-re |
| `County118Capital` | 118 | 23 | Perzelevel | perzel + evel | PER-zel-e-vel |
| `County119Capital` | 119 | 23 | Velblenastel | velblen + astel | VEL-blen-as-tel |
| `County120Capital` | 120 | 23 | Wesmorevir | wesmor + evir | WES-mor-e-vir |
| `County121Capital` | 121 | 23 | Valdrenain | valdren + ain | VAL-dren-ain |

#### Villages

| Existing node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County097Village1` | 97 | 19 | Velfeyaldre | velfey + aldre | VEL-fey-al-dre |
| `County097Village2` | 97 | 19 | Pertavelle | pertav + elle | PER-tav-el-le |
| `County097Village3` | 97 | 19 | Velnimeran | velnim + eran | VEL-nim-e-ran |
| `County097Village4` | 97 | 19 | Weshanarve | weshan + arve | WE-shan-ar-ve |
| `County097Village5` | 97 | 19 | Venzelerel | venzel + erel | VEN-zel-e-rel |
| `County097Village6` | 97 | 19 | Wesblenesse | wesblen + esse | WES-blen-es-se |
| `County097Village7` | 97 | 19 | Permororent | permor + orent | PER-mor-o-rent |
| `County097Village8` | 97 | 19 | Veldalerel | veldal + erel | VEL-dal-e-rel |
| `County097Village9` | 97 | 19 | Wesfeyesse | wesfey + esse | WES-fey-es-se |
| `County097Village10` | 97 | 19 | Ventavorent | ventav + orent | VEN-tav-o-rent |
| `County098Village1` | 98 | 19 | Wesnimovre | wesnim + ovre | WES-nim-ov-re |
| `County098Village2` | 98 | 19 | Pershanevel | pershan + evel | PER-shan-e-vel |
| `County098Village3` | 98 | 19 | Velzelastel | velzel + astel | VEL-zel-as-tel |
| `County098Village4` | 98 | 19 | Perblenevir | perblen + evir | PER-blen-e-vir |
| `County098Village5` | 98 | 19 | Venmorain | venmor + ain | VEN-mor-ain |
| `County098Village6` | 98 | 19 | Wesdalaldre | wesdal + aldre | WES-dal-al-dre |
| `County098Village7` | 98 | 19 | Perfeyelle | perfey + elle | PER-fey-el-le |
| `County099Village1` | 99 | 19 | Veltaveran | veltav + eran | VEL-tav-e-ran |
| `County099Village2` | 99 | 19 | Pernimarve | pernim + arve | PER-nim-ar-ve |
| `County099Village3` | 99 | 19 | Venshanerel | venshan + erel | VEN-shan-e-rel |
| `County100Village1` | 100 | 19 | Weszelesse | weszel + esse | WES-zel-es-se |
| `County100Village2` | 100 | 19 | Venblenorent | venblen + orent | VEN-blen-o-rent |
| `County100Village3` | 100 | 19 | Velmorovre | velmor + ovre | VEL-mor-ov-re |
| `County100Village4` | 100 | 19 | Perdalevel | perdal + evel | PER-dal-e-vel |
| `County100Village5` | 100 | 19 | Venfeyastel | venfey + astel | VEN-fey-as-tel |
| `County100Village6` | 100 | 19 | Westavevir | westav + evir | WES-tav-e-vir |
| `County100Village7` | 100 | 19 | Vennimain | vennim + ain | VEN-nim-ain |
| `County100Village8` | 100 | 19 | Velshanaldre | velshan + aldre | VEL-shan-al-dre |
| `County100Village9` | 100 | 19 | Perzelelle | perzel + elle | PER-zel-el-le |
| `County101Village1` | 101 | 19 | Velbleneran | velblen + eran | VEL-blen-e-ran |
| `County102Village1` | 102 | 20 | Wesmorarve | wesmor + arve | WES-mor-ar-ve |
| `County102Village2` | 102 | 20 | Valdrenerel | valdren + erel | VAL-dren-e-rel |
| `County102Village3` | 102 | 20 | Velfeyesse | velfey + esse | VEL-fey-es-se |
| `County102Village4` | 102 | 20 | Pertavorent | pertav + orent | PER-tav-o-rent |
| `County102Village5` | 102 | 20 | Velnimovre | velnim + ovre | VEL-nim-ov-re |
| `County102Village6` | 102 | 20 | Weshanevel | weshan + evel | WE-shan-e-vel |
| `County102Village7` | 102 | 20 | Venzelastel | venzel + astel | VEN-zel-as-tel |
| `County102Village8` | 102 | 20 | Wesblenevir | wesblen + evir | WES-blen-e-vir |
| `County102Village9` | 102 | 20 | Permoravain | permor + avain | PER-mor-a-vain |
| `County102Village10` | 102 | 20 | Veldalastel | veldal + astel | VEL-dal-as-tel |
| `County103Village1` | 103 | 20 | Wesfeyevir | wesfey + evir | WES-fey-e-vir |
| `County103Village2` | 103 | 20 | Ventavain | ventav + ain | VEN-tav-ain |
| `County103Village3` | 103 | 20 | Wesnimaldre | wesnim + aldre | WES-nim-al-dre |
| `County103Village4` | 103 | 20 | Pershanelle | pershan + elle | PER-shan-el-le |
| `County103Village5` | 103 | 20 | Velzeleran | velzel + eran | VEL-zel-e-ran |
| `County103Village6` | 103 | 20 | Perblenarve | perblen + arve | PER-blen-ar-ve |
| `County103Village7` | 103 | 20 | Venmorerel | venmor + erel | VEN-mor-e-rel |
| `County103Village8` | 103 | 20 | Wesdalesse | wesdal + esse | WES-dal-es-se |
| `County103Village9` | 103 | 20 | Perfeyorent | perfey + orent | PER-fey-o-rent |
| `County104Village1` | 104 | 20 | Veltavovre | veltav + ovre | VEL-tav-ov-re |
| `County104Village2` | 104 | 20 | Pernimevel | pernim + evel | PER-nim-e-vel |
| `County104Village3` | 104 | 20 | Venshanastel | venshan + astel | VEN-shan-as-tel |
| `County104Village4` | 104 | 20 | Weszelevir | weszel + evir | WES-zel-e-vir |
| `County104Village5` | 104 | 20 | Venblenain | venblen + ain | VEN-blen-ain |
| `County104Village6` | 104 | 20 | Velmoraldre | velmor + aldre | VEL-mor-al-dre |
| `County104Village7` | 104 | 20 | Perdalelle | perdal + elle | PER-dal-el-le |
| `County104Village8` | 104 | 20 | Venfeyeran | venfey + eran | VEN-fey-e-ran |
| `County104Village9` | 104 | 20 | Westavarve | westav + arve | WES-tav-ar-ve |
| `County104Village10` | 104 | 20 | Vennimerel | vennim + erel | VEN-nim-e-rel |
| `County104Village11` | 104 | 20 | Velshanesse | velshan + esse | VEL-shan-es-se |
| `County104Village12` | 104 | 20 | Perzelorent | perzel + orent | PER-zel-o-rent |
| `County105Village1` | 105 | 20 | Velblenovre | velblen + ovre | VEL-blen-ov-re |
| `County105Village2` | 105 | 20 | Wesmorevel | wesmor + evel | WES-mor-e-vel |
| `County105Village3` | 105 | 20 | Valdrenastel | valdren + astel | VAL-dren-as-tel |
| `County105Village4` | 105 | 20 | Velfeyevir | velfey + evir | VEL-fey-e-vir |
| `County105Village5` | 105 | 20 | Pertavain | pertav + ain | PER-tav-ain |
| `County105Village6` | 105 | 20 | Velnimaldre | velnim + aldre | VEL-nim-al-dre |
| `County105Village7` | 105 | 20 | Weshanelle | weshan + elle | WE-shan-el-le |
| `County105Village8` | 105 | 20 | Venzeleran | venzel + eran | VEN-zel-e-ran |
| `County105Village9` | 105 | 20 | Wesblenarve | wesblen + arve | WES-blen-ar-ve |
| `County105Village10` | 105 | 20 | Permorerel | permor + erel | PER-mor-e-rel |
| `County105Village11` | 105 | 20 | Veldaleran | veldal + eran | VEL-dal-e-ran |
| `County105Village12` | 105 | 20 | Wesfeyarve | wesfey + arve | WES-fey-ar-ve |
| `County105Village13` | 105 | 20 | Ventaverel | ventav + erel | VEN-tav-e-rel |
| `County105Village14` | 105 | 20 | Wesnimesse | wesnim + esse | WES-nim-es-se |
| `County105Village15` | 105 | 20 | Pershanorent | pershan + orent | PER-shan-o-rent |
| `County105Village16` | 105 | 20 | Velzelovre | velzel + ovre | VEL-zel-ov-re |
| `County105Village17` | 105 | 20 | Perblenevel | perblen + evel | PER-blen-e-vel |
| `County105Village18` | 105 | 20 | Venmorastel | venmor + astel | VEN-mor-as-tel |
| `County106Village1` | 106 | 20 | Wesdalevir | wesdal + evir | WES-dal-e-vir |
| `County106Village2` | 106 | 20 | Perfeyain | perfey + ain | PER-fey-ain |
| `County106Village3` | 106 | 20 | Veltavaldre | veltav + aldre | VEL-tav-al-dre |
| `County106Village4` | 106 | 20 | Pernimelle | pernim + elle | PER-nim-el-le |
| `County106Village5` | 106 | 20 | Venshaneran | venshan + eran | VEN-shan-e-ran |
| `County106Village6` | 106 | 20 | Weszelarve | weszel + arve | WES-zel-ar-ve |
| `County106Village7` | 106 | 20 | Venblenerel | venblen + erel | VEN-blen-e-rel |
| `County106Village8` | 106 | 20 | Velmoresse | velmor + esse | VEL-mor-es-se |
| `County106Village9` | 106 | 20 | Perdalorent | perdal + orent | PER-dal-o-rent |
| `County106Village10` | 106 | 20 | Venfeyovre | venfey + ovre | VEN-fey-ov-re |
| `County106Village11` | 106 | 20 | Westavevel | westav + evel | WES-tav-e-vel |
| `County106Village12` | 106 | 20 | Vennimastel | vennim + astel | VEN-nim-as-tel |
| `County106Village13` | 106 | 20 | Velshanevir | velshan + evir | VEL-shan-e-vir |
| `County106Village14` | 106 | 20 | Perzelain | perzel + ain | PER-zel-ain |
| `County107Village1` | 107 | 21 | Velblenaldre | velblen + aldre | VEL-blen-al-dre |
| `County107Village2` | 107 | 21 | Wesmorelle | wesmor + elle | WES-mor-el-le |
| `County108Village1` | 108 | 21 | Valdreneran | valdren + eran | VAL-dren-e-ran |
| `County108Village2` | 108 | 21 | Velfeyarve | velfey + arve | VEL-fey-ar-ve |
| `County108Village3` | 108 | 21 | Pertaverel | pertav + erel | PER-tav-e-rel |
| `County109Village1` | 109 | 21 | Velnimesse | velnim + esse | VEL-nim-es-se |
| `County109Village2` | 109 | 21 | Weshanorent | weshan + orent | WE-shan-o-rent |
| `County109Village3` | 109 | 21 | Venzelovre | venzel + ovre | VEN-zel-ov-re |
| `County109Village4` | 109 | 21 | Wesblenevel | wesblen + evel | WES-blen-e-vel |
| `County109Village5` | 109 | 21 | Permorastel | permor + astel | PER-mor-as-tel |
| `County109Village6` | 109 | 21 | Veldalovre | veldal + ovre | VEL-dal-ov-re |
| `County109Village7` | 109 | 21 | Wesfeyevel | wesfey + evel | WES-fey-e-vel |
| `County109Village8` | 109 | 21 | Ventavastel | ventav + astel | VEN-tav-as-tel |
| `County110Village1` | 110 | 21 | Wesnimevir | wesnim + evir | WES-nim-e-vir |
| `County110Village2` | 110 | 21 | Pershanain | pershan + ain | PER-shan-ain |
| `County110Village3` | 110 | 21 | Velzelaldre | velzel + aldre | VEL-zel-al-dre |
| `County110Village4` | 110 | 21 | Perblenelle | perblen + elle | PER-blen-el-le |
| `County111Village1` | 111 | 21 | Venmoreran | venmor + eran | VEN-mor-e-ran |
| `County111Village2` | 111 | 21 | Wesdalarve | wesdal + arve | WES-dal-ar-ve |
| `County111Village3` | 111 | 21 | Perfeyerel | perfey + erel | PER-fey-e-rel |
| `County111Village4` | 111 | 21 | Veltavesse | veltav + esse | VEL-tav-es-se |
| `County111Village5` | 111 | 21 | Pernimorent | pernim + orent | PER-nim-o-rent |
| `County111Village6` | 111 | 21 | Venshanovre | venshan + ovre | VEN-shan-ov-re |
| `County111Village7` | 111 | 21 | Weszelevel | weszel + evel | WES-zel-e-vel |
| `County112Village1` | 112 | 22 | Venblenastel | venblen + astel | VEN-blen-as-tel |
| `County112Village2` | 112 | 22 | Velmorevir | velmor + evir | VEL-mor-e-vir |
| `County112Village3` | 112 | 22 | Perdalain | perdal + ain | PER-dal-ain |
| `County112Village4` | 112 | 22 | Venfeyaldre | venfey + aldre | VEN-fey-al-dre |
| `County112Village5` | 112 | 22 | Westavirelle | westav + irelle | WES-tav-i-rel-le |
| `County112Village6` | 112 | 22 | Vennimeran | vennim + eran | VEN-nim-e-ran |
| `County112Village7` | 112 | 22 | Velshanarve | velshan + arve | VEL-shan-ar-ve |
| `County112Village8` | 112 | 22 | Perzelerel | perzel + erel | PER-zel-e-rel |
| `County112Village9` | 112 | 22 | Velblenesse | velblen + esse | VEL-blen-es-se |
| `County112Village10` | 112 | 22 | Wesmororent | wesmor + orent | WES-mor-o-rent |
| `County112Village11` | 112 | 22 | Valdrenovre | valdren + ovre | VAL-dren-ov-re |
| `County112Village12` | 112 | 22 | Velfeyevel | velfey + evel | VEL-fey-e-vel |
| `County113Village1` | 113 | 22 | Pertavastel | pertav + astel | PER-tav-as-tel |
| `County113Village2` | 113 | 22 | Velnimevir | velnim + evir | VEL-nim-e-vir |
| `County113Village3` | 113 | 22 | Weshanain | weshan + ain | WE-shan-ain |
| `County113Village4` | 113 | 22 | Venzelaldre | venzel + aldre | VEN-zel-al-dre |
| `County113Village5` | 113 | 22 | Wesblenelle | wesblen + elle | WES-blen-el-le |
| `County113Village6` | 113 | 22 | Permoreran | permor + eran | PER-mor-e-ran |
| `County113Village7` | 113 | 22 | Veldalaldre | veldal + aldre | VEL-dal-al-dre |
| `County113Village8` | 113 | 22 | Wesfeyelle | wesfey + elle | WES-fey-el-le |
| `County113Village9` | 113 | 22 | Ventaveran | ventav + eran | VEN-tav-e-ran |
| `County113Village10` | 113 | 22 | Wesnimarve | wesnim + arve | WES-nim-ar-ve |
| `County113Village11` | 113 | 22 | Pershanerel | pershan + erel | PER-shan-e-rel |
| `County113Village12` | 113 | 22 | Velzelesse | velzel + esse | VEL-zel-es-se |
| `County113Village13` | 113 | 22 | Perblenorent | perblen + orent | PER-blen-o-rent |
| `County113Village14` | 113 | 22 | Venmorovre | venmor + ovre | VEN-mor-ov-re |
| `County113Village15` | 113 | 22 | Wesdalevel | wesdal + evel | WES-dal-e-vel |
| `County113Village16` | 113 | 22 | Perfeyastel | perfey + astel | PER-fey-as-tel |
| `County113Village17` | 113 | 22 | Veltavevir | veltav + evir | VEL-tav-e-vir |
| `County114Village1` | 114 | 22 | Pernimain | pernim + ain | PER-nim-ain |
| `County114Village2` | 114 | 22 | Venshanaldre | venshan + aldre | VEN-shan-al-dre |
| `County114Village3` | 114 | 22 | Weszelelle | weszel + elle | WES-zel-el-le |
| `County114Village4` | 114 | 22 | Venbleneran | venblen + eran | VEN-blen-e-ran |
| `County114Village5` | 114 | 22 | Velmorarve | velmor + arve | VEL-mor-ar-ve |
| `County114Village6` | 114 | 22 | Perdalerel | perdal + erel | PER-dal-e-rel |
| `County114Village7` | 114 | 22 | Venfeyesse | venfey + esse | VEN-fey-es-se |
| `County114Village8` | 114 | 22 | Westavorent | westav + orent | WES-tav-o-rent |
| `County114Village9` | 114 | 22 | Vennimovre | vennim + ovre | VEN-nim-ov-re |
| `County115Village1` | 115 | 22 | Velshanevel | velshan + evel | VEL-shan-e-vel |
| `County115Village2` | 115 | 22 | Perzelastel | perzel + astel | PER-zel-as-tel |
| `County115Village3` | 115 | 22 | Velblenevir | velblen + evir | VEL-blen-e-vir |
| `County115Village4` | 115 | 22 | Wesmorain | wesmor + ain | WES-mor-ain |
| `County115Village5` | 115 | 22 | Valdrenaldre | valdren + aldre | VAL-dren-al-dre |
| `County115Village6` | 115 | 22 | Velfeyelle | velfey + elle | VEL-fey-el-le |
| `County115Village7` | 115 | 22 | Pertaveran | pertav + eran | PER-tav-e-ran |
| `County115Village8` | 115 | 22 | Velnimarve | velnim + arve | VEL-nim-ar-ve |
| `County115Village9` | 115 | 22 | Weshanerel | weshan + erel | WE-shan-e-rel |
| `County115Village10` | 115 | 22 | Venzelesse | venzel + esse | VEN-zel-es-se |
| `County115Village11` | 115 | 22 | Wesblenorent | wesblen + orent | WES-blen-o-rent |
| `County115Village12` | 115 | 22 | Permorovre | permor + ovre | PER-mor-ov-re |
| `County115Village13` | 115 | 22 | Veldalesse | veldal + esse | VEL-dal-es-se |
| `County116Village1` | 116 | 22 | Wesfeyorent | wesfey + orent | WES-fey-o-rent |
| `County116Village2` | 116 | 22 | Ventavovre | ventav + ovre | VEN-tav-ov-re |
| `County116Village3` | 116 | 22 | Wesnimevel | wesnim + evel | WES-nim-e-vel |
| `County117Village1` | 117 | 23 | Pershanastel | pershan + astel | PER-shan-as-tel |
| `County117Village2` | 117 | 23 | Velzelevir | velzel + evir | VEL-zel-e-vir |
| `County117Village3` | 117 | 23 | Perblenain | perblen + ain | PER-blen-ain |
| `County117Village4` | 117 | 23 | Venmoraldre | venmor + aldre | VEN-mor-al-dre |
| `County117Village5` | 117 | 23 | Wesdalelle | wesdal + elle | WES-dal-el-le |
| `County117Village6` | 117 | 23 | Perfeyeran | perfey + eran | PER-fey-e-ran |
| `County117Village7` | 117 | 23 | Veltavarve | veltav + arve | VEL-tav-ar-ve |
| `County117Village8` | 117 | 23 | Pernimerel | pernim + erel | PER-nim-e-rel |
| `County117Village9` | 117 | 23 | Venshanesse | venshan + esse | VEN-shan-es-se |
| `County118Village1` | 118 | 23 | Weszelorent | weszel + orent | WES-zel-o-rent |
| `County118Village2` | 118 | 23 | Venblenovre | venblen + ovre | VEN-blen-ov-re |
| `County118Village3` | 118 | 23 | Velmorevel | velmor + evel | VEL-mor-e-vel |
| `County118Village4` | 118 | 23 | Perdalastel | perdal + astel | PER-dal-as-tel |
| `County118Village5` | 118 | 23 | Venfeyevir | venfey + evir | VEN-fey-e-vir |
| `County118Village6` | 118 | 23 | Westavain | westav + ain | WES-tav-ain |
| `County118Village7` | 118 | 23 | Vennimaldre | vennim + aldre | VEN-nim-al-dre |
| `County118Village8` | 118 | 23 | Velshanelle | velshan + elle | VEL-shan-el-le |
| `County118Village9` | 118 | 23 | Perzeleran | perzel + eran | PER-zel-e-ran |
| `County119Village1` | 119 | 23 | Velblenarve | velblen + arve | VEL-blen-ar-ve |
| `County119Village2` | 119 | 23 | Wesmorerel | wesmor + erel | WES-mor-e-rel |
| `County119Village3` | 119 | 23 | Valdrenesse | valdren + esse | VAL-dren-es-se |
| `County119Village4` | 119 | 23 | Velfeyorent | velfey + orent | VEL-fey-o-rent |
| `County119Village5` | 119 | 23 | Pertavovre | pertav + ovre | PER-tav-ov-re |
| `County119Village6` | 119 | 23 | Velnimevel | velnim + evel | VEL-nim-e-vel |
| `County119Village7` | 119 | 23 | Weshanastel | weshan + astel | WE-shan-as-tel |
| `County119Village8` | 119 | 23 | Venzelevir | venzel + evir | VEN-zel-e-vir |
| `County120Village1` | 120 | 23 | Wesblenain | wesblen + ain | WES-blen-ain |
| `County120Village2` | 120 | 23 | Permoraldre | permor + aldre | PER-mor-al-dre |
| `County120Village3` | 120 | 23 | Veldalevir | veldal + evir | VEL-dal-e-vir |
| `County120Village4` | 120 | 23 | Wesfeyain | wesfey + ain | WES-fey-ain |
| `County120Village5` | 120 | 23 | Ventavaldre | ventav + aldre | VEN-tav-al-dre |
| `County120Village6` | 120 | 23 | Wesnimelle | wesnim + elle | WES-nim-el-le |
| `County120Village7` | 120 | 23 | Pershaneran | pershan + eran | PER-shan-e-ran |
| `County121Village1` | 121 | 23 | Velzelarve | velzel + arve | VEL-zel-ar-ve |
| `County121Village2` | 121 | 23 | Perblenerel | perblen + erel | PER-blen-e-rel |
| `County121Village3` | 121 | 23 | Venmoresse | venmor + esse | VEN-mor-es-se |
| `County121Village4` | 121 | 23 | Wesdalorent | wesdal + orent | WES-dal-o-rent |
| `County121Village5` | 121 | 23 | Perfeyovre | perfey + ovre | PER-fey-ov-re |
| `County121Village6` | 121 | 23 | Veltavevel | veltav + evel | VEL-tav-e-vel |
| `County121Village7` | 121 | 23 | Pernimastel | pernim + astel | PER-nim-as-tel |
| `County121Village8` | 121 | 23 | Venshanevir | venshan + evir | VEN-shan-e-vir |
| `County121Village9` | 121 | 23 | Weszelain | weszel + ain | WES-zel-ain |
| `County121Village10` | 121 | 23 | Venblenaldre | venblen + aldre | VEN-blen-al-dre |
| `County121Village11` | 121 | 23 | Velmorelle | velmor + elle | VEL-mor-el-le |
| `County121Village12` | 121 | 23 | Perdaleran | perdal + eran | PER-dal-e-ran |
| `County121Village13` | 121 | 23 | Venfeyarve | venfey + arve | VEN-fey-ar-ve |

#### Hamlets

| Existing node | County | Duchy | Proposed name | Construction | Pronunciation |
| --- | --- | --- | --- | --- | --- |
| `County097Hamlet1` | 97 | 19 | Westaverel | westav + erel | WES-tav-e-rel |
| `County097Hamlet2` | 97 | 19 | Vennimesse | vennim + esse | VEN-nim-es-se |
| `County097Hamlet3` | 97 | 19 | Velshanorent | velshan + orent | VEL-shan-o-rent |
| `County097Hamlet4` | 97 | 19 | Perzelovre | perzel + ovre | PER-zel-ov-re |
| `County097Hamlet5` | 97 | 19 | Velblenevel | velblen + evel | VEL-blen-e-vel |
| `County097Hamlet6` | 97 | 19 | Wesmorastel | wesmor + astel | WES-mor-as-tel |
| `County097Hamlet7` | 97 | 19 | Valdrenevir | valdren + evir | VAL-dren-e-vir |
| `County097Hamlet8` | 97 | 19 | Velfeyain | velfey + ain | VEL-fey-ain |
| `County097Hamlet9` | 97 | 19 | Pertavaldre | pertav + aldre | PER-tav-al-dre |
| `County097Hamlet10` | 97 | 19 | Velnimelle | velnim + elle | VEL-nim-el-le |
| `County097Hamlet11` | 97 | 19 | Weshaneran | weshan + eran | WE-shan-e-ran |
| `County098Hamlet1` | 98 | 19 | Venzelarve | venzel + arve | VEN-zel-ar-ve |
| `County098Hamlet2` | 98 | 19 | Wesblenerel | wesblen + erel | WES-blen-e-rel |
| `County098Hamlet3` | 98 | 19 | Permoresse | permor + esse | PER-mor-es-se |
| `County098Hamlet4` | 98 | 19 | Veldalarve | veldal + arve | VEL-dal-ar-ve |
| `County098Hamlet5` | 98 | 19 | Wesfeyerel | wesfey + erel | WES-fey-e-rel |
| `County099Hamlet1` | 99 | 19 | Ventavesse | ventav + esse | VEN-tav-es-se |
| `County099Hamlet2` | 99 | 19 | Wesnimorent | wesnim + orent | WES-nim-o-rent |
| `County099Hamlet3` | 99 | 19 | Pershanovre | pershan + ovre | PER-shan-ov-re |
| `County100Hamlet1` | 100 | 19 | Velzelevel | velzel + evel | VEL-zel-e-vel |
| `County100Hamlet2` | 100 | 19 | Perblenastel | perblen + astel | PER-blen-as-tel |
| `County100Hamlet3` | 100 | 19 | Venmorevir | venmor + evir | VEN-mor-e-vir |
| `County100Hamlet4` | 100 | 19 | Wesdalain | wesdal + ain | WES-dal-ain |
| `County100Hamlet5` | 100 | 19 | Perfeyaldre | perfey + aldre | PER-fey-al-dre |
| `County100Hamlet6` | 100 | 19 | Veltavelle | veltav + elle | VEL-tav-el-le |
| `County101Hamlet1` | 101 | 19 | Pernimeran | pernim + eran | PER-nim-e-ran |
| `County101Hamlet2` | 101 | 19 | Venshanarve | venshan + arve | VEN-shan-ar-ve |
| `County101Hamlet3` | 101 | 19 | Weszelerel | weszel + erel | WES-zel-e-rel |
| `County101Hamlet4` | 101 | 19 | Venblenesse | venblen + esse | VEN-blen-es-se |
| `County102Hamlet1` | 102 | 20 | Velmororent | velmor + orent | VEL-mor-o-rent |
| `County102Hamlet2` | 102 | 20 | Perdalovre | perdal + ovre | PER-dal-ov-re |
| `County102Hamlet3` | 102 | 20 | Venfeyevel | venfey + evel | VEN-fey-e-vel |
| `County103Hamlet1` | 103 | 20 | Westavastel | westav + astel | WES-tav-as-tel |
| `County103Hamlet2` | 103 | 20 | Vennimevir | vennim + evir | VEN-nim-e-vir |
| `County103Hamlet3` | 103 | 20 | Velshanain | velshan + ain | VEL-shan-ain |
| `County104Hamlet1` | 104 | 20 | Perzelaldre | perzel + aldre | PER-zel-al-dre |
| `County104Hamlet2` | 104 | 20 | Velblenelle | velblen + elle | VEL-blen-el-le |
| `County104Hamlet3` | 104 | 20 | Wesmoreran | wesmor + eran | WES-mor-e-ran |
| `County105Hamlet1` | 105 | 20 | Valdrenarve | valdren + arve | VAL-dren-ar-ve |
| `County105Hamlet2` | 105 | 20 | Velfeyerel | velfey + erel | VEL-fey-e-rel |
| `County105Hamlet3` | 105 | 20 | Pertavesse | pertav + esse | PER-tav-es-se |
| `County105Hamlet4` | 105 | 20 | Velnimorent | velnim + orent | VEL-nim-o-rent |
| `County105Hamlet5` | 105 | 20 | Weshanovre | weshan + ovre | WE-shan-ov-re |
| `County106Hamlet1` | 106 | 20 | Venzelevel | venzel + evel | VEN-zel-e-vel |
| `County106Hamlet2` | 106 | 20 | Wesblenastel | wesblen + astel | WES-blen-as-tel |
| `County106Hamlet3` | 106 | 20 | Permorevir | permor + evir | PER-mor-e-vir |
| `County106Hamlet4` | 106 | 20 | Veldalevel | veldal + evel | VEL-dal-e-vel |
| `County106Hamlet5` | 106 | 20 | Wesfeyastel | wesfey + astel | WES-fey-as-tel |
| `County108Hamlet1` | 108 | 21 | Ventavevir | ventav + evir | VEN-tav-e-vir |
| `County108Hamlet2` | 108 | 21 | Wesnimain | wesnim + ain | WES-nim-ain |
| `County108Hamlet3` | 108 | 21 | Pershanaldre | pershan + aldre | PER-shan-al-dre |
| `County108Hamlet4` | 108 | 21 | Velzelelle | velzel + elle | VEL-zel-el-le |
| `County109Hamlet1` | 109 | 21 | Perbleneran | perblen + eran | PER-blen-e-ran |
| `County109Hamlet2` | 109 | 21 | Venmorarve | venmor + arve | VEN-mor-ar-ve |
| `County109Hamlet3` | 109 | 21 | Wesdalerel | wesdal + erel | WES-dal-e-rel |
| `County110Hamlet1` | 110 | 21 | Perfeyesse | perfey + esse | PER-fey-es-se |
| `County110Hamlet2` | 110 | 21 | Veltavorent | veltav + orent | VEL-tav-o-rent |
| `County110Hamlet3` | 110 | 21 | Pernimovre | pernim + ovre | PER-nim-ov-re |
| `County110Hamlet4` | 110 | 21 | Venshanevel | venshan + evel | VEN-shan-e-vel |
| `County111Hamlet1` | 111 | 21 | Weszelastel | weszel + astel | WES-zel-as-tel |
| `County111Hamlet2` | 111 | 21 | Venblenevir | venblen + evir | VEN-blen-e-vir |
| `County111Hamlet3` | 111 | 21 | Velmorain | velmor + ain | VEL-mor-ain |
| `County111Hamlet4` | 111 | 21 | Perdalaldre | perdal + aldre | PER-dal-al-dre |
| `County111Hamlet5` | 111 | 21 | Venfeyelle | venfey + elle | VEN-fey-el-le |
| `County112Hamlet1` | 112 | 22 | Westaveran | westav + eran | WES-tav-e-ran |
| `County112Hamlet2` | 112 | 22 | Vennimarve | vennim + arve | VEN-nim-ar-ve |
| `County112Hamlet3` | 112 | 22 | Velshanerel | velshan + erel | VEL-shan-e-rel |
| `County112Hamlet4` | 112 | 22 | Perzelesse | perzel + esse | PER-zel-es-se |
| `County113Hamlet1` | 113 | 22 | Velblenorent | velblen + orent | VEL-blen-o-rent |
| `County113Hamlet2` | 113 | 22 | Wesmorovre | wesmor + ovre | WES-mor-ov-re |
| `County114Hamlet1` | 114 | 22 | Valdrenevel | valdren + evel | VAL-dren-e-vel |
| `County114Hamlet2` | 114 | 22 | Velfeyastel | velfey + astel | VEL-fey-as-tel |
| `County114Hamlet3` | 114 | 22 | Pertavevir | pertav + evir | PER-tav-e-vir |
| `County114Hamlet4` | 114 | 22 | Velnimain | velnim + ain | VEL-nim-ain |
| `County114Hamlet5` | 114 | 22 | Weshanaldre | weshan + aldre | WE-shan-al-dre |
| `County114Hamlet6` | 114 | 22 | Venzelelle | venzel + elle | VEN-zel-el-le |
| `County114Hamlet7` | 114 | 22 | Wesbleneran | wesblen + eran | WES-blen-e-ran |
| `County115Hamlet1` | 115 | 22 | Permorarve | permor + arve | PER-mor-ar-ve |
| `County115Hamlet2` | 115 | 22 | Veldalelle | veldal + elle | VEL-dal-el-le |
| `County115Hamlet3` | 115 | 22 | Wesfeyeran | wesfey + eran | WES-fey-e-ran |
| `County115Hamlet4` | 115 | 22 | Ventavarve | ventav + arve | VEN-tav-ar-ve |
| `County115Hamlet5` | 115 | 22 | Wesnimerel | wesnim + erel | WES-nim-e-rel |
| `County115Hamlet6` | 115 | 22 | Pershanesse | pershan + esse | PER-shan-es-se |
| `County115Hamlet7` | 115 | 22 | Velzelorent | velzel + orent | VEL-zel-o-rent |
| `County115Hamlet8` | 115 | 22 | Perblenovre | perblen + ovre | PER-blen-ov-re |
| `County115Hamlet9` | 115 | 22 | Venmorevel | venmor + evel | VEN-mor-e-vel |
| `County116Hamlet1` | 116 | 22 | Wesdalastel | wesdal + astel | WES-dal-as-tel |
| `County116Hamlet2` | 116 | 22 | Perfeyevir | perfey + evir | PER-fey-e-vir |
| `County116Hamlet3` | 116 | 22 | Veltavain | veltav + ain | VEL-tav-ain |
| `County116Hamlet4` | 116 | 22 | Pernimaldre | pernim + aldre | PER-nim-al-dre |
| `County116Hamlet5` | 116 | 22 | Venshanelle | venshan + elle | VEN-shan-el-le |
| `County116Hamlet6` | 116 | 22 | Weszeleran | weszel + eran | WES-zel-e-ran |
| `County116Hamlet7` | 116 | 22 | Venblenarve | venblen + arve | VEN-blen-ar-ve |
| `County117Hamlet1` | 117 | 23 | Velmorerel | velmor + erel | VEL-mor-e-rel |
| `County117Hamlet2` | 117 | 23 | Perdalesse | perdal + esse | PER-dal-es-se |
| `County117Hamlet3` | 117 | 23 | Venfeyorent | venfey + orent | VEN-fey-o-rent |
| `County117Hamlet4` | 117 | 23 | Westavovre | westav + ovre | WES-tav-ov-re |
| `County117Hamlet5` | 117 | 23 | Vennimevel | vennim + evel | VEN-nim-e-vel |
| `County118Hamlet1` | 118 | 23 | Velshanastel | velshan + astel | VEL-shan-as-tel |
| `County118Hamlet2` | 118 | 23 | Perzelevir | perzel + evir | PER-zel-e-vir |
| `County118Hamlet3` | 118 | 23 | Velblenain | velblen + ain | VEL-blen-ain |
| `County118Hamlet4` | 118 | 23 | Wesmoraldre | wesmor + aldre | WES-mor-al-dre |
| `County119Hamlet1` | 119 | 23 | Valdrenelle | valdren + elle | VAL-dren-el-le |
| `County119Hamlet2` | 119 | 23 | Velfeyeran | velfey + eran | VEL-fey-e-ran |
| `County119Hamlet3` | 119 | 23 | Pertavarve | pertav + arve | PER-tav-ar-ve |
| `County120Hamlet1` | 120 | 23 | Velnimerel | velnim + erel | VEL-nim-e-rel |
| `County120Hamlet2` | 120 | 23 | Weshanesse | weshan + esse | WE-shan-es-se |
| `County120Hamlet3` | 120 | 23 | Venzelorent | venzel + orent | VEN-zel-o-rent |
| `County120Hamlet4` | 120 | 23 | Wesblenovre | wesblen + ovre | WES-blen-ov-re |
| `County120Hamlet5` | 120 | 23 | Permorevel | permor + evel | PER-mor-e-vel |
| `County120Hamlet6` | 120 | 23 | Veldalorent | veldal + orent | VEL-dal-o-rent |
| `County120Hamlet7` | 120 | 23 | Wesfeyovre | wesfey + ovre | WES-fey-ov-re |
| `County121Hamlet1` | 121 | 23 | Ventavevel | ventav + evel | VEN-tav-e-vel |
| `County121Hamlet2` | 121 | 23 | Wesnimastel | wesnim + astel | WES-nim-as-tel |
| `County121Hamlet3` | 121 | 23 | Pershanevir | pershan + evir | PER-shan-e-vir |
| `County121Hamlet4` | 121 | 23 | Velzelain | velzel + ain | VEL-zel-ain |
| `County121Hamlet5` | 121 | 23 | Perblenaldre | perblen + aldre | PER-blen-al-dre |

### Person names

Use mononyms after the existing rank: **King Pershaniel**, **Duke Veldalor**,
**Count Wesmoriel**. Names are ungendered. No surnames, dynasties, or additional
incumbents are created. The wishes express hopes attached to a name, not a
claim that the current holder possesses a particular virtue.

| Personal tail | Pronunciation | Fictional wish |
| --- | --- | --- |
| iel | i-el | fair judgement |
| ant | ant | steadfastness |
| ert | ert | resourcefulness |
| ise | i-se | hospitality |
| ald | ald | care for the common good |
| eris | e-ris | hospitality; expanded alternative to ise |
| or | or | patient stewardship |

These tails and meanings are authorial choices. Their occasional resemblance
to real European name elements is part of the intended sound, not an assertion
that they translate these virtues in German or French.

| Proposed person | Pronunciation | Construction | Fictional naming wish |
| --- | --- | --- | --- |
| Pershaniel | PER-shan-i-el | pershan + iel | fair judgement; imagery of grazing commons / fresh grass |
| Velnimant | VEL-nim-ant | velnim + ant | steadfastness; imagery of tilled fields / watering places |
| Westavert | WES-tav-ert | westav + ert | resourcefulness; imagery of hay meadows / level grassland |
| Perfeyise | PER-fey-i-se | perfey + ise | hospitality; imagery of grazing commons / tended herds |
| Veldalor | VEL-dal-or | veldal + or | patient stewardship; imagery of tilled fields / open steppe |
| Wesmoriel | WES-mor-i-el | wesmor + iel | fair judgement; imagery of hay meadows / horse routes |
| Venblenant | VEN-blen-ant | venblen + ant | steadfastness; imagery of open winds / wide plains |
| Velzelert | VEL-zel-ert | velzel + ert | resourcefulness; imagery of tilled fields / moving air |
| Weshanise | WE-shan-i-se | weshan + ise | hospitality; imagery of hay meadows / fresh grass |
| Vennimald | VEN-nim-ald | vennim + ald | care for the common good; imagery of open winds / watering places |
| Veltaviel | VEL-tav-i-el | veltav + iel | fair judgement; imagery of tilled fields / level grassland |
| Wesfeyant | WES-fey-ant | wesfey + ant | steadfastness; imagery of hay meadows / tended herds |
| Valdrenert | VAL-dren-ert | valdren + ert | resourcefulness; imagery of open winds / open steppe |
| Velmorise | VEL-mor-i-se | velmor + ise | hospitality; imagery of tilled fields / horse routes |
| Perblenald | PER-blen-ald | perblen + ald | care for the common good; imagery of grazing commons / wide plains |
| Venzeliel | VEN-zel-i-el | venzel + iel | fair judgement; imagery of open winds / moving air |
| Velshanant | VEL-shan-ant | velshan + ant | steadfastness; imagery of tilled fields / fresh grass |
| Pernimert | PER-nim-ert | pernim + ert | resourcefulness; imagery of grazing commons / watering places |
| Ventaveris | VEN-tav-e-ris | ventav + eris | hospitality; imagery of open winds / level grassland |
| Velfeyald | VEL-fey-ald | velfey + ald | care for the common good; imagery of tilled fields / tended herds |
| Perdaliel | PER-dal-i-el | perdal + iel | fair judgement; imagery of grazing commons / open steppe |
| Venmorant | VEN-mor-ant | venmor + ant | steadfastness; imagery of open winds / horse routes |
| Wesblenert | WES-blen-ert | wesblen + ert | resourcefulness; imagery of hay meadows / wide plains |
| Perzelise | PER-zel-i-se | perzel + ise | hospitality; imagery of grazing commons / moving air |
| Venshanald | VEN-shan-ald | venshan + ald | care for the common good; imagery of open winds / fresh grass |

### Court assignment register

| Existing court resource | Rank | Proposed person | Seat node | Proposed seat | County | Duchy |
| --- | --- | --- | --- | --- | --- | --- |
| `Court_Kingdom5Capital` | King | Pershaniel | `Kingdom5Capital` | Veldalain | 97 | 19 |
| `Court_Duchy20Capital` | Duke | Velnimant | `Duchy20Capital` | Wesfeyaldre | 102 | 20 |
| `Court_Duchy21Capital` | Duke | Westavert | `Duchy21Capital` | Ventavelle | 107 | 21 |
| `Court_Duchy22Capital` | Duke | Perfeyise | `Duchy22Capital` | Wesnimeran | 112 | 22 |
| `Court_Duchy23Capital` | Duke | Veldalor | `Duchy23Capital` | Pershanarve | 117 | 23 |
| `Court_County098Capital` | Count | Wesmoriel | `County098Capital` | Velzelerel | 98 | 19 |
| `Court_County099Capital` | Count | Venblenant | `County099Capital` | Perblenesse | 99 | 19 |
| `Court_County100Capital` | Count | Velzelert | `County100Capital` | Venmororent | 100 | 19 |
| `Court_County101Capital` | Count | Weshanise | `County101Capital` | Wesdalovre | 101 | 19 |
| `Court_County103Capital` | Count | Vennimald | `County103Capital` | Perfeyevel | 103 | 20 |
| `Court_County104Capital` | Count | Veltaviel | `County104Capital` | Veltavastel | 104 | 20 |
| `Court_County105Capital` | Count | Wesfeyant | `County105Capital` | Pernimevir | 105 | 20 |
| `Court_County106Capital` | Count | Valdrenert | `County106Capital` | Venshanain | 106 | 20 |
| `Court_County108Capital` | Count | Velmorise | `County108Capital` | Weszelaldre | 108 | 21 |
| `Court_County109Capital` | Count | Perblenald | `County109Capital` | Venblenelle | 109 | 21 |
| `Court_County110Capital` | Count | Venzeliel | `County110Capital` | Velmoreran | 110 | 21 |
| `Court_County111Capital` | Count | Velshanant | `County111Capital` | Perdalarve | 111 | 21 |
| `Court_County113Capital` | Count | Pernimert | `County113Capital` | Venfeyerel | 113 | 22 |
| `Court_County114Capital` | Count | Ventaveris | `County114Capital` | Westavesse | 114 | 22 |
| `Court_County115Capital` | Count | Velfeyald | `County115Capital` | Vennimorent | 115 | 22 |
| `Court_County116Capital` | Count | Perdaliel | `County116Capital` | Velshanovre | 116 | 22 |
| `Court_County118Capital` | Count | Venmorant | `County118Capital` | Perzelevel | 118 | 23 |
| `Court_County119Capital` | Count | Wesblenert | `County119Capital` | Velblenastel | 119 | 23 |
| `Court_County120Capital` | Count | Perzelise | `County120Capital` | Wesmorevir | 120 | 23 |
| `Court_County121Capital` | Count | Venshanald | `County121Capital` | Valdrenain | 121 | 23 |

### Shared seats

| Existing capital | Seat coverage visible in metadata | Existing incumbent |
| --- | --- | --- |
| `Kingdom5Capital` (Veldalain) | County 97, Duchy 19, Kingdom 5 | King Pershaniel |
| `Duchy20Capital` (Wesfeyaldre) | County 102, Duchy 20 | Duke Velnimant |
| `Duchy21Capital` (Ventavelle) | County 107, Duchy 21 | Duke Westavert |
| `Duchy22Capital` (Wesnimeran) | County 112, Duchy 22 | Duke Perfeyise |
| `Duchy23Capital` (Pershanarve) | County 117, Duchy 23 | Duke Veldalor |

There is no separate county-capital court at Counties 97, 102, 107, 112, or
117, nor a separate Duchy 19 capital court. Name the 25 existing incumbents;
shared geography does not prove combined legal titles or require extra people.

### Review, revisions, and collision screening

The assignment audit checks all 359 Kingdom 5 settlement nodes, all 25 linked
court resources, rank labels, and county/duchy metadata. All **384 final full
names** are unique within this pass and have no exact full-name duplicates
in the prior biome registers. Pronunciation spellings and root/ending joins
are checked against the tables.

Quoted full-name web searches were completed for **384 initial candidates**.
Review produced **74 revised spellings** (71 settlement names, 3 person names),
including changes propagated through whole ending/root families. Every revised
spelling was searched again. No exact full-name matches were returned for those
74 replacements. This is an indexed-web check, not proof of universal uniqueness.

| Review finding | Decision and examples |
| --- | --- |
| Short -el forms repeatedly overlapped existing names or products | Replace the settlement ending -el throughout with -evel. Examples: Wesmorel → Wesmorevel, Permorel → Permorevel, Veltavel → Veltavevel, Ventavel → Ventavevel, Vennimel → Vennimevel |
| Several -ove forms overlapped a company, a handle, or inflected surname forms | Replace settlement -ove throughout with -ovre. Examples: Veldalove → Veldalovre, Perzelove → Perzelovre, Pershanove → Pershanovre |
| Vendalain appeared in genealogical indexing, and Vendalelle was an inflected literary character name | Recast the entire ven + dal family as valdren. Examples: Vendalain → Valdrenain, Vendalelle → Valdrenelle, Vendalert → Valdrenert; this also supersedes the intermediate -ove decision for Vendalove |
| Permorain matched a filter-product name | Use Permoravain, with expanded -avain |
| Westavelle matched a commercial mark | Use Westavirelle, with expanded -irelle |
| Ventavise matched an inflected medicine name | Use Ventaveris, with the personal tail -eris |
| Veldalald repeated the dal/ald sounds awkwardly | Use Veldalor; the new personal tail expresses patient stewardship |

Representative evidence supporting the revisions:
[Permorain filter product](https://www.manomano.es/p/new-73929681),
[Westavelle mark](https://uspto.report/TM/99338859),
[Veltavel product entry](https://www.lsgeotar.ru/drugs/veltavel-ACVO),
[Ventavel company](https://www.dnb.com/business-directory/company-profiles.ventavel_energaiaki_sa.f384bd19d187a862dd892f0dddfc310a.html),
[Permorel in a civil register index](https://www.geneanet.org/registres/view/52090),
[Perzel surname in municipal history](https://www.donjikraljevec.hr/povijest-opcine/),
and the [Finnish text of *No Thoroughfare*](https://www.gutenberg.org/cache/epub/19934/pg19934-images.html)
for Vendale/Vendalelle.

Remaining incidental hits were reviewed as apparent OCR errors, concatenated
ordinary words, spelling variants, or prose rather than identifiable place/person
names. Examples retained include Pernimert in garbled OCR and Perdalain in
concatenated Indonesian administrative prose. A matching string does not on its
own establish a copied name. The revised forms avoid the clearer collisions.

For reproduction, sort capitals first (kingdom, duchy, county), then villages,
then hamlets; within each group sort by county and numeric node identifier.
The initial root index was `(13*i + 2) mod 32`, with roots in ledger order
and the valdren position originally vendal. The initial ending index was
`(floor(i/32) + 5*(i mod 32)) mod 12`, using the first twelve ending rows,
originally el in place of evel and ove in place of ovre. Apply the revisions
above; the printed assignment tables are authoritative. For people, use
`(11*i + 22) mod 32` across the 25 capital seats and cycle the first five
personal tails, then apply the three personal revisions. These distribution
rules spread the authored vocabulary; they are not claims about linguistic
history.

### Research sources for this pass

Consulted 2026-11-07. Sources establish the ordinary vocabulary only.
Invented transformations, meanings, histories, and naming wishes are separate.

- **GR1:** Duden, [Feld](https://www.duden.de/rechtschreibung/Feld),
  open-ground and cultivated-field senses.
- **GR2:** Duden, [Wiese](https://www.duden.de/rechtschreibung/Wiese),
  meadow.
- **GR3:** Académie française, [pré, third edition](https://www.dictionnaire-academie.fr/article/A3P1350),
  meadow/hay ground; corroborated by the indexed [Le Robert entry](https://dictionnaire.lerobert.com/definition/pre).
  Only the ordinary word is used, not a historic place-name convention.
- **GR4:** Académie française, [vent, ninth edition](https://dictionnaire-academie.fr/article/A9V0381),
  wind.
- **GR5:** [*High School Lakota Language Bowl Vocabulary Packet 2015*](https://wotakuye.weebly.com/uploads/2/3/7/4/23749479/2015_lni_hs.pdf),
  printed p. 10, obláye; p. 7, mní, also present in the environmental compounds.
  The packet's ceremonial terms, tribal names, and sacred-site names are not
  used as naming ingredients.
- **GR6:** Nazarbayev Intellectual Schools, [*History of Kazakhstan*, grade 7 glossary, p. 171](https://textbooks.nis.edu.kz/wp-content/uploads/2020/7cl/G7_History%20of%20Kazakhstan_LB_EN_NIS/files/basic-html/page171.html),
  indexed bilingual entry steppe / дала. The indexed excerpt was available;
  direct retrieval returned a gateway error during this pass.
- **GR7:** [“Features of the 14th century dictionary ‘Kitab Bulgat al-Mushtaq’ and its thematic composition”](https://bulletin-orientalism.kaznu.kz/index.php/1-vostok/article/download/1747/1371/4354),
  *KazNU Oriental Studies* 1(100), 2022, comparison explicitly identifying
  modern Kazakh жел as wind. The older dictionary's yel is not silently
  presented as the modern Kazakh form.
- **GR8:** *Монгол хэлний их тайлбар толь*,
  [тал](https://www.mongoltoli.mn/dictionary/detail/83873),
  broad level terrain with little elevation variation; the plain sense
  supplies the grassland association.
- **GR9:** Same dictionary, [морь](https://mongoltoli.mn/dictionary/index.php/detail/57564),
  horse entry; corroborating [Tsevel dictionary entry](https://tsevel.toli.query.mn/dictionary_items/5900).
  Indexed entry material was available, although direct retrieval timed out.
  No historical ruler's name or equestrian ceremonial title is borrowed.
- **GR10:** UCLA Phonetics Lab Archive, [Zulu word list, 1985](https://archive.phonetics.ucla.edu/Language/ZUL/zul_word-list_1985_01.html),
  items 46 (imfuyo, livestock) and 55 (utshani, grass). The recorded tones
  and noun forms belong to Zulu; the game's clipped fragments do not reproduce
  that grammar or pronunciation system.

## Territorial names: counties, duchies, and kingdoms

### Scope and decisions

Added 2026-11-07 at the user's request. This is a third naming category alongside
settlements and people. It names **220 counties, 44 duchies, and 9 kingdoms**:
**273 distinct territories**, verified against the Land hierarchy in
`vcom/Scenes/Map.tscn`. These names are authored proposals in this document;
territorial labels have not been applied to the game in this pass.

Territories have their own names. A capital, its county, its duchy, and its
kingdom can therefore all have different names, even when one settlement is the
seat of all three. Shared roots are intentional vocabulary, not a rule that a
territory inherits its capital's name. No additional rulers, courts, dynasties,
demonyms, or ethnic groups are created.

Use **County of <name>**, **Duchy of <name>**, and **Kingdom of <name>** when
a title is useful; use the bare name in compact map labels. The name itself
contains no English rank word. Rank remains separate data, so a later political
change would not require renaming a region.

The naming scale broadens from a settlement's homes, workshops, or landing to
its surrounding drainage, grazing grounds, connected valleys, or wider homeland.
These are invented name stories, not proof of terrain, trade routes, borders,
or historical institutions at the assigned scene location.

### Verified hierarchy

| Kingdom ID | Biome | Counties | Duchies | Kingdoms |
| --- | --- | --- | --- | --- |
| `Kingdom1` | Tundra / Frozen Mountains | 24 | 4 | 1 |
| `Kingdom2` | Volcanic Mountains / Ruins | 24 | 4 | 1 |
| `Kingdom3` | Temperate Mountains | 24 | 6 | 1 |
| `Kingdom4` | Desert | 24 | 4 | 1 |
| `Kingdom5` | Grassland | 25 | 5 | 1 |
| `Kingdom6` | Evergreen Temperate Rainforest | 25 | 5 | 1 |
| `Kingdom7` | Swamp | 24 | 6 | 1 |
| `Kingdom8` | Deciduous Forest | 25 | 5 | 1 |
| `Kingdom9` | Tropical Rainforest | 25 | 5 | 1 |
| **Total** | | **220** | **44** | **9** |

All counties and duchies are included, including those without a separately
named county-capital or duchy-capital settlement. The earlier 220-ruler count
is not a territorial count: 9 kingdom capitals also occupy duchy seats,
and higher capitals also occupy county seats. This register gives names to
the territories without inventing the absent lower-ranking incumbents.
**County220 remains in Duchy33, Kingdom7**; its unusual numbering is preserved.

### Method, continuity, and pronunciation

1. Retain the exact scene identifier and parent path; do not reconstruct the
   hierarchy from consecutive numbers or from the count of courts.
2. Reuse the biome's established mixed-root ledger, with its documented source
   pairings and transformations. Every territorial name therefore already has
   at least two language inspirations. All of each biome's requested traditions
   remain represented across its territorial register.
3. Add a regional formative from the new ledger below, replacing the
   settlement-form ending rather than appending to a complete settlement name.
   These are fictional lexical elements. Their uses here favor local districts
   for counties, connected regions for duchies, and wider homelands for kingdoms;
   they are not authentic translations of the game's feudal ranks.
4. Preserve each biome's existing vowels, consonant rules, and stress.
   Tundra, temperate mountains, Deciduous Forest, and Grassland use initial
   stress; desert and swamp use penultimate stress; volcanic names stress the
   third-last syllable; evergreen names stress the final syllable; tropical names
   stress the second syllable. Capitals in the guides mark stress, not spelling.
5. Preserve the desert's vowel-joining rule: insert v when a vowel-final root
   meets a vowel-initial formative. The inserted v begins the formative's first
   syllable: `soru + v + adren` becomes `so-ru-VAD-ren`.
   Desert `adren` introduces a modest dr cluster, pronounced without an extra
   vowel. Tundra y retains its established i sound; guides may use i for y.
6. Keep the two European-leaning traditions distinct: woodland roots and
   firmer closures for Deciduous Forest; open-country roots and flowing
   `-ance/-erre/-ardel` patterns for Grassland. Their regional names still
   contain Korean/Mohawk or Plains/steppe/Mongolian/Zulu material respectively.
7. Check complete names against the existing registers and web results,
   revise collisions, and verify every seat against settlement metadata.
   A shared seat records geography; it does not assign an additional title.

### Additional inspiration and research

Four newly consulted ordinary land/region words inform selected kingdom
formatives. Their semantic contribution is broader than their surviving
letter fragments. The full forms below are inventions, not native suffixes.

| Biome | Additional word and source | Authored use |
| --- | --- | --- |
| Volcanic Mountains / Ruins | Hawaiian `ʻāina`, land/earth/island [TN1] | Retain na and add ya to coin `naya`, shared land; attach it to the existing api/pōhaku-derived apohu. Neither the ending nor Apohunaya is presented as Hawaiian grammar |
| Temperate Mountains | Southern Quechua `suyu`, region [TN2] | Retain su and add ren to coin `suren`, a broad region; attach it to the Sherpa/Quechua/Blackfoot mixed root rikumet. This does not copy a historical Inca division or government |
| Deciduous Forest | Irish `tír`, land/country, also region/district [TN3] | Reshape tir to ter and add ne: `terne`, woodland country; attach it to the Irish/Mohawk root colner |
| Grassland | French `pays`, country or a region with a shared identity [TN4] | Retain pa and add rain: `parain`, open homeland; attach it to the German/Mongolian root velmor. Rain is an invented sound sequence here, pronounced with the Grassland ai vowel, not the English weather word |

The other five schemes already contain suitable material for a territorial
scale, so they extend that material instead of adding an unrelated language:

- **Tundra:** Inuktut nuna and Unangam Tunuu tanax̂ already supply land imagery;
  Norwegian/Icelandic upland and snow material, Nenets snow-season imagery,
  and Evenki river/water vocabulary support connected winter-country names.
  These remain the specific selections documented under T1–T6.
- **Desert:** water-sharing and basin routes broaden the existing
  Tamasheq/Amazigh, Hausa, Khoekhoegowab, Hopi, Diné Bizaad, and Mescalero Apache
  mixtures. The Mogollon contribution remains architectural imagery, now
  extended imaginatively from clustered shelter to linked inhabited basins.
  No purported Mogollon word or political institution is invented.
- **Evergreen rainforest:** historical Chinuk Wawa illahie already supplies
  earth/land alongside Lushootseed water/cedar and Tlingit rain/tree/water.
  Local woodland imagery expands to connected forest drainages.
- **Tropical rainforest:** Nheengatu canoe/vegetation, Lingala forest/rain,
  Iban wood/water, and West Kewa tree/water material supports linked waterways
  and canopy country. Connections between settlements are fictional images.
- **Swamp:** Uru reed/water, historical Nahuatl reed/water, Cajun French
  paddle/swamp-wood, Tunica water/moss, and Biloxi water imagery expands to
  connected channels and wetland basins.

The new English senses assigned to all formatives are authorial decisions.
Real roots do not establish an authentic translation of the finished names.
No source culture is assigned to one duchy or county.

### New regional formative ledger

The first two ordinary forms for each biome are used for counties, the next
two for duchies, and the last for its kingdom in this initial allocation.
This is an authoring pattern, not a rule that a sound encodes political rank.
Extended alternatives introduced in review retain their base form's image.

| Biome | Formative | Syllables | Fictional regional image | Basis |
| --- | --- | --- | --- | --- |
| Tundra / Frozen Mountains | esh | esh | local snow-country district | Invented sound form and sense |
| Tundra / Frozen Mountains | orn | orn | river approach district | Invented sound form and sense |
| Tundra / Frozen Mountains | avren | a-vren | connected winter routes | Invented sound form and sense |
| Tundra / Frozen Mountains | eldun | el-dun | linked upland basins | Invented sound form and sense |
| Tundra / Frozen Mountains | evrak | ev-rak | broad northern homeland | Invented sound form and sense |
| Tundra / Frozen Mountains | ornek | or-nek | river approach district; extended orn | Invented sound form and sense |
| Volcanic Mountains / Ruins | luma | lu-ma | slope district | Invented sound form and sense |
| Volcanic Mountains / Ruins | hena | he-na | valley hinterland | Invented sound form and sense |
| Volcanic Mountains / Ruins | raya | ra-ya | linked ridges | Invented sound form and sense |
| Volcanic Mountains / Ruins | malo | ma-lo | connected rebuilding lands | Invented sound form and sense |
| Volcanic Mountains / Ruins | naya | na-ya | shared land | New Hawaiian land-word inspiration [TN1] |
| Temperate Mountains | evan | e-van | upland district | Invented sound form and sense |
| Temperate Mountains | olma | ol-ma | valley catchment | Invented sound form and sense |
| Temperate Mountains | arun | a-run | connected passes | Invented sound form and sense |
| Temperate Mountains | emra | em-ra | ridge-and-valley region | Invented sound form and sense |
| Temperate Mountains | suren | su-ren | broad mountain region | New Quechua region-word inspiration [TN2] |
| Desert | eshal | e-shal | local water-sharing ground | Invented sound form and sense |
| Desert | adren | a-dren | basin hinterland | Invented sound form and sense |
| Desert | eshar | e-shar | linked sheltered basins | Invented sound form and sense |
| Desert | uraven | u-ra-ven | connected dry-country routes | Invented sound form and sense |
| Desert | uzara | u-za-ra | shared desert homeland | Invented sound form and sense |
| Desert | veshal | ve-shal | local water-sharing ground; extended eshal | Invented sound form and sense |
| Grassland | ance | an-ce | open-country district | Invented sound form and sense |
| Grassland | erre | er-re | grazing hinterland | Invented sound form and sense |
| Grassland | ardel | ar-del | linked field districts | Invented sound form and sense |
| Grassland | evrie | ev-ri-e | wide route country | Invented sound form and sense |
| Grassland | parain | pa-rain | shared open homeland | New French country/region-word inspiration [TN4] |
| Evergreen Temperate Rainforest | eshan | e-shan | local wooded drainage | Invented sound form and sense |
| Evergreen Temperate Rainforest | ulth | ulth | forest hinterland | Invented sound form and sense |
| Evergreen Temperate Rainforest | awen | a-wen | linked watersheds | Invented sound form and sense |
| Evergreen Temperate Rainforest | enwel | en-wel | connected forest routes | Invented sound form and sense |
| Evergreen Temperate Rainforest | athen | a-then | shared rain-country homeland | Invented sound form and sense |
| Swamp | avon | a-von | local channel district | Invented sound form and sense |
| Swamp | esse | es-se | reed-margin hinterland | Invented sound form and sense |
| Swamp | oranne | o-ran-ne | connected wetland basins | Invented sound form and sense |
| Swamp | elau | e-lau | linked navigable channels | Invented sound form and sense |
| Swamp | aurel | au-rel | shared wetland homeland | Invented sound form and sense |
| Deciduous Forest | ethen | e-then | local woodland district | Invented sound form and sense |
| Deciduous Forest | ervan | er-van | field-and-wood hinterland | Invented sound form and sense |
| Deciduous Forest | ornel | or-nel | connected woodland districts | Invented sound form and sense |
| Deciduous Forest | aveth | a-veth | linked river woods | Invented sound form and sense |
| Deciduous Forest | terne | ter-ne | shared woodland country | New Irish land-word inspiration [TN3] |
| Tropical Rainforest | mela | me-la | local forest drainage | Invented sound form and sense |
| Tropical Rainforest | dali | da-li | waterside hinterland | Invented sound form and sense |
| Tropical Rainforest | ngara | nga-ra | linked forest waterways | Invented sound form and sense |
| Tropical Rainforest | mbali | mba-li | connected canopy country | Invented sound form and sense |
| Tropical Rainforest | ndara | nda-ra | shared forest homeland | Invented sound form and sense |

### Kingdom register

The root column refers to the existing biome ledger. Capital names are already
in the game; the new territory names are separate proposals.

| Existing kingdom | Biome | Proposed kingdom name | Construction | Pronunciation | Existing capital | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `Kingdom1` | Tundra / Frozen Mountains | Nuksirevrak | nuksir + evrak | NUK-sir-ev-rak | Nufelask (`Kingdom1Capital`) | firm ground under snow; broad northern homeland |
| `Kingdom2` | Volcanic Mountains / Ruins | Apohunaya | apohu + naya | a-po-HU-na-ya | Lehamarava (`Kingdom2Capital`) | fire-marked stone; shared land |
| `Kingdom3` | Temperate Mountains | Rikumetsuren | rikumet + suren | RI-ku-met-su-ren | Urkelamad (`Kingdom3Capital`) | interlocking ridges; broad mountain region |
| `Kingdom4` | Desert | Amaruzara | amar + uzara | a-mar-u-ZA-ra | Amaravel (`Kingdom4Capital`) | stored/shared water; shared desert homeland |
| `Kingdom5` | Grassland | Velmorparain | velmor + parain | VEL-mor-pa-rain | Veldalain (`Kingdom5Capital`) | tilled fields / horse routes; shared open homeland |
| `Kingdom6` | Evergreen Temperate Rainforest | Sekwanathen | sekwan + athen | se-kwan-a-THEN | Pashenelth (`Kingdom6Capital`) | collected rainfall; shared rain-country homeland |
| `Kingdom7` | Swamp | Juwacelaurel | juwacel + aurel | ju-wa-cel-AU-rel | Qasirelenne (`Kingdom7Capital`) | dense reed margins; shared wetland homeland |
| `Kingdom8` | Deciduous Forest | Colnerterne | colner + terne | COL-ner-ter-ne | Darontavel (`Kingdom8Capital`) | hazel / fallen leaves; shared woodland country |
| `Kingdom9` | Tropical Rainforest | Zarepandara | zarepa + ndara | za-RE-pa-nda-ra | Mirumbunalo (`Kingdom9Capital`) | deep wooded country; shared forest homeland |

### Tundra / Frozen Mountains: Nuksirevrak

Parent kingdom: `Kingdom1`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy01` | Tuprelavren | tuprel + avren | TUP-rel-a-vren | Syratnuk (`Duchy01Capital`) | shelter below a ridge; connected winter routes |
| `Duchy02` | Birsneleldun | birsnel + eldun | BIR-snel-el-dun | Felyrom (`Duchy02Capital`) | snow-fed river; linked upland basins |
| `Duchy03` | Birnunavren | birnun + avren | BIR-nun-a-vren | Nufelask (`Kingdom1Capital`) | ground beside a river; connected winter routes |
| `Duchy04` | Feltupeldun | feltup + eldun | FEL-tup-el-dun | Tuprelust (`Duchy04Capital`) | upland shelter; linked upland basins |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County001` | Sirumesh | Tuprelavren (`Duchy01`) | sirum + esh | SI-rum-esh | Syratnuk (`Duchy01Capital`) | water drawn from snow; local snow-country district |
| `County002` | Syratornek | Tuprelavren (`Duchy01`) | syrat + ornek | SI-rat-or-nek | Birsnelal (`County002Capital`) | winter stopping-ground; river approach district; extended orn |
| `County003` | Birsnelesh | Tuprelavren (`Duchy01`) | birsnel + esh | BIR-snel-esh | Birnunir (`County003Capital`) | snow-fed river; local snow-country district |
| `County004` | Tanfelorn | Tuprelavren (`Duchy01`) | tanfel + orn | TAN-fel-orn | Feltupask (`County004Capital`) | mountain footing; river approach district |
| `County005` | Imnelesh | Tuprelavren (`Duchy01`) | imnel + esh | IM-nel-esh | Tanfelim (`County005Capital`) | snow on the heights; local snow-country district |
| `County006` | Sytanorn | Tuprelavren (`Duchy01`) | sytan + orn | SI-tan-orn | Tanbirom (`County006Capital`) | ground used in the snow season; river approach district |
| `County007` | Nufelesh | Birsneleldun (`Duchy02`) | nufel + esh | NU-fel-esh | Felyrom (`Duchy02Capital`) | upland ground; local snow-country district |
| `County008` | Tuprelorn | Birsneleldun (`Duchy02`) | tuprel + orn | TUP-rel-orn | Nuksirust (`County008Capital`) | shelter below a ridge; river approach district |
| `County009` | Feltupesh | Birsneleldun (`Duchy02`) | feltup + esh | FEL-tup-esh | Imnelal (`County009Capital`) | upland shelter; local snow-country district |
| `County010` | Nuksirorn | Birsneleldun (`Duchy02`) | nuksir + orn | NUK-sir-orn | Tansyrir (`County010Capital`) | firm ground under snow; river approach district |
| `County011` | Snetanesh | Birsneleldun (`Duchy02`) | snetan + esh | SNE-tan-esh | Snetanask (`County011Capital`) | snow-covered ground; local snow-country district |
| `County012` | Nurimorn | Birsneleldun (`Duchy02`) | nurim + orn | NU-rim-orn | Sytanek (`County012Capital`) | snow-covered open country; river approach district |
| `County013` | Felyresh | Birnunavren (`Duchy03`) | felyr + esh | FEL-ir-esh | Nufelask (`Kingdom1Capital`) | winter ridge; local snow-country district |
| `County014` | Birnunorn | Birnunavren (`Duchy03`) | birnun + orn | BIR-nun-orn | Sirumom (`County014Capital`) | ground beside a river; river approach district |
| `County015` | Tanbiresh | Birnunavren (`Duchy03`) | tanbir + esh | TAN-bir-esh | Nurimust (`County015Capital`) | river approach; local snow-country district |
| `County016` | Tansyrorn | Birnunavren (`Duchy03`) | tansyr + orn | TAN-sir-orn | Nufelir (`County016Capital`) | seasonal return-ground; river approach district |
| `County017` | Sirumorn | Birnunavren (`Duchy03`) | sirum + orn | SI-rum-orn | Syratask (`County017Capital`) | water drawn from snow; river approach district |
| `County018` | Syratesh | Birnunavren (`Duchy03`) | syrat + esh | SI-rat-esh | Felyrek (`County018Capital`) | winter stopping-ground; local snow-country district |
| `County019` | Birsnelorn | Feltupeldun (`Duchy04`) | birsnel + orn | BIR-snel-orn | Tuprelust (`Duchy04Capital`) | snow-fed river; river approach district |
| `County020` | Tanfelesh | Feltupeldun (`Duchy04`) | tanfel + esh | TAN-fel-esh | Tuprelom (`County020Capital`) | mountain footing; local snow-country district |
| `County021` | Imnelorn | Feltupeldun (`Duchy04`) | imnel + orn | IM-nel-orn | Birsnelust (`County021Capital`) | snow on the heights; river approach district |
| `County022` | Sytanesh | Feltupeldun (`Duchy04`) | sytan + esh | SI-tan-esh | Birnunal (`County022Capital`) | ground used in the snow season; local snow-country district |
| `County023` | Nufelorn | Feltupeldun (`Duchy04`) | nufel + orn | NU-fel-orn | Feltupir (`County023Capital`) | upland ground; river approach district |
| `County024` | Tuprelesh | Feltupeldun (`Duchy04`) | tuprel + esh | TUP-rel-esh | Tanfelask (`County024Capital`) | shelter below a ridge; local snow-country district |

### Volcanic Mountains / Ruins: Apohunaya

Parent kingdom: `Kingdom2`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy05` | Tanahuraya | tanahu + raya | ta-na-HU-ra-ya | Abulenelo (`Duchy05Capital`) | ash-settled valley; linked ridges |
| `Duchy06` | Hutalemalo | hutale + malo | hu-ta-LE-ma-lo | Lehamarava (`Kingdom2Capital`) | settled ash soil; connected rebuilding lands |
| `Duchy07` | Yamaburaya | yamabu + raya | ya-ma-BU-ra-ya | Kawelumeka (`Duchy07Capital`) | ash mountain; linked ridges |
| `Duchy08` | Ulayamalo | ulaya + malo | u-la-YA-ma-lo | Tabuyasulo (`Duchy08Capital`) | regrowth on the heights; connected rebuilding lands |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County025` | Ulayaluma | Tanahuraya (`Duchy05`) | ulaya + luma | u-la-YA-lu-ma | Abulenelo (`Duchy05Capital`) | regrowth on the heights; slope district |
| `County026` | Abulehena | Tanahuraya (`Duchy05`) | abule + hena | a-bu-LE-he-na | Yamolukera (`County026Capital`) | deep ash ground; valley hinterland |
| `County027` | Hutaleluma | Tanahuraya (`Duchy05`) | hutale + luma | hu-ta-LE-lu-ma | Poyamavani (`County027Capital`) | settled ash soil; slope district |
| `County028` | Tanapihena | Tanahuraya (`Duchy05`) | tanapi + hena | ta-na-PI-he-na | Kawaburemu (`County028Capital`) | fire-marked valley; valley hinterland |
| `County029` | Hulumaluma | Tanahuraya (`Duchy05`) | huluma + luma | hu-lu-MA-lu-ma | Pohanirava (`County029Capital`) | new growth on an ash slope; slope district |
| `County030` | Bateluhena | Tanahuraya (`Duchy05`) | batelu + hena | ba-te-LU-he-na | Pokawanelo (`County030Capital`) | stone amid ash; valley hinterland |
| `County031` | Pokawaluma | Hutalemalo (`Duchy06`) | pokawa + luma | po-ka-WA-lu-ma | Lehamarava (`Kingdom2Capital`) | river-cut stone; slope district |
| `County032` | Ulapihena | Hutalemalo (`Duchy06`) | ulapi + hena | u-la-PI-he-na | Yatanumeka (`County032Capital`) | regrowth after burning; valley hinterland |
| `County033` | Kawabuluma | Hutalemalo (`Duchy06`) | kawabu + luma | ka-wa-BU-lu-ma | Hulumasulo (`County033Capital`) | riverborne ash; slope district |
| `County034` | Pobumihena | Hutalemalo (`Duchy06`) | pobumi + hena | po-bu-MI-he-na | Tanahukera (`County034Capital`) | stone emerging from ash; valley hinterland |
| `County035` | Yamoluluma | Hutalemalo (`Duchy06`) | yamolu + luma | ya-mo-LU-lu-ma | Hutalevani (`County035Capital`) | renewed mountain ground; slope district |
| `County036` | Tanuluhena | Hutalemalo (`Duchy06`) | tanulu + hena | ta-nu-LU-he-na | Yamaburemu (`County036Capital`) | cultivated soil; valley hinterland |
| `County037` | Kaweluluma | Yamaburaya (`Duchy07`) | kawelu + luma | ka-we-LU-lu-ma | Kawelumeka (`Duchy07Capital`) | river through ash ground; slope district |
| `County038` | Yamabuhena | Yamaburaya (`Duchy07`) | yamabu + hena | ya-ma-BU-he-na | Ulayarava (`County038Capital`) | ash mountain; valley hinterland |
| `County039` | Lehamaluma | Yamaburaya (`Duchy07`) | lehama + luma | le-ha-MA-lu-ma | Tanulunelo (`County039Capital`) | ash-covered heights; slope district |
| `County040` | Tanahuhena | Yamaburaya (`Duchy07`) | tanahu + hena | ta-na-HU-he-na | Batanimeka (`County040Capital`) | ash-settled valley; valley hinterland |
| `County041` | Lebatuluma | Yamaburaya (`Duchy07`) | lebatu + luma | le-ba-TU-lu-ma | Pobumisulo (`County041Capital`) | ash over old masonry; slope district |
| `County042` | Yatanuhena | Yamaburaya (`Duchy07`) | yatanu + hena | ya-ta-NU-he-na | Apohukera (`County042Capital`) | mountain soil; valley hinterland |
| `County043` | Kabatuluma | Ulayamalo (`Duchy08`) | kabatu + luma | ka-ba-TU-lu-ma | Tabuyasulo (`Duchy08Capital`) | river stones; slope district |
| `County044` | Pohanihena | Ulayamalo (`Duchy08`) | pohani + hena | po-ha-NI-he-na | Ulapivani (`County044Capital`) | stone-sided valley; valley hinterland |
| `County045` | Apohuluma | Ulayamalo (`Duchy08`) | apohu + luma | a-po-HU-lu-ma | Kabaturemu (`County045Capital`) | fire-marked stone; slope district |
| `County046` | Poyamahena | Ulayamalo (`Duchy08`) | poyama + hena | po-ya-MA-he-na | Batelurava (`County046Capital`) | rocky heights; valley hinterland |
| `County047` | Bataniluma | Ulayamalo (`Duchy08`) | batani + luma | ba-ta-NI-lu-ma | Lebatunelo (`County047Capital`) | stone valley; slope district |
| `County048` | Tabuyahena | Ulayamalo (`Duchy08`) | tabuya + hena | ta-bu-YA-he-na | Tanapimeka (`County048Capital`) | ash valley between heights; valley hinterland |

### Temperate Mountains: Rikumetsuren

Parent kingdom: `Kingdom3`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy09` | Serumayarun | serumay + arun | SE-ru-may-a-run | Rumistalek (`Duchy09Capital`) | provisions carried along a river; connected passes |
| `Duchy10` | Ritupelemra | ritupel + emra | RI-tu-pel-em-ra | Mayucherurna (`Duchy10Capital`) | sheltering outcrops; ridge-and-valley region |
| `Duchy11` | Tulamurarun | tulamur + arun | TU-la-mur-a-run | Urkelamad (`Kingdom3Capital`) | a path between rocks; connected passes |
| `Duchy12` | Mayucheremra | mayucher + emra | MA-yu-cher-em-ra | Laturmietal (`Duchy12Capital`) | river-worn stone; ridge-and-valley region |
| `Duchy13` | Miseruqarun | miseruq + arun | MI-se-ruq-a-run | Tuperiom (`Duchy13Capital`) | provisions carried into the heights; connected passes |
| `Duchy14` | Pwerumiemra | pwerumi + emra | PWE-ru-mi-em-ra | Serumayard (`Duchy14Capital`) | stones fitted together; ridge-and-valley region |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County049` | Mayucherevan | Serumayarun (`Duchy09`) | mayucher + evan | MA-yu-cher-e-van | Rumistalek (`Duchy09Capital`) | river-worn stone; upland district |
| `County050` | Lamutakolma | Serumayarun (`Duchy09`) | lamutak + olma | LA-mu-tak-ol-ma | Rikumetevi (`County050Capital`) | a route across a mountain shoulder; valley catchment |
| `County051` | Ritupelevan | Serumayarun (`Duchy09`) | ritupel + evan | RI-tu-pel-e-van | Lamutakosk (`County051Capital`) | sheltering outcrops; upland district |
| `County052` | Urmitakolma | Serumayarun (`Duchy09`) | urmitak + olma | UR-mi-tak-ol-ma | Urwetsaira (`County052Capital`) | heights overlooking lower slopes; valley catchment |
| `County053` | Urqaseevan | Ritupelemra (`Duchy10`) | urqase + evan | UR-qa-se-e-van | Mayucherurna (`Duchy10Capital`) | a place to gather upland provisions; upland district |
| `County054` | Laturmiolma | Ritupelemra (`Duchy10`) | laturmi + olma | LA-tur-mi-ol-ma | Miseruqust (`County054Capital`) | stone-laid paths; valley catchment |
| `County055` | Urwetsaevan | Ritupelemra (`Duchy10`) | urwetsa + evan | UR-wet-sa-e-van | Rumilamalen (`County055Capital`) | stony upland ground; upland district |
| `County056` | Serurqaolma | Ritupelemra (`Duchy10`) | serurqa + olma | SE-rur-qa-ol-ma | Mayutalad (`County056Capital`) | supplies stored above the valley; valley catchment |
| `County057` | Riyumaevan | Tulamurarun (`Duchy11`) | riyuma + evan | RI-yu-ma-e-van | Urkelamad (`Kingdom3Capital`) | river-fed mountain country; upland district |
| `County058` | Rumetakolma | Tulamurarun (`Duchy11`) | rumetak + olma | RU-me-tak-ol-ma | Ritupelek (`County058Capital`) | exposed stone above the valley; valley catchment |
| `County059` | Tuperievan | Tulamurarun (`Duchy11`) | tuperi + evan | TU-pe-ri-e-van | Serurqaurna (`County059Capital`) | rocky high ground; upland district |
| `County060` | Miseruqolma | Tulamurarun (`Duchy11`) | miseruq + olma | MI-se-ruq-ol-ma | Takurmietal (`County060Capital`) | provisions carried into the heights; valley catchment |
| `County061` | Takurmievan | Mayucheremra (`Duchy12`) | takurmi + evan | TA-kur-mi-e-van | Laturmietal (`Duchy12Capital`) | broken stone on a slope; upland district |
| `County062` | Tulamurolma | Mayucheremra (`Duchy12`) | tulamur + olma | TU-la-mur-ol-ma | Lamuyekom (`County062Capital`) | a path between rocks; valley catchment |
| `County063` | Urkelamevan | Mayucheremra (`Duchy12`) | urkelam + evan | UR-ke-lam-e-van | Pwerumiard (`County063Capital`) | paths across the heights; upland district |
| `County064` | Serumayolma | Mayucheremra (`Duchy12`) | serumay + olma | SE-ru-may-ol-ma | Urmitakevi (`County064Capital`) | provisions carried along a river; valley catchment |
| `County065` | Rumilamevan | Miseruqarun (`Duchy13`) | rumilam + evan | RU-mi-lam-e-van | Tuperiom (`Duchy13Capital`) | a dependable stone path; upland district |
| `County066` | Lamuyekolma | Miseruqarun (`Duchy13`) | lamuyek + olma | LA-mu-yek-ol-ma | Riyumaosk (`County066Capital`) | a path following the river; valley catchment |
| `County067` | Mayuserevan | Miseruqarun (`Duchy13`) | mayuser + evan | MA-yu-ser-e-van | Tulamurira (`County067Capital`) | goods carried between riverside homes; upland district |
| `County068` | Rumistalolma | Miseruqarun (`Duchy13`) | rumistal + olma | RU-mi-stal-ol-ma | Mayuserust (`County068Capital`) | stone mountain shoulders; valley catchment |
| `County069` | Rikumetevan | Pwerumiemra (`Duchy14`) | rikumet + evan | RI-ku-met-e-van | Serumayard (`Duchy14Capital`) | interlocking ridges; upland district |
| `County070` | Mayutalolma | Pwerumiemra (`Duchy14`) | mayutal + olma | MA-yu-tal-ol-ma | Stakerialen (`County070Capital`) | river below a ridge; valley catchment |
| `County071` | Pwerumievan | Pwerumiemra (`Duchy14`) | pwerumi + evan | PWE-ru-mi-e-van | Urqasead (`County071Capital`) | stones fitted together; upland district |
| `County072` | Stakeriolma | Pwerumiemra (`Duchy14`) | stakeri + olma | STA-ke-ri-ol-ma | Rumetakek (`County072Capital`) | successive mountain shoulders; valley catchment |

### Desert: Amaruzara

Parent kingdom: `Kingdom4`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy15` | Tumareshar | tumar + eshar | tu-mar-E-shar | Arukesh (`Duchy15Capital`) | dependable well; linked sheltered basins |
| `Duchy16` | Amaruraven | amar + uraven | a-mar-u-RA-ven | Sazelor (`Duchy16Capital`) | stored/shared water; connected dry-country routes |
| `Duchy17` | Pazekeshar | pazek + eshar | pa-zek-E-shar | Amaravel (`Kingdom4Capital`) | stone-edged cultivated ground; linked sheltered basins |
| `Duchy18` | Arukuraven | aruk + uraven | a-ruk-u-RA-ven | Kisarvek (`Duchy18Capital`) | ridge runoff; connected dry-country routes |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County073` | Arukeshal | Tumareshar (`Duchy15`) | aruk + eshal | a-ruk-E-shal | Arukesh (`Duchy15Capital`) | ridge runoff; local water-sharing ground |
| `County074` | Pazekadren | Tumareshar (`Duchy15`) | pazek + adren | pa-zek-A-dren | Kiraivesh (`County074Capital`) | stone-edged cultivated ground; basin hinterland |
| `County075` | Amarveshal | Tumareshar (`Duchy15`) | amar + veshal | a-mar-VE-shal | Zoruvel (`County075Capital`) | stored/shared water; local water-sharing ground |
| `County076` | Tumaradren | Tumareshar (`Duchy15`) | tumar + adren | tu-mar-A-dren | Sazelen (`County076Capital`) | dependable well; basin hinterland |
| `County077` | Kisareshal | Tumareshar (`Duchy15`) | kisar + eshal | ki-sar-E-shal | Soruvek (`County077Capital`) | dry-season shelter; local water-sharing ground |
| `County078` | Soruvadren | Tumareshar (`Duchy15`) | soru + v + adren | so-ru-VA-dren | Raituvesh (`County078Capital`) | seasonal rainwater; basin hinterland |
| `County079` | Kiraiveshal | Amaruraven (`Duchy16`) | kirai + v + eshal | ki-rai-VE-shal | Sazelor (`Duchy16Capital`) | dwellings among sand; local water-sharing ground |
| `County080` | Azekadren | Amaruraven (`Duchy16`) | azek + adren | a-zek-A-dren | Kisaror (`County080Capital`) | water held in stone; basin hinterland |
| `County081` | Tusereshal | Amaruraven (`Duchy16`) | tuser + eshal | tu-ser-E-shal | Tumarvek (`County081Capital`) | water kept after the rains; local water-sharing ground |
| `County082` | Zoruvadren | Amaruraven (`Duchy16`) | zoru + v + adren | zo-ru-VA-dren | Kiraiven (`County082Capital`) | water running across rock; basin hinterland |
| `County083` | Sazeleshal | Amaruraven (`Duchy16`) | sazel + eshal | sa-zel-E-shal | Pazekor (`County083Capital`) | dry stone ground; local water-sharing ground |
| `County084` | Raituvadren | Amaruraven (`Duchy16`) | raitu + v + adren | rai-tu-VA-dren | Tuseren (`County084Capital`) | water beneath sand; basin hinterland |
| `County085` | Arukadren | Pazekeshar (`Duchy17`) | aruk + adren | a-ruk-A-dren | Amaravel (`Kingdom4Capital`) | ridge runoff; basin hinterland |
| `County086` | Pazekeshal | Pazekeshar (`Duchy17`) | pazek + eshal | pa-zek-E-shal | Azekavel (`County086Capital`) | stone-edged cultivated ground; local water-sharing ground |
| `County087` | Amaradren | Pazekeshar (`Duchy17`) | amar + adren | a-mar-A-dren | Zoruvesh (`County087Capital`) | stored/shared water; basin hinterland |
| `County088` | Tumareshal | Pazekeshar (`Duchy17`) | tumar + eshal | tu-mar-E-shal | Sazelavel (`County088Capital`) | dependable well; local water-sharing ground |
| `County089` | Kisaradren | Pazekeshar (`Duchy17`) | kisar + adren | ki-sar-A-dren | Amarkiven (`County089Capital`) | dry-season shelter; basin hinterland |
| `County090` | Soruveshal | Pazekeshar (`Duchy17`) | soru + v + eshal | so-ru-VE-shal | Pazekavel (`County090Capital`) | seasonal rainwater; local water-sharing ground |
| `County091` | Kiraivadren | Arukuraven (`Duchy18`) | kirai + v + adren | ki-rai-VA-dren | Kisarvek (`Duchy18Capital`) | dwellings among sand; basin hinterland |
| `County092` | Azekeshal | Arukuraven (`Duchy18`) | azek + eshal | a-zek-E-shal | Tumaror (`County092Capital`) | water held in stone; local water-sharing ground |
| `County093` | Tuseradren | Arukuraven (`Duchy18`) | tuser + adren | tu-ser-A-dren | Kisaravel (`County093Capital`) | water kept after the rains; basin hinterland |
| `County094` | Zoruveshal | Arukuraven (`Duchy18`) | zoru + v + eshal | zo-ru-VE-shal | Raituvek (`County094Capital`) | water running across rock; local water-sharing ground |
| `County095` | Sazeladren | Arukuraven (`Duchy18`) | sazel + adren | sa-zel-A-dren | Tuseresh (`County095Capital`) | dry stone ground; basin hinterland |
| `County096` | Raituveshal | Arukuraven (`Duchy18`) | raitu + v + eshal | rai-tu-VE-shal | Arukor (`County096Capital`) | water beneath sand; local water-sharing ground |

### Grassland: Velmorparain

Parent kingdom: `Kingdom5`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy19` | Velmorardel | velmor + ardel | VEL-mor-ar-del | Veldalain (`Kingdom5Capital`) | tilled fields / horse routes; linked field districts |
| `Duchy20` | Westavevrie | westav + evrie | WES-tav-ev-ri-e | Wesfeyaldre (`Duchy20Capital`) | hay meadows / level grassland; wide route country |
| `Duchy21` | Perzelardel | perzel + ardel | PER-zel-ar-del | Ventavelle (`Duchy21Capital`) | grazing commons / moving air; linked field districts |
| `Duchy22` | Valdrenevrie | valdren + evrie | VAL-dren-ev-ri-e | Wesnimeran (`Duchy22Capital`) | open winds / open steppe; wide route country |
| `Duchy23` | Velnimardel | velnim + ardel | VEL-nim-ar-del | Pershanarve (`Duchy23Capital`) | tilled fields / watering places; linked field districts |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County097` | Veldalance | Velmorardel (`Duchy19`) | veldal + ance | VEL-dal-an-ce | Veldalain (`Kingdom5Capital`) | tilled fields / open steppe; open-country district |
| `County098` | Velfeyerre | Velmorardel (`Duchy19`) | velfey + erre | VEL-fey-er-re | Velzelerel (`County098Capital`) | tilled fields / tended herds; grazing hinterland |
| `County099` | Westavance | Velmorardel (`Duchy19`) | westav + ance | WES-tav-an-ce | Perblenesse (`County099Capital`) | hay meadows / level grassland; open-country district |
| `County100` | Pernimerre | Velmorardel (`Duchy19`) | pernim + erre | PER-nim-er-re | Venmororent (`County100Capital`) | grazing commons / watering places; grazing hinterland |
| `County101` | Pershanance | Velmorardel (`Duchy19`) | pershan + ance | PER-shan-an-ce | Wesdalovre (`County101Capital`) | grazing commons / fresh grass; open-country district |
| `County102` | Venzelerre | Westavevrie (`Duchy20`) | venzel + erre | VEN-zel-er-re | Wesfeyaldre (`Duchy20Capital`) | open winds / moving air; grazing hinterland |
| `County103` | Velblenance | Westavevrie (`Duchy20`) | velblen + ance | VEL-blen-an-ce | Perfeyevel (`County103Capital`) | tilled fields / wide plains; open-country district |
| `County104` | Velmorerre | Westavevrie (`Duchy20`) | velmor + erre | VEL-mor-er-re | Veltavastel (`County104Capital`) | tilled fields / horse routes; grazing hinterland |
| `County105` | Wesdalance | Westavevrie (`Duchy20`) | wesdal + ance | WES-dal-an-ce | Pernimevir (`County105Capital`) | hay meadows / open steppe; open-country district |
| `County106` | Wesfeyerre | Westavevrie (`Duchy20`) | wesfey + erre | WES-fey-er-re | Venshanain (`County106Capital`) | hay meadows / tended herds; grazing hinterland |
| `County107` | Pertavance | Perzelardel (`Duchy21`) | pertav + ance | PER-tav-an-ce | Ventavelle (`Duchy21Capital`) | grazing commons / level grassland; open-country district |
| `County108` | Vennimerre | Perzelardel (`Duchy21`) | vennim + erre | VEN-nim-er-re | Weszelaldre (`County108Capital`) | open winds / watering places; grazing hinterland |
| `County109` | Venshanance | Perzelardel (`Duchy21`) | venshan + ance | VEN-shan-an-ce | Venblenelle (`County109Capital`) | open winds / fresh grass; open-country district |
| `County110` | Velzelerre | Perzelardel (`Duchy21`) | velzel + erre | VEL-zel-er-re | Velmoreran (`County110Capital`) | tilled fields / moving air; grazing hinterland |
| `County111` | Wesblenance | Perzelardel (`Duchy21`) | wesblen + ance | WES-blen-an-ce | Perdalarve (`County111Capital`) | hay meadows / wide plains; open-country district |
| `County112` | Wesmorerre | Valdrenevrie (`Duchy22`) | wesmor + erre | WES-mor-er-re | Wesnimeran (`Duchy22Capital`) | hay meadows / horse routes; grazing hinterland |
| `County113` | Perdalance | Valdrenevrie (`Duchy22`) | perdal + ance | PER-dal-an-ce | Venfeyerel (`County113Capital`) | grazing commons / open steppe; open-country district |
| `County114` | Perfeyerre | Valdrenevrie (`Duchy22`) | perfey + erre | PER-fey-er-re | Westavesse (`County114Capital`) | grazing commons / tended herds; grazing hinterland |
| `County115` | Ventavance | Valdrenevrie (`Duchy22`) | ventav + ance | VEN-tav-an-ce | Vennimorent (`County115Capital`) | open winds / level grassland; open-country district |
| `County116` | Velnimerre | Valdrenevrie (`Duchy22`) | velnim + erre | VEL-nim-er-re | Velshanovre (`County116Capital`) | tilled fields / watering places; grazing hinterland |
| `County117` | Velshanance | Velnimardel (`Duchy23`) | velshan + ance | VEL-shan-an-ce | Pershanarve (`Duchy23Capital`) | tilled fields / fresh grass; open-country district |
| `County118` | Weszelerre | Velnimardel (`Duchy23`) | weszel + erre | WES-zel-er-re | Perzelevel (`County118Capital`) | hay meadows / moving air; grazing hinterland |
| `County119` | Perblenance | Velnimardel (`Duchy23`) | perblen + ance | PER-blen-an-ce | Velblenastel (`County119Capital`) | grazing commons / wide plains; open-country district |
| `County120` | Permorerre | Velnimardel (`Duchy23`) | permor + erre | PER-mor-er-re | Wesmorevir (`County120Capital`) | grazing commons / horse routes; grazing hinterland |
| `County121` | Valdrenance | Velnimardel (`Duchy23`) | valdren + ance | VAL-dren-an-ce | Valdrenain (`County121Capital`) | open winds / open steppe; open-country district |

### Evergreen Temperate Rainforest: Sekwanathen

Parent kingdom: `Kingdom6`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy24` | Tiphenawen | tiphen + awen | tip-hen-a-WEN | Pashenelth (`Kingdom6Capital`) | green riverbank; linked watersheds |
| `Duchy25` | Kwasenenwel | kwasen + enwel | kwa-sen-en-WEL | Sehpaiowan (`Duchy25Capital`) | water beneath trees; connected forest routes |
| `Duchy26` | Hepayawen | hepay + awen | he-pay-a-WEN | Sekwanesh (`Duchy26Capital`) | cedar beside a channel; linked watersheds |
| `Duchy27` | Asnipenwel | asnip + enwel | as-nip-en-WEL | Asanilavel (`Duchy27Capital`) | leafy woodland; connected forest routes |
| `Duchy28` | Asnawawen | asnaw + awen | as-naw-a-WEN | Paynasun (`Duchy28Capital`) | rain-dark canopy; linked watersheds |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County122` | Asnipeshan | Tiphenawen (`Duchy24`) | asnip + eshan | as-nip-e-SHAN | Pashenelth (`Kingdom6Capital`) | leafy woodland; local wooded drainage |
| `County123` | Sehpaiulth | Tiphenawen (`Duchy24`) | sehpai + ulth | seh-pai-ULTH | Pasileth (`County123Capital`) | rain beneath cedar; forest hinterland |
| `County124` | Kwaseneshan | Tiphenawen (`Duchy24`) | kwasen + eshan | kwa-sen-e-SHAN | Kwalisolan (`County124Capital`) | water beneath trees; local wooded drainage |
| `County125` | Naswenulth | Tiphenawen (`Duchy24`) | naswen + ulth | nas-wen-ULTH | Kwaselem (`County125Capital`) | rain through the trees; forest hinterland |
| `County126` | Paysineshan | Tiphenawen (`Duchy24`) | paysin + eshan | pay-sin-e-SHAN | Ilasenask (`County126Capital`) | cedar undergrowth; local wooded drainage |
| `County127` | Hesnalulth | Kwasenenwel (`Duchy25`) | hesnal + ulth | hes-nal-ULTH | Sehpaiowan (`Duchy25Capital`) | rain-swollen stream; forest hinterland |
| `County128` | Ilaseneshan | Kwasenenwel (`Duchy25`) | ilasen + eshan | i-la-sen-e-SHAN | Ilhenowen (`County128Capital`) | wooded earth; local wooded drainage |
| `County129` | Tipasulth | Kwasenenwel (`Duchy25`) | tipas + ulth | ti-pas-ULTH | Paysinelth (`County129Capital`) | leaf-covered woodland; forest hinterland |
| `County130` | Kwaliseshan | Kwasenenwel (`Duchy25`) | kwalis + eshan | kwa-lis-e-SHAN | Tiphenowan (`County130Capital`) | waterlogged earth; local wooded drainage |
| `County131` | Snakwuulth | Kwasenenwel (`Duchy25`) | snakwu + ulth | sna-kwu-ULTH | Kwasenesh (`County131Capital`) | water gathered after rain; forest hinterland |
| `County132` | Paynaseshan | Hepayawen (`Duchy26`) | paynas + eshan | pay-nas-e-SHAN | Sekwanesh (`Duchy26Capital`) | rain on cedar; local wooded drainage |
| `County133` | Asnawulth | Hepayawen (`Duchy26`) | asnaw + ulth | as-naw-ULTH | Hepayavel (`County133Capital`) | rain-dark canopy; forest hinterland |
| `County134` | Sekwaneshan | Hepayawen (`Duchy26`) | sekwan + eshan | se-kwan-e-SHAN | Asnipun (`County134Capital`) | collected rainfall; local wooded drainage |
| `County135` | Hepayulth | Hepayawen (`Duchy26`) | hepay + ulth | he-pay-ULTH | Asnaweth (`County135Capital`) | cedar beside a channel; forest hinterland |
| `County136` | Pasheneshan | Hepayawen (`Duchy26`) | pashen + eshan | pa-shen-e-SHAN | Pasewolan (`County136Capital`) | cedar-lined water; local wooded drainage |
| `County137` | Tiphenulth | Asnipenwel (`Duchy27`) | tiphen + ulth | tip-hen-ULTH | Asanilavel (`Duchy27Capital`) | green riverbank; forest hinterland |
| `County138` | Hentileshan | Asnipenwel (`Duchy27`) | hentil + eshan | hen-til-e-SHAN | Snakwuem (`County138Capital`) | leaves beside water; local wooded drainage |
| `County139` | Ilhenulth | Asnipenwel (`Duchy27`) | ilhen + ulth | il-hen-ULTH | Kwatilask (`County139Capital`) | ground beside a stream; forest hinterland |
| `County140` | Tisekeshan | Asnipenwel (`Duchy27`) | tisek + eshan | ti-sek-e-SHAN | Tipasowen (`County140Capital`) | rain-bright foliage; local wooded drainage |
| `County141` | Kwaselulth | Asnipenwel (`Duchy27`) | kwasel + ulth | kwa-sel-ULTH | Tisekelth (`County141Capital`) | rain-fed pools; forest hinterland |
| `County142` | Kwatileshan | Asnawawen (`Duchy28`) | kwatil + eshan | kwa-til-e-SHAN | Paynasun (`Duchy28Capital`) | wet undergrowth; local wooded drainage |
| `County143` | Pasilulth | Asnawawen (`Duchy28`) | pasil + ulth | pa-sil-ULTH | Hesnalowan (`County143Capital`) | cedar-rooted ground; forest hinterland |
| `County144` | Paseweshan | Asnawawen (`Duchy28`) | pasew + eshan | pa-sew-e-SHAN | Hentilesh (`County144Capital`) | wet cedar boughs; local wooded drainage |
| `County145` | Asanilulth | Asnawawen (`Duchy28`) | asanil + ulth | a-sa-nil-ULTH | Naswenavel (`County145Capital`) | deep woodland soil; forest hinterland |
| `County146` | Asnipulth | Asnawawen (`Duchy28`) | asnip + ulth | as-nip-ULTH | Pashenowan (`County146Capital`) | leafy woodland; forest hinterland |

### Swamp: Juwacelaurel

Parent kingdom: `Kingdom7`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy29` | Qasitinoranne | qasitin + oranne | qa-si-tin-o-RAN-ne | Qasirelenne (`Kingdom7Capital`) | moss above quiet water; connected wetland basins |
| `Duchy30` | Qaspagaelau | qaspaga + elau | qas-pa-ga-E-lau | Juwacelovel (`Duchy30Capital`) | a navigable shallow channel; linked navigable channels |
| `Duchy31` | Juwateloranne | juwatel + oranne | ju-wa-tel-o-RAN-ne | Acawishaume (`Duchy31Capital`) | flood-fed reeds; connected wetland basins |
| `Duchy32` | Acawishelau | acawish + elau | a-ca-wish-E-lau | Moharelossel (`Duchy32Capital`) | water between reeds; linked navigable channels |
| `Duchy33` | Jupareloranne | juparel + oranne | ju-pa-rel-o-RAN-ne | Paganieche (`Duchy33Capital`) | paddled paths through reeds; connected wetland basins |
| `Duchy34` | Qasanielau | qasani + elau | qa-sa-ni-E-lau | Qasitinulon (`Duchy34Capital`) | connected shallow pools; linked navigable channels |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County147` | Acawishavon | Qasitinoranne (`Duchy29`) | acawish + avon | a-ca-wish-A-von | Qasirelenne (`Kingdom7Capital`) | water between reeds; local channel district |
| `County148` | Anacelesse | Qasitinoranne (`Duchy29`) | anacel + esse | a-na-cel-ES-se | Shiwareliren (`County148Capital`) | reeds along a channel; reed-margin hinterland |
| `County149` | Qaspagaavon | Qasitinoranne (`Duchy29`) | qaspaga + avon | qas-pa-ga-A-von | Anaceloreth (`County149Capital`) | a navigable shallow channel; local channel district |
| `County150` | Shicayaesse | Qasitinoranne (`Duchy29`) | shicaya + esse | shi-ca-ya-ES-se | Siwashienne (`County150Capital`) | a passage opened through reeds; reed-margin hinterland |
| `County151` | Qacatelavon | Qaspagaelau (`Duchy30`) | qacatel + avon | qa-ca-tel-A-von | Juwacelovel (`Duchy30Capital`) | shallow water among canes; local channel district |
| `County152` | Moharelesse | Qaspagaelau (`Duchy30`) | moharel + esse | mo-ha-rel-ES-se | Juparelovel (`County152Capital`) | moss-hung swamp trees; reed-margin hinterland |
| `County153` | Siwashiavon | Qaspagaelau (`Duchy30`) | siwashi + avon | si-wa-shi-A-von | Atamohaume (`County153Capital`) | woodland pools; local channel district |
| `County154` | Acaprelesse | Qaspagaelau (`Duchy30`) | acaprel + esse | a-ca-prel-ES-se | Anijuossel (`County154Capital`) | reed edge beside swamp woods; reed-margin hinterland |
| `County155` | Aniprelavon | Juwateloranne (`Duchy31`) | aniprel + avon | a-ni-prel-A-von | Acawishaume (`Duchy31Capital`) | water in the swamp woods; local channel district |
| `County156` | Jushaniesse | Juwateloranne (`Duchy31`) | jushani + esse | ju-sha-ni-ES-se | Qaspagaeche (`County156Capital`) | reedy waterways meeting; reed-margin hinterland |
| `County157` | Paganiavon | Juwateloranne (`Duchy31`) | pagani + avon | pa-ga-ni-A-von | Acaprelulon (`County157Capital`) | water crossed by paddle; local channel district |
| `County158` | Juparelesse | Juwateloranne (`Duchy31`) | juparel + esse | ju-pa-rel-ES-se | Mohajuiren (`County158Capital`) | paddled paths through reeds; reed-margin hinterland |
| `County159` | Mohajuavon | Acawishelau (`Duchy32`) | mohaju + avon | mo-ha-ju-A-von | Moharelossel (`Duchy32Capital`) | reeds beneath hanging moss; local channel district |
| `County160` | Juwatelesse | Acawishelau (`Duchy32`) | juwatel + esse | ju-wa-tel-ES-se | Pagateloreth (`County160Capital`) | flood-fed reeds; reed-margin hinterland |
| `County161` | Qasirelavon | Acawishelau (`Duchy32`) | qasirel + avon | qa-si-rel-A-von | Qasanienne (`County161Capital`) | wooded shallow water; local channel district |
| `County162` | Qasitinesse | Acawishelau (`Duchy32`) | qasitin + esse | qa-si-tin-ES-se | Shicayaovel (`County162Capital`) | moss above quiet water; reed-margin hinterland |
| `County163` | Atamohavon | Jupareloranne (`Duchy33`) | atamoh + avon | a-ta-moh-A-von | Paganieche (`Duchy33Capital`) | moss-shaded water; local channel district |
| `County164` | Pagatelesse | Jupareloranne (`Duchy33`) | pagatel + esse | pa-ga-tel-ES-se | Aniprelaume (`County164Capital`) | a familiar paddling route; reed-margin hinterland |
| `County165` | Mohaniavon | Jupareloranne (`Duchy33`) | mohani + avon | mo-ha-ni-A-von | Juwatelossel (`County165Capital`) | moss over sheltered water; local channel district |
| `County166` | Juwacelesse | Qasanielau (`Duchy34`) | juwacel + esse | ju-wa-cel-ES-se | Qasitinulon (`Duchy34Capital`) | dense reed margins; reed-margin hinterland |
| `County167` | Shiwarelavon | Qasanielau (`Duchy34`) | shiwarel + avon | shi-wa-rel-A-von | Mohanieche (`County167Capital`) | reed channels below wooded banks; local channel district |
| `County168` | Anijuesse | Qasanielau (`Duchy34`) | aniju + esse | a-ni-ju-ES-se | Pagashiulon (`County168Capital`) | water at reed beds; reed-margin hinterland |
| `County169` | Qasaniavon | Qasanielau (`Duchy34`) | qasani + avon | qa-sa-ni-A-von | Qacateliren (`County169Capital`) | connected shallow pools; local channel district |
| `County220` | Pagashiesse | Jupareloranne (`Duchy33`) | pagashi + esse | pa-ga-shi-ES-se | Jushanioreth (`County220Capital`) | a crossing kept open; reed-margin hinterland |

### Deciduous Forest: Colnerterne

Parent kingdom: `Kingdom8`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy35` | Darionornel | darion + ornel | DAR-i-on-or-nel | Cranivesk (`Duchy35Capital`) | oak / woodland streams; connected woodland districts |
| `Duchy36` | Crannamaveth | crannam + aveth | CRAN-nam-a-veth | Gelsuverlan (`Duchy36Capital`) | timber / standing trees; linked river woods |
| `Duchy37` | Lassuvornel | lassuv + ornel | LAS-suv-or-nel | Darontavel (`Kingdom8Capital`) | woodland / deep shade; connected woodland districts |
| `Duchy38` | Gelivaveth | geliv + aveth | GEL-iv-a-veth | Darnameld (`Duchy38Capital`) | grove / new leaves; linked river woods |
| `Duchy39` | Dovrontornel | dovront + ornel | DOV-ront-or-nel | Colionovan (`Duchy39Capital`) | old oak / worked timber; connected woodland districts |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County170` | Darivethen | Darionornel (`Duchy35`) | dariv + ethen | DAR-iv-e-then | Cranivesk (`Duchy35Capital`) | oak / new leaves; local woodland district |
| `County171` | Colsuvervan | Darionornel (`Duchy35`) | colsuv + ervan | COL-suv-er-van | Lasnerund (`County171Capital`) | hazel / deep shade; field-and-wood hinterland |
| `County172` | Crannamethen | Darionornel (`Duchy35`) | crannam + ethen | CRAN-nam-e-then | Dovrontorin (`County172Capital`) | timber / standing trees; local woodland district |
| `County173` | Cranionervan | Darionornel (`Duchy35`) | cranion + ervan | CRAN-i-on-er-van | Coliverent (`County173Capital`) | timber / woodland streams; field-and-wood hinterland |
| `County174` | Lasnerethen | Darionornel (`Duchy35`) | lasner + ethen | LAS-ner-e-then | Lassuvalven (`County174Capital`) | woodland / fallen leaves; local woodland district |
| `County175` | Gelrontervan | Crannamaveth (`Duchy36`) | gelront + ervan | GEL-ront-er-van | Gelsuverlan (`Duchy36Capital`) | grove / worked timber; field-and-wood hinterland |
| `County176` | Dovivethen | Crannamaveth (`Duchy36`) | doviv + ethen | DOV-iv-e-then | Dovnamast (`County176Capital`) | old oak / new leaves; local woodland district |
| `County177` | Darsuvervan | Crannamaveth (`Duchy36`) | darsuv + ervan | DAR-suv-er-van | Darionavren (`County177Capital`) | oak / deep shade; field-and-wood hinterland |
| `County178` | Colnamethen | Crannamaveth (`Duchy36`) | colnam + ethen | COL-nam-e-then | Crannerern (`County178Capital`) | hazel / standing trees; local woodland district |
| `County179` | Colionervan | Crannamaveth (`Duchy36`) | colion + ervan | COL-i-on-er-van | Gelrontevren (`County179Capital`) | hazel / woodland streams; field-and-wood hinterland |
| `County180` | Crannerethen | Lassuvornel (`Duchy37`) | cranner + ethen | CRAN-ner-e-then | Darontavel (`Kingdom8Capital`) | timber / fallen leaves; local woodland district |
| `County181` | Lasrontervan | Lassuvornel (`Duchy37`) | lasront + ervan | LAS-ront-er-van | Darivord (`County181Capital`) | woodland / worked timber; field-and-wood hinterland |
| `County182` | Gelivethen | Lassuvornel (`Duchy37`) | geliv + ethen | GEL-iv-e-then | Cransuvevard (`County182Capital`) | grove / new leaves; local woodland district |
| `County183` | Dovsuvervan | Lassuvornel (`Duchy37`) | dovsuv + ervan | DOV-suv-er-van | Gelnamolt (`County183Capital`) | old oak / deep shade; field-and-wood hinterland |
| `County184` | Darnamethen | Lassuvornel (`Duchy37`) | darnam + ethen | DAR-nam-e-then | Dovionelvar (`County184Capital`) | oak / standing trees; local woodland district |
| `County185` | Darionervan | Gelivaveth (`Duchy38`) | darion + ervan | DAR-i-on-er-van | Darnameld (`Duchy38Capital`) | oak / woodland streams; field-and-wood hinterland |
| `County186` | Colnerethen | Gelivaveth (`Duchy38`) | colner + ethen | COL-ner-e-then | Colnerald (`County186Capital`) | hazel / fallen leaves; local woodland district |
| `County187` | Cranontervan | Gelivaveth (`Duchy38`) | cranont + ervan | CRAN-ont-er-van | Lasrontarden (`County187Capital`) | timber / worked timber; field-and-wood hinterland |
| `County188` | Lasivethen | Gelivaveth (`Duchy38`) | lasiv + ethen | LAS-iv-e-then | Dovivost (`County188Capital`) | woodland / new leaves; local woodland district |
| `County189` | Gelsuvervan | Gelivaveth (`Duchy38`) | gelsuv + ervan | GEL-suv-er-van | Colsuvavel (`County189Capital`) | grove / deep shade; field-and-wood hinterland |
| `County190` | Dovnamethen | Dovrontornel (`Duchy39`) | dovnam + ethen | DOV-nam-e-then | Colionovan (`Duchy39Capital`) | old oak / standing trees; local woodland district |
| `County191` | Dovionervan | Dovrontornel (`Duchy39`) | dovion + ervan | DOV-i-on-er-van | Lasnamesk (`County191Capital`) | old oak / woodland streams; field-and-wood hinterland |
| `County192` | Darnerethen | Dovrontornel (`Duchy39`) | darner + ethen | DAR-ner-e-then | Gelionerlan (`County192Capital`) | oak / fallen leaves; local woodland district |
| `County193` | Colrontervan | Dovrontornel (`Duchy39`) | colront + ervan | COL-ront-er-van | Darnereld (`County193Capital`) | hazel / worked timber; field-and-wood hinterland |
| `County194` | Cranivethen | Dovrontornel (`Duchy39`) | craniv + ethen | CRAN-iv-e-then | Cranontovan (`County194Capital`) | timber / new leaves; local woodland district |

### Tropical Rainforest: Zarepandara

Parent kingdom: `Kingdom9`. Root meanings, source mixtures, and reading rules
come from this biome's earlier ledger; the new ending senses appear above.

#### Duchies

| Existing duchy | Proposed name | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- |
| `Duchy40` | Repayungara | repayu + ngara | re-PA-yu-nga-ra | Mirumbunalo (`Kingdom9Capital`) | wood for shared construction; linked forest waterways |
| `Duchy41` | Mbukayambali | mbukaya + mbali | mbu-KA-ya-mba-li | Garanzadume (`Duchy41Capital`) | rain caught by branches; connected canopy country |
| `Duchy42` | Mburepangara | mburepa + ngara | mbu-RE-pa-nga-ra | Kambulepeli (`Duchy42Capital`) | wet timber and fresh growth; linked forest waterways |
| `Duchy43` | Kambulembali | kambule + mbali | ka-MBU-le-mba-li | Zarepawena (`Duchy43Capital`) | rain-fed undergrowth; connected canopy country |
| `Duchy44` | Mirayungara | mirayu + ngara | mi-RA-yu-nga-ra | Nzekayusumi (`Duchy44Capital`) | layered canopy; linked forest waterways |

#### Counties

| Existing county | Proposed name | Parent duchy | Construction | Pronunciation | Existing seat | Fictional name image |
| --- | --- | --- | --- | --- | --- | --- |
| `County195` | Kambulemela | Repayungara (`Duchy40`) | kambule + mela | ka-MBU-le-me-la | Mirumbunalo (`Kingdom9Capital`) | rain-fed undergrowth; local forest drainage |
| `County196` | Ipamirudali | Repayungara (`Duchy40`) | ipamiru + dali | i-PA-mi-ru-da-li | Repayungali (`County196Capital`) | water beneath trees; waterside hinterland |
| `County197` | Mbukayamela | Repayungara (`Duchy40`) | mbukaya + mela | mbu-KA-ya-me-la | Kayumbabelo (`County197Capital`) | rain caught by branches; local forest drainage |
| `County198` | Kayipunadali | Repayungara (`Duchy40`) | kayipuna + dali | ka-YI-pu-na-da-li | Ipamiruruni (`County198Capital`) | water among roots; waterside hinterland |
| `County199` | Mirenzemela | Repayungara (`Duchy40`) | mirenze + mela | mi-RE-nze-me-la | Aygaranalo (`County199Capital`) | branches meeting overhead; local forest drainage |
| `County200` | Zarepadali | Mbukayambali (`Duchy41`) | zarepa + dali | za-RE-pa-da-li | Garanzadume (`Duchy41Capital`) | deep wooded country; waterside hinterland |
| `County201` | Aygaramela | Mbukayambali (`Duchy41`) | aygara + mela | ay-GA-ra-me-la | Mirayudume (`County201Capital`) | passage by boat; local forest drainage |
| `County202` | Zambayudali | Mbukayambali (`Duchy41`) | zambayu + dali | za-MBA-yu-da-li | Garipapeli (`County202Capital`) | dense tree cover; waterside hinterland |
| `County203` | Garayunmela | Mbukayambali (`Duchy41`) | garayun + mela | ga-RA-yun-me-la | Repenzawena (`County203Capital`) | wooden boats; local forest drainage |
| `County204` | Ayrependali | Mbukayambali (`Duchy41`) | ayrepen + dali | ay-RE-pen-da-li | Mbukayasumi (`County204Capital`) | streamside trees; waterside hinterland |
| `County205` | Nzekayumela | Mburepangara (`Duchy42`) | nzekayu + mela | nze-KA-yu-me-la | Kambulepeli (`Duchy42Capital`) | interwoven tree canopy; local forest drainage |
| `County206` | Mirayudali | Mburepangara (`Duchy42`) | mirayu + dali | mi-RA-yu-da-li | Zambayungali (`County206Capital`) | layered canopy; waterside hinterland |
| `County207` | Karemimela | Mburepangara (`Duchy42`) | karemi + mela | ka-RE-mi-me-la | Karemibelo (`County207Capital`) | regrowth around old trunks; local forest drainage |
| `County208` | Mburepadali | Mburepangara (`Duchy42`) | mburepa + dali | mbu-RE-pa-da-li | Penayuruni (`County208Capital`) | wet timber and fresh growth; waterside hinterland |
| `County209` | Mirumbumela | Mburepangara (`Duchy42`) | mirumbu + mela | mi-RU-mbu-me-la | Nzepiranalo (`County209Capital`) | rain through tall trees; local forest drainage |
| `County210` | Repayudali | Kambulembali (`Duchy43`) | repayu + dali | re-PA-yu-da-li | Zarepawena (`Duchy43Capital`) | wood for shared construction; waterside hinterland |
| `County211` | Garipamela | Kambulembali (`Duchy43`) | garipa + mela | ga-RI-pa-me-la | Kayipunadume (`County211Capital`) | boat landing water; local forest drainage |
| `County212` | Penayudali | Kambulembali (`Duchy43`) | penayu + dali | pe-NA-yu-da-li | Garayunpeli (`County212Capital`) | timber carried along paths; waterside hinterland |
| `County213` | Kamayumela | Kambulembali (`Duchy43`) | kamayu + mela | ka-MA-yu-me-la | Mburepawena (`County213Capital`) | green understory; local forest drainage |
| `County214` | Garanzadali | Kambulembali (`Duchy43`) | garanza + dali | ga-RA-nza-da-li | Kamayusumi (`County214Capital`) | boat routes into forest; waterside hinterland |
| `County215` | Kayumbamela | Mirayungara (`Duchy44`) | kayumba + mela | ka-YU-mba-me-la | Nzekayusumi (`Duchy44Capital`) | rain-washed trunks; local forest drainage |
| `County216` | Repenzadali | Mirayungara (`Duchy44`) | repenza + dali | re-PE-nza-da-li | Ipazamengali (`County216Capital`) | woodland building ground; waterside hinterland |
| `County217` | Nzepiramela | Mirayungara (`Duchy44`) | nzepira + mela | nze-PI-ra-me-la | Mirenzebelo (`County217Capital`) | trees beside running water; local forest drainage |
| `County218` | Ipazamedali | Mirayungara (`Duchy44`) | ipazame + dali | i-PA-za-me-da-li | Ayrepenruni (`County218Capital`) | water through forest; waterside hinterland |
| `County219` | Kambuledali | Mirayungara (`Duchy44`) | kambule + dali | ka-MBU-le-da-li | Mirumbudume (`County219Capital`) | rain-fed undergrowth; waterside hinterland |

### Assignment and originality checks

The 273 identifiers are a one-to-one match to the current Land hierarchy.
All county-to-duchy and duchy-to-kingdom assignments match scene parent paths.
Seats are selected from current capital settlements by county/duchy/kingdom
metadata, allowing a kingdom capital to serve lower territorial levels.
All 273 final territorial names are mutually distinct and have no exact
full-name duplicates in the settlement or person registers.

Quoted complete-name web searches were completed for all **273 initial
candidates**, followed by **28 first-round revisions** and **one further
replacement**. No results were returned for the nine final kingdom names.
Screening is not a guarantee of worldwide uniqueness, and apparent OCR or
ordinary-word matches are not automatically names.

| Initial candidate or family | Revision | Reason |
| --- | --- | --- |
| Syratorn | Syratornek | Existing Swedish industrial term in the [Norrland business archive](https://nin.nu/digitalt-arkiv/); use the extended local-region formative ornek |
| Desert county -eth | -eshal, with Amarveshal using -veshal | Initial Aruketh appeared as a game-character name, Amareth as a handle/name, and Kisareth as an [existing game studio](https://www.indiedb.com/company/kisareth-studios). Extend the whole family; a second name-like match prompted Amareshal → Amarveshal |
| Desert county -adan | -adren | Initial Arukadan matched an existing surname on a [company's own site](https://hibasgroup.com/), while Amaradan matched a commercial mark. Revise the family rather than retain inconsistent short forms |
| Desert duchy -urak | -uraven | Amarurak appeared in an indexed personal-name context; lengthen the form for both affected duchies |
| Desert kingdom Amaruzan | Amaruzara | The initial spelling matched an existing given name; replace the realm formative uzan with uzara |

The revised spelling ledger below records every changed identifier, including
the intermediate Amareshal form, so screening decisions remain auditable.

| Territory ID | Initial candidate | Final name |
| --- | --- | --- |
| `County002` | Syratorn | Syratornek |
| `Kingdom4` | Amaruzan | Amaruzara |
| `Duchy16` | Amarurak | Amaruraven |
| `Duchy18` | Arukurak | Arukuraven |
| `County073` | Aruketh | Arukeshal |
| `County074` | Pazekadan | Pazekadren |
| `County075` | Amareth → Amareshal | Amarveshal |
| `County076` | Tumaradan | Tumaradren |
| `County077` | Kisareth | Kisareshal |
| `County078` | Soruvadan | Soruvadren |
| `County079` | Kiraiveth | Kiraiveshal |
| `County080` | Azekadan | Azekadren |
| `County081` | Tusereth | Tusereshal |
| `County082` | Zoruvadan | Zoruvadren |
| `County083` | Sazeleth | Sazeleshal |
| `County084` | Raituvadan | Raituvadren |
| `County085` | Arukadan | Arukadren |
| `County086` | Pazeketh | Pazekeshal |
| `County087` | Amaradan | Amaradren |
| `County088` | Tumareth | Tumareshal |
| `County089` | Kisaradan | Kisaradren |
| `County090` | Soruveth | Soruveshal |
| `County091` | Kiraivadan | Kiraivadren |
| `County092` | Azeketh | Azekeshal |
| `County093` | Tuseradan | Tuseradren |
| `County094` | Zoruveth | Zoruveshal |
| `County095` | Sazeladan | Sazeladren |
| `County096` | Raituveth | Raituveshal |

Retained incidental matches include Imnelesh in an automatically generated
anagram list, Syratesh in conversational transliteration, Tanahuhena inside
historical prose, and Ventavance across concatenated text. These were not
identified as existing place or character names and were not used as sources
for the coined names.

For reproduction, take roots in their original biome-ledger order. Sort
territories by numeric ID within each kingdom and rank. For county index i,
select root `(5*i + 2) mod root_count` and local formative
`(i + floor(i/root_count)) mod 2`. For duchy index i, select root
`(7*i + 5) mod root_count` and alternate the two regional forms. The kingdom
roots were selected individually for their broad environmental image, not
derived from the royal seat. Apply the recorded revisions and stress/joining
rules. The printed tables are authoritative; these formulas distribute the
authored vocabulary and do not assert linguistic history.

### Additional research sources

Consulted 2026-11-07. Earlier biome source references continue to supply the
mixed-root etymological inspirations.

- **TN1:** University of Hawaiʻi at Hilo, [*Papa Wehewehe ʻŌlelo / Glossary*](https://hilo.hawaii.edu/strategicplan/2021-31/glossary.php),
  ʻāina, land/earth/island. Only this ordinary land word motivates naya.
- **TN2:** Peru Ministry of Education, [*Urin qichwa qillqay*, Southern Quechua writing manual](https://cdn.www.gob.pe/uploads/document/file/5013101/manual-escritura-quechua-sur_comprimido.pdf),
  indexed suyu / región entry; direct PDF retrieval returned 403 during this
  pass. Corroborating region/territory senses appear in the [Quechua–Spanish dictionary, volume 2](https://fcctp.usmp.edu.pe/librosfcctp/DICCIONARIO-Quechua-espanol-VOL_2.pdf).
  Historical division names are not copied.
- **TN3:** Ó Dónaill, *Foclóir Gaeilge–Béarla*, [tír](https://www.teanglann.ie/en/fgb/t%C3%ADr),
  land/country and region/district senses. The entry's real territorial and
  mythological names are not reused.
- **TN4:** Larousse, [pays](https://www.larousse.fr/dictionnaires/francais/pays/58825),
  country and region senses. No modern French administrative institution is
  imported into the fictional hierarchy.

## Coverage and future additions

All nine requested kingdoms now have initial settlement, person-name, and territorial
registers. Completion here means authored assignments, not user approval of
every individual name or implementation in the game.

| Biome | Settlements | Existing rulers |
| --- | --- | --- |
| Desert | 64 | 24 |
| Tundra / Frozen Mountains | 77 | 24 |
| Volcanic Mountains / Ruins | 157 | 24 |
| Evergreen Temperate Rainforest | 226 | 25 |
| Tropical Rainforest | 192 | 25 |
| Swamp | 192 | 24 |
| Temperate Mountains | 258 | 24 |
| Deciduous Forest | 695 | 25 |
| Grassland | 359 | 25 |
| **Total** | **2,220** | **220** |

For additional biomes or new settlements, record the source palette, fictional
sound rules, root/endings ledger, research, and exact assignments. Check new
names against all nine biomes and all three naming categories. The territorial
register adds 220 counties, 44 duchies, and 9 kingdoms to the totals above.
Keep dynasties and any later surname system as separate decisions.
Earlier screening limitations, including
the Deciduous Forest web-search gaps, remain as documented in their sections.

## Research sources

Consulted 2026-11-06. Sources establish the stated inspirations, not the invented
names or their fictional meanings. Short glosses are paraphrased where appropriate.

- **S1:** David Sudlow, [*The Tamasheq of North-East Burkina Faso: Notes on Grammar
  and Syntax Including a Key Vocabulary*](https://www.temehu.com/imazighen/dictionaries/Amawals/Tamasheq-of-North-East-Burkina-Faso-Notes-on-Grammar-and-Syntax-Including-a-Key-Vocabulary.pdf).
  Vocabulary records `aman`, water/liquid.
- **S2:** [Tamazgha lexicon](https://www.amazigharchive.org/lexicon), entries `aman`
  and `adrar`. Secondary cross-variety reference; do not extend its generalizations
  into claims about every local naming practice.
- **S3:** [Bargery Hausa dictionary, R entries](https://www.hausadictionary.com/r_bargeryhausa),
  including `rairayi` and `ruwa`. A historical dictionary transcription, used for
  basic lexical inspiration rather than current naming etiquette.
- **S4:** Michael Schnegg, [“There was no future in the past: Time and the environment
  in rural Namibia”](https://www.ethnologie.uni-hamburg.de/pdfs/michael-schnegg/schnegg-m-2023-there-was-no-future-in-the-past.pdf),
  *HAU* 13(1), 2023, especially the seasonal discussion on PDF page 6.
- **S5:** National Park Service, [“The Mogollon”](https://home.nps.gov/gicl/learn/historyculture/the-mogollon.htm).
  Archaeological naming, sheltered dwellings, and stream access at Gila.
- **S6:** Milo Kalectaca, edited by Ronald W. Langacker, [*Lessons in Hopi*](https://hopidictionary.com/wp-content/uploads/2024/10/learnhopi.pdf),
  1978, printed pp. 114–115 / PDF pp. 122–123 and vocabulary. `kiihu` and `paasa`
  ground the dwelling and field inspirations; the game's compounds are not Hopi.
- **S7:** Indian Pueblo Cultural Center, [FAQs](https://indianpueblo.org/faqs/).
  Distinct Pueblo tribes and languages; context for avoiding a single “Pueblo language.”
- **S8:** [Navajo Particle Lexicon](https://talkingdictionary.swarthmore.edu/navajo_particle/?entry=3644),
  example `Tsé ’éí háadi?`, with rock gloss. Authorship is credited on the lexicon.
- **S9:** Mescalero Apache Tribe Language Program, [*Apache Scout*, June 2017](https://mescaleroapachetribe.com/apachescout/as-june-2017/),
  “Some Apache Language Words for the Feast,” `tú`, water. For differences between
  Apache varieties, see also the [Dilzhe’e dictionary spelling guide](https://dilzhee.western-apache.org/Spelling).

## Decision log

| Date | Decision | Authority |
| --- | --- | --- |
| 2026-11-06 | Distinct biome naming, mixed real-language inspiration, settlement/person categories; start with desert and seven specified inspirations | User brief |
| 2026-11-06 | All seven across the tradition; a smaller blend in each name | User clarification |
| 2026-11-06 | Concrete language selections, sound rules, mixed roots, invented architectural endings, 64 assignments | First authored proposal |
| 2026-11-06 | Mogollon contribution is architectural; invented endings are not attributed to an undocumented language | Research boundary |
| 2026-11-06 | Assignment register only; individual names await review, game display names not changed | Scope of this pass |
| 2026-11-06 | Extend the same approach to desert person names, including all counts, dukes, and the king | User follow-up |
| 2026-11-06 | Mononyms, title-first display, ungendered name forms, personal naming wishes, and assignments for all 24 existing courts | Authored person-name proposal |
| 2026-11-06 | Record shared seats explicitly; do not infer five additional incumbents or a legal rule of combined titles from scene co-location | Current court structure and scope decision |
| 2026-11-07 | Add both settlement and person names for tundra/frozen mountains, using Inuit, Aleut, Nordic, Nenet, and Siberian inspiration | User follow-up |
| 2026-11-07 | Select Inuktut, Unangam Tunuu, Norwegian/Icelandic, Yamal Nenets, and Evenki sources; use first-syllable stress and separate fictional roots/endings | Authored tundra proposal |
| 2026-11-07 | Assign all 77 Kingdom 1 settlements and all 24 current courts; screen candidates, document revisions, and retain document-only status | Authored tundra proposal and verified scene inventory |
| 2026-11-07 | Add both settlement and person names for Volcanic Mountains/Ruins using Hawaiian, Japanese, and Indonesian inspiration | User follow-up |
| 2026-11-07 | Select ordinary Hawaiian/Japanese/Bahasa Indonesia roots; use open syllables, third-last-syllable stress, invented habitation endings, and renewal imagery | Authored volcanic proposal |
| 2026-11-07 | Assign 157 Kingdom 2 settlements and 24 existing courts, screen full names, revise two candidates, and record incidental overlaps; retain document-only status | Authored volcanic proposal and scene inventory |
| 2026-11-07 | Add evergreen temperate rainforest settlement and person names using Pacific Northwest cultures and languages | User follow-up |
| 2026-11-07 | Select Lushootseed, Tlingit, and historically attested Chinuk Wawa vocabulary; use final stress, mixed stems, invented habitation endings and personal tails | Authored rainforest proposal |
| 2026-11-07 | Assign all 226 Kingdom 6 settlements and 25 courts (20 counts, 4 dukes, 1 king); screen full names and record revisions, preserving document-only scope | Current scene inventory and authored rainforest proposal |
| 2026-11-07 | Add tropical rainforest settlement and person names drawing from Amazon, Congo, Borneo, and New Guinea cultures and languages | User follow-up |
| 2026-11-07 | Select Nheengatu, Lingala, Iban, and West Kewa roots; use second-syllable stress, nasal clusters, mixed stems, invented habitation endings and personal tails | Authored tropical proposal |
| 2026-11-07 | Assign all 192 Kingdom 9 settlements and 25 courts, screen 217 candidates and two replacements, and retain document-only scope | Current scene inventory and authored tropical proposal |
| 2026-11-07 | Add swamp settlement and person names inspired by Uros, Aztec, Cajan, and Native Louisiana cultures/languages | User follow-up |
| 2026-11-07 | Interpret Cajan as Cajun; select documented Uru/Uchumataqu, historical Nahuatl, Cajun French, Tunica, and Biloxi forms; distinguish the real languages and source periods | Editorial assumption and authored swamp proposal |
| 2026-11-07 | Use penultimate stress, soft consonants, mixed stems, invented habitation endings and personal tails; assign 192 Kingdom 7 settlements and 24 courts, including County 220 | Authored swamp proposal and current scene inventory |
| 2026-11-07 | Screen 216 initial candidates and four replacements; retain documentation-only scope | Swamp review process |
| 2026-11-07 | Add temperate mountain settlement and person names drawing on Indigenous Andes, especially Incan, Himalayan, and Rocky Mountain cultures/languages | User follow-up |
| 2026-11-07 | Emphasize Quechua in 19 of 24 stem families; blend Sherpa, documented Northern Ute material, and Blackfoot; use initial stress and separate invented settlement endings/personal tails | Authored temperate mountain proposal |
| 2026-11-07 | Assign all 258 Kingdom 3 settlements and 24 courts; screen 282 initial names and replacements, revise a place-like family and one person candidate, preserve document-only scope | Current scene inventory and review process |
| 2026-11-07 | Add Deciduous Forest settlements and rulers using Celtic, Slavic, Korean, and Iroquoian inspiration; give this and the future Grassland scheme a clearer European feel | User follow-up |
| 2026-11-07 | Select Irish, Polish, Korean, and Mohawk; combine one European-source and one Korean/Mohawk element in every root, with initial stress and compact consonant endings | Authored deciduous forest proposal |
| 2026-11-07 | Assign 695 Kingdom 8 settlements and 25 existing courts (20 counts, 4 dukes, 1 king); retain exact identifiers and document-only scope | Current scene inventory |
| 2026-11-07 | Review 316 initial settlement candidates through web search, revise seven overlaps, and record rate-limited screening gaps; validate all final names locally | Deciduous forest review process |
| 2026-11-07 | Complete Grassland settlements and rulers with Germanic, French, Plains North American, Eurasian Steppe, Mongolian, and Zulu inspiration, retaining the requested European sound | User follow-up |
| 2026-11-07 | Select German, French, Lakota, Kazakh, Mongolian, and Zulu; pair European-source fragments with one of the other four sources, use initial stress and flowing settlement endings | Authored grassland proposal |
| 2026-11-07 | Assign all 359 Kingdom 5 settlements and 25 existing courts; retain exact identifiers, shared-seat distinctions, and documentation-only scope | Current scene inventory |
| 2026-11-07 | Screen all 384 initial names and 74 revised spellings; revise recurrent collision-prone endings and one root family, then verify assignments and local uniqueness | Grassland review process |
| 2026-11-07 | All nine requested kingdoms have initial registers: 2,220 settlements and 220 rulers; retain earlier screening caveats and separate future kingdom/dynasty naming decisions | Coverage audit |
| 2026-11-07 | Apply all 220 assigned person names to Court display_name and ruler_name in Map.tscn, preserving titles and existing court assignments; defer settlement-name integration | User request and court-label integration |
| 2026-11-07 | Add the settlement name as the Details-page heading; apply all 2,220 assigned settlement display names so headings and map tooltips use the authored names | User request for settlement-name headings |
| 2026-11-07 | Name every county, duchy, and kingdom using the established biome schemes, adding relevant research where useful | User follow-up |
| 2026-11-07 | Assign all 220 counties, 44 duchies, and 9 kingdoms, preserving scene IDs, parent hierarchy, shared seats, and County220 in Duchy33 | Verified scene inventory and authored territorial proposal |
| 2026-11-07 | Reuse mixed roots with regional formatives; add Hawaiian land, Quechua region, Irish land/country, and French country/region inspirations; preserve biome stress and sound rules | Territorial design and sources TN1–TN4 |
| 2026-11-07 | Screen 273 initial candidates and 29 replacement spellings; document revisions, constructions, pronunciations, fictional images, and exact assignments; leave territorial game integration for a separate change | Territorial review and scope |
