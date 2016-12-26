  http POST instabattle2.herokuapp.com/users/ username=yung_lean email=yung@le.an password=123
  http POST instabattle2.herokuapp.com/users/ username=wackloner email=wack@lon.er password=qwerty
  http POST instabattle2.herokuapp.com/users/ username=snoop_dogg email=snoop@dogg.gg password=123
  http POST instabattle2.herokuapp.com/users/ username=egor_bb email=msicar.ot.on.yas@gmail.com password=123
  http POST instabattle2.herokuapp.com/battles/ user_id=3 latitude=59.9342889 longitude=30.30667 name="St. Isaac's Cathedral" radius=300 description="One of the most famous SPb buildings" -a snoop_dogg:123
  http POST instabattle2.herokuapp.com/entries/ latitude=0 longitude=0 user_id=1 battle_id=1
  http POST instabattle2.herokuapp.com/entries/ latitude=0 longitude=0 user_id=3 battle_id=1
  http POST instabattle2.herokuapp.com/entries/ latitude=0 longitude=0 user_id=4 battle_id=1
  http GET instabattle2.herokuapp.com/entries/
