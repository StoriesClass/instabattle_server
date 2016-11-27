from .schemas import BattleSchema, EntrySchema

battle_schema = BattleSchema()
battles_list_schema = BattleSchema(many=True)
entry_schema = EntrySchema()
entries_list_schema = EntrySchema(many=True)
