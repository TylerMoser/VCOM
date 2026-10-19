## 10, revisited · The map as it was when 10 was revisited (commit c2e885c), at the standard views,
## captioned for 10's variants. 10b has been applied since, so kit.as_revisited() takes it, 14b and
## 19a back out.
extends RefCounted

const NAME := "The map as it is now"
const LABEL := "10 now"


func apply(kit) -> void:
	kit.as_revisited()
