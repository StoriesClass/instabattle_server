from .schemas import BattleSchema, EntrySchema, UserSchema

battle_schema = BattleSchema()
battles_list_schema = BattleSchema(many=True)
entry_schema = EntrySchema()
entries_list_schema = EntrySchema(many=True)
user_schema = UserSchema()
users_list_schema = UserSchema(many=True)