# Quest journal

The pause menu's Quests tab sits between Campaign and Roster, with Main Quests,
Major Quests, and Minor Quests sub-tabs. The settlement Quest Board instead
shows one combined list without sub-tabs. Both use a scrolling list on the left
(one third of the width) and independently scrolling details on the right.
Type appears below the title as Main Quest,
Major Quest, or Minor Quest, followed by description and the remaining details.
The menu uses the existing item detail typography.

Lists start empty. `Campaign.quests` holds `Quest` resources; each resource
has a category, title, description, objectives, status, quest giver, location,
and rewards. Status is Active, Completed or Failed. Objectives and rewards
are multiline display text. These fields describe the journal entry; they do
not grant rewards or implement quest progression.

Opening the pause menu refreshes all categories and starts on Main Quests.
Each list's selected resource is retained when
possible, otherwise the first entry is selected. Mouse clicks or keyboard/
gamepad focus select a quest. Down from the journal sub-tab row or settlement
tab row enters the selected quest. An empty list shows an empty-list message
and detail hint.

## Accepting quests

County 115's capital opens on Details, then Court of Count, Quest Board,
Hiring Board, and Market.
Its `Resources/Locations/County115QuestBoard.tres` resource starts empty;
populate its `quests` array with Quest resources to offer them in game.
The board combines all quest types and uses the same details as the journal, with an
Accept Quest button fixed at bottom-right. Enter/Space/gamepad A on a quest
moves focus to that button; activating the button accepts the selected quest.

`Campaign.quests_on(board)` returns the remaining runtime offers. These are
copies of authored quests, retained across settlement visits for this session.
`Campaign.accept_quest(board, quest)` removes an offered quest and adds it to
`Campaign.quests`, rejecting unavailable or already accepted entries. The UI
refreshes the list and disables acceptance when the board is empty, returning
focus to the settlement tabs. No cost or reward is applied.

Run `Godot --headless --path vcom res://Tests/QuestBoardTest.tscn` to
check acceptance, repeated acceptance, source isolation, return visits,
combined board list, journal categories, type labels, empty-board focus, and the
settlement's authored board order.
